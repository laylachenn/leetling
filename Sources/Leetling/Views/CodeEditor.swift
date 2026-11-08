import AppKit
import LeetlingShared
import SwiftUI

/// A small Python code editor: syntax highlighting, line numbers, auto-indent,
/// Tab = 4 spaces, Shift-Tab dedent, smart backspace, ⌘/ toggles comments.
struct CodeEditor: NSViewRepresentable {
    @Binding var text: String
    var fontSize: CGFloat = 14

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeNSView(context: Context) -> NSScrollView {
        let storage = NSTextStorage()
        let layout = NSLayoutManager()
        storage.addLayoutManager(layout)
        let container = NSTextContainer(size: NSSize(width: 0, height: CGFloat.greatestFiniteMagnitude))
        container.widthTracksTextView = true
        layout.addTextContainer(container)

        let textView = CodeTextView(frame: .zero, textContainer: container)
        textView.font = Self.font(fontSize)
        textView.isRichText = false
        textView.allowsUndo = true
        textView.isAutomaticQuoteSubstitutionEnabled = false
        textView.isAutomaticDashSubstitutionEnabled = false
        textView.isAutomaticTextReplacementEnabled = false
        textView.isAutomaticSpellingCorrectionEnabled = false
        textView.isContinuousSpellCheckingEnabled = false
        textView.isGrammarCheckingEnabled = false
        textView.isAutomaticLinkDetectionEnabled = false
        textView.smartInsertDeleteEnabled = false
        textView.usesFindBar = true
        textView.isIncrementalSearchingEnabled = true
        textView.backgroundColor = NSColor(Theme.paper)
        textView.insertionPointColor = NSColor(Theme.roseDeep)
        textView.selectedTextAttributes = [.backgroundColor: NSColor(Theme.blush)]
        textView.textContainerInset = NSSize(width: 8, height: 12)
        textView.isVerticallyResizable = true
        textView.isHorizontallyResizable = false
        textView.autoresizingMask = [.width]
        textView.minSize = NSSize(width: 0, height: 0)
        textView.maxSize = NSSize(width: CGFloat.greatestFiniteMagnitude, height: CGFloat.greatestFiniteMagnitude)
        let paragraph = NSMutableParagraphStyle()
        paragraph.lineSpacing = 3
        textView.defaultParagraphStyle = paragraph
        textView.typingAttributes = [.font: Self.font(fontSize), .foregroundColor: Highlighter.plain, .paragraphStyle: paragraph]
        textView.delegate = context.coordinator
        textView.string = text

        let scroll = NSScrollView()
        scroll.hasVerticalScroller = true
        scroll.drawsBackground = true
        scroll.backgroundColor = NSColor(Theme.paper)
        scroll.documentView = textView
        scroll.contentView.postsBoundsChangedNotifications = true

        let ruler = LineNumberRuler(textView: textView, scrollView: scroll)
        scroll.verticalRulerView = ruler
        scroll.hasVerticalRuler = true
        scroll.rulersVisible = true
        context.coordinator.ruler = ruler

        NotificationCenter.default.addObserver(forName: NSView.boundsDidChangeNotification, object: scroll.contentView, queue: .main) { _ in
            ruler.needsDisplay = true
        }

        Highlighter.apply(to: textView, fontSize: fontSize)
        return scroll
    }

    func updateNSView(_ scroll: NSScrollView, context: Context) {
        context.coordinator.parent = self
        guard let textView = scroll.documentView as? NSTextView else { return }
        if textView.string != text {
            textView.string = text
            Highlighter.apply(to: textView, fontSize: fontSize)
            context.coordinator.ruler?.needsDisplay = true
        }
    }

    static func font(_ size: CGFloat) -> NSFont {
        NSFont(name: "SF Mono", size: size) ?? NSFont.monospacedSystemFont(ofSize: size, weight: .regular)
    }

    final class Coordinator: NSObject, NSTextViewDelegate {
        var parent: CodeEditor
        weak var ruler: LineNumberRuler?

        init(_ parent: CodeEditor) { self.parent = parent }

        func textDidChange(_ notification: Notification) {
            guard let textView = notification.object as? NSTextView else { return }
            Highlighter.apply(to: textView, fontSize: parent.fontSize)
            ruler?.needsDisplay = true
            parent.text = textView.string
        }

