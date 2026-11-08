import Foundation

/// Day keys are local-calendar dates formatted "yyyy-MM-dd".
public enum DayKey {
    private static let formatter: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.calendar = Calendar(identifier: .gregorian)
        f.dateFormat = "yyyy-MM-dd"
        return f
    }()

    public static func key(_ date: Date = Date()) -> String {
        formatter.timeZone = .current
        return formatter.string(from: date)
    }

    public static func date(_ key: String) -> Date? {
        formatter.timeZone = .current
        return formatter.date(from: key)
    }

    public static func daysAgo(_ n: Int, from date: Date = Date()) -> Date {
        Calendar.current.date(byAdding: .day, value: -n, to: Calendar.current.startOfDay(for: date))!
    }
}

/// The small slice of progress the widget (and desktop buddy) needs.
/// The app writes it to ~/Library/Application Support/Leetling/widget.json;
/// the sandboxed widget reads it through a read-only temporary-exception entitlement.
public struct LeetlingSnapshot: Codable, Equatable {
    public var dayCounts: [String: Int]   // day key → problems accepted that day
    public var goal: Int
    public var solvedTotal: Int
    public var totalProblems: Int
    public var packsWaiting: Int
    public var nextProblemTitle: String?
    public var buddyEmoji: String
    public var updated: Date

    public init(dayCounts: [String: Int] = [:], goal: Int = 1, solvedTotal: Int = 0, totalProblems: Int = 75,
                packsWaiting: Int = 0, nextProblemTitle: String? = nil, buddyEmoji: String = "🥚", updated: Date = Date()) {
        self.dayCounts = dayCounts
        self.goal = goal
        self.solvedTotal = solvedTotal
        self.totalProblems = totalProblems
        self.packsWaiting = packsWaiting
        self.nextProblemTitle = nextProblemTitle
        self.buddyEmoji = buddyEmoji
        self.updated = updated
    }

    public static let placeholder = LeetlingSnapshot(
        dayCounts: Dictionary(uniqueKeysWithValues: (1...5).map { (DayKey.key(DayKey.daysAgo($0)), 1) }),
        goal: 1, solvedTotal: 12, packsWaiting: 1, nextProblemTitle: "Two Sum", buddyEmoji: "🐰")

    // MARK: file location

    /// The real home directory, even inside the widget's sandbox container.
    public static var realHome: URL {
        if let pw = getpwuid(getuid()), let dir = pw.pointee.pw_dir {
            return URL(fileURLWithPath: String(cString: dir), isDirectory: true)
        }
        return FileManager.default.homeDirectoryForCurrentUser
    }

    public static var supportDirectory: URL {
        // LEETLING_DATA_DIR lets tests/dev runs use a throwaway folder instead of your real progress.
        if let override = ProcessInfo.processInfo.environment["LEETLING_DATA_DIR"], !override.isEmpty {
            return URL(fileURLWithPath: override, isDirectory: true)
        }
        return realHome.appendingPathComponent("Library/Application Support/Leetling", isDirectory: true)
    }

    public static var fileURL: URL { supportDirectory.appendingPathComponent("widget.json") }

    public static func load() -> LeetlingSnapshot? {
        guard let data = try? Data(contentsOf: fileURL) else { return nil }
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return try? decoder.decode(LeetlingSnapshot.self, from: data)
    }

    public func save() {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        guard let data = try? encoder.encode(self) else { return }
        try? FileManager.default.createDirectory(at: Self.supportDirectory, withIntermediateDirectories: true)
        try? data.write(to: Self.fileURL, options: .atomic)
    }

    // MARK: derived values (computed relative to "now", so a stale file still renders correctly)

    public func count(on date: Date) -> Int { dayCounts[DayKey.key(date)] ?? 0 }

    public func todayCount(now: Date = Date()) -> Int { count(on: now) }

    /// Consecutive days with at least one solve, ending today — or yesterday, if today isn't done yet
    /// (the streak is still alive until midnight).
    public func streak(now: Date = Date()) -> Int {
        var offset = count(on: now) > 0 ? 0 : 1
        var total = 0
        while count(on: DayKey.daysAgo(offset, from: now)) > 0 {
            total += 1
            offset += 1
        }
        return total
    }

    public func week(now: Date = Date()) -> [DayCell] {
        (0..<7).reversed().map { ago in
            let date = DayKey.daysAgo(ago, from: now)
            return DayCell(date: date, count: count(on: date), goal: goal, isToday: ago == 0)
        }
    }
}

public struct DayCell: Identifiable, Hashable {
    public let date: Date
    public let count: Int
    public let goal: Int
    public let isToday: Bool

    public var id: Date { date }
    public var done: Bool { count > 0 }
    public var goalMet: Bool { count >= goal }

    public var dayNumber: String { String(Calendar.current.component(.day, from: date)) }

    public var weekdayShort: String {
        let f = DateFormatter()
        f.dateFormat = "EE"
        return String(f.string(from: date).prefix(2))
    }
}
