import LeetlingShared
import SwiftUI

struct ProblemView: View {
    @Environment(AppStore.self) private var store
    let problem: Problem

    @Local private var code = ""
    @Local private var loaded = false
    @Local private var result: RunResult? = nil
    @Local private var running: CodeRunner.Mode? = nil
    @Local private var confirmReset = false

    var body: some View {
        VStack(spacing: 0) {
            topBar
            HSplitView {
                ProblemInfoPane(problem: problem)
                    .frame(minWidth: 360, idealWidth: 470, maxWidth: 700)
                VSplitView {
                    editorPane
                        .frame(minHeight: 260)
                    ConsolePane(result: result, running: running)
                        .frame(minHeight: 150, idealHeight: 240)
                }
                .frame(minWidth: 480)
            }
        }
        .onAppear {
            guard !loaded else { return }
            code = store.draft(for: problem)
            loaded = true
        }
        .onChange(of: code) { _, newValue in
            if loaded { store.setDraft(newValue, for: problem) }
        }
        .alert("Reset your code?", isPresented: $confirmReset) {
            Button("Reset", role: .destructive) {
                store.resetDraft(for: problem)
                code = problem.starter
            }
            Button("Keep it", role: .cancel) {}
        } message: {
            Text("This replaces your current code with the starter template.")
        }
    }

    private var topBar: some View {
        HStack(spacing: 12) {
            Button {
                store.openProblemID = nil
            } label: {
                Label(store.section.title, systemImage: "chevron.left")
            }
            .buttonStyle(.cozy(.quiet, compact: true))
            .keyboardShortcut(.escape, modifiers: [])

            Text(problem.categoryEmoji)
            Text("\(problem.title)")
                .font(.system(size: 17, weight: .heavy, design: .rounded))
                .foregroundStyle(Theme.plum)
                .lineLimit(1)
            DifficultyPill(difficulty: problem.difficulty)
            if store.progress.isSolved(problem.id) { Pill(text: "✓ Solved", color: Theme.mintDeep) }
            Spacer()
            Text("Python 3")
                .font(.system(size: 11.5, weight: .bold, design: .monospaced))
                .foregroundStyle(Theme.mauve)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(Theme.cream)
        .overlay(alignment: .bottom) { Divider().overlay(Theme.blush) }
    }

    private var editorPane: some View {
        VStack(spacing: 0) {
            HStack(spacing: 8) {
                Image(systemName: "chevron.left.forwardslash.chevron.right")
                    .foregroundStyle(Theme.rose)
                Text("solution.py")
                    .font(.system(size: 12.5, weight: .semibold, design: .monospaced))
                    .foregroundStyle(Theme.plum)
                Spacer()
                Button {
                    confirmReset = true
                } label: {
                    Image(systemName: "arrow.counterclockwise")
                }
                .buttonStyle(.cozy(.quiet, compact: true))
                .help("Reset to starter code")

                Button {
                    execute(.run)
                } label: {
                    Label(running == .run ? "Running…" : "Run", systemImage: "play.fill")
                }
                .buttonStyle(.cozy(.secondary, compact: true))
                .keyboardShortcut("r", modifiers: [.command])
                .help("Run the example tests (⌘R)")
                .disabled(running != nil)

                Button {
                    execute(.submit)
                } label: {
                    Label(running == .submit ? "Judging…" : "Submit", systemImage: "paperplane.fill")
                }
                .buttonStyle(.cozy(.mint, compact: true))
                .keyboardShortcut(.return, modifiers: [.command])
                .help("Run every test, including hidden ones (⌘↩)")
                .disabled(running != nil)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Theme.cream)

            CodeEditor(text: $code)
        }
    }

    private func execute(_ mode: CodeRunner.Mode) {
        guard running == nil else { return }
        running = mode
        store.setDraft(code, for: problem)
        if mode == .submit { store.recordAttempt(problem) }
        let source = code
        Task {
            let r = await CodeRunner.run(problemID: problem.id, code: source, mode: mode)
            withAnimation(.spring(response: 0.35)) {
                result = r
                running = nil
            }
            if mode == .submit && r.accepted {
                store.recordAccepted(problem)
            }
        }
    }
}

// MARK: - Left pane: description, examples, hints, solution

private struct ProblemInfoPane: View {
    @Environment(AppStore.self) private var store
    let problem: Problem
    @Local private var showSolution = false
    @Local private var confirmPeek = false

