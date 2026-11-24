import { html, render, useEffect, useRef, useState } from "../vendor/preact-htm.mjs";
import { COPIES_TO_EVOLVE, DEX, ELEMENTS, lineOf, PACK_KINDS, PACKS, RARITIES, stars } from "./dex.js";
import { CodeEditor, KeyBar } from "./editor.js";
import { judge, onPythonStatus, pythonStatus, warmUp } from "./python.js";
import { CATEGORY_EMOJI, MODES, store } from "./store.js";
import { blockMD, inlineMD } from "./text.js";

// ---------------------------------------------------------------- routing & tiny utilities

const SECTIONS = [
  { id: "today", title: "Today", icon: "☀️" },
  { id: "problems", title: "Problems", icon: "📚" },
  { id: "packs", title: "Packs", icon: "🎁" },
  { id: "dex", title: "Leetdex", icon: "📖" },
  { id: "settings", title: "Settings", icon: "⚙️" },
];

function parseRoute() {
  const parts = location.hash.replace(/^#\/?/, "").split("/");
  if (parts[0] === "problem" && parts[1]) return { section: "problem", id: Number(parts[1]) };
  return { section: SECTIONS.some((s) => s.id === parts[0]) ? parts[0] : "today", id: null };
}

const go = (path) => { location.hash = "#/" + path; };
let lastSection = "today";

function useStore() {
  const [, force] = useState(0);
  useEffect(() => store.subscribe(() => force((n) => n + 1)), []);
  return store;
}

const plural = (n, word, many = word + "s") => `${n} ${n === 1 ? word : many}`;
const MD = ({ text, block = false, cls = "" }) =>
  html`<div class=${"md " + cls} dangerouslySetInnerHTML=${{ __html: block ? blockMD(text) : inlineMD(text) }}></div>`;

// A gentle confirm dialog (instead of window.confirm).
let showDialog = () => {};
function ask({ title, message, ok = "OK", cancel = "Cancel", danger = false }) {
  return new Promise((resolve) => showDialog({ title, message, ok, cancel, danger, resolve }));
}

function Dialog() {
  const [d, setD] = useState(null);
  showDialog = setD;
  if (!d) return null;
  const close = (v) => { setD(null); d.resolve(v); };
  // Tapping outside resolves null (falsy, so it still reads as "cancel" for yes/no questions).
  return html`<div class="overlay" onClick=${(e) => e.target === e.currentTarget && close(null)}>
    <div class="dialog card pop" role="dialog" aria-modal="true">
      <h3>${d.title}</h3>
      <p>${d.message}</p>
      <div class="row end gap">
        <button class="btn quiet" onClick=${() => close(false)}>${d.cancel}</button>
        <button class=${"btn " + (d.danger ? "danger" : "primary")} onClick=${() => close(true)}>${d.ok}</button>
      </div>
    </div>
  </div>`;
}

// ---------------------------------------------------------------- shared bits

const Pill = ({ text, color, filled }) =>
  html`<span class="pill" style=${filled ? { background: color, color: "#fff" } : { color, background: color + "24" }}>${text}</span>`;

const DIFF_COLOR = { Easy: "#4FB892", Medium: "#E89B3C", Hard: "#E8638F" };
const DifficultyPill = ({ difficulty }) => html`<${Pill} text=${difficulty} color=${DIFF_COLOR[difficulty]} />`;

const SectionTitle = ({ title, emoji }) => html`<h2 class="section-title"><span>${emoji}</span> ${title}</h2>`;

const ProgressBar = ({ value, colors = ["#FF8FB1", "#C8B6FF"], height = 8 }) =>
  html`<div class="bar" style=${{ height }}>
    <div style=${{ width: `${Math.max(0, Math.min(1, value)) * 100}%`, background: `linear-gradient(90deg, ${colors[0]}, ${colors[1]})` }}></div>
  </div>`;

function LeetlingArt({ critter, size = 48, silhouette = false }) {
  return html`<span class=${"art" + (silhouette ? " silhouette" : "")} style=${{ fontSize: size + "px" }}>
    ${critter.emoji}
    ${critter.accessory && !silhouette && html`<span class="acc" style=${{ fontSize: size * 0.42 + "px" }}>${critter.accessory}</span>`}
  </span>`;
}

function LeetlingCard({ critter, shiny = false, isNew = false, width = 150 }) {
  const el = ELEMENTS[critter.element];
  const r = RARITIES[critter.rarity];
  return html`<div class=${"lcard" + (shiny ? " shiny" : "")}
      style=${{ width: width + "px", background: `linear-gradient(180deg, ${el.colors[0]}, ${el.colors[1]})` }}>
    <div class="lcard-top"><span>${el.icon} ${el.name}</span><span style=${{ color: r.color }}>${stars(critter.rarity)}</span></div>
    <div class="lcard-art"><${LeetlingArt} critter=${critter} size=${width * 0.38} /></div>
    <div class="lcard-name">${critter.name}${shiny ? " ✨" : ""}</div>
    <div class="lcard-meta" style=${{ color: r.color }}>${r.name}${isNew ? html` · <b class="new">NEW!</b>` : ""}</div>
  </div>`;
}

const WEEKDAY = (d) => d.toLocaleDateString(undefined, { weekday: "short" }).slice(0, 2);

function StreakCard({ compact = false }) {
  const week = store.week();
  const streak = store.streak;
  const month = new Date().toLocaleDateString(undefined, { month: "long" });
  return html`<div class=${"streak-card" + (compact ? " compact" : "")}>
    <div class="sc-row sc-head">
      <div class="sc-label month">${month}</div>
      ${week.map((d) => html`<div class=${"sc-day" + (d.isToday ? " today" : "")}>
        <div>${d.date.getDate()}</div><div>${WEEKDAY(d.date)}</div></div>`)}
    </div>
    <div class="sc-row sc-strip">
      <div class="sc-label">
        <div class="sc-streak"><span class=${streak > 0 ? "flame on" : "flame"}>🔥</span>${streak}</div>
        <div class="sc-name">Leetling</div>
      </div>
      ${week.map((d) => html`<div class="sc-mark">${d.goalMet ? html`<span class="heart">♥</span>`
        : d.done ? html`<span class="check">✓</span>`
        : d.mended ? html`<span class="mend" title="Mended with extra solves">🩹</span>`
        : d.isToday ? html`<span class="ring"></span>` : html`<span class="dot"></span>`}</div>`)}
    </div>
  </div>`;
}

// ---------------------------------------------------------------- navigation

function Nav({ route }) {
  const badge = (id) => {
    if (id === "packs" && store.totalPacks > 0) return String(store.totalPacks);
    if (id === "dex" && store.anyEvolvable) return "✦";
    return null;
  };
  const active = route.section === "problem" ? lastSection : route.section;
  return html`<nav class="nav">
    <div class="brand">
      <span class="brand-buddy">${store.buddy?.emoji ?? "🥚"}</span>
      <div><div class="brand-name">Leetling</div><div class="brand-sub">Blind 75, one day at a time</div></div>
    </div>
    <div class="nav-items">
      ${SECTIONS.map((s) => html`<a href=${"#/" + s.id} class=${"nav-item" + (active === s.id ? " active" : "")}
          aria-current=${active === s.id ? "page" : undefined}>
        <span class="nav-icon">${s.icon}</span><span class="nav-title">${s.title}</span>
        ${badge(s.id) && html`<span class="badge">${badge(s.id)}</span>`}
      </a>`)}
    </div>
    <div class="nav-foot">
      <div class="nav-streak">🔥 ${store.streak}-day streak</div>
      <${ProgressBar} value=${store.solvedCount / Math.max(1, store.problems.length)} />
      <div class="muted small">${store.solvedCount} / ${store.problems.length} solved</div>
    </div>
  </nav>`;
}

// ---------------------------------------------------------------- Today

const ENCOURAGEMENT = [
  "Every expert was once a beginner who didn't quit. 🌱",
  "One problem a day keeps the interview nerves away. 💌",
  "You don't have to be fast. You just have to show up. 🐢💖",
  "Wrong answers are just hints in disguise. ✨",
  "Tiny steps, big bloom. 🌷",
  "Your future self is already proud of you. 🫶",
  "Brew a cozy drink and let's crack one open. ☕️",
  "Patterns > memorizing. You've got this. 🧠🎀",
  "Consistency is the cutest flex. 💅",
  "Hard problems are just easy problems in a trench coat. 🧥",
];

function greeting() {
  const h = new Date().getHours();
  if (h >= 5 && h < 12) return ["Good morning", "☀️"];
  if (h >= 12 && h < 17) return ["Good afternoon", "🌷"];
  if (h >= 17 && h < 22) return ["Good evening", "🌙"];
  return ["Hi night owl", "🦉"];
}

function TodayView() {
  useEffect(() => { store.ensureRandomPick(); }, []);
  const [hello, emoji] = greeting();
  const day = Math.floor(Date.now() / 86400000);
  return html`<div class="page">
    <header class="page-head">
      <h1>${hello}, ${store.displayName} ${emoji}</h1>
      <p class="muted">${ENCOURAGEMENT[day % ENCOURAGEMENT.length]}</p>
    </header>
    <div class="today-top">
      <div class="card"><${StreakCard} /></div>
      <${BuddyCard} />
    </div>
    <${ModePicker} />
    <${NextProblemCard} />
    ${store.totalPacks > 0 && html`<a class="packs-teaser" href="#/packs">
      <span class="big">🎁</span>
      <div><b>You have ${plural(store.totalPacks, "pack")} to open!</b><div class="small">Go see who's inside ✨</div></div>
      <span class="chev">›</span>
    </a>`}
    <${TopicGrid} />
  </div>`;
}

function BuddyCard() {
  const today = store.todayCount, goal = store.progress.dailyGoal, buddy = store.buddy;
  let message;
  const mend = store.mendHint;
  if (mend) message = `Solve ${today === 0 ? `${mend.needed} problem${mend.needed === 1 ? "" : "s"}` : `${mend.needed} more`} today to mend our streak back to ${mend.wouldBe}! 🩹🔥`;
  else if (store.problems.length && store.solvedCount === store.problems.length) message = "You finished the Blind 75?! I'm crying 😭💖";
  else if (today >= goal) message = today > goal ? "Overachiever!! I love you 💞" : "Goal met! I'm so proud of you 💖";
  else if (today > 0) message = `One down! ${goal - today} more for today's goal 🌷`;
  else if (store.streak > 0) message = `Let's keep our ${store.streak}-day streak alive! 🔥`;
  else message = "Let's do just one problem today? 🥺👉👈";
  return html`<div class="card buddy-card">
    <div class="bubble">${message}</div>
    ${buddy ? html`<${LeetlingArt} critter=${buddy} size=${58} /><div class="muted bold">${buddy.name}</div>`
      : html`<span class="art" style="font-size:58px">🥚</span><div class="muted small bold">Open a pack to meet your buddy!</div>`}
    <div class="hearts">
      ${Array.from({ length: goal }, (_, i) => html`<span class="heart">${i < today ? "♥" : "♡"}</span>`)}
      <b>${Math.min(today, goal)}/${goal} today</b>
    </div>
  </div>`;
}

function ModePicker() {
  const mode = store.progress.mode;
  return html`<section>
    <${SectionTitle} title="How do you want to practice?" emoji="🎀" />
    <div class="modes">
      ${Object.entries(MODES).map(([id, m]) => html`<button class=${"mode" + (mode === id ? " selected" : "")}
          onClick=${() => store.setMode(id)} aria-pressed=${mode === id}>
        <div class="mode-head"><span class="mode-emoji">${m.emoji}</span><b>${m.label}</b>
          ${mode === id && html`<span class="tick">✓</span>`}</div>
        <div class="muted small">${m.blurb}</div>
      </button>`)}
    </div>
    ${mode === "topic" && html`<label class="topic-pick">
      <b>Topic:</b>
      <select value=${store.progress.topic} onChange=${(e) => store.setTopic(e.target.value)}>
        ${store.categories.map((c) => html`<option value=${c}>${CATEGORY_EMOJI[c]} ${c} (${store.solvedIn(c)}/${store.problemsIn(c).length})</option>`)}
      </select>
    </label>`}
  </section>`;
}

function NextProblemCard() {
  const p = store.nextProblem;
  const mode = store.progress.mode;
  if (!p) {
    return html`<section class="card">
      <${SectionTitle} title="Today's problem" emoji="💌" />
      <div class="row gap"><span class="big">🏆</span><div>
        <h3>${mode === "topic" ? `You finished ${store.progress.topic}!` : "You solved every problem!"}</h3>
        <p class="muted">${mode === "topic" ? "Pick another topic above, or switch to Random for review." : "Switch to Random mode to keep reviewing 💖"}</p>
      </div></div>
    </section>`;
  }
  const solved = store.isSolved(p.id);
  let subtitle;
  if (mode === "easyFirst") {
    const left = store.problems.filter((q) => q.difficulty === p.difficulty && !store.isSolved(q.id)).length;
    subtitle = `${left} ${p.difficulty} problem${left === 1 ? "" : "s"} left before leveling up`;
  } else if (mode === "topic") {
    subtitle = `${store.solvedIn(p.category)}/${store.problemsIn(p.category).length} done in ${p.category}`;
  } else {
    subtitle = `LeetCode #${p.lc} · rolled just for you today 🎲`;
  }
  return html`<section class="card">
    <${SectionTitle} title="Today's problem" emoji="💌" />
    <div class="next">
      <div class="next-emoji">${CATEGORY_EMOJI[p.category]}</div>
      <div class="next-info">
        <h3>${p.title}</h3>
        <div class="pills"><${DifficultyPill} difficulty=${p.difficulty} /><${Pill} text=${p.category} color="#8C6FE0" />
          ${solved && html`<${Pill} text="✓ Solved" color="#4FB892" />`}</div>
        <div class="muted small">${subtitle}</div>
      </div>
      <div class="next-actions">
        <a class="btn primary" href=${"#/problem/" + p.id}>${solved ? "Practice again" : "Start solving ✨"}</a>
        ${mode === "random" && html`<button class="btn secondary compact" onClick=${() => store.shuffleRandomPick()}>🔀 Shuffle</button>`}
      </div>
    </div>
  </section>`;
}

function TopicGrid() {
  return html`<section>
    <div class="row between wrap">
      <${SectionTitle} title="Your garden of topics" emoji="🌼" />
      <span class="muted small bold">${store.solvedCount}/${store.problems.length} · best streak ${store.bestStreak} 🔥</span>
    </div>
    <div class="topics">
      ${store.categories.map((c) => {
        const done = store.solvedIn(c), total = store.problemsIn(c).length;
        return html`<button class="topic" onClick=${() => { store.setTopic(c); store.setMode("topic"); window.scrollTo({ top: 0, behavior: "smooth" }); }}
            title=${"Practice " + c + " in order"}>
          <div class="row between"><span class="topic-name">${CATEGORY_EMOJI[c]} ${c}</span>
            <span class="muted small bold">${done === total ? "🌸" : `${done}/${total}`}</span></div>
          <${ProgressBar} value=${done / total} height=${7} colors=${done === total ? ["#BDEFD9", "#4FB892"] : undefined} />
        </button>`;
      })}
    </div>
  </section>`;
}

// ---------------------------------------------------------------- Problems list

function ProblemListView() {
  const [search, setSearch] = useState("");
  const [difficulty, setDifficulty] = useState(null);
  const [unsolvedOnly, setUnsolvedOnly] = useState(false);
  const q = search.trim().toLowerCase();
  const matches = (p) => (!q || p.title.toLowerCase().includes(q) || String(p.lc) === q || p.category.toLowerCase().includes(q))
    && (!difficulty || p.difficulty === difficulty) && (!unsolvedOnly || !store.isSolved(p.id));
  return html`<div class="page">
    <header class="page-head row between wrap">
      <h1>All 75 problems 📚</h1>
      <span class="muted bold">${store.solvedCount} solved</span>
    </header>
    <div class="filters">
      <input class="search" type="search" placeholder="Search problems…" value=${search} onInput=${(e) => setSearch(e.target.value)} />
      <div class="seg">
        ${[null, "Easy", "Medium", "Hard"].map((d) => html`<button class=${difficulty === d ? "on" : ""} onClick=${() => setDifficulty(d)}>${d ?? "All"}</button>`)}
      </div>
      <label class="toggle"><input type="checkbox" checked=${unsolvedOnly} onChange=${(e) => setUnsolvedOnly(e.target.checked)} /> Unsolved only</label>
    </div>
    ${store.categories.map((c) => {
      const list = store.problemsIn(c).filter(matches);
      if (!list.length) return null;
      return html`<section class="card list-group">
        <div class="row between"><h3>${CATEGORY_EMOJI[c]} ${c}</h3>
          <span class="muted small bold">${store.solvedIn(c)}/${store.problemsIn(c).length}</span></div>
        ${list.map((p) => {
          const solved = store.isSolved(p.id), attempts = store.progress.attempts[String(p.id)] ?? 0;
          return html`<a class="prow" href=${"#/problem/" + p.id}>
            <span class=${"pstate" + (solved ? " solved" : attempts ? " tried" : "")}>${solved ? "✓" : attempts ? "◐" : "○"}</span>
            <span class="pname"><span class="muted">${p.id}.</span> ${p.title}</span>
            ${attempts > 0 && html`<span class="muted small tries">${attempts} tr${attempts === 1 ? "y" : "ies"}</span>`}
            <${DifficultyPill} difficulty=${p.difficulty} />
          </a>`;
        })}
      </section>`;
    })}
  </div>`;
}

// ---------------------------------------------------------------- Problem

const HINT_LABELS = [["🌱", "Nudge"], ["🌷", "Approach"], ["🌸", "Almost there"]];

const STATUS = {
  accepted: ["Accepted", "🌸", "#4FB892"],
  wrong_answer: ["Wrong Answer", "🤔", "#E89B3C"],
  runtime_error: ["Runtime Error", "🩹", "#D94F70"],
  time_limit: ["Time Limit Exceeded", "🐢", "#D94F70"],
  syntax_error: ["Syntax Error", "✏️", "#D94F70"],
  setup_error: ["Couldn't run your code", "🩹", "#D94F70"],
};

function ProblemView({ problem }) {
  const [code, setCode] = useState(() => store.draft(problem));
  const [editorKey, setEditorKey] = useState(0);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(null);
  const [tab, setTab] = useState("problem");
  const [py, setPy] = useState(pythonStatus());
  const taRef = useRef(null);
  const codeRef = useRef(code);

  useEffect(() => { warmUp(); return onPythonStatus(setPy); }, []);
  useEffect(() => () => store.saveNow(), []);

  const onChange = (v) => { codeRef.current = v; store.setDraft(problem, v); };

  const execute = async (mode) => {
    if (running) return;
    setRunning(mode);
    setTab("console");
    const source = codeRef.current;
    store.setDraft(problem, source);
    if (mode === "submit") store.recordAttempt(problem);
    const r = await judge(problem.id, source, mode);
    setResult(r);
    setRunning(null);
    if (mode === "submit" && r.status === "accepted") store.recordAccepted(problem);
  };

  const reset = async () => {
    const ok = await ask({ title: "Reset your code?", message: "This replaces your current code with the starter template.",
                           ok: "Reset", cancel: "Keep it", danger: true });
    if (!ok) return;
    store.resetDraft(problem);
    codeRef.current = problem.starter;
    setCode(problem.starter);
    setEditorKey((k) => k + 1);
  };

  const solved = store.isSolved(problem.id);
  return html`<div class="problem" data-tab=${tab}>
    <div class="ptop">
      <a class="btn quiet compact" href=${"#/" + lastSection}>‹ ${SECTIONS.find((s) => s.id === lastSection)?.title ?? "Back"}</a>
      <span class="ptitle">${CATEGORY_EMOJI[problem.category]} ${problem.title}</span>
      <span class="ptop-pills"><${DifficultyPill} difficulty=${problem.difficulty} />
        ${solved && html`<${Pill} text="✓ Solved" color="#4FB892" />`}</span>
    </div>
    <div class="ptabs seg" role="tablist">
      <button role="tab" class=${tab === "problem" ? "on" : ""} onClick=${() => setTab("problem")}>📖 Problem</button>
      <button role="tab" class=${tab === "code" ? "on" : ""} onClick=${() => setTab("code")}>✏️ Code</button>
      <button role="tab" class=${tab === "console" ? "on" : ""} onClick=${() => setTab("console")}>
        🧪 Results${result && html` <span class="dotmark" style=${{ background: (STATUS[result.status] || STATUS.setup_error)[2] }}></span>`}</button>
    </div>
    <div class="pbody">
      <div class="pane info-pane"><${ProblemInfo} problem=${problem} /></div>
      <div class="pane work-pane">
        <div class="editor-pane">
          <div class="editor-bar">
            <span class="file">‹/› solution.py</span>
            <button class="btn quiet compact icon" onClick=${reset} title="Reset to starter code" aria-label="Reset to starter code">↺</button>
            <span class="spacer"></span>
            <button class="btn secondary compact" disabled=${!!running} onClick=${() => execute("run")} title="Run the example tests (⌘R)">
              ${running === "run" ? "Running…" : "▶ Run"}</button>
            <button class="btn mint compact" disabled=${!!running} onClick=${() => execute("submit")} title="Run every test, including hidden ones (⌘↩)">
              ${running === "submit" ? "Judging…" : "Submit ✈︎"}</button>
          </div>
          <${KeyBar} taRef=${taRef} />
          <${CodeEditor} key=${editorKey} value=${code} onChange=${onChange} taRef=${taRef}
            onRun=${() => execute("run")} onSubmit=${() => execute("submit")} />
        </div>
        <${ConsolePane} result=${result} running=${running} py=${py} />
      </div>
    </div>
  </div>`;
}

function ProblemInfo({ problem }) {
  const revealed = store.hintsRevealed(problem);
  const solved = store.isSolved(problem.id);
  const peeked = store.progress.solutionPeeked.includes(problem.id);
  const [showSolution, setShowSolution] = useState(false);
  const unlocked = solved || revealed >= 3;

  const peek = async () => {
    if (!solved && !peeked) {
      const ok = await ask({ title: "Peek at the solution?",
        message: "No judgment! Reading a solution and then re-writing it from memory tomorrow is a great way to learn.",
        ok: "Show me 👀", cancel: "I'll try a bit more 💪" });
      if (!ok) return;
      store.peekSolution(problem);
    }
    setShowSolution(true);
  };

  return html`<div class="info">
    <h2>${problem.id}. ${problem.title}</h2>
    <div class="pills"><${DifficultyPill} difficulty=${problem.difficulty} /><${Pill} text=${problem.category} color="#8C6FE0" />
      <${Pill} text=${"LeetCode #" + problem.lc} color="#9A7A90" /></div>
    <${MD} text=${problem.description} block cls="desc" />
    ${problem.examples.map((ex, i) => html`<div class="example">
      <div class="label">Example ${i + 1}</div>
      <div class="kv"><span>Input</span><pre>${ex.input}</pre></div>
      <div class="kv"><span>Output</span><pre>${ex.output}</pre></div>
      ${ex.explanation && html`<div class="kv"><span>Why</span><${MD} text=${ex.explanation} /></div>`}
    </div>`)}
    ${problem.constraints.length > 0 && html`<div class="constraints"><div class="label">Constraints</div>
      <ul>${problem.constraints.map((c) => html`<li><code>${c}</code></li>`)}</ul></div>`}

    <div class="hints">
      <div class="row between"><b>${store.buddy?.emoji ?? "🐰"} Stuck? Ask for a hint</b><span class="muted small bold">${revealed}/3</span></div>
      <p class="muted small">Hints go from a gentle nudge to almost the whole idea. Try one at a time!</p>
      ${problem.hints.slice(0, revealed).map((h, i) => html`<div class="hint">
        <div class="hint-label">${HINT_LABELS[i][0]} Hint ${i + 1} · ${HINT_LABELS[i][1]}</div><${MD} text=${h} /></div>`)}
      ${revealed < 3 && html`<button class="btn secondary compact" onClick=${() => store.revealHint(problem)}>
        ${HINT_LABELS[revealed][0]} ${HINT_LABELS[revealed][1]}</button>`}
    </div>

    <div class="solution">
      <div class="row between">
        <b>📖 Solution</b>
        ${unlocked && (showSolution ? html`<button class="btn quiet compact" onClick=${() => setShowSolution(false)}>Hide</button>`
          : html`<button class="btn secondary compact" onClick=${peek}>${solved ? "Compare with mine" : "Peek 👀"}</button>`)}
      </div>
      ${!unlocked && html`<p class="muted small">🔒 Unlocks after you solve it, or after all 3 hints.</p>`}
      ${showSolution && html`<pre class="code-block">${problem.solution}</pre><div class="muted small bold">⏱ ${problem.complexity}</div>`}
    </div>
  </div>`;
}

function ConsolePane({ result, running, py }) {
  const [selected, setSelected] = useState(0);
  useEffect(() => {
    if (!result) return;
    const i = result.results.findIndex((t) => !t.passed);
    setSelected(i === -1 ? 0 : i);
  }, [result]);

  let body;
  if (running) {
    const loading = py.state === "loading";
    body = html`<div class="running"><span class="spinner"></span>
      ${loading ? "Waking up Python… 🐍 (the first time takes a few seconds)"
        : running === "run" ? "Running the examples… 🐇" : "Judging against every test… 🧑‍⚖️"}</div>`;
  } else if (!result) {
    body = html`<p class="muted small"><b>Run</b> tries the examples. <b>Submit</b> checks every test, including hidden ones.
      Pass them all to earn your rewards 🎁</p>
      <p class="muted small">${py.state === "ready" ? `🐍 Python ${py.version} is ready, running right here on your device.`
        : py.state === "loading" ? "🐍 Getting Python ready…" : py.state === "error" ? "🐍 Python couldn't load. Check your connection." : ""}</p>`;
  } else {
    const [title, emoji, color] = STATUS[result.status] || STATUS.setup_error;
    const t = result.results[selected];
    body = html`
      <div class="verdict" style=${{ color }}><span>${emoji}</span> <b>${title}</b>
        ${result.total > 0 && html`<span class="muted small">${result.passed}/${result.total} tests passed</span>`}
        ${result.runtime_ms != null && html`<span class="muted small">· ${result.runtime_ms} ms</span>`}</div>
      ${result.message && html`<pre class="code-block err">${result.message}</pre>`}
      ${(result.status === "wrong_answer" || result.status === "runtime_error") && html`<p class="muted small">
        ${result.passed > 0 ? "So close, you're on the right track! 💪" : "Every bug is a lesson. Check the case below 🔎"}</p>`}
      ${result.results.length > 0 && html`<div class="cases">
        ${result.results.map((c, i) => html`<button class=${"case" + (i === selected ? " on" : "")} onClick=${() => setSelected(i)}>
          <span class=${"cdot " + (c.passed ? "ok" : "bad")}></span>${c.hidden ? "Hidden test" : `Case ${c.index + 1}`}</button>`)}
      </div>`}
      ${t && html`<div class="case-detail">
        <${Field} label="Input" value=${t.input} />
        ${t.error ? html`<${Field} label="Error" value=${t.error} err />` : html`<${Field} label="Your output" value=${t.output} err=${!t.passed} />`}
        <${Field} label="Expected" value=${t.expected} />
        ${t.stdout && html`<${Field} label="Stdout (your print statements)" value=${t.stdout} />`}
      </div>`}`;
  }
  return html`<div class="console"><div class="console-title">Console</div>${body}</div>`;
}

const Field = ({ label, value, err }) =>
  html`<div class="field"><div class="label">${label}</div><pre class=${"code-block" + (err ? " err" : "")}>${value || " "}</pre></div>`;

// ---------------------------------------------------------------- Celebration

function Celebration({ c }) {
  const pieces = ["🌸", "💖", "✨", "🎀", "⭐️", "🌷", "💕", "🫧"];
  const confetti = useRef(Array.from({ length: 36 }, (_, i) => ({
    e: pieces[i % pieces.length], left: Math.random() * 100, delay: Math.random() * 0.8,
    dur: 2.4 + Math.random() * 1.6, size: 16 + Math.random() * 16, drift: (Math.random() - 0.5) * 120,
  }))).current;
  const close = () => store.dismissCelebration();
  return html`<div class="overlay" onClick=${(e) => e.target === e.currentTarget && close()}>
    <div class="confetti" aria-hidden="true">${confetti.map((p) => html`<span style=${{ left: p.left + "%", fontSize: p.size + "px",
      animationDelay: p.delay + "s", animationDuration: p.dur + "s", "--drift": p.drift + "px" }}>${p.e}</span>`)}</div>
    <div class="card celebrate pop" role="dialog" aria-modal="true">
      <div class="big-emoji">🌸</div>
      <h2>Accepted!</h2>
      <p dangerouslySetInnerHTML=${{ __html: c.firstSolve ? `You solved <b>${c.problemTitle}</b> for the first time!`
        : `You solved <b>${c.problemTitle}</b> again, that's how it sticks 🧠` }}></p>
      <div class="stats">
        <div><b>🔥 ${c.streak}</b><span>${c.streakMended ? "streak mended 🩹" : "day streak"}</span></div>
        <div><b>💖 ${c.todayCount}/${c.goal}</b><span>today</span></div>
        <div><b>📚 ${store.solvedCount}/${store.problems.length}</b><span>solved</span></div>
      </div>
      ${c.rewards.length ? html`<div class="rewards">${c.rewards.map((r) => html`<div class="reward"
          style=${{ background: `linear-gradient(90deg, ${PACKS[r.pack].colors[0]}, ${PACKS[r.pack].colors[1]})` }}>
        <span>${PACKS[r.pack].emoji}</span><div><b>+1 ${PACKS[r.pack].name}</b><div class="small">${r.reason}</div></div></div>`)}</div>`
        : html`<p class="muted small">No new packs this time, but every rep counts! 💪</p>`}
      <div class="row center gap wrap">
        ${c.rewards.length > 0 && html`<button class="btn primary" onClick=${() => { close(); go("packs"); }}>Open my packs 🎁</button>`}
        <button class="btn secondary" onClick=${close}>Keep coding</button>
      </div>
    </div>
  </div>`;
}

// ---------------------------------------------------------------- Packs

function PacksView() {
  const [session, setSession] = useState(null);
  return html`<div class="page">
    <header class="page-head">
      <h1>Your packs 🎁</h1>
      <p class="muted">Every pack holds Leetlings. Collect 3 of the same one to evolve it!</p>
    </header>
    <div class="pack-shelf">
      ${PACK_KINDS.map((kind) => {
        const count = store.packCount(kind);
        return html`<div class="pack-slot">
          <${PackArt} kind=${kind} count=${count} />
          <b>${PACKS[kind].emoji} ${PACKS[kind].name}</b>
          <div class="muted small center">${PACKS[kind].howToEarn}</div>
          <button class="btn primary" disabled=${count === 0} onClick=${() => setSession({ kind, pulls: null })}>
            ${count > 0 ? "Open ✨" : "None yet"}</button>
        </div>`;
      })}
    </div>
    <section class="card">
      <${SectionTitle} title="Pack guide" emoji="📜" />
      ${PACK_KINDS.map((kind) => {
        const p = PACKS[kind];
        return html`<p class="small"><b>${p.emoji} ${p.name}</b> · ${p.howToEarn.toLowerCase()} · ${p.cards} cards ·
          last card ${RARITIES[p.guaranteedLast].name}+ · ${Math.round(p.shiny * 100)}% shiny per card</p>`;
      })}
      <p class="muted small">Shiny Leetlings ✨ sparkle and are extra rare. Legendaries can't evolve, but they're legendary. 💅</p>
    </section>
    ${session && html`<${PackOpening} session=${session} setSession=${setSession} />`}
  </div>`;
}

function PackArt({ kind, count, tearing = false, onClick }) {
  const p = PACKS[kind];
  return html`<div class=${"pack-art" + (tearing ? " tearing" : "") + (onClick ? " tappable" : "")} onClick=${onClick}
      style=${{ background: `linear-gradient(160deg, ${p.colors[0]}, ${p.colors[1]})` }}>
    <div class="crimp top"></div>
    <div class="pack-face"><div class="pack-emoji">${p.emoji}</div><div class="pack-brand">✿ LEETLINGS ✿</div></div>
    <div class="crimp bottom"></div>
    ${count != null && count > 0 && html`<span class="pack-count">×${count}</span>`}
  </div>`;
}

function PackOpening({ session, setSession }) {
  const [tearing, setTearing] = useState(false);
  const [flipped, setFlipped] = useState([]);
  const { kind, pulls } = session;

  const tear = () => {
    if (tearing) return;
    setTearing(true);
    setTimeout(() => {
      const result = store.openPack(kind);
      if (!result) return setSession(null);
      setFlipped(result.map(() => false));
      setSession({ kind, pulls: result });
    }, 650);
  };

  const allFlipped = pulls && flipped.every(Boolean);
  let summary = "";
  if (pulls) {
    const parts = [];
    const fresh = pulls.filter((p) => p.isNew).length, shiny = pulls.filter((p) => p.shiny).length;
    if (fresh) parts.push(`${fresh} new Leetling${fresh === 1 ? "" : "s"}!`);
    if (shiny) parts.push(`${shiny} shiny ✨`);
    if (pulls.some((p) => p.critter.rarity === 4)) parts.push("A LEGENDARY?!");
    summary = parts.length ? parts.join(" · ") : "Nice pulls! 🎉";
  }

  return html`<div class="overlay opening">
    ${!pulls ? html`<div class="open-stage">
        <${PackArt} kind=${kind} tearing=${tearing} onClick=${tear} />
        <p class="open-hint">${tearing ? "✨✨✨" : "Tap the pack to open it!"}</p>
        <button class="btn quiet" onClick=${() => setSession(null)}>Not now</button>
      </div>`
      : html`<div class="open-stage">
        <p class="open-hint">${allFlipped ? summary : "Tap each card to reveal ✨"}</p>
        <div class="pulls">
          ${pulls.map((pull, i) => html`<button class=${"flip" + (flipped[i] ? " flipped" : "")}
              onClick=${() => setFlipped((f) => f.map((v, j) => (j === i ? true : v)))} aria-label=${flipped[i] ? pull.critter.name : "Hidden card"}>
            <div class="flip-inner">
              <div class="flip-back"><span>✿</span><b>LEETLING</b></div>
              <div class="flip-front"><${LeetlingCard} critter=${pull.critter} shiny=${pull.shiny} isNew=${pull.isNew} width=${132} /></div>
            </div>
          </button>`)}
        </div>
        <div class="row center gap">
          ${!allFlipped && html`<button class="btn secondary" onClick=${() => setFlipped(pulls.map(() => true))}>Reveal all</button>`}
          <button class="btn primary" onClick=${() => setSession(null)}>${allFlipped ? "Add to my Leetdex 💖" : "Skip"}</button>
        </div>
      </div>`}
  </div>`;
}

// ---------------------------------------------------------------- Leetdex

function DexView() {
  const [ownedOnly, setOwnedOnly] = useState(false);
  const [open, setOpen] = useState(null);
  const caught = store.progress.caught;
  const shinyCount = Object.values(store.progress.collection).reduce((n, o) => n + (o.shiny > 0 ? 1 : 0), 0);
  const list = DEX.filter((c) => !ownedOnly || store.owned(c.id).count > 0);
  return html`<div class="page">
    <header class="page-head row between wrap">
      <div><h1>Leetdex 📖</h1>
        <p class="muted">${caught.length} of ${DEX.length} discovered · ${shinyCount} shiny ✨ · ${store.progress.packsOpened} packs opened</p></div>
      <label class="toggle"><input type="checkbox" checked=${ownedOnly} onChange=${(e) => setOwnedOnly(e.target.checked)} /> Owned only</label>
    </header>
    ${store.anyEvolvable && html`<div class="notice">✦ Some of your Leetlings are ready to evolve! Tap one with a ✦ badge.</div>`}
    <div class="dex-grid">
      ${list.map((c) => {
        const seen = caught.includes(c.id), o = store.owned(c.id);
        const el = ELEMENTS[c.element];
        return html`<button class=${"dex-cell" + (seen ? "" : " unseen")} onClick=${() => seen && setOpen(c)} disabled=${!seen}
            style=${seen ? { background: `linear-gradient(180deg, ${el.colors[0]}, ${el.colors[1]})` } : {}}>
          ${store.canEvolve(c) && html`<span class="evo-badge">✦</span>`}
          ${o.shiny > 0 && html`<span class="shiny-badge">✨</span>`}
          <${LeetlingArt} critter=${c} size=${40} silhouette=${!seen} />
          <div class="dex-name">${seen ? c.name : "???"}</div>
          <div class="dex-num">#${String(c.dexNumber).padStart(3, "0")}${o.count > 1 ? ` · ×${o.count}` : ""}</div>
        </button>`;
      })}
    </div>
    ${open && html`<${DexDetail} critter=${open} close=${() => setOpen(null)} />`}
  </div>`;
}

function DexDetail({ critter, close }) {
  const [banner, setBanner] = useState(null);
  const o = store.owned(critter.id);
  const el = ELEMENTS[critter.element], r = RARITIES[critter.rarity];
  const line = lineOf(critter);
  const evolve = () => {
    const next = store.evolve(critter);
    if (next) setBanner(`✨ ${critter.name} evolved into ${next.name}! ✨`);
  };
  return html`<div class="overlay" onClick=${(e) => e.target === e.currentTarget && close()}>
    <div class="card dex-detail pop" role="dialog" aria-modal="true">
      ${banner && html`<div class="notice">${banner}</div>`}
      <div class="row gap top">
        <${LeetlingCard} critter=${critter} shiny=${o.shiny > 0} width=${150} />
        <div class="dd-info">
          <h2>${critter.name}</h2>
          <div class="pills"><${Pill} text=${el.icon + " " + el.name} color="#8C6FE0" /><${Pill} text=${stars(critter.rarity) + " " + r.name} color=${r.color} />
            ${critter.stage > 0 && html`<${Pill} text=${"Stage " + critter.stage} color="#9A7A90" />`}</div>
          <p class="flavor">${critter.flavor}</p>
          <p class="small bold">You have ${o.count}${o.shiny > 0 ? ` (${o.shiny} shiny ✨)` : ""}</p>
        </div>
      </div>
      ${line.length > 1 && html`<div class="line">${line.map((c, i) => {
        const seen = store.progress.caught.includes(c.id);
        return html`<div class=${"line-step" + (c.id === critter.id ? " me" : "")}>
          <${LeetlingArt} critter=${c} size=${30} silhouette=${!seen} /><div class="small">${seen ? c.name : "???"}</div></div>
          ${i < line.length - 1 && html`<span class="muted">→</span>`}`;
      })}</div>`}
      <div class="row gap wrap end">
        ${critter.evolvesTo && html`<button class="btn mint" disabled=${!store.canEvolve(critter)} onClick=${evolve}>
          ${store.canEvolve(critter) ? `Evolve ✦ (uses ${COPIES_TO_EVOLVE})` : `Evolve at ${COPIES_TO_EVOLVE} copies`}</button>`}
        <button class="btn secondary" disabled=${o.count === 0 || store.progress.buddy === critter.id} onClick=${() => store.setBuddy(critter)}>
          ${store.progress.buddy === critter.id ? "Your buddy 💖" : "Make my buddy"}</button>
        <button class="btn quiet" onClick=${close}>Close</button>
      </div>
    </div>
  </div>`;
}

// ---------------------------------------------------------------- Settings

// First sync on a device that already has progress, while the gist has some too.
store.chooseSyncMerge = async () => {
  const combine = await ask({
    title: "You have progress in two places 🌷",
    message: "This device and your synced copy both have solves and Leetlings. Combine them into one, or replace this device's progress with the synced copy?",
    ok: "Combine both", cancel: "Use the synced copy",
  });
  return combine === false ? "remote" : "combine";
};

const TOKEN_URL = "https://github.com/settings/tokens/new?scopes=gist&description=Leetling%20sync";

function ago(date) {
  if (!date) return "";
  const s = Math.round((Date.now() - date.getTime()) / 1000);
  if (s < 45) return "just now";
  if (s < 3600) return `${Math.round(s / 60)} min ago`;
  return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

function SyncCard() {
  const [token, setToken] = useState("");
  const [busy, setBusy] = useState(false);
  const st = store.syncStatus;

  const connect = async () => {
    if (!token.trim()) return;
    setBusy(true);
    const ok = await store.connectSync(token);
    setBusy(false);
    if (ok) setToken("");
  };

  const disconnect = async () => {
    const ok = await ask({ title: "Stop syncing this device?",
      message: "Your progress stays on this device and in your gist. It just won't stay in step anymore.",
      ok: "Stop syncing", cancel: "Keep syncing" });
    if (ok) store.disconnectSync();
  };

  if (!store.syncConnected) {
    return html`<section class="card">
      <${SectionTitle} title="Sync your devices" emoji="☁️" />
      <p class="small">Keep your iPhone, Mac and browser in step. Your progress is saved to a <b>private gist</b> on your GitHub account,
        and solves from every device add up.</p>
      <ol class="small steps">
        <li><a href=${TOKEN_URL} target="_blank" rel="noopener">Make a GitHub token</a> with only the <b>gist</b> box ticked.
          Pick “No expiration” so it keeps working.</li>
        <li>Paste it here, then do the same on your other devices (Mac: Settings → Sync).</li>
      </ol>
      <div class="setting">
        <input type="password" autocomplete="off" spellcheck="false" placeholder="ghp_…" value=${token}
          onInput=${(e) => setToken(e.target.value)} onKeyDown=${(e) => e.key === "Enter" && connect()} />
        <button class="btn primary compact" disabled=${busy || !token.trim()} onClick=${connect}>${busy ? "Connecting…" : "Connect"}</button>
      </div>
      ${st.state === "error" && html`<p class="small bold">${st.message}</p>`}
      <p class="muted small">The token stays on this device and is only ever sent to GitHub.</p>
    </section>`;
  }

  const line = st.state === "syncing" ? "Syncing… 🔄"
    : st.state === "error" ? st.message
    : st.lastSynced ? `Synced ✨ ${ago(st.lastSynced)}` : "Connected ✨";
  return html`<section class="card">
    <${SectionTitle} title="Sync your devices" emoji="☁️" />
    <p class="small bold">${line}</p>
    <p class="muted small">Leetling syncs when it opens and a few seconds after you make progress.</p>
    <div class="row gap wrap">
      <button class="btn secondary compact" disabled=${st.state === "syncing"} onClick=${() => store.syncNow()}>🔄 Sync now</button>
      <button class="btn quiet compact" onClick=${disconnect}>Disconnect</button>
    </div>
  </section>`;
}

function SettingsView() {
  const [py, setPy] = useState(pythonStatus());
  const [note, setNote] = useState(null);
  const fileRef = useRef(null);
  useEffect(() => onPythonStatus(setPy), []);
  const standalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone;

  const exportData = async () => {
    const name = `leetling-progress-${new Date().toISOString().slice(0, 10)}.json`;
    const file = new File([store.exportJSON()], name, { type: "application/json" });
    if (navigator.canShare?.({ files: [file] }) && /iPhone|iPad|Android/i.test(navigator.userAgent)) {
      try { await navigator.share({ files: [file], title: "Leetling progress" }); return; } catch (e) { if (e.name === "AbortError") return; }
    }
    const a = document.createElement("a");
    a.href = URL.createObjectURL(file);
    a.download = name;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  };

  const importData = async (e) => {
    const f = e.target.files?.[0];
    e.target.value = "";
    if (!f) return;
    const ok = await ask({ title: "Import this progress?", message: "It replaces the progress on this device (solves, streak, packs and Leetlings) with the file's."
                             + (store.syncConnected ? " Your synced devices will get it too." : ""),
                           ok: "Import", cancel: "Cancel" });
    if (!ok) return;
    try {
      store.importJSON(await f.text());
      setNote("Imported! Welcome back 💖");
    } catch (err) {
      setNote(`Hmm, that didn't work: ${err.message}`);
    }
  };

  const reset = async () => {
    const ok = await ask({ title: "Reset all progress?", message: store.syncConnected
                             ? "This erases your solves, streak history, packs and Leetdex on this device and every synced device. It can't be undone."
                             : "This erases your solves, streak history, packs and Leetdex on this device. It can't be undone.",
                           ok: "Reset everything", cancel: "Cancel", danger: true });
    if (ok) store.resetAll();
  };

  return html`<div class="page settings">
    <header class="page-head"><h1>Settings ⚙️</h1></header>
    <section class="card">
      <${SectionTitle} title="You" emoji="🎀" />
      <label class="setting"><span>What should I call you?</span>
        <input type="text" value=${store.progress.name ?? ""} placeholder="friend" onInput=${(e) => store.setName(e.target.value)} /></label>
      <label class="setting"><span>Daily goal (problems per day)</span>
        <div class="seg">${[1, 2, 3, 4].map((g) => html`<button class=${store.progress.dailyGoal === g ? "on" : ""} onClick=${() => store.setGoal(g)}>${g}</button>`)}</div></label>
      <p class="muted small">Hitting your goal earns a Bloom Pack 🌷 each day. Your streak only needs 1 problem a day.</p>
    </section>
    <section class="card">
      <${SectionTitle} title="On your iPhone" emoji="📱" />
      ${standalone ? html`<p class="small">You're using Leetling from your Home Screen. Cozy! 🏡</p>`
        : html`<p class="small">For the full app feel, open this page in <b>Safari</b>, tap <b>Share</b> → <b>Add to Home Screen</b>.
          It opens full-screen, works offline after the first run, and your progress stays put.</p>`}
      <p class="muted small">Heads up: the Home Screen app and a Safari tab keep <i>separate</i> progress, so pick one (the Home Screen app is best),
        or turn on sync in both.</p>
    </section>
    <${SyncCard} />
    <section class="card">
      <${SectionTitle} title="Python" emoji="🐍" />
      <p class="small">${py.state === "ready" ? `Running your code with Python ${py.version} (Pyodide), right in your browser.`
        : py.state === "loading" ? "Loading Python…" : py.state === "error" ? "Python couldn't load. It needs internet the first time." : "Python loads when you open a problem."}</p>
      <p class="muted small">Your code never leaves your device. Runs stop after 10s (30s for a submit). Very deep recursion
        (thousands of levels) can hit the browser's smaller stack. An iterative version always works.</p>
    </section>
    <section class="card">
      <${SectionTitle} title="Your data" emoji="💾" />
      <p class="small">Progress is saved on this device. Export a backup now and then, or move progress between devices.
        It's the same format as the Mac app's <code>progress.json</code>, so you can import that file here too.</p>
      <div class="row gap wrap">
        <button class="btn secondary" onClick=${exportData}>⬇︎ Export progress</button>
        <button class="btn secondary" onClick=${() => fileRef.current.click()}>⬆︎ Import progress</button>
        <input ref=${fileRef} type="file" accept=".json,application/json" hidden onChange=${importData} />
      </div>
      ${note && html`<p class="small bold">${note}</p>`}
      <div class="row between wrap gap" style="margin-top:14px">
        <span class="muted small">Start completely fresh (solves, streak, packs and Leetlings).</span>
        <button class="btn danger compact" onClick=${reset}>Reset everything…</button>
      </div>
    </section>
  </div>`;
}

// ---------------------------------------------------------------- App

function App() {
  useStore();
  const [route, setRoute] = useState(parseRoute());
  const [error, setError] = useState(null);

  useEffect(() => {
    const onHash = () => {
      const r = parseRoute();
      if (r.section !== "problem") lastSection = r.section;
      setRoute(r);
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", onHash);
    if (route.section !== "problem") lastSection = route.section;
    fetch("data/problems.json").then((r) => r.json()).then((list) => store.setProblems(list))
      .catch(() => setError("I couldn't load the problems. Check your connection and refresh? 🌷"));
    const flush = () => {
      if (document.visibilityState === "hidden") {
        store.saveNow();
        if (store.syncConnected && store.syncDirty) store.syncNow({ keepalive: true });
      } else store.syncNow(); // pull what other devices did while we were away
    };
    document.addEventListener("visibilitychange", flush);
    store.syncNow();
    const poll = setInterval(() => document.visibilityState === "visible" && store.syncNow(), 5 * 60 * 1000);
    // Ask the browser not to evict our data when storage is tight.
    navigator.storage?.persist?.();
    return () => {
      window.removeEventListener("hashchange", onHash);
      document.removeEventListener("visibilitychange", flush);
      clearInterval(poll);
    };
  }, []);

  let page;
  if (error) page = html`<div class="page"><div class="card"><p>${error}</p></div></div>`;
  else if (!store.problems.length) page = html`<div class="page loading"><span class="spinner"></span> Loading… 🐰</div>`;
  else if (route.section === "problem") {
    const p = store.problem(route.id);
    page = p ? html`<${ProblemView} key=${p.id} problem=${p} />` : html`<div class="page"><p>That problem wandered off 🐾 <a href="#/problems">See all problems</a></p></div>`;
  } else {
    page = { today: TodayView, problems: ProblemListView, packs: PacksView, dex: DexView, settings: SettingsView }[route.section];
    page = html`<${page} />`;
  }

  return html`<div class=${"app" + (route.section === "problem" ? " in-problem" : "")}>
    <${Nav} route=${route} />
    <main class="main">${page}</main>
    ${store.celebration && html`<${Celebration} key=${store.celebration.id} c=${store.celebration} />`}
    <${Dialog} />
  </div>`;
}

render(html`<${App} />`, document.getElementById("app"));

if ("serviceWorker" in navigator && location.protocol === "https:") {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
