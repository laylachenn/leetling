import LeetlingShared
import SwiftUI

struct TodayView: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                header
                HStack(alignment: .top, spacing: 18) {
                    StreakCard(snapshot: store.snapshot)
                        .cozyCard()
                        .frame(maxWidth: .infinity)
                    BuddyCard()
                        .frame(width: 270)
                }
                ModePicker()
                NextProblemCard()
                if store.progress.totalPacks > 0 { packsTeaser }
                TopicProgressGrid()
            }
            .padding(28)
            .frame(maxWidth: 980)
            .frame(maxWidth: .infinity)
        }
        .onAppear { store.ensureRandomPick() }
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("\(greeting), \(store.displayName) \(greetingEmoji)")
                .font(.system(size: 30, weight: .heavy, design: .rounded))
                .foregroundStyle(Theme.plum)
            Text(Encouragement.line(for: Date()))
                .font(.system(size: 15, weight: .medium, design: .rounded))
                .foregroundStyle(Theme.mauve)
        }
    }

    private var greeting: String {
        switch Calendar.current.component(.hour, from: Date()) {
        case 5..<12: return "Good morning"
        case 12..<17: return "Good afternoon"
        case 17..<22: return "Good evening"
        default: return "Hi night owl"
        }
    }

    private var greetingEmoji: String {
        switch Calendar.current.component(.hour, from: Date()) {
        case 5..<12: return "☀️"
        case 12..<17: return "🌷"
        case 17..<22: return "🌙"
        default: return "🦉"
        }
    }

    private var packsTeaser: some View {
        Button {
            store.section = .packs
        } label: {
            HStack(spacing: 14) {
                Text("🎁").font(.system(size: 34))
                VStack(alignment: .leading, spacing: 2) {
                    Text("You have \(store.progress.totalPacks) pack\(store.progress.totalPacks == 1 ? "" : "s") to open!")
                        .font(.system(size: 17, weight: .heavy, design: .rounded))
                    Text("Go see who's inside ✨")
                        .font(.system(size: 13, weight: .medium, design: .rounded))
                        .opacity(0.85)
                }
                Spacer()
                Image(systemName: "chevron.right").font(.system(size: 16, weight: .bold))
            }
            .foregroundStyle(.white)
            .padding(18)
            .background(RoundedRectangle(cornerRadius: 22, style: .continuous).fill(
                LinearGradient(colors: [Theme.rose, Color(hex: 0xB59CFF)], startPoint: .leading, endPoint: .trailing)))
            .shadow(color: Theme.rose.opacity(0.35), radius: 12, y: 6)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Buddy

private struct BuddyCard: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        VStack(spacing: 10) {
            Text(message)
                .font(.system(size: 13, weight: .semibold, design: .rounded))
                .foregroundStyle(Theme.plum)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 12).padding(.vertical, 9)
                .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(Theme.lilac))
                .fixedSize(horizontal: false, vertical: true)
            // The buddy stays still on purpose; the user found the bouncing distracting.
            if let buddy = store.buddy {
                LeetlingArt(critter: buddy, size: 58)
                Text(buddy.name)
                    .font(.system(size: 13, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            } else {
                Text("🥚").font(.system(size: 58))
                Text("Open a pack to meet your buddy!")
                    .font(.system(size: 12, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
            HStack(spacing: 5) {
                ForEach(0..<store.progress.dailyGoal, id: \.self) { i in
                    Image(systemName: i < store.todayCount ? "heart.fill" : "heart")
                        .foregroundStyle(Theme.roseDeep)
                }
                Text("\(min(store.todayCount, store.progress.dailyGoal))/\(store.progress.dailyGoal) today")
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.plum)
            }
        }
        .frame(maxWidth: .infinity)
        .cozyCard(padding: 16)
    }

    private var message: String {
        let today = store.todayCount, goal = store.progress.dailyGoal
        if store.solvedCount == store.problems.count { return "You finished the Blind 75?! I'm crying 😭💖" }
        if today >= goal { return today > goal ? "Overachiever!! I love you 💞" : "Goal met! I'm so proud of you 💖" }
        if today > 0 { return "One down! \(goal - today) more for today's goal 🌷" }
        if store.streak > 0 { return "Let's keep our \(store.streak)-day streak alive! 🔥" }
        return "Let's do just one problem today? 🥺👉👈"
    }
}

// MARK: - Mode picker

private struct ModePicker: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            SectionTitle(title: "How do you want to practice?", emoji: "🎀")
            HStack(spacing: 12) {
                ForEach(PracticeMode.allCases) { mode in
                    let selected = store.progress.mode == mode
                    Button {
                        withAnimation(.spring(response: 0.35)) { store.setMode(mode) }
                    } label: {
                        VStack(alignment: .leading, spacing: 5) {
                            HStack {
                                Text(mode.emoji).font(.system(size: 22))
                                Text(mode.label).font(.system(size: 15, weight: .heavy, design: .rounded))
                                Spacer()
                                if selected { Image(systemName: "checkmark.circle.fill").foregroundStyle(Theme.roseDeep) }
                            }
                            Text(mode.blurb)
                                .font(.system(size: 12, weight: .medium, design: .rounded))
                                .foregroundStyle(Theme.mauve)
                                .fixedSize(horizontal: false, vertical: true)
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .foregroundStyle(Theme.plum)
                        .padding(14)
                        .frame(maxWidth: .infinity, minHeight: 86, alignment: .topLeading)
                        .background(RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .fill(selected ? Theme.blush.opacity(0.55) : Theme.paper))
                        .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .strokeBorder(selected ? Theme.rose : Theme.blush, lineWidth: selected ? 2 : 1))
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                }
            }
            if store.progress.mode == .topic {
                HStack(spacing: 8) {
                    Text("Topic:")
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.plum)
                    Menu {
                        ForEach(store.categories, id: \.self) { cat in
                            Button("\(Problem.categoryEmoji[cat] ?? "") \(cat)  (\(store.solvedCount(in: cat))/\(store.problems(in: cat).count))") {
                                store.progress.topic = cat
                            }
                        }
                    } label: {
                        Text("\(Problem.categoryEmoji[store.progress.topic] ?? "") \(store.progress.topic)")
                            .font(.system(size: 13, weight: .semibold, design: .rounded))
                    }
                    .menuStyle(.borderlessButton)
                    .fixedSize()
                    .padding(.horizontal, 12).padding(.vertical, 6)
                    .background(Capsule().fill(Theme.paper))
                    .overlay(Capsule().strokeBorder(Theme.blush))
                }
                .transition(.opacity.combined(with: .move(edge: .top)))
            }
        }
    }
}

