import LeetlingShared
import SwiftUI

struct ProblemListView: View {
    @Environment(AppStore.self) private var store
    @Local private var search = ""
    @Local private var difficulty: String? = nil
    @Local private var unsolvedOnly = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                HStack(alignment: .firstTextBaseline) {
                    Text("All 75 problems 📚")
                        .font(.system(size: 28, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.plum)
                    Spacer()
                    Text("\(store.solvedCount) solved")
                        .font(.system(size: 14, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }
                filters
                ForEach(store.categories, id: \.self) { cat in
                    let items = store.problems(in: cat).filter(matches)
                    if !items.isEmpty {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                SectionTitle(title: cat, emoji: Problem.categoryEmoji[cat])
                                Spacer()
                                Text("\(store.solvedCount(in: cat))/\(store.problems(in: cat).count)")
                                    .font(.system(size: 12, weight: .heavy, design: .rounded))
                                    .foregroundStyle(Theme.mauve)
                            }
                            VStack(spacing: 0) {
                                ForEach(Array(items.enumerated()), id: \.element.id) { i, p in
                                    ProblemRow(problem: p)
                                    if i < items.count - 1 { Divider().overlay(Theme.blush) }
                                }
                            }
                            .cozyCard(padding: 4)
                        }
                    }
                }
            }
            .padding(28)
            .frame(maxWidth: 900)
            .frame(maxWidth: .infinity)
        }
    }

    private var filters: some View {
        HStack(spacing: 8) {
            HStack(spacing: 6) {
                Image(systemName: "magnifyingglass").foregroundStyle(Theme.mauve)
                TextField("Search problems…", text: $search)
                    .textFieldStyle(.plain)
                    .font(.system(size: 13, design: .rounded))
            }
            .padding(.horizontal, 12).padding(.vertical, 8)
            .background(Capsule().fill(Theme.paper))
            .overlay(Capsule().strokeBorder(Theme.blush))
            .frame(maxWidth: 260)

            ForEach([nil, "Easy", "Medium", "Hard"], id: \.self) { d in
                let selected = difficulty == d
                Button(d ?? "All") { difficulty = d }
                    .buttonStyle(.cozy(selected ? .primary : .quiet, compact: true))
            }
            Spacer()
            Toggle("Unsolved only", isOn: $unsolvedOnly)
                .toggleStyle(.switch)
                .controlSize(.small)
                .font(.system(size: 12.5, weight: .semibold, design: .rounded))
                .foregroundStyle(Theme.plum)
        }
    }

    private func matches(_ p: Problem) -> Bool {
        if let difficulty, p.difficulty != difficulty { return false }
        if unsolvedOnly, store.progress.isSolved(p.id) { return false }
        if !search.isEmpty, !p.title.localizedCaseInsensitiveContains(search), String(p.lc) != search { return false }
        return true
    }
}

private struct ProblemRow: View {
    @Environment(AppStore.self) private var store
    let problem: Problem
    @Local private var hovering = false

    var body: some View {
        let solved = store.progress.isSolved(problem.id)
        let attempts = store.progress.attempts[String(problem.id)] ?? 0
        Button { store.open(problem) } label: {
            HStack(spacing: 12) {
                Image(systemName: solved ? "checkmark.circle.fill" : attempts > 0 ? "circle.lefthalf.filled" : "circle")
                    .font(.system(size: 16))
                    .foregroundStyle(solved ? Theme.mintDeep : attempts > 0 ? Theme.medium : Theme.blush)
                Text("\(problem.id).")
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
                    .frame(width: 26, alignment: .trailing)
                Text(problem.title)
                    .font(.system(size: 14, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.plum)
                Spacer()
                if attempts > 0 && !solved {
                    Text("\(attempts) tr\(attempts == 1 ? "y" : "ies")")
                        .font(.system(size: 11, weight: .semibold, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }
                Text("LC \(problem.lc)")
                    .font(.system(size: 11, weight: .semibold, design: .monospaced))
                    .foregroundStyle(Theme.mauve.opacity(0.8))
                DifficultyPill(difficulty: problem.difficulty)
                    .frame(width: 70, alignment: .trailing)
            }
            .padding(.horizontal, 14).padding(.vertical, 10)
            .background(RoundedRectangle(cornerRadius: 14).fill(hovering ? Theme.blush.opacity(0.3) : .clear))
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .onHover { hovering = $0 }
    }
}