        func textView(_ textView: NSTextView, doCommandBy selector: Selector) -> Bool {
            switch selector {
            case #selector(NSResponder.insertNewline(_:)): return Editing.newline(textView)
            case #selector(NSResponder.insertTab(_:)): return Editing.tab(textView)
            case #selector(NSResponder.insertBacktab(_:)): return Editing.backtab(textView)
            case #selector(NSResponder.deleteBackward(_:)): return Editing.smartBackspace(textView)
            default: return false
            }
        }
    }
}

final class CodeTextView: NSTextView {
    override func performKeyEquivalent(with event: NSEvent) -> Bool {
        if event.modifierFlags.intersection(.deviceIndependentFlagsMask) == .command,
           event.charactersIgnoringModifiers == "/", window?.firstResponder === self {
            Editing.toggleComment(self)
            return true
        }
        return super.performKeyEquivalent(with: event)
    }
}

// MARK: - Editing behaviors

enum Editing {
    static let indentUnit = "    "

    private static func replace(_ tv: NSTextView, _ range: NSRange, with string: String, select: NSRange? = nil) {
        guard tv.shouldChangeText(in: range, replacementString: string) else { return }
        tv.textStorage?.replaceCharacters(in: range, with: string)
        tv.didChangeText()
        tv.setSelectedRange(select ?? NSRange(location: range.location + (string as NSString).length, length: 0))
    }

    static func newline(_ tv: NSTextView) -> Bool {
        let ns = tv.string as NSString
        let sel = tv.selectedRange()
        let line = ns.lineRange(for: NSRange(location: sel.location, length: 0))
        let beforeCursor = ns.substring(with: NSRange(location: line.location, length: sel.location - line.location))
        let indent = String(beforeCursor.prefix { $0 == " " || $0 == "\t" })
        let trimmed = beforeCursor.trimmingCharacters(in: .whitespaces)
        var extra = ""
        if trimmed.hasSuffix(":") || trimmed.hasSuffix("(") || trimmed.hasSuffix("[") || trimmed.hasSuffix("{") {
            extra = indentUnit
        }
        tv.insertText("\n" + indent + extra, replacementRange: sel)
        return true
    }

    private static func selectedLines(_ tv: NSTextView) -> NSRange {
        (tv.string as NSString).lineRange(for: tv.selectedRange())
    }

    static func tab(_ tv: NSTextView) -> Bool {
        let ns = tv.string as NSString
        let sel = tv.selectedRange()
        let lines = selectedLines(tv)
        if sel.length > 0, ns.substring(with: sel).contains("\n") {
            let block = ns.substring(with: lines)
            let indented = block.split(separator: "\n", omittingEmptySubsequences: false).enumerated().map { i, l in
                (l.isEmpty && i > 0) ? String(l) : indentUnit + l
            }.joined(separator: "\n")
            replace(tv, lines, with: indented, select: NSRange(location: lines.location, length: (indented as NSString).length))
        } else {
            let column = sel.location - ns.lineRange(for: NSRange(location: sel.location, length: 0)).location
            let spaces = 4 - (column % 4)
            tv.insertText(String(repeating: " ", count: spaces), replacementRange: sel)
        }
        return true
    }

    static func backtab(_ tv: NSTextView) -> Bool {
        let ns = tv.string as NSString
        let lines = selectedLines(tv)
        let block = ns.substring(with: lines)
        let dedented = block.split(separator: "\n", omittingEmptySubsequences: false).map { l -> String in
            let n = min(4, l.prefix { $0 == " " }.count)
            return String(l.dropFirst(n))
        }.joined(separator: "\n")
        if dedented != block {
            replace(tv, lines, with: dedented, select: NSRange(location: lines.location, length: (dedented as NSString).length))
        }
        return true
    }

    static func smartBackspace(_ tv: NSTextView) -> Bool {
        let ns = tv.string as NSString
        let sel = tv.selectedRange()
        guard sel.length == 0, sel.location > 0 else { return false }
        let line = ns.lineRange(for: NSRange(location: sel.location, length: 0))
        let before = ns.substring(with: NSRange(location: line.location, length: sel.location - line.location))
        guard !before.isEmpty, before.allSatisfy({ $0 == " " }) else { return false }
        let n = before.count % 4 == 0 ? 4 : before.count % 4
        replace(tv, NSRange(location: sel.location - n, length: n), with: "")
        return true
    }

