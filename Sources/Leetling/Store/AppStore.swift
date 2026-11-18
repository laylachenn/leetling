import Foundation
import LeetlingShared
import Observation
import SwiftUI
import WidgetKit

enum Section: String, CaseIterable, Identifiable, Hashable {
    case today, problems, packs, dex, settings
    var id: String { rawValue }

    var title: String {
        switch self {
        case .today: return "Today"
        case .problems: return "Problems"
        case .packs: return "Packs"
        case .dex: return "Leetdex"
        case .settings: return "Settings"
        }
    }

    var icon: String {
        switch self {
        case .today: return "sun.max.fill"
        case .problems: return "list.bullet.rectangle.portrait.fill"
        case .packs: return "gift.fill"
        case .dex: return "book.closed.fill"
        case .settings: return "gearshape.fill"
        }
    }
}

struct Reward: Identifiable, Hashable {
    let id = UUID()
    let pack: PackKind
    let reason: String
}

struct Celebration: Identifiable {
    let id = UUID()
    let problemTitle: String
    let firstSolve: Bool
    let rewards: [Reward]
    let streak: Int
    let todayCount: Int
    let goal: Int
}

@MainActor
@Observable
final class AppStore {
    let problems: [Problem]
    private let byID: [Int: Problem]

    var progress: Progress {
        didSet { scheduleSave() }
    }

    // Navigation / transient UI state
    var section: Section = .today
    var openProblemID: Int? = nil
    var celebration: Celebration? = nil

    /// GitHub Gist sync across devices (see Sync.swift).
    let sync = SyncService()
    /// Shows/hides the desktop buddy when a sync or import flips that setting (wired up by AppDelegate).
    var onDesktopBuddyChange: ((Bool) -> Void)?

    static let streakMilestones = [3, 7, 14, 21, 30, 45, 60, 75, 100, 150, 200, 365]

    private static var progressURL: URL {
        LeetlingSnapshot.supportDirectory.appendingPathComponent("progress.json")
    }

    private var saveTask: Task<Void, Never>?

    init() {
        problems = Problem.loadAll()
        byID = Dictionary(uniqueKeysWithValues: problems.map { ($0.id, $0) })
        if let data = try? Data(contentsOf: Self.progressURL) {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            progress = (try? decoder.decode(Progress.self, from: data)) ?? Progress()
        } else {
            progress = Progress()
            // A little welcome gift so there's something to open on day one.
            progress.packs[PackKind.sprout.rawValue] = 1
        }
        writeSnapshot()
        sync.store = self
    }

    // MARK: persistence

    private func scheduleSave() {
        saveTask?.cancel()
        saveTask = Task { [weak self] in
            try? await Task.sleep(nanoseconds: 400_000_000)
            guard !Task.isCancelled else { return }
            self?.saveNow()
        }
    }

    func saveNow() {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        guard let data = try? encoder.encode(progress) else { return }
        try? FileManager.default.createDirectory(at: LeetlingSnapshot.supportDirectory, withIntermediateDirectories: true)
        try? data.write(to: Self.progressURL, options: .atomic)
        writeSnapshot()
        sync.scheduleIfDirty()
    }

    /// Replace progress with the merged copy from a sync.
    func applySynced(_ merged: Progress) {
        let buddyWas = progress.showDesktopBuddy
        progress = merged
        saveNow()
        if merged.showDesktopBuddy != buddyWas { onDesktopBuddyChange?(merged.showDesktopBuddy) }
    }

    func exportProgress(to url: URL) throws {
        try Data(GistAPI.encode(progress).utf8).write(to: url, options: .atomic)
    }

    /// Replace this Mac's progress with a file exported from here or from the web app.
    func importProgress(from url: URL) throws {
        let text = try String(contentsOf: url, encoding: .utf8)
        guard let raw = try? JSONSerialization.jsonObject(with: Data(text.utf8)) as? [String: Any],
              raw["solved"] != nil || raw["dayLog"] != nil || raw["collection"] != nil else {
            throw SyncError(message: "That file doesn't look like Leetling progress.")
        }
        let imported = try GistAPI.decode(text)
        let buddyWas = progress.showDesktopBuddy
        progress = imported
        saveNow()
        if imported.showDesktopBuddy != buddyWas { onDesktopBuddyChange?(imported.showDesktopBuddy) }
        sync.request(overwrite: true)
    }

    var snapshot: LeetlingSnapshot {
        LeetlingSnapshot(
            dayCounts: progress.dayLog.mapValues(\.count),
            goal: progress.dailyGoal,
            solvedTotal: solvedCount,
            totalProblems: problems.count,
            packsWaiting: progress.totalPacks,
            nextProblemTitle: nextProblem?.title,
            buddyEmoji: buddy?.emoji ?? "🥚",
            updated: Date())
    }