// MARK: - Next problem

private struct NextProblemCard: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            SectionTitle(title: "Today's problem", emoji: "💌")
            if let problem = store.nextProblem {
                let solved = store.progress.isSolved(problem.id)
                HStack(alignment: .center, spacing: 18) {
                    Text(problem.categoryEmoji)
                        .font(.system(size: 40))
                        .frame(width: 72, height: 72)
                        .background(Circle().fill(Theme.lilac))
                    VStack(alignment: .leading, spacing: 7) {
                        Text(problem.title)
                            .font(.system(size: 22, weight: .heavy, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        HStack(spacing: 6) {
                            DifficultyPill(difficulty: problem.difficulty)
                            Pill(text: problem.category, color: Color(hex: 0x8C6FE0))
                            if solved { Pill(text: "✓ Solved", color: Theme.mintDeep) }
                        }
                        Text(subtitle(problem))
                            .font(.system(size: 12.5, weight: .medium, design: .rounded))
                            .foregroundStyle(Theme.mauve)
                    }
                    Spacer()
                    VStack(alignment: .trailing, spacing: 8) {
                        Button(solved ? "Practice again" : "Start solving ✨") { store.open(problem) }
                            .buttonStyle(.cozy(.primary))
                            .keyboardShortcut(.return, modifiers: [.command])
                        if store.progress.mode == .random {
                            Button("🔀 Shuffle") {
                                withAnimation { store.shuffleRandomPick() }
                            }
                            .buttonStyle(.cozy(.secondary, compact: true))
                        }
                    }
                }
            } else {
                HStack(spacing: 14) {
                    Text("🏆").font(.system(size: 40))
                    VStack(alignment: .leading, spacing: 4) {
                        Text(store.progress.mode == .topic ? "You finished \(store.progress.topic)!" : "You solved every problem!")
                            .font(.system(size: 20, weight: .heavy, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        Text(store.progress.mode == .topic ? "Pick another topic above, or switch to Random for review." : "Switch to Random mode to keep reviewing 💖")
                            .font(.system(size: 13, weight: .medium, design: .rounded))
                            .foregroundStyle(Theme.mauve)
                    }
                }
            }
        }
        .cozyCard()
    }

    private func subtitle(_ p: Problem) -> String {
        switch store.progress.mode {
        case .easyFirst:
            let left = store.problems.filter { $0.difficulty == p.difficulty && !store.progress.isSolved($0.id) }.count
            return "\(left) \(p.difficulty) problem\(left == 1 ? "" : "s") left before leveling up"
        case .topic:
            let done = store.solvedCount(in: p.category), total = store.problems(in: p.category).count
            return "\(done)/\(total) done in \(p.category)"
        case .random:
            return "LeetCode #\(p.lc) · rolled just for you today 🎲"
        }
    }
}

// MARK: - Topic progress

private struct TopicProgressGrid: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                SectionTitle(title: "Your garden of topics", emoji: "🌼")
                Spacer()
                Text("\(store.solvedCount)/\(store.problems.count) · best streak \(store.bestStreak) 🔥")
                    .font(.system(size: 12, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 200), spacing: 12)], spacing: 12) {
                ForEach(store.categories, id: \.self) { cat in
                    let done = store.solvedCount(in: cat), total = store.problems(in: cat).count
                    Button {
                        store.progress.topic = cat
                        store.setMode(.topic)
                    } label: {
                        VStack(alignment: .leading, spacing: 7) {
                            HStack(spacing: 6) {
                                Text(Problem.categoryEmoji[cat] ?? "")
                                Text(cat)
                                    .font(.system(size: 12.5, weight: .bold, design: .rounded))
                                    .lineLimit(1)
                                    .minimumScaleFactor(0.8)
                                Spacer(minLength: 0)
                                Text(done == total ? "🌸" : "\(done)/\(total)")
                                    .font(.system(size: 11.5, weight: .heavy, design: .rounded))
                                    .foregroundStyle(Theme.mauve)
                            }
                            .foregroundStyle(Theme.plum)
                            CozyProgressBar(value: Double(done) / Double(max(1, total)), height: 7,
                                            colors: done == total ? [Theme.mint, Theme.mintDeep] : [Theme.rose, Theme.lavender])
                        }
                        .padding(12)
                        .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(Theme.paper))
                        .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous).strokeBorder(Theme.blush))
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                    .help("Practice \(cat) in order")
                }
            }
        }
    }
}

enum Encouragement {
    static let lines = [
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
    ]

    static func line(for date: Date) -> String {
        let day = Calendar.current.ordinality(of: .day, in: .era, for: date) ?? 0
        return lines[day % lines.count]
    }
}
