// The web app's store: a port of Sources/Leetling/Store/AppStore.swift.
// Progress is saved to localStorage in the *same JSON shape* as the Mac app's progress.json,
// so you can export from one and import into the other (Settings → Your data).

import { COPIES_TO_EVOLVE, DEX, DEX_BY_ID, PACK_KINDS, PACKS, rollPack } from "./dex.js";
import { canonical, createGist, findGist, isFresh, mergeProgress, readGist, writeGist } from "./sync.js";

export const CATEGORY_ORDER = [
  "Arrays & Hashing", "Two Pointers", "Sliding Window", "Stack", "Binary Search", "Linked List",
  "Trees", "Tries", "Heap / Priority Queue", "Backtracking", "Graphs", "Advanced Graphs",
  "1-D Dynamic Programming", "2-D Dynamic Programming", "Greedy", "Intervals",
  "Math & Geometry", "Bit Manipulation",
];

export const CATEGORY_EMOJI = {
  "Arrays & Hashing": "🧺", "Two Pointers": "👯‍♀️", "Sliding Window": "🪟", "Stack": "🥞",
  "Binary Search": "🔍", "Linked List": "🔗", "Trees": "🌳", "Tries": "🌷",
  "Heap / Priority Queue": "⛰️", "Backtracking": "🧶", "Graphs": "🕸️", "Advanced Graphs": "🌌",
  "1-D Dynamic Programming": "🧁", "2-D Dynamic Programming": "🍰", "Greedy": "🍓",
  "Intervals": "📅", "Math & Geometry": "📐", "Bit Manipulation": "💡",
};

export const MODES = {
  easyFirst: { label: "Easy First", emoji: "🌱", blurb: "All the Easys first, then Mediums, then Hards." },
  topic: { label: "By Topic", emoji: "📚", blurb: "Work through one topic in order, like a mini-course." },
  random: { label: "Random", emoji: "🎲", blurb: "A surprise problem each day. Shuffle if it's not vibing." },
};

export const STREAK_MILESTONES = [3, 7, 14, 21, 30, 45, 60, 75, 100, 150, 200, 365];
const DIFFICULTY_RANK = { Easy: 0, Medium: 1, Hard: 2 };
const STORAGE_KEY = "leetling.progress.v1";
const SYNC_KEY = "leetling.sync.v1";

// ---------------------------------------------------------------- days

const pad = (n) => String(n).padStart(2, "0");
/** Local-calendar "yyyy-MM-dd", same as the Mac app's DayKey. */
export const dayKey = (d = new Date()) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
export function daysAgo(n, from = new Date()) {
  const d = new Date(from.getFullYear(), from.getMonth(), from.getDate());
  d.setDate(d.getDate() - n);
  return d;
}
/** Swift's .iso8601 date strategy rejects fractional seconds, so drop them. */
const isoNow = () => new Date().toISOString().replace(/\.\d{3}Z$/, "Z");

/** The longest run of missed days that can still be mended. */
export const MAX_MEND_GAP = 7;

/** Same as LeetlingSnapshot.streakDetail in Swift: keep the two identical.
 *  Every problem beyond the first on a day is a make-up credit. Walking back from today, a gap of up to
 *  MAX_MEND_GAP missed days is mended (and counts toward the streak) if the days after it banked at least
 *  one credit per missed day. Credits are spent on the newest gap first. */
export function streakDetail(dayLog, now = new Date()) {
  const count = (d) => (dayLog[dayKey(d)] || []).length;
  let offset = count(now) > 0 ? 0 : 1;
  let total = 0, credit = 0;
  const mended = new Set();
  for (;;) {
    const c = count(daysAgo(offset, now));
    if (c > 0) { total++; credit += c - 1; offset++; continue; }
    if (total === 0) break;   // a gap needs solves after it to be mended
    let gap = 0;
    while (gap <= MAX_MEND_GAP && count(daysAgo(offset + gap, now)) === 0) gap++;
    if (gap > MAX_MEND_GAP || credit < gap) break;   // too long, or not made up yet
    credit -= gap;
    for (let i = 0; i < gap; i++) mended.add(dayKey(daysAgo(offset + i, now)));
    total += gap;
    offset += gap;
  }
  return { length: total, mended };
}