    private var lastSnapshot: LeetlingSnapshot?

    private func writeSnapshot() {
        var snap = snapshot
        // Avoid needless widget reloads when only drafts changed.
        snap.updated = lastSnapshot?.updated ?? snap.updated
        guard snap != lastSnapshot else { return }
        snap.updated = Date()
        snap.save()
        lastSnapshot = snap
        WidgetCenter.shared.reloadAllTimelines()
    }

    // MARK: problem queries

    func problem(_ id: Int) -> Problem? { byID[id] }

    var solvedCount: Int { problems.filter { progress.isSolved($0.id) }.count }

    var categories: [String] { Problem.categoryOrder.filter { c in problems.contains { $0.category == c } } }

    func problems(in category: String) -> [Problem] { problems.filter { $0.category == category } }

    func solvedCount(in category: String) -> Int { problems(in: category).filter { progress.isSolved($0.id) }.count }

    var easyFirstOrder: [Problem] {
        problems.sorted { ($0.difficultyRank, $0.id) < ($1.difficultyRank, $1.id) }
    }

    /// The suggested problem for the current practice mode.
    var nextProblem: Problem? {
        let unsolved = { (p: Problem) in !self.progress.isSolved(p.id) }
        switch progress.mode {
        case .easyFirst:
            return easyFirstOrder.first(where: unsolved)
        case .topic:
            return problems(in: progress.topic).first(where: unsolved)
        case .random:
            // Deterministic so redraws don't reshuffle; ensureRandomPick() rolls a new one each day.
            if let id = progress.randomPick, let p = problem(id) { return p }
            return problems.first(where: unsolved) ?? problems.first
        }
    }

    /// Roll a fresh random pick once per day (the pick stays put while you work on it).
    func ensureRandomPick() {
        guard progress.mode == .random else { return }
        if progress.randomPickDay != DayKey.key() || progress.randomPick == nil { shuffleRandomPick() }
    }

    func shuffleRandomPick() {
        let unsolved = problems.filter { !progress.isSolved($0.id) && $0.id != progress.randomPick }
        let pick = unsolved.randomElement() ?? problems.filter { $0.id != progress.randomPick }.randomElement()
        progress.randomPick = pick?.id
        progress.randomPickDay = DayKey.key()
    }

    // MARK: streaks

    var todayCount: Int { progress.dayLog[DayKey.key()]?.count ?? 0 }
    var streak: Int { snapshot.streak() }

    var bestStreak: Int {
        let days = progress.dayLog.filter { !$0.value.isEmpty }.keys.compactMap(DayKey.date).sorted()
        var best = 0, run = 0
        var previous: Date?
        for d in days {
            if let p = previous, Calendar.current.dateComponents([.day], from: p, to: d).day == 1 { run += 1 } else { run = 1 }
            best = max(best, run)
            previous = d
        }
        return best
    }

    var nextMilestone: Int? { Self.streakMilestones.first { $0 > streak } }

    // MARK: editor state

    func draft(for problem: Problem) -> String { progress.drafts[String(problem.id)] ?? problem.starter }

    func setDraft(_ code: String, for problem: Problem) {
        if progress.drafts[String(problem.id)] != code { progress.drafts[String(problem.id)] = code }
    }

    func resetDraft(for problem: Problem) { progress.drafts[String(problem.id)] = problem.starter }

    func hintsRevealed(_ problem: Problem) -> Int { progress.hintsRevealed[String(problem.id)] ?? 0 }

    func revealHint(_ problem: Problem) {
        progress.hintsRevealed[String(problem.id)] = min(3, hintsRevealed(problem) + 1)
    }

    func peekSolution(_ problem: Problem) { progress.solutionPeeked.insert(problem.id) }

    // MARK: submissions & rewards

    func recordAttempt(_ problem: Problem) {
        progress.attempts[String(problem.id), default: 0] += 1
    }

