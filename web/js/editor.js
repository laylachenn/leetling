// A tiny Python editor: a transparent <textarea> on top of a highlighted <pre>.
// The textarea grows to fit its content, so a single scroll container moves both layers
// together (no scroll syncing). Works with the iPhone keyboard; the key bar adds the keys
// iOS hides (Tab, brackets, colon…).

import { html, useEffect, useRef, useState } from "../vendor/preact-htm.mjs";
import { highlightPython } from "./text.js";

const INDENT = "    ";

function lineStart(text, pos) {
  return text.lastIndexOf("\n", pos - 1) + 1;
}

/** Replace [start, end) keeping the browser's undo stack when possible. */
function replaceRange(ta, start, end, text, selStart = start + text.length, selEnd = selStart) {
  ta.focus();
  ta.setSelectionRange(start, end);
  let ok = false;
  try {
    ok = document.execCommand("insertText", false, text);
  } catch { /* not supported */ }
  if (!ok) ta.setRangeText(text, start, end, "end");
  ta.setSelectionRange(selStart, selEnd);
  ta.dispatchEvent(new Event("input", { bubbles: true }));
}

/** Apply fn to each selected line; fn returns the new line. Keeps the lines selected. */
function editLines(ta, fn) {
  const v = ta.value;
  const s = lineStart(v, ta.selectionStart);
  let e = ta.selectionEnd;
  if (e > s && v[e - 1] === "\n") e--;
  const endIdx = v.indexOf("\n", e);
  const end = endIdx === -1 ? v.length : endIdx;
  const lines = v.slice(s, end).split("\n");
  const out = lines.map(fn).join("\n");
  if (lines.length === 1) {
    const delta = out.length - lines[0].length;
    const caret = Math.max(s, ta.selectionStart + delta);
    replaceRange(ta, s, end, out, caret, Math.max(caret, ta.selectionEnd + delta));
  } else {
    replaceRange(ta, s, end, out, s, s + out.length);
  }
}

