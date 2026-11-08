import Foundation

enum PracticeMode: String, Codable, CaseIterable, Identifiable {
    case easyFirst, topic, random
    var id: String { rawValue }

    var label: String {
        switch self {
        case .easyFirst: return "Easy First"
        case .topic: return "By Topic"
        case .random: return "Random"
        }
    }

    var emoji: String {
        switch self {
        case .easyFirst: return "🌱"
        case .topic: return "📚"
        case .random: return "🎲"
        }
    }

    var blurb: String {
        switch self {
        case .easyFirst: return "All the Easys first, then Mediums, then Hards."
        case .topic: return "Work through one topic in order, like a mini-course."
        case .random: return "A surprise problem each day. Shuffle if it's not vibing."
        }
    }
}

struct SolveRecord: Codable, Hashable {
    var firstSolved: Date
    var lastSolved: Date
    var timesAccepted: Int
}

struct OwnedLeetling: Codable, Hashable {
    var count: Int = 0
    var shiny: Int = 0   // how many of `count` are shiny
}

/// Everything the app persists, stored as JSON at ~/Library/Application Support/Leetling/progress.json.
/// Every field decodes with a default so older files keep loading as fields get added.
struct Progress: Codable {
    var solved: [String: SolveRecord] = [:]          // problem id → record
    var attempts: [String: Int] = [:]                // problem id → submissions
    var drafts: [String: String] = [:]               // problem id → code in the editor
    var hintsRevealed: [String: Int] = [:]           // problem id → 0…3
    var solutionPeeked: Set<Int> = []
    var dayLog: [String: [Int]] = [:]                // day key → distinct problem ids accepted that day
    var packs: [String: Int] = [:]                   // PackKind.rawValue → unopened count
    var collection: [String: OwnedLeetling] = [:]
    var caught: Set<String> = []                     // every Leetling ever owned (for the dex)
    var buddy: String? = nil
    var goalBonusDays: Set<String> = []
    var milestonesClaimed: Set<String> = []          // "<streak start day>:<milestone>"
    var topicsCompleted: Set<String> = []
    var mode: PracticeMode = .easyFirst
    var topic: String = "Arrays & Hashing"
    var dailyGoal: Int = 1
    var randomPick: Int? = nil
    var randomPickDay: String? = nil
    var showDesktopBuddy: Bool = false
    var packsOpened: Int = 0
    var name: String? = nil

    init() {}

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        func get<T: Decodable>(_ key: CodingKeys, _ fallback: T) -> T {
            (try? c.decodeIfPresent(T.self, forKey: key)) ?? fallback
        }
        let d = Progress()
        solved = get(.solved, d.solved)
        attempts = get(.attempts, d.attempts)
        drafts = get(.drafts, d.drafts)
        hintsRevealed = get(.hintsRevealed, d.hintsRevealed)
        solutionPeeked = get(.solutionPeeked, d.solutionPeeked)
        dayLog = get(.dayLog, d.dayLog)
        packs = get(.packs, d.packs)
        collection = get(.collection, d.collection)
        caught = get(.caught, d.caught)
        buddy = get(.buddy, d.buddy)
        goalBonusDays = get(.goalBonusDays, d.goalBonusDays)
        milestonesClaimed = get(.milestonesClaimed, d.milestonesClaimed)
        topicsCompleted = get(.topicsCompleted, d.topicsCompleted)
        mode = get(.mode, d.mode)
        topic = get(.topic, d.topic)
        dailyGoal = get(.dailyGoal, d.dailyGoal)
        randomPick = get(.randomPick, d.randomPick)
        randomPickDay = get(.randomPickDay, d.randomPickDay)
        showDesktopBuddy = get(.showDesktopBuddy, d.showDesktopBuddy)
        packsOpened = get(.packsOpened, d.packsOpened)
        name = get(.name, d.name)
    }

    func packCount(_ kind: PackKind) -> Int { packs[kind.rawValue] ?? 0 }
    var totalPacks: Int { PackKind.allCases.reduce(0) { $0 + packCount($1) } }
    func isSolved(_ id: Int) -> Bool { solved[String(id)] != nil }
}