    @discardableResult
    func recordAccepted(_ problem: Problem) -> Celebration {
        let now = Date()
        let today = DayKey.key(now)
        let key = String(problem.id)
        let firstSolve = progress.solved[key] == nil
        var p = progress   // batch all mutations into one save

        if var rec = p.solved[key] {
            rec.lastSolved = now
            rec.timesAccepted += 1
            p.solved[key] = rec
        } else {
            p.solved[key] = SolveRecord(firstSolved: now, lastSolved: now, timesAccepted: 1)
        }
        var todays = p.dayLog[today] ?? []
        if !todays.contains(problem.id) { todays.append(problem.id) }
        p.dayLog[today] = todays

        var rewards: [Reward] = []
        func give(_ kind: PackKind, _ reason: String) {
            p.packs[kind.rawValue, default: 0] += 1
            rewards.append(Reward(pack: kind, reason: reason))
        }

        if firstSolve { give(.sprout, "First time solving \(problem.title)") }

        if todays.count >= p.dailyGoal, !p.goalBonusDays.contains(today) {
            p.goalBonusDays.insert(today)
            give(.bloom, p.dailyGoal == 1 ? "Daily goal reached!" : "Daily goal of \(p.dailyGoal) reached!")
        }

        let snap = LeetlingSnapshot(dayCounts: p.dayLog.mapValues(\.count), goal: p.dailyGoal)
        let streak = snap.streak(now: now)
        let streakStart = DayKey.key(DayKey.daysAgo(max(0, streak - 1), from: now))
        for m in Self.streakMilestones where streak >= m {
            let tag = "\(streakStart):\(m)"
            if !p.milestonesClaimed.contains(tag) {
                p.milestonesClaimed.insert(tag)
                give(.starlight, "\(m)-day streak! 🔥")
            }
        }

        if firstSolve, !p.topicsCompleted.contains(problem.category),
           problems(in: problem.category).allSatisfy({ p.solved[String($0.id)] != nil }) {
            p.topicsCompleted.insert(problem.category)
            give(.starlight, "Finished every \(problem.category) problem!")
        }

        progress = p
        saveNow()
        let celebration = Celebration(problemTitle: problem.title, firstSolve: firstSolve, rewards: rewards,
                                      streak: streak, todayCount: todays.count, goal: p.dailyGoal)
        self.celebration = celebration
        return celebration
    }

    // MARK: packs & collection

    func openPack(_ kind: PackKind) -> [PackPull]? {
        guard progress.packCount(kind) > 0 else { return nil }
        var rng = SystemRandomNumberGenerator()
        let rolled = PackOpener.roll(kind, using: &rng)
        var p = progress
        p.packs[kind.rawValue, default: 0] -= 1
        p.packsOpened += 1
        var pulls: [PackPull] = []
        for (critter, shiny) in rolled {
            let isNew = !p.caught.contains(critter.id)
            p.caught.insert(critter.id)
            var owned = p.collection[critter.id] ?? OwnedLeetling()
            owned.count += 1
            if shiny { owned.shiny += 1 }
            p.collection[critter.id] = owned
            pulls.append(PackPull(leetling: critter, shiny: shiny, isNew: isNew))
        }
        if p.buddy == nil { p.buddy = pulls.max(by: { $0.leetling.rarity < $1.leetling.rarity })?.leetling.id }
        progress = p
        saveNow()
        return pulls
    }

    func owned(_ id: String) -> OwnedLeetling { progress.collection[id] ?? OwnedLeetling() }

    func canEvolve(_ critter: Leetling) -> Bool {
        critter.evolvesTo != nil && owned(critter.id).count >= Dex.copiesToEvolve
    }

    /// Trade 3 copies for one of the next form. Uses non-shiny copies first.
    @discardableResult
    func evolve(_ critter: Leetling) -> Leetling? {
        guard canEvolve(critter), let nextID = critter.evolvesTo, let next = Dex.of(nextID) else { return nil }
        var p = progress
        var from = p.collection[critter.id] ?? OwnedLeetling()
        let normal = from.count - from.shiny
        let shinyUsed = max(0, Dex.copiesToEvolve - normal)
        from.count -= Dex.copiesToEvolve
        from.shiny -= shinyUsed
        p.collection[critter.id] = from
        var to = p.collection[nextID] ?? OwnedLeetling()
        to.count += 1
        if shinyUsed == Dex.copiesToEvolve { to.shiny += 1 }
        p.collection[nextID] = to
        p.caught.insert(nextID)
        if p.buddy == critter.id && from.count == 0 { p.buddy = nextID }
        progress = p
        saveNow()
        return next
    }

    var buddy: Leetling? { progress.buddy.flatMap(Dex.of) }

    func setBuddy(_ critter: Leetling) {
        progress.buddy = critter.id
        saveNow()
    }

    // MARK: settings

    func setMode(_ mode: PracticeMode) {
        progress.mode = mode
        if mode == .random { ensureRandomPick() }
        saveNow()
    }

    func setGoal(_ goal: Int) {
        progress.dailyGoal = max(1, min(5, goal))
        saveNow()
    }

    func resetAllProgress() {
        progress = Progress()
        progress.packs[PackKind.sprout.rawValue] = 1
        saveNow()
        sync.request(overwrite: true)
    }

    var displayName: String {
        if let n = progress.name, !n.isEmpty { return n }
        return NSFullUserName().split(separator: " ").first.map(String.init) ?? "friend"
    }

    func open(_ problem: Problem) {
        openProblemID = problem.id
    }
}