export const editorActions = {
  indent(ta) {
    if (ta.selectionStart === ta.selectionEnd) {
      const col = ta.selectionStart - lineStart(ta.value, ta.selectionStart);
      replaceRange(ta, ta.selectionStart, ta.selectionEnd, " ".repeat(4 - (col % 4)));
    } else {
      editLines(ta, (l) => INDENT + l);
    }
  },
  outdent(ta) {
    editLines(ta, (l) => l.replace(/^ {1,4}/, ""));
  },
  toggleComment(ta) {
    const v = ta.value;
    const s = lineStart(v, ta.selectionStart);
    const endIdx = v.indexOf("\n", ta.selectionEnd);
    const lines = v.slice(s, endIdx === -1 ? v.length : endIdx).split("\n").filter((l) => l.trim());
    const allCommented = lines.length && lines.every((l) => l.trimStart().startsWith("#"));
    editLines(ta, (l) => {
      if (!l.trim()) return l;
      if (allCommented) return l.replace(/^(\s*)# ?/, "$1");
      return l.replace(/^(\s*)/, "$1# ");
    });
  },
  newline(ta) {
    const v = ta.value;
    const pos = ta.selectionStart;
    const line = v.slice(lineStart(v, pos), pos);
    let indent = line.match(/^ */)[0];
    const trimmed = line.replace(/#.*$/, "").trimEnd();
    if (trimmed.endsWith(":") || /[([{]$/.test(trimmed)) indent += INDENT;
    else if (/^\s*(return|pass|break|continue|raise)\b/.test(line)) indent = indent.slice(INDENT.length);
    replaceRange(ta, pos, ta.selectionEnd, "\n" + indent);
  },
  /** Backspace inside leading whitespace removes back to the previous 4-column stop. */
  backspace(ta) {
    const v = ta.value;
    const pos = ta.selectionStart;
    if (pos !== ta.selectionEnd) return false;
    const before = v.slice(lineStart(v, pos), pos);
    if (!before.length || /[^ ]/.test(before)) return false;
    const remove = before.length % 4 || 4;
    replaceRange(ta, pos - remove, pos, "");
    return true;
  },
  insert(ta, text, caretBack = 0) {
    const end = ta.selectionStart + text.length - caretBack;
    replaceRange(ta, ta.selectionStart, ta.selectionEnd, text, end);
  },
  moveCaret(ta, delta) {
    ta.focus();
    const p = Math.max(0, Math.min(ta.value.length, ta.selectionStart + delta));
    ta.setSelectionRange(p, p);
  },
};

const KEYS = [
  { label: "⇥", title: "Indent", run: (ta) => editorActions.indent(ta) },
  { label: "⇤", title: "Outdent", run: (ta) => editorActions.outdent(ta) },
  { label: "( )", run: (ta) => editorActions.insert(ta, "()", 1) },
  { label: "[ ]", run: (ta) => editorActions.insert(ta, "[]", 1) },
  { label: "{ }", run: (ta) => editorActions.insert(ta, "{}", 1) },
  { label: ":", run: (ta) => editorActions.insert(ta, ":") },
  { label: "=", run: (ta) => editorActions.insert(ta, "=") },
  { label: "\"", run: (ta) => editorActions.insert(ta, "\"") },
  { label: "'", run: (ta) => editorActions.insert(ta, "'") },
  { label: "_", run: (ta) => editorActions.insert(ta, "_") },
  { label: "#", title: "Toggle comment", run: (ta) => editorActions.toggleComment(ta) },
  { label: "◀", title: "Left", run: (ta) => editorActions.moveCaret(ta, -1) },
  { label: "▶", title: "Right", run: (ta) => editorActions.moveCaret(ta, 1) },
];

export function KeyBar({ taRef }) {
  // pointerdown + preventDefault keeps the keyboard open (focus never leaves the textarea).
  return html`<div class="keybar" role="toolbar" aria-label="Code keys">
    ${KEYS.map((k) => html`<button type="button" class="key" title=${k.title || k.label}
      onPointerDown=${(e) => { e.preventDefault(); if (taRef.current) k.run(taRef.current); }}>${k.label}</button>`)}
  </div>`;
}

export function CodeEditor({ value, onChange, onRun, onSubmit, taRef }) {
  const [code, setCode] = useState(value);
  const localRef = useRef(null);
  const ref = taRef || localRef;

  useEffect(() => { setCode(value); }, [value]);

  const lines = code.split("\n");
  const longest = lines.reduce((m, l) => Math.max(m, l.length), 0);

  const onInput = (e) => {
    setCode(e.target.value);
    onChange(e.target.value);
    requestAnimationFrame(() => snapLeft(e.target));
  };

  // The browser scrolls sideways to follow the caret along a long line, but never scrolls back.
  // When the caret's line fits on screen again, return to the left edge.
  const snapLeft = (ta) => {
    const scroller = ta.closest(".editor");
    if (!scroller || !scroller.scrollLeft) return;
    const v = ta.value, pos = ta.selectionStart;
    const col = pos - (v.lastIndexOf("\n", pos - 1) + 1);
    const ch = parseFloat(getComputedStyle(ta).fontSize) * 0.6; // SF Mono / Menlo advance ≈ 0.6em
    const gutter = scroller.querySelector(".gutter")?.offsetWidth ?? 0;
    if ((col + 2) * ch + 12 < scroller.clientWidth - gutter) scroller.scrollLeft = 0;
  };

  const onKeyDown = (e) => {
    const ta = e.currentTarget;
    const mod = e.metaKey || e.ctrlKey;
    if (e.key === "Tab") {
      e.preventDefault();
      e.shiftKey ? editorActions.outdent(ta) : editorActions.indent(ta);
    } else if (e.key === "Enter" && mod) {
      e.preventDefault();
      onSubmit?.();
    } else if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      editorActions.newline(ta);
    } else if (e.key === "Backspace" && !mod && !e.altKey) {
      if (editorActions.backspace(ta)) e.preventDefault();
    } else if (mod && e.key === "/") {
      e.preventDefault();
      editorActions.toggleComment(ta);
    } else if (mod && (e.key === "r" || e.key === "R") && !e.shiftKey) {
      e.preventDefault();
      onRun?.();
    } else if (mod && e.key === "]") {
      e.preventDefault();
      editorActions.indent(ta);
    } else if (mod && e.key === "[") {
      e.preventDefault();
      editorActions.outdent(ta);
    }
  };

  return html`<div class="editor" onClick=${(e) => { if (e.target === e.currentTarget) ref.current?.focus(); }}>
    <div class="editor-inner" style=${{ "--cols": longest + 2, "--rows": lines.length }}>
      <div class="gutter" aria-hidden="true">${lines.map((_, i) => html`<div>${i + 1}</div>`)}</div>
      <div class="code-layers">
        <pre class="code-hl" aria-hidden="true" dangerouslySetInnerHTML=${{ __html: highlightPython(code) + "\n" }}></pre>
        <textarea ref=${ref} class="code-input" value=${code} onInput=${onInput} onKeyDown=${onKeyDown}
          onKeyUp=${(e) => snapLeft(e.currentTarget)} onClick=${(e) => snapLeft(e.currentTarget)}
          rows=${lines.length} spellcheck=${false} autocapitalize="off" autocomplete="off" autocorrect="off"
          wrap="off" aria-label="Your Python solution"></textarea>
      </div>
    </div>
  </div>`;
}