export function streakFrom(dayLog, now = new Date()) { return streakDetail(dayLog, now).length; }

/** If solving more today would mend a broken streak: { needed, wouldBe }, else null. */
export function mendHint(dayLog, now = new Date()) {
  const today = dayKey(now);
  const have = (dayLog[today] || []).length;
  // Only the length of today's list matters to the streak, so pad it with placeholders.
  const streakWith = (n) => streakFrom({ ...dayLog, [today]: Array(n).fill(0) }, now);
  const baseline = streakWith(Math.max(have, 1));
  for (let more = 1; more <= MAX_MEND_GAP + 1; more++) {
    const s = streakWith(have + more);
    if (s > baseline) return { needed: more, wouldBe: s };
  }
  return null;
}

// ---------------------------------------------------------------- progress

function defaultProgress() {
  return {
    solved: {}, attempts: {}, drafts: {}, hintsRevealed: {}, solutionPeeked: [], dayLog: {}, packs: {},
    collection: {}, caught: [], buddy: null, goalBonusDays: [], milestonesClaimed: [], topicsCompleted: [],
    mode: "easyFirst", topic: "Arrays & Hashing", dailyGoal: 1, randomPick: null, randomPickDay: null,
    showDesktopBuddy: false, packsOpened: 0, name: null,
  };
}

/** Like the Swift decoder: every field falls back to its default if missing or the wrong type. */
export function normalizeProgress(raw) {
  const d = defaultProgress();
  if (!raw || typeof raw !== "object") return d;
  const out = {};
  for (const [k, fallback] of Object.entries(d)) {
    const v = raw[k];
    const ok = Array.isArray(fallback) ? Array.isArray(v)
      : fallback === null ? v === null || typeof v === "string" || typeof v === "number"
      : typeof v === typeof fallback && !Array.isArray(v) && v !== null;
    out[k] = ok ? v : fallback;
  }
  if (!MODES[out.mode]) out.mode = "easyFirst";
  out.dailyGoal = Math.max(1, Math.min(4, Math.round(out.dailyGoal) || 1));
  // Keep any keys a newer app version might have written, so a round-trip doesn't lose them.
  return { ...raw, ...out };
}

function loadProgress() {
  try {
    const text = localStorage.getItem(STORAGE_KEY);
    if (text) return normalizeProgress(JSON.parse(text));
  } catch { /* fall through to a fresh start */ }
  const p = defaultProgress();
  p.packs.sprout = 1; // a little welcome gift so there's something to open on day one
  return p;
}

function loadSyncConfig() {
  try {
    const cfg = JSON.parse(localStorage.getItem(SYNC_KEY) || "null");
    if (cfg && typeof cfg.token === "string" && cfg.token) return cfg;
  } catch { /* not connected */ }
  return null;
}

const addToSet = (arr, v) => (arr.includes(v) ? arr : [...arr, v]);

// ---------------------------------------------------------------- store

class Store {
  constructor() {
    this.problems = [];
    this.byID = {};
    this.progress = loadProgress();
    this.celebration = null;
    this.listeners = new Set();
    this.saveTimer = null;
    // Gist sync (see sync.js). `syncConfig` = { token, gistId, base } lives in its own localStorage key.
    this.syncConfig = loadSyncConfig();
    this.syncStatus = { state: this.syncConfig ? "idle" : "off", lastSynced: null, message: null };
    this.syncTimer = null;
    this.syncRunning = Promise.resolve(); // the sync in flight (syncs run one at a time)
    this.syncQueued = null;               // the next sync, if one is waiting (extra requests join it)
    this.chooseSyncMerge = async () => "combine"; // replaced by the UI with a friendly dialog
  }

