// Small text helpers: the catalog's mini-Markdown and Python syntax highlighting.

export const escapeHTML = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/** Inline Markdown used by descriptions and hints: `code`, **bold**, *italic*. */
export function inlineMD(s) {
  return escapeHTML(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*\w])\*([^*\s][^*]*)\*(?!\w)/g, "$1<em>$2</em>");
}

/** Paragraphs separated by blank lines; a paragraph whose lines start with "- " is a bullet list. */
export function blockMD(s) {
  return s.split(/\n\s*\n/).map((para) => {
    const lines = para.split("\n");
    if (lines.every((l) => l.startsWith("- "))) {
      return `<ul>${lines.map((l) => `<li>${inlineMD(l.slice(2))}</li>`).join("")}</ul>`;
    }
    return `<p>${inlineMD(para).replace(/\n/g, "<br>")}</p>`;
  }).join("");
}

// ---------------------------------------------------------------- Python highlighting

const KEYWORDS = new Set(("False None True and as assert async await break class continue def del elif else except " +
  "finally for from global if import in is lambda nonlocal not or pass raise return try while with yield match case").split(" "));
const BUILTINS = new Set(("self len range enumerate zip min max sum sorted reversed abs int str float bool list dict set " +
  "tuple print map filter any all isinstance ord chr divmod pow round iter next super object type hash id " +
  "List Optional Dict Set Tuple Deque ListNode TreeNode Node deque defaultdict Counter heapq heappush heappop " +
  "heapify bisect math inf collections lru_cache cache functools itertools").split(" "));

const TOKEN = /(#[^\n]*)|("""[\s\S]*?(?:"""|$)|'''[\s\S]*?(?:'''|$)|[rbfu]{0,2}"(?:\\.|[^"\\\n])*"?|[rbfu]{0,2}'(?:\\.|[^'\\\n])*'?)|(\b\d[\d_]*(?:\.\d+)?(?:e[+-]?\d+)?\b)|([A-Za-z_]\w*)/g;

export function highlightPython(code) {
  let out = "";
  let last = 0;
  let afterDef = false;
  for (const m of code.matchAll(TOKEN)) {
    out += escapeHTML(code.slice(last, m.index));
    last = m.index + m[0].length;
    const t = escapeHTML(m[0]);
    if (m[1]) out += `<span class="tk-c">${t}</span>`;
    else if (m[2]) out += `<span class="tk-s">${t}</span>`;
    else if (m[3]) out += `<span class="tk-n">${t}</span>`;
    else if (afterDef) out += `<span class="tk-d">${t}</span>`;
    else if (KEYWORDS.has(m[4])) out += `<span class="tk-k">${t}</span>`;
    else if (BUILTINS.has(m[4])) out += `<span class="tk-b">${t}</span>`;
    else out += t;
    afterDef = m[4] === "def" || m[4] === "class";
  }
  return out + escapeHTML(code.slice(last));
}
