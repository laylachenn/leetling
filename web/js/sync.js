// Sync progress across devices through a private GitHub Gist (a port lives in
// Sources/Leetling/Store/Sync.swift; keep the merge rules identical).
//
// Each device remembers the "base": the copy it last agreed on with the gist. Syncing is a
// three-way merge of base, this device, and the gist, so progress made on several devices
// between syncs adds up instead of one copy overwriting the other:
// - counters (unopened packs, Leetling copies, attempts, packs opened, times accepted):
//   gist + (this device − base), so packs opened or Leetlings evolved on one device stay spent
// - sets (dex caught, bonus days, milestones, topics, peeks) and the day log: union
// - hints revealed: the higher count; first/last solve dates: earliest/latest
// - settings, buddy and drafts: whichever side changed since the base (this device on a tie)

export const GIST_FILE = "leetling-progress.json";
const GIST_DESCRIPTION = "Leetling progress 🐰 (synced by the Leetling app, please don't edit by hand)";
const API = "https://api.github.com";

const SET_FIELDS = ["solutionPeeked", "caught", "goalBonusDays", "milestonesClaimed", "topicsCompleted"];
const SCALAR_FIELDS = ["buddy", "mode", "topic", "dailyGoal", "randomPick", "randomPickDay", "showDesktopBuddy", "name"];

const sortSet = (arr) => [...new Set(arr)].sort((a, b) =>
  typeof a === "number" && typeof b === "number" ? a - b : String(a).localeCompare(String(b)));
const union = (a = [], b = []) => sortSet([...a, ...b]);
const num = (v) => (typeof v === "number" && isFinite(v) ? v : 0);
const same = (a, b) => JSON.stringify(a ?? null) === JSON.stringify(b ?? null);
const keys = (...objs) => [...new Set(objs.flatMap((o) => Object.keys(o || {})))];

/** Three-way merge. `base` may be null (first sync of a device that has its own progress: add both up). */
export function mergeProgress(base, local, remote) {
  base = base || {};
  const out = { ...remote, ...local };
  const counter = (b, l, r) => Math.max(0, num(r) + num(l) - num(b));
  const pick = (b, l, r) => (same(l, b) ? r : l);

  out.packs = {};
  for (const k of keys(local.packs, remote.packs)) {
    out.packs[k] = counter(base.packs?.[k], local.packs?.[k], remote.packs?.[k]);
  }
  out.attempts = {};
  for (const k of keys(local.attempts, remote.attempts)) {
    out.attempts[k] = counter(base.attempts?.[k], local.attempts?.[k], remote.attempts?.[k]);
  }
  out.packsOpened = counter(base.packsOpened, local.packsOpened, remote.packsOpened);

  out.collection = {};
  for (const k of keys(local.collection, remote.collection)) {
    const [b, l, r] = [base.collection?.[k], local.collection?.[k], remote.collection?.[k]];
    const count = counter(b?.count, l?.count, r?.count);
    out.collection[k] = { count, shiny: Math.min(count, counter(b?.shiny, l?.shiny, r?.shiny)) };
  }

  out.solved = {};
  for (const k of keys(local.solved, remote.solved)) {
    const [b, l, r] = [base.solved?.[k], local.solved?.[k], remote.solved?.[k]];
    if (!l || !r) { out.solved[k] = { ...(l || r) }; continue; }
    out.solved[k] = {
      firstSolved: l.firstSolved < r.firstSolved ? l.firstSolved : r.firstSolved,
      lastSolved: l.lastSolved > r.lastSolved ? l.lastSolved : r.lastSolved,
      timesAccepted: Math.max(1, counter(b?.timesAccepted, l.timesAccepted, r.timesAccepted)),
    };
  }

  out.dayLog = {};
  for (const k of keys(local.dayLog, remote.dayLog)) out.dayLog[k] = union(local.dayLog?.[k], remote.dayLog?.[k]);

  out.hintsRevealed = {};
  for (const k of keys(local.hintsRevealed, remote.hintsRevealed)) {
    out.hintsRevealed[k] = Math.max(num(local.hintsRevealed?.[k]), num(remote.hintsRevealed?.[k]));
  }

  out.drafts = {};
  for (const k of keys(local.drafts, remote.drafts)) {
    const v = pick(base.drafts?.[k], local.drafts?.[k], remote.drafts?.[k]);
    if (typeof v === "string") out.drafts[k] = v;
  }

  for (const f of SET_FIELDS) out[f] = union(local[f], remote[f]);
  for (const f of SCALAR_FIELDS) out[f] = pick(base[f], local[f], remote[f]) ?? null;
  if (out.buddy && !out.caught.includes(out.buddy)) out.buddy = local.buddy ?? remote.buddy ?? null;
  return out;
}