    static func toggleComment(_ tv: NSTextView) {
        let ns = tv.string as NSString
        let lines = selectedLines(tv)
        var block = ns.substring(with: lines)
        let hadTrailingNewline = block.hasSuffix("\n")
        if hadTrailingNewline { block.removeLast() }
        let parts = block.split(separator: "\n", omittingEmptySubsequences: false).map(String.init)
        let nonEmpty = parts.filter { !$0.trimmingCharacters(in: .whitespaces).isEmpty }
        let allCommented = !nonEmpty.isEmpty && nonEmpty.allSatisfy { $0.trimmingCharacters(in: .whitespaces).hasPrefix("#") }
        let minIndent = nonEmpty.map { $0.prefix { $0 == " " }.count }.min() ?? 0
        let result = parts.map { l -> String in
            if l.trimmingCharacters(in: .whitespaces).isEmpty { return l }
            if allCommented {
                guard let r = l.range(of: "#") else { return l }
                var after = l[r.upperBound...]
                if after.hasPrefix(" ") { after = after.dropFirst() }
                return String(l[..<r.lowerBound]) + after
            }
            let idx = l.index(l.startIndex, offsetBy: minIndent)
            return String(l[..<idx]) + "# " + String(l[idx...])
        }.joined(separator: "\n") + (hadTrailingNewline ? "\n" : "")
        replace(tv, lines, with: result, select: NSRange(location: lines.location, length: (result as NSString).length))
    }
}

// MARK: - Syntax highlighting

enum Highlighter {
    static let plain = NSColor(Theme.plum)
    static let keyword = NSColor(Color(hex: 0xD6457A))
    static let builtin = NSColor(Color(hex: 0x7B5BD6))
    static let string = NSColor(Color(hex: 0x2E9C74))
    static let number = NSColor(Color(hex: 0xD9822B))
    static let comment = NSColor(Color(hex: 0xA894A2))
    static let definition = NSColor(Color(hex: 0x3B7DD8))

    private static let keywords = ["False", "None", "True", "and", "as", "assert", "break", "class", "continue", "def", "del",
                                   "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in", "is",
                                   "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"]
    private static let builtins = ["self", "len", "range", "enumerate", "zip", "min", "max", "sum", "sorted", "reversed", "list",
                                   "dict", "set", "tuple", "int", "str", "float", "bool", "print", "abs", "any", "all", "map",
                                   "filter", "ord", "chr", "isinstance", "List", "Optional", "Dict", "Set", "Tuple", "deque",
                                   "defaultdict", "Counter", "heapq", "inf", "float", "super", "iter", "next", "divmod", "pow",
                                   "ListNode", "TreeNode", "Node", "collections", "math", "bisect"]

    private static func regex(_ pattern: String) -> NSRegularExpression {
        try! NSRegularExpression(pattern: pattern)
    }