  setProblems(list) {
    this.problems = [...list].sort((a, b) => a.id - b.id);
    this.byID = Object.fromEntries(this.problems.map((p) => [p.id, p]));
    this.emit();
  }

  subscribe(fn) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  emit() {
    for (const fn of this.listeners) fn();
  }

  /** Apply a change to progress. `immediate` saves now (solves, packs); otherwise debounced. */
  update(fn, { immediate = false, silent = false } = {}) {
    const p = structuredClone(this.progress);
    fn(p);
    this.progress = p;
    clearTimeout(this.saveTimer);
    if (immediate) this.saveNow();
    else this.saveTimer = setTimeout(() => this.saveNow(), 400);
    this.scheduleSync(immediate ? 1500 : 8000);
    if (!silent) this.emit();
  }

  saveNow() {
    clearTimeout(this.saveTimer);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.progress));
    } catch (e) {
      console.warn("Leetling: couldn't save progress", e);
    }
  }

  // ------------------------------------------------------------ queries

  problem(id) { return this.byID[id]; }
  isSolved(id) { return this.progress.solved[String(id)] != null; }
  get solvedCount() { return this.problems.filter((p) => this.isSolved(p.id)).length; }
  get categories() { return CATEGORY_ORDER.filter((c) => this.problems.some((p) => p.category === c)); }
  problemsIn(category) { return this.problems.filter((p) => p.category === category); }
  solvedIn(category) { return this.problemsIn(category).filter((p) => this.isSolved(p.id)).length; }

  get easyFirstOrder() {
    return [...this.problems].sort((a, b) =>
      DIFFICULTY_RANK[a.difficulty] - DIFFICULTY_RANK[b.difficulty] || a.id - b.id);
  }

  get nextProblem() {
    const unsolved = (p) => !this.isSolved(p.id);
    switch (this.progress.mode) {
      case "topic": return this.problemsIn(this.progress.topic).find(unsolved) ?? null;
      case "random": {
        const p = this.problem(this.progress.randomPick);
        return p ?? this.problems.find(unsolved) ?? this.problems[0] ?? null;
      }
      default: return this.easyFirstOrder.find(unsolved) ?? null;
    }
  }

  ensureRandomPick() {
    if (this.progress.mode !== "random") return;
    if (this.progress.randomPickDay !== dayKey() || this.progress.randomPick == null) this.shuffleRandomPick();
  }

  shuffleRandomPick() {
    const current = this.progress.randomPick;
    let pool = this.problems.filter((p) => !this.isSolved(p.id) && p.id !== current);
    if (!pool.length) pool = this.problems.filter((p) => p.id !== current);
    const pick = pool[Math.floor(Math.random() * pool.length)];
    this.update((p) => {
      p.randomPick = pick?.id ?? null;
      p.randomPickDay = dayKey();
    });
  }

  // ------------------------------------------------------------ streaks

  get todayCount() { return (this.progress.dayLog[dayKey()] || []).length; }
  get streak() { return streakFrom(this.progress.dayLog); }

  /** The longest streak ever, mends included. */
  get bestStreak() {
    let best = 0;
    for (const k of Object.keys(this.progress.dayLog)) {
      if (!this.progress.dayLog[k].length) continue;
      const [y, m, d] = k.split("-").map(Number);
      best = Math.max(best, streakFrom(this.progress.dayLog, new Date(y, m - 1, d)));
    }
    return best;
  }

  get mendHint() { return mendHint(this.progress.dayLog); }

  get nextMilestone() { return STREAK_MILESTONES.find((m) => m > this.streak) ?? null; }

  /** The 7-day strip for the streak card, oldest first. */
  week(now = new Date()) {
    const { mended } = streakDetail(this.progress.dayLog, now);
    return [6, 5, 4, 3, 2, 1, 0].map((ago) => {
      const date = daysAgo(ago, now);
      const count = (this.progress.dayLog[dayKey(date)] || []).length;
      return { date, count, isToday: ago === 0, done: count > 0,
               mended: mended.has(dayKey(date)), goalMet: count >= this.progress.dailyGoal };
    });
  }

  // ------------------------------------------------------------ editor state

  draft(problem) { return this.progress.drafts[String(problem.id)] ?? problem.starter; }

  setDraft(problem, code) {
    if (this.progress.drafts[String(problem.id)] === code) return;
    this.update((p) => { p.drafts[String(problem.id)] = code; }, { silent: true });
  }

  resetDraft(problem) { this.update((p) => { p.drafts[String(problem.id)] = problem.starter; }); }
  hintsRevealed(problem) { return this.progress.hintsRevealed[String(problem.id)] ?? 0; }

  revealHint(problem) {
    this.update((p) => { p.hintsRevealed[String(problem.id)] = Math.min(3, this.hintsRevealed(problem) + 1); });
  }

  peekSolution(problem) { this.update((p) => { p.solutionPeeked = addToSet(p.solutionPeeked, problem.id); }); }
  recordAttempt(problem) { this.update((p) => { p.attempts[String(problem.id)] = (p.attempts[String(problem.id)] ?? 0) + 1; }); }

  // ------------------------------------------------------------ rewards

  recordAccepted(problem) {
    const now = new Date();
    const today = dayKey(now);
    const key = String(problem.id);
    const firstSolve = this.progress.solved[key] == null;
    const rewards = [];
    let streak = 0, todays = [], streakMended = false;
    const streakBefore = this.streak;

    this.update((p) => {
      const rec = p.solved[key];
      p.solved[key] = rec
        ? { ...rec, lastSolved: isoNow(), timesAccepted: rec.timesAccepted + 1 }
        : { firstSolved: isoNow(), lastSolved: isoNow(), timesAccepted: 1 };
      todays = addToSet(p.dayLog[today] || [], problem.id);
      p.dayLog[today] = todays;

      const give = (kind, reason) => {
        p.packs[kind] = (p.packs[kind] ?? 0) + 1;
        rewards.push({ pack: kind, reason });
      };

      if (firstSolve) give("sprout", `First time solving ${problem.title}`);

      if (todays.length >= p.dailyGoal && !p.goalBonusDays.includes(today)) {
        p.goalBonusDays = addToSet(p.goalBonusDays, today);
        give("bloom", p.dailyGoal === 1 ? "Daily goal reached!" : `Daily goal of ${p.dailyGoal} reached!`);
      }

      streak = streakFrom(p.dayLog, now);
      streakMended = streak > streakBefore + 1;
      const streakStart = dayKey(daysAgo(Math.max(0, streak - 1), now));
      for (const m of STREAK_MILESTONES) {
        if (streak < m) continue;
        const tag = `${streakStart}:${m}`;
        if (!p.milestonesClaimed.includes(tag)) {
          p.milestonesClaimed = addToSet(p.milestonesClaimed, tag);
          give("starlight", `${m}-day streak! 🔥`);
        }
      }

      if (firstSolve && !p.topicsCompleted.includes(problem.category) &&
          this.problemsIn(problem.category).every((q) => p.solved[String(q.id)] != null)) {
        p.topicsCompleted = addToSet(p.topicsCompleted, problem.category);
        give("starlight", `Finished every ${problem.category} problem!`);
      }
    }, { immediate: true, silent: true });

    this.celebration = { id: Math.random(), problemTitle: problem.title, firstSolve, rewards, streak,
                         streakMended, todayCount: todays.length, goal: this.progress.dailyGoal };
    this.emit();
  }

  dismissCelebration() {
    this.celebration = null;
    this.emit();
  }

  // ------------------------------------------------------------ packs & collection

  packCount(kind) { return this.progress.packs[kind] ?? 0; }
  get totalPacks() { return PACK_KINDS.reduce((n, k) => n + this.packCount(k), 0); }
  owned(id) { return this.progress.collection[id] ?? { count: 0, shiny: 0 }; }

  openPack(kind) {
    if (this.packCount(kind) <= 0) return null;
    const rolled = rollPack(kind);
    const pulls = [];
    this.update((p) => {
      p.packs[kind] -= 1;
      p.packsOpened += 1;
      for (const { critter, shiny } of rolled) {
        const isNew = !p.caught.includes(critter.id);
        p.caught = addToSet(p.caught, critter.id);
        const o = p.collection[critter.id] ?? { count: 0, shiny: 0 };
        p.collection[critter.id] = { count: o.count + 1, shiny: o.shiny + (shiny ? 1 : 0) };
        pulls.push({ critter, shiny, isNew });
      }
      if (!p.buddy) p.buddy = [...pulls].sort((a, b) => b.critter.rarity - a.critter.rarity)[0].critter.id;
    }, { immediate: true });
    return pulls;
  }

  canEvolve(critter) { return critter.evolvesTo != null && this.owned(critter.id).count >= COPIES_TO_EVOLVE; }
  get anyEvolvable() { return DEX.some((c) => this.canEvolve(c)); }

  /** Trade 3 copies for one of the next form. Non-shiny copies are used first. */
  evolve(critter) {
    if (!this.canEvolve(critter)) return null;
    const next = DEX_BY_ID[critter.evolvesTo];
    this.update((p) => {
      const from = { ...(p.collection[critter.id] ?? { count: 0, shiny: 0 }) };
      const normal = from.count - from.shiny;
      const shinyUsed = Math.max(0, COPIES_TO_EVOLVE - normal);
      from.count -= COPIES_TO_EVOLVE;
      from.shiny -= shinyUsed;
      p.collection[critter.id] = from;
      const to = p.collection[next.id] ?? { count: 0, shiny: 0 };
      p.collection[next.id] = { count: to.count + 1, shiny: to.shiny + (shinyUsed === COPIES_TO_EVOLVE ? 1 : 0) };
      p.caught = addToSet(p.caught, next.id);
      if (p.buddy === critter.id && from.count === 0) p.buddy = next.id;
    }, { immediate: true });
    return next;
  }

  get buddy() { return this.progress.buddy ? DEX_BY_ID[this.progress.buddy] ?? null : null; }
  setBuddy(critter) { this.update((p) => { p.buddy = critter.id; }, { immediate: true }); }

  // ------------------------------------------------------------ settings & data

  setMode(mode) {
    this.update((p) => { p.mode = mode; }, { immediate: true });
    if (mode === "random") this.ensureRandomPick();
  }

  setTopic(topic) { this.update((p) => { p.topic = topic; }, { immediate: true }); }
  setGoal(goal) { this.update((p) => { p.dailyGoal = Math.max(1, Math.min(4, goal)); }, { immediate: true }); }
  setName(name) { this.update((p) => { p.name = name || null; }); }

  get displayName() { return this.progress.name?.trim() || "friend"; }

  exportJSON() { return JSON.stringify(this.progress, null, 2); }

  importJSON(text) {
    const parsed = JSON.parse(text);
    if (!parsed || typeof parsed !== "object" || !("solved" in parsed || "dayLog" in parsed || "collection" in parsed)) {
      throw new Error("That file doesn't look like Leetling progress.");
    }
    this.progress = normalizeProgress(parsed);
    this.saveNow();
    this.emit();
    this.syncNow({ overwrite: true });
  }

  resetAll() {
    const p = defaultProgress();
    p.packs.sprout = 1;
    this.progress = p;
    this.saveNow();
    this.emit();
    this.syncNow({ overwrite: true });
  }

  // ------------------------------------------------------------ sync

  get syncConnected() { return !!this.syncConfig?.token; }

  saveSyncConfig() {
    try {
      if (this.syncConfig) localStorage.setItem(SYNC_KEY, JSON.stringify(this.syncConfig));
      else localStorage.removeItem(SYNC_KEY);
    } catch (e) {
      console.warn("Leetling: couldn't save sync settings", e);
    }
  }

  setSyncStatus(patch) {
    this.syncStatus = { ...this.syncStatus, ...patch };
    this.emit();
  }

  /** Changes since the last sync that the gist doesn't have yet. */
  get syncDirty() {
    const base = this.syncConfig?.base;
    return !base || canonical(base) !== canonical(this.progress);
  }

  scheduleSync(delay) {
    if (!this.syncConnected) return;
    clearTimeout(this.syncTimer);
    this.syncTimer = setTimeout(() => { if (this.syncDirty) this.syncNow(); }, delay);
  }

  async connectSync(token) {
    this.syncConfig = { token: token.trim(), gistId: null, base: null };
    this.saveSyncConfig();
    const ok = await this.syncNow();
    if (!ok && this.syncStatus.auth) {
      this.syncConfig = null;
      this.saveSyncConfig();
      this.setSyncStatus({ state: "off" });
    }
    return ok;
  }

  disconnectSync() {
    clearTimeout(this.syncTimer);
    this.syncConfig = null;
    this.saveSyncConfig();
    this.setSyncStatus({ state: "off", lastSynced: null, message: null, auth: false });
  }

  /**
   * Pull the gist, merge it with this device, and push the result. `overwrite` replaces the gist
   * with this device's progress (after an import or a reset). Returns true when it worked.
   */
  syncNow({ overwrite = false, keepalive = false } = {}) {
    if (!this.syncConnected) return Promise.resolve(false);
    if (this.syncQueued) {
      this.syncQueued.overwrite ||= overwrite;
      return this.syncQueued.promise;
    }
    const job = { overwrite, keepalive };
    job.promise = this.syncRunning.then(() => {
      this.syncQueued = null;
      return this.runSync(job);
    });
    this.syncQueued = job;
    this.syncRunning = job.promise;
    return job.promise;
  }

  async runSync({ overwrite, keepalive }) {
    const cfg = this.syncConfig;
    if (!cfg?.token) return false;
    clearTimeout(this.syncTimer);
    this.setSyncStatus({ state: "syncing" });
    try {
      if (!cfg.gistId) cfg.gistId = await findGist(cfg.token);
      let remote = cfg.gistId ? await readGist(cfg.token, cfg.gistId) : null;
      if (!remote) {
        const snapshot = structuredClone(this.progress);
        cfg.gistId = await createGist(cfg.token, snapshot);
        cfg.base = snapshot;
      } else {
        remote = normalizeProgress(remote);
        let merged;
        if (overwrite) merged = this.progress;
        else if (cfg.base) merged = mergeProgress(cfg.base, this.progress, remote);
        else if (isFresh(this.progress)) merged = remote;
        else {
          const choice = await this.chooseSyncMerge();
          merged = choice === "remote" ? remote : mergeProgress(null, this.progress, remote);
        }
        merged = normalizeProgress(structuredClone(merged));
        // This device now holds everything in `remote`, so remote is the right base even if the push fails.
        cfg.base = remote;
        if (canonical(merged) !== canonical(this.progress)) {
          this.progress = merged;
          this.saveNow();
        }
        if (canonical(merged) !== canonical(remote)) await writeGist(cfg.token, cfg.gistId, merged, { keepalive });
        cfg.base = merged;
      }
      this.saveSyncConfig();
      this.setSyncStatus({ state: "idle", lastSynced: new Date(), message: null, auth: false });
      return true;
    } catch (e) {
      this.saveSyncConfig();
      console.warn("Leetling sync:", e);
      this.setSyncStatus({ state: "error", message: e.message || "Sync didn't work this time 🌙", auth: !!e.auth });
      return false;
    }
  }
}

export const store = new Store();
export { PACKS, PACK_KINDS };
