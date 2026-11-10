// Talks to the Pyodide worker. The worker can't be interrupted mid-run, so a run that takes too
// long (an infinite loop, say) gets the whole worker terminated and a fresh one started.

const LIMIT_MS = { run: 10000, submit: 30000 };

let worker = null;
let nextID = 1;
const pending = new Map();
let status = { state: "idle", version: null }; // idle | loading | ready | error
const statusListeners = new Set();

function setStatus(s) {
  status = { ...status, ...s };
  for (const fn of statusListeners) fn(status);
}

export const pythonStatus = () => status;
export function onPythonStatus(fn) {
  statusListeners.add(fn);
  return () => statusListeners.delete(fn);
}

function spawn() {
  worker = new Worker("js/runner-worker.js");
  worker.onmessage = (e) => {
    const job = pending.get(e.data.id);
    if (!job) return;
    pending.delete(e.data.id);
    clearTimeout(job.timer);
    if (e.data.ok) job.resolve(e.data);
    else job.reject(new Error(e.data.error));
  };
  worker.onerror = (e) => restart(e.message || "Python stopped unexpectedly");
}

function restart(reason = "Python was restarted") {
  worker?.terminate();
  worker = null;
  for (const job of pending.values()) {
    clearTimeout(job.timer);
    job.reject(new Error(reason));
  }
  pending.clear();
  setStatus({ state: "idle" });
}

function send(msg, timeoutMs) {
  if (!worker) spawn();
  const id = nextID++;
  return new Promise((resolve, reject) => {
    const timer = timeoutMs
      ? setTimeout(() => {
          pending.delete(id);
          restart();
          reject(Object.assign(new Error("timeout"), { timeout: true }));
        }, timeoutMs)
      : null;
    pending.set(id, { resolve, reject, timer });
    worker.postMessage({ id, ...msg });
  });
}

/** Start loading Python in the background (it's a ~10 MB download the first time). */
let warming = null;
export function warmUp() {
  if (status.state === "ready") return Promise.resolve();
  warming ??= (async () => {
    setStatus({ state: "loading" });
    try {
      const r = await send({ type: "warmup" }, 120000);
      setStatus({ state: "ready", version: r.version });
    } catch (e) {
      setStatus({ state: "error", error: String(e.message || e) });
    } finally {
      warming = null;
    }
  })();
  return warming;
}

const failure = (status, message) => ({ status, passed: 0, total: 0, results: [], message });

/** Judge code. Resolves to a RunResult-shaped object (see runner.py). Never rejects. */
export async function judge(pid, code, mode) {
  if (status.state !== "ready") await warmUp();
  if (status.state === "error") {
    return failure("setup_error",
      "Python couldn't load. It needs internet the first time; after that it's cached on your device. " +
      "Check your connection and try again 🌷");
  }
  try {
    const r = await send({ type: "judge", pid, code, mode }, LIMIT_MS[mode]);
    return r.result;
  } catch (e) {
    if (e.timeout) {
      warmUp();
      return failure("time_limit",
        `Your code ran for over ${LIMIT_MS[mode] / 1000}s, so I stopped it 🐢 Is there a loop that never ends, ` +
        "or a slow approach on a big input?");
    }
    restart();
    warmUp();
    const msg = String(e.message || e);
    if (/call stack|recursion/i.test(msg)) {
      return failure("runtime_error",
        "RecursionError: the recursion went deeper than the browser can handle.\n" +
        "(Is there a missing base case? If not, an iterative version will always work here 🌷)");
    }
    return failure("runtime_error", `Python stopped unexpectedly: ${msg}\nI restarted it, so you can try again.`);
  }
}
