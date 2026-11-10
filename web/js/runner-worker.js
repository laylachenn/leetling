// Runs Python in a Web Worker with Pyodide so a slow solution never freezes the page.
// The main thread kills this worker if a run takes too long (see python.js).
const PYODIDE_VERSION = "0.28.3";
importScripts(`https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/pyodide.js`);

// Relative URLs in a worker resolve against this file (js/), hence the ../data paths.
let ready = null;

async function boot() {
  const pyodide = await loadPyodide({ indexURL: `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/` });
  const [runner, judge, problems] = await Promise.all([
    fetch("../data/runner.py").then((r) => r.text()),
    fetch("judge.py").then((r) => r.text()),
    fetch("../data/problems-full.json").then((r) => r.text()),
  ]);
  pyodide.FS.writeFile("/home/pyodide/runner.py", runner);
  pyodide.FS.writeFile("/home/pyodide/judge.py", judge);
  pyodide.runPython("import sys; sys.path.insert(0, '/home/pyodide')");
  const mod = pyodide.pyimport("judge");
  mod.load(problems);
  const version = pyodide.runPython("import sys; sys.version.split()[0]");
  return { pyodide, judge: mod, version };
}

self.onmessage = async (event) => {
  const { id, type } = event.data;
  try {
    ready ??= boot();
    const env = await ready;
    if (type === "warmup") {
      self.postMessage({ id, ok: true, version: env.version });
      return;
    }
    const { pid, code, mode } = event.data;
    const json = env.judge.judge(pid, code, mode);
    self.postMessage({ id, ok: true, result: JSON.parse(json) });
  } catch (err) {
    ready = null;
    self.postMessage({ id, ok: false, error: String(err && err.message ? err.message : err) });
  }
};