/** A stable string for "did anything change?": sorted keys, sets sorted (Swift writes sets in any order). */
export function canonical(p) {
  const norm = (v, path) => {
    if (Array.isArray(v)) return SET_FIELDS.includes(path) || path === "dayLog" ? sortSet(v) : v.map((x) => norm(x));
    if (v && typeof v === "object") {
      return Object.fromEntries(Object.keys(v).sort().map((k) => [k, norm(v[k], path === "dayLog" ? "dayLog" : path ? path + "." + k : k)]));
    }
    return v;
  };
  return JSON.stringify(norm(p, ""));
}

/** "Fresh" = nothing worth keeping yet, so the first sync can just adopt the gist's copy. */
export const isFresh = (p) => !Object.keys(p.solved || {}).length && !num(p.packsOpened) && !Object.keys(p.dayLog || {}).length;

// ---------------------------------------------------------------- GitHub Gist API

export class SyncError extends Error {
  constructor(message, { auth = false } = {}) {
    super(message);
    this.auth = auth;
  }
}

async function gh(token, path, { method = "GET", body, keepalive = false } = {}) {
  let res;
  try {
    res = await fetch(API + path, {
      method, keepalive, cache: "no-store",
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "X-GitHub-Api-Version": "2022-11-28",
        ...(body ? { "Content-Type": "application/json" } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new SyncError("Couldn't reach GitHub. Are you online? I'll try again later 🌙");
  }
  if (res.status === 401) throw new SyncError("GitHub didn't accept that token. It may have expired 🔑", { auth: true });
  if (res.status === 403 || res.status === 404) {
    if (path.startsWith("/gists/") && res.status === 404) return null; // the gist was deleted
    throw new SyncError("That token can't use gists. Make sure the “gist” box is ticked 🔑", { auth: true });
  }
  if (!res.ok) throw new SyncError(`GitHub had a hiccup (${res.status}). I'll try again later 🌙`);
  return res.status === 204 ? null : res.json();
}

/** Find the Leetling gist on this account, or null. */
export async function findGist(token) {
  for (let page = 1; page <= 10; page++) {
    const list = await gh(token, `/gists?per_page=100&page=${page}`);
    const hit = list.find((g) => g.files && g.files[GIST_FILE]);
    if (hit) return hit.id;
    if (list.length < 100) return null;
  }
  return null;
}

/** The progress stored in the gist, or null if the gist is gone. */
export async function readGist(token, id) {
  const g = await gh(token, `/gists/${id}?t=${Date.now()}`);
  const f = g?.files?.[GIST_FILE];
  if (!f) return null;
  let text = f.content;
  if (f.truncated) text = await (await fetch(f.raw_url, { cache: "no-store" })).text();
  try {
    return JSON.parse(text);
  } catch {
    throw new SyncError("The synced copy on GitHub looks scrambled, so I left it alone 🧶");
  }
}

export async function createGist(token, progress) {
  const g = await gh(token, "/gists", {
    method: "POST",
    body: { description: GIST_DESCRIPTION, public: false, files: { [GIST_FILE]: { content: JSON.stringify(progress, null, 2) } } },
  });
  return g.id;
}

export async function writeGist(token, id, progress, { keepalive = false } = {}) {
  const res = await gh(token, `/gists/${id}`, {
    method: "PATCH", keepalive,
    body: { files: { [GIST_FILE]: { content: JSON.stringify(progress, null, 2) } } },
  });
  if (res === null) throw new SyncError("The synced gist disappeared. Tap Sync now to make a new one 🌱");
}