    private let hintLabels = [("🌱", "Nudge"), ("🌷", "Approach"), ("🌸", "Almost there")]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("\(problem.id). \(problem.title)")
                        .font(.system(size: 22, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.plum)
                    HStack(spacing: 6) {
                        DifficultyPill(difficulty: problem.difficulty)
                        Pill(text: problem.category, color: Color(hex: 0x8C6FE0))
                        Pill(text: "LeetCode #\(problem.lc)", color: Theme.mauve)
                    }
                }

                RichText(text: problem.description)

                ForEach(Array(problem.examples.enumerated()), id: \.offset) { i, ex in
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Example \(i + 1)")
                            .font(.system(size: 13, weight: .heavy, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        VStack(alignment: .leading, spacing: 4) {
                            labeled("Input", ex.input)
                            labeled("Output", ex.output)
                            if let why = ex.explanation {
                                Text(why)
                                    .font(.system(size: 12.5, design: .rounded))
                                    .foregroundStyle(Theme.mauve)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                        .padding(12)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(RoundedRectangle(cornerRadius: 12, style: .continuous).fill(Theme.lilac.opacity(0.6)))
                    }
                }

                if !problem.constraints.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Constraints")
                            .font(.system(size: 13, weight: .heavy, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        ForEach(problem.constraints, id: \.self) { c in
                            HStack(alignment: .firstTextBaseline, spacing: 6) {
                                Text("•").foregroundStyle(Theme.rose)
                                Text(c).font(.system(size: 12, design: .monospaced)).foregroundStyle(Theme.plum)
                            }
                        }
                    }
                }

                hints
                solution
            }
            .padding(22)
        }
        .background(Theme.paper)
        .alert("Peek at the solution?", isPresented: $confirmPeek) {
            Button("Show me 👀") {
                store.peekSolution(problem)
                withAnimation { showSolution = true }
            }
            Button("I'll try a bit more 💪", role: .cancel) {}
        } message: {
            Text("No judgment! Reading a solution and then re-writing it from memory tomorrow is a great way to learn.")
        }
    }

    private func labeled(_ label: String, _ value: String) -> some View {
        HStack(alignment: .firstTextBaseline, spacing: 6) {
            Text(label + ":")
                .font(.system(size: 12, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.plum)
            Text(value)
                .font(.system(size: 12, design: .monospaced))
                .foregroundStyle(Theme.plum)
                .textSelection(.enabled)
                .fixedSize(horizontal: false, vertical: true)
        }
    }

    private var hints: some View {
        let revealed = store.hintsRevealed(problem)
        return VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("\(store.buddy?.emoji ?? "🐰") Stuck? Ask for a hint")
                    .font(.system(size: 15, weight: .heavy, design: .rounded))
                    .foregroundStyle(Theme.plum)
                Spacer()
                Text("\(revealed)/3")
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
            Text("Hints go from a gentle nudge to almost the whole idea. Try one at a time!")
                .font(.system(size: 12, design: .rounded))
                .foregroundStyle(Theme.mauve)

            ForEach(0..<min(revealed, problem.hints.count), id: \.self) { i in
                VStack(alignment: .leading, spacing: 6) {
                    Text("\(hintLabels[i].0) Hint \(i + 1) · \(hintLabels[i].1)")
                        .font(.system(size: 12, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.roseDeep)
                    RichText(text: problem.hints[i], size: 13)
                }
                .padding(12)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(Theme.blush.opacity(0.4)))
                .transition(.opacity.combined(with: .move(edge: .top)))
            }

            HStack(spacing: 8) {
                ForEach(0..<3, id: \.self) { i in
                    Button {
                        withAnimation(.spring(response: 0.4)) { store.revealHint(problem) }
                    } label: {
                        Text("\(hintLabels[i].0) \(hintLabels[i].1)")
                    }
                    .buttonStyle(.cozy(i < revealed ? .quiet : .secondary, compact: true))
                    .disabled(i != revealed)
                    .opacity(i > revealed ? 0.45 : 1)
                }
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 18, style: .continuous).strokeBorder(Theme.blush, lineWidth: 1.5))
    }