    private static let keywordRegex = regex("\\b(" + keywords.joined(separator: "|") + ")\\b")
    private static let builtinRegex = regex("\\b(" + builtins.joined(separator: "|") + ")\\b")
    private static let numberRegex = regex("\\b(0x[0-9a-fA-F]+|\\d+(\\.\\d+)?)\\b")
    private static let definitionRegex = regex("\\b(?:def|class)\\s+([A-Za-z_][A-Za-z0-9_]*)")
    private static let decoratorRegex = regex("^\\s*@[A-Za-z_][\\w.]*")
    private static let stringOrComment = regex(#"("""[\s\S]*?(?:"""|\z)|'''[\s\S]*?(?:'''|\z)|"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?|#[^\n]*)"#)

    static func apply(to textView: NSTextView, fontSize: CGFloat) {
        guard let storage = textView.textStorage else { return }
        let text = storage.string
        let full = NSRange(location: 0, length: (text as NSString).length)
        let font = CodeEditor.font(fontSize)
        let italic = NSFontManager.shared.convert(font, toHaveTrait: .italicFontMask)
        let paragraph = textView.defaultParagraphStyle ?? NSParagraphStyle.default

        storage.beginEditing()
        storage.setAttributes([.font: font, .foregroundColor: plain, .paragraphStyle: paragraph], range: full)
        numberRegex.enumerateMatches(in: text, range: full) { m, _, _ in
            if let r = m?.range { storage.addAttribute(.foregroundColor, value: number, range: r) }
        }
        builtinRegex.enumerateMatches(in: text, range: full) { m, _, _ in
            if let r = m?.range { storage.addAttribute(.foregroundColor, value: builtin, range: r) }
        }
        keywordRegex.enumerateMatches(in: text, range: full) { m, _, _ in
            if let r = m?.range { storage.addAttributes([.foregroundColor: keyword, .font: NSFontManager.shared.convert(font, toHaveTrait: .boldFontMask)], range: r) }
        }
        definitionRegex.enumerateMatches(in: text, range: full) { m, _, _ in
            if let r = m?.range(at: 1) { storage.addAttribute(.foregroundColor, value: definition, range: r) }
        }
        decoratorRegex.enumerateMatches(in: text, options: [], range: full) { m, _, _ in
            if let r = m?.range { storage.addAttribute(.foregroundColor, value: builtin, range: r) }
        }
        stringOrComment.enumerateMatches(in: text, range: full) { m, _, _ in
            guard let r = m?.range, r.length > 0 else { return }
            let isComment = (text as NSString).character(at: r.location) == UInt16(UInt8(ascii: "#"))
            storage.addAttributes(isComment ? [.foregroundColor: comment, .font: italic] : [.foregroundColor: string, .font: font], range: r)
        }
        storage.endEditing()
        textView.typingAttributes = [.font: font, .foregroundColor: plain, .paragraphStyle: paragraph]
    }
}

// MARK: - Line numbers

final class LineNumberRuler: NSRulerView {
    private weak var textView: NSTextView?

    init(textView: NSTextView, scrollView: NSScrollView) {
        self.textView = textView
        super.init(scrollView: scrollView, orientation: .verticalRuler)
        clientView = textView
        ruleThickness = 38
    }

    required init(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    override func drawHashMarksAndLabels(in rect: NSRect) {
        NSColor(Theme.blush.opacity(0.35)).setFill()
        bounds.fill()
        guard let tv = textView, let lm = tv.layoutManager, let tc = tv.textContainer else { return }

        let attrs: [NSAttributedString.Key: Any] = [
            .font: NSFont.monospacedDigitSystemFont(ofSize: 11, weight: .medium),
            .foregroundColor: NSColor(Theme.mauve.opacity(0.85)),
        ]
        let ns = tv.string as NSString
        let visible = tv.visibleRect
        let glyphs = lm.glyphRange(forBoundingRect: visible, in: tc)
        let chars = lm.characterRange(forGlyphRange: glyphs, actualGlyphRange: nil)

        var lineNumber = 1
        if chars.location > 0 {
            let prefix = ns.substring(to: chars.location)
            lineNumber += prefix.reduce(0) { $1 == "\n" ? $0 + 1 : $0 }
        }

        func draw(_ n: Int, atY y: CGFloat, height: CGFloat) {
            let label = "\(n)" as NSString
            let size = label.size(withAttributes: attrs)
            let point = convert(NSPoint(x: 0, y: y), from: tv)
            label.draw(at: NSPoint(x: ruleThickness - size.width - 8, y: point.y + (height - size.height) / 2), withAttributes: attrs)
        }

        var index = chars.location
        while index < NSMaxRange(chars) {
            let lineRange = ns.lineRange(for: NSRange(location: index, length: 0))
            let glyph = lm.glyphIndexForCharacter(at: lineRange.location)
            let frag = lm.lineFragmentRect(forGlyphAt: glyph, effectiveRange: nil)
            draw(lineNumber, atY: frag.minY + tv.textContainerInset.height, height: frag.height - 3)
            lineNumber += 1
            index = NSMaxRange(lineRange)
        }
        let extra = lm.extraLineFragmentRect
        if ns.length == 0 || ns.hasSuffix("\n"), extra.height > 0 {
            draw(lineNumber, atY: extra.minY + tv.textContainerInset.height, height: extra.height - 3)
        }
    }
}