    @ViewBuilder private var solution: some View {
        let solved = store.progress.isSolved(problem.id)
        let unlocked = solved || store.hintsRevealed(problem) >= 3
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("📖 Solution")
                    .font(.system(size: 15, weight: .heavy, design: .rounded))
                    .foregroundStyle(Theme.plum)
                Spacer()
                if showSolution {
                    Button("Hide") { withAnimation { showSolution = false } }
                        .buttonStyle(.cozy(.quiet, compact: true))
                } else if unlocked {
                    Button(solved ? "Compare with mine" : "Peek 👀") {
                        if solved { withAnimation { showSolution = true } } else { confirmPeek = true }
                    }
                    .buttonStyle(.cozy(.secondary, compact: true))
                }
            }
            if !unlocked {
                Text("🔒 Unlocks after you solve it, or after all 3 hints.")
                    .font(.system(size: 12, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
            if showSolution {
                Text(problem.solution)
                    .font(.system(size: 12.5, design: .monospaced))
                    .foregroundStyle(Theme.plum)
                    .textSelection(.enabled)
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 12, style: .continuous).fill(Theme.lilac.opacity(0.6)))
                Text("⏱ \(problem.complexity)")
                    .font(.system(size: 12, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
        }
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 18, style: .continuous).strokeBorder(Theme.blush, lineWidth: 1.5))
    }
}

// MARK: - Console

private struct ConsolePane: View {
    let result: RunResult?
    let running: CodeRunner.Mode?
    @Local private var selected = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack {
                Text("Console")
                    .font(.system(size: 12.5, weight: .heavy, design: .rounded))
                    .foregroundStyle(Theme.plum)
                Spacer()
                if let r = result, let ms = r.runtime_ms {
                    Text("\(ms) ms")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundStyle(Theme.mauve)
                }
            }
            .padding(.horizontal, 14).padding(.vertical, 7)
            .background(Theme.cream)
            Divider().overlay(Theme.blush)

            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    if let running {
                        HStack(spacing: 10) {
                            ProgressView().controlSize(.small)
                            Text(running == .run ? "Running the examples… 🐇" : "Judging against every test… 🧑‍⚖️")
                                .font(.system(size: 13, weight: .semibold, design: .rounded))
                                .foregroundStyle(Theme.plum)
                        }
                    } else if let result {
                        resultView(result)
                    } else {
                        Text("**Run** (⌘R) tries the examples. **Submit** (⌘↩) checks every test, including hidden ones — pass them all to earn your rewards 🎁")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.mauve)
                    }
                }
                .padding(14)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
        }
        .background(Theme.paper)
        .onChange(of: result) { _, r in
            selected = r?.results.firstIndex(where: { !$0.passed }) ?? 0
        }
    }

    private func color(_ r: RunResult) -> Color { r.accepted ? Theme.mintDeep : r.status == "wrong_answer" ? Theme.medium : Theme.berry }

    @ViewBuilder private func resultView(_ r: RunResult) -> some View {
        HStack(spacing: 8) {
            Text(r.emoji).font(.system(size: 20))
            Text(r.title)
                .font(.system(size: 17, weight: .heavy, design: .rounded))
                .foregroundStyle(color(r))
            if r.total > 0 {
                Text("\(r.passed)/\(r.total) tests passed")
                    .font(.system(size: 12.5, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
        }
        if !r.message.isEmpty { codeBlock(r.message, tint: Theme.berry) }
        if r.status == "wrong_answer" || r.status == "runtime_error" {
            Text(r.passed > 0 ? "So close — you're on the right track! 💪" : "Every bug is a lesson. Check the case below 🔎")
                .font(.system(size: 12, weight: .medium, design: .rounded))
                .foregroundStyle(Theme.mauve)
        }

        if !r.results.isEmpty {
            HStack(spacing: 6) {
                ForEach(Array(r.results.enumerated()), id: \.offset) { i, t in
                    Button {
                        selected = i
                    } label: {
                        HStack(spacing: 4) {
                            Circle().fill(t.passed ? Theme.mintDeep : Theme.berry).frame(width: 7, height: 7)
                            Text(t.hidden ? "Hidden test" : "Case \(t.index + 1)")
                        }
                    }
                    .buttonStyle(.cozy(selected == i ? .quiet : .secondary, compact: true))
                }
            }
            if r.results.indices.contains(selected) {
                let t = r.results[selected]
                VStack(alignment: .leading, spacing: 8) {
                    field("Input", t.input)
                    if !t.error.isEmpty {
                        field("Error", t.error, tint: Theme.berry)
                    } else {
                        field("Your output", t.output, tint: t.passed ? nil : Theme.berry)
                    }
                    field("Expected", t.expected)
                    if !t.stdout.isEmpty { field("Stdout (your print statements)", t.stdout) }
                }
            }
        }
    }

    private func field(_ label: String, _ value: String, tint: Color? = nil) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.system(size: 11.5, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.mauve)
            codeBlock(value.isEmpty ? " " : value, tint: tint)
        }
    }

    private func codeBlock(_ s: String, tint: Color? = nil) -> some View {
        Text(s)
            .font(.system(size: 12.5, design: .monospaced))
            .foregroundStyle(tint ?? Theme.plum)
            .textSelection(.enabled)
            .padding(10)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(RoundedRectangle(cornerRadius: 10, style: .continuous).fill(Theme.lilac.opacity(0.55)))
    }
}
