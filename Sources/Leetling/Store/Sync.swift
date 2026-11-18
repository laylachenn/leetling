import AppKit
import Foundation
import LeetlingShared
import Observation

// Sync progress across devices through a private GitHub Gist. This is a port of web/js/sync.js
// and the sync part of web/js/store.js; keep the merge rules identical.
//
// Each device remembers the "base": the copy it last agreed on with the gist. Syncing is a
// three-way merge of base, this device and the gist, so progress made on several devices adds up:
// - counters (unopened packs, Leetling copies, attempts, packs opened, times accepted):
//   gist + (this device − base), so packs opened or Leetlings evolved on one device stay spent
// - sets (dex caught, bonus days, milestones, topics, peeks) and the day log: union
// - hints revealed: the higher count; first/last solve dates: earliest/latest
// - settings, buddy and drafts: whichever side changed since the base (this device on a tie)

enum SyncMerge {
    /// `base` is nil on the first sync of a device that has its own progress: add both up.
    static func merge(base: Progress?, local: Progress, remote: Progress) -> Progress {
        let b = base ?? Progress()
        var out = local
        func counter(_ b: Int?, _ l: Int?, _ r: Int?) -> Int { max(0, (r ?? 0) + (l ?? 0) - (b ?? 0)) }
        // With no base (combining two copies), this device's settings and drafts win.
        func pick<T: Equatable>(_ b: T, _ l: T, _ r: T) -> T { base != nil && l == b ? r : l }
        // ...but an empty one on this device is filled in from the other copy.
        func pick<T: Equatable>(_ b: T?, _ l: T?, _ r: T?) -> T? { base == nil ? l ?? r : l == b ? r : l }
        func keys<V>(_ x: [String: V], _ y: [String: V]) -> Set<String> { Set(x.keys).union(y.keys) }
        func second(_ d: Date) -> Date { Date(timeIntervalSince1970: floor(d.timeIntervalSince1970)) }

        out.packs = [:]
        for k in keys(local.packs, remote.packs) { out.packs[k] = counter(b.packs[k], local.packs[k], remote.packs[k]) }
        out.attempts = [:]
        for k in keys(local.attempts, remote.attempts) {
            out.attempts[k] = counter(b.attempts[k], local.attempts[k], remote.attempts[k])
        }
        out.packsOpened = counter(b.packsOpened, local.packsOpened, remote.packsOpened)

        out.collection = [:]
        for k in keys(local.collection, remote.collection) {
            let (bo, lo, ro) = (b.collection[k], local.collection[k], remote.collection[k])
            let count = counter(bo?.count, lo?.count, ro?.count)
            out.collection[k] = OwnedLeetling(count: count, shiny: min(count, counter(bo?.shiny, lo?.shiny, ro?.shiny)))
        }

        out.solved = [:]
        for k in keys(local.solved, remote.solved) {
            switch (local.solved[k], remote.solved[k]) {
            case let (l?, r?):
                out.solved[k] = SolveRecord(
                    firstSolved: second(min(l.firstSolved, r.firstSolved)),
                    lastSolved: second(max(l.lastSolved, r.lastSolved)),
                    timesAccepted: max(1, counter(b.solved[k]?.timesAccepted, l.timesAccepted, r.timesAccepted)))
            case let (one?, nil), let (nil, one?):
                out.solved[k] = SolveRecord(firstSolved: second(one.firstSolved), lastSolved: second(one.lastSolved),
                                            timesAccepted: one.timesAccepted)
            case (nil, nil): break
            }
        }

        out.dayLog = [:]
        for k in keys(local.dayLog, remote.dayLog) {
            out.dayLog[k] = Set((local.dayLog[k] ?? []) + (remote.dayLog[k] ?? [])).sorted()
        }

        out.hintsRevealed = [:]
        for k in keys(local.hintsRevealed, remote.hintsRevealed) {
            out.hintsRevealed[k] = max(local.hintsRevealed[k] ?? 0, remote.hintsRevealed[k] ?? 0)
        }

        out.drafts = [:]
        for k in keys(local.drafts, remote.drafts) {
            if let v = pick(b.drafts[k], local.drafts[k], remote.drafts[k]) { out.drafts[k] = v }
        }

        out.solutionPeeked = local.solutionPeeked.union(remote.solutionPeeked)
        out.caught = local.caught.union(remote.caught)
        out.goalBonusDays = local.goalBonusDays.union(remote.goalBonusDays)
        out.milestonesClaimed = local.milestonesClaimed.union(remote.milestonesClaimed)
        out.topicsCompleted = local.topicsCompleted.union(remote.topicsCompleted)

        out.buddy = pick(b.buddy, local.buddy, remote.buddy)
        out.mode = pick(b.mode, local.mode, remote.mode)
        out.topic = pick(b.topic, local.topic, remote.topic)
        out.dailyGoal = pick(b.dailyGoal, local.dailyGoal, remote.dailyGoal)
        out.randomPick = pick(b.randomPick, local.randomPick, remote.randomPick)
        out.randomPickDay = pick(b.randomPickDay, local.randomPickDay, remote.randomPickDay)
        out.showDesktopBuddy = pick(b.showDesktopBuddy, local.showDesktopBuddy, remote.showDesktopBuddy)
        out.name = pick(b.name, local.name, remote.name)
        if let buddy = out.buddy, !out.caught.contains(buddy) { out.buddy = local.buddy ?? remote.buddy }
        return out
    }

    /// "Fresh" = nothing worth keeping yet, so the first sync can just adopt the gist's copy.
    static func isFresh(_ p: Progress) -> Bool { p.solved.isEmpty && p.packsOpened == 0 && p.dayLog.isEmpty }
}

// MARK: - GitHub Gist API

struct SyncError: LocalizedError {
    let message: String
    var auth = false
    var errorDescription: String? { message }
}

enum GistAPI {
    static let fileName = "leetling-progress.json"
    static let gistDescription = "Leetling progress 🐰 (synced by the Leetling app, please don't edit by hand)"

    static func encode(_ p: Progress) throws -> String {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return String(decoding: try encoder.encode(p), as: UTF8.self)
    }

    static func decode(_ text: String) throws -> Progress {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        guard let p = try? decoder.decode(Progress.self, from: Data(text.utf8)) else {
            throw SyncError(message: "The synced copy on GitHub looks scrambled, so I left it alone 🧶")
        }
        return p
    }

    /// Returns the decoded JSON, or nil for a missing gist.
    private static func call(_ token: String, _ path: String, method: String = "GET", body: Any? = nil) async throws -> Any? {
        var req = URLRequest(url: URL(string: "https://api.github.com" + path)!)
        req.httpMethod = method
        req.cachePolicy = .reloadIgnoringLocalCacheData
        req.timeoutInterval = 20
        req.setValue("application/vnd.github+json", forHTTPHeaderField: "Accept")
        req.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        req.setValue("2022-11-28", forHTTPHeaderField: "X-GitHub-Api-Version")
        if let body {
            req.httpBody = try JSONSerialization.data(withJSONObject: body)
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        }
        let data: Data, response: URLResponse
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw SyncError(message: "Couldn't reach GitHub. Are you online? I'll try again later 🌙")
        }
        let status = (response as? HTTPURLResponse)?.statusCode ?? 0
        if status == 401 { throw SyncError(message: "GitHub didn't accept that token. It may have expired 🔑", auth: true) }
        if status == 404 && path.hasPrefix("/gists/") { return nil }
        if status == 403 || status == 404 {
            throw SyncError(message: "That token can't use gists. Make sure the “gist” box is ticked 🔑", auth: true)
        }
        guard (200..<300).contains(status) else {
            throw SyncError(message: "GitHub had a hiccup (\(status)). I'll try again later 🌙")
        }
        return data.isEmpty ? [:] : try JSONSerialization.jsonObject(with: data)
    }

    static func find(_ token: String) async throws -> String? {
        for page in 1...10 {
            let list = try await call(token, "/gists?per_page=100&page=\(page)") as? [[String: Any]] ?? []
            if let hit = list.first(where: { ($0["files"] as? [String: Any])?[fileName] != nil }) { return hit["id"] as? String }
            if list.count < 100 { return nil }
        }
        return nil
    }

    static func read(_ token: String, _ id: String) async throws -> Progress? {
        let stamp = Int(Date().timeIntervalSince1970 * 1000)
        guard let gist = try await call(token, "/gists/\(id)?t=\(stamp)") as? [String: Any],
              let file = (gist["files"] as? [String: Any])?[fileName] as? [String: Any] else { return nil }
        var text = file["content"] as? String ?? ""
        if file["truncated"] as? Bool == true, let raw = (file["raw_url"] as? String).flatMap(URL.init(string:)) {
            let (data, _) = try await URLSession.shared.data(for: URLRequest(url: raw, cachePolicy: .reloadIgnoringLocalCacheData))
            text = String(decoding: data, as: UTF8.self)
        }
        return try decode(text)
    }

    static func create(_ token: String, _ p: Progress) async throws -> String {
        let body: [String: Any] = ["description": gistDescription, "public": false,
                                   "files": [fileName: ["content": try encode(p)]]]
        guard let gist = try await call(token, "/gists", method: "POST", body: body) as? [String: Any],
              let id = gist["id"] as? String else { throw SyncError(message: "GitHub didn't make the gist. Try again? 🌱") }
        return id
    }

    static func write(_ token: String, _ id: String, _ p: Progress) async throws {
        let body: [String: Any] = ["files": [fileName: ["content": try encode(p)]]]
        if try await call(token, "/gists/\(id)", method: "PATCH", body: body) == nil {
            throw SyncError(message: "The synced gist disappeared. Click Sync now to make a new one 🌱")
        }
    }
}

// MARK: - Sync service

/// Saved as sync.json next to progress.json (owner-only permissions, since it holds the token).
struct SyncConfig: Codable {
    var token: String
    var gistID: String?
    var base: Progress?
}

@MainActor
@Observable
final class SyncService {
    enum State: Equatable { case off, idle, syncing, error(String) }
    enum Choice { case combine, remote }

    private(set) var state: State = .off
    private(set) var lastSynced: Date?
    private(set) var config: SyncConfig?
    /// Set while asking "combine or use the synced copy?" (shown by LeetlingApp as an alert).
    var isChoosing = false

    @ObservationIgnored weak var store: AppStore?
    @ObservationIgnored private var choiceContinuation: CheckedContinuation<Choice, Never>?
    @ObservationIgnored private var running: Task<Bool, Never>?
    @ObservationIgnored private var queued: Task<Bool, Never>?
    @ObservationIgnored private var queuedOverwrite = false
    @ObservationIgnored private var scheduled: Task<Void, Never>?
    @ObservationIgnored private var poller: Timer?

    private static var configURL: URL { LeetlingSnapshot.supportDirectory.appendingPathComponent("sync.json") }

    init() {
        if let data = try? Data(contentsOf: Self.configURL) {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            if let cfg = try? decoder.decode(SyncConfig.self, from: data), !cfg.token.isEmpty {
                config = cfg
                state = .idle
            }
        }
    }

    var isConnected: Bool { config != nil }

    var statusLine: String {
        switch state {
        case .off: return "Not connected"
        case .syncing: return "Syncing… 🔄"
        case .error(let message): return message
        case .idle:
            guard let lastSynced else { return "Connected ✨" }
            let f = RelativeDateTimeFormatter()
            f.unitsStyle = .full
            let seconds = Date().timeIntervalSince(lastSynced)
            return "Synced ✨ " + (seconds < 45 ? "just now" : f.localizedString(for: lastSynced, relativeTo: Date()))
        }
    }

    private func saveConfig() {
        let url = Self.configURL
        guard let config else {
            try? FileManager.default.removeItem(at: url)
            return
        }
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        guard let data = try? encoder.encode(config) else { return }
        try? FileManager.default.createDirectory(at: LeetlingSnapshot.supportDirectory, withIntermediateDirectories: true)
        try? data.write(to: url, options: .atomic)
        try? FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: url.path)
    }

    /// Changes since the last sync that the gist doesn't have yet.
    var isDirty: Bool {
        guard let store, let config else { return false }
        return config.base != store.progress
    }

    /// Start syncing when the app opens, comes to the front, and every 10 minutes.
    func start() {
        NotificationCenter.default.addObserver(forName: NSApplication.didBecomeActiveNotification, object: nil, queue: .main) { _ in
            MainActor.assumeIsolated { self.request() }
        }
        poller = Timer.scheduledTimer(withTimeInterval: 600, repeats: true) { _ in
            MainActor.assumeIsolated { self.request() }
        }
        request()
    }

    /// Called after every save: push a few seconds later if anything changed.
    func scheduleIfDirty(after seconds: Double = 3) {
        guard isConnected else { return }
        scheduled?.cancel()
        scheduled = Task { [weak self] in
            try? await Task.sleep(nanoseconds: UInt64(seconds * 1_000_000_000))
            guard !Task.isCancelled, let self, self.isDirty else { return }
            await self.syncNow()
        }
    }

    func request(overwrite: Bool = false) {
        guard isConnected else { return }
        Task { await self.syncNow(overwrite: overwrite) }
    }

    func connect(token: String) async -> Bool {
        config = SyncConfig(token: token.trimmingCharacters(in: .whitespacesAndNewlines), gistID: nil, base: nil)
        saveConfig()
        let ok = await syncNow()
        if !ok, case .error = state, lastAuthFailed {
            config = nil
            saveConfig()
        }
        return ok
    }

    func disconnect() {
        scheduled?.cancel()
        config = nil
        saveConfig()
        state = .off
        lastSynced = nil
    }

    func resolveChoice(_ choice: Choice) {
        isChoosing = false
        choiceContinuation?.resume(returning: choice)
        choiceContinuation = nil
    }

    private func askChoice() async -> Choice {
        await withCheckedContinuation { c in
            choiceContinuation = c
            isChoosing = true
            NSApp.activate(ignoringOtherApps: true)
        }
    }

    @ObservationIgnored private var lastAuthFailed = false

    /// Pull the gist, merge it with this Mac, and push the result. `overwrite` replaces the gist with
    /// this Mac's progress (after an import or a reset). Syncs run one at a time; extra requests join the next one.
    @discardableResult
    func syncNow(overwrite: Bool = false) async -> Bool {
        guard isConnected else { return false }
        if let queued {
            queuedOverwrite = queuedOverwrite || overwrite
            return await queued.value
        }
        let previous = running
        queuedOverwrite = overwrite
        let task = Task { @MainActor [weak self] () -> Bool in
            _ = await previous?.value
            guard let self else { return false }
            self.queued = nil
            let ow = self.queuedOverwrite
            self.queuedOverwrite = false
            return await self.run(overwrite: ow)
        }
        queued = task
        running = task
        return await task.value
    }

    private func run(overwrite: Bool) async -> Bool {
        guard var cfg = config, let store else { return false }
        scheduled?.cancel()
        state = .syncing
        do {
            if cfg.gistID == nil { cfg.gistID = try await GistAPI.find(cfg.token) }
            let remote: Progress? = if let id = cfg.gistID { try await GistAPI.read(cfg.token, id) } else { nil }
            if let remote, let id = cfg.gistID {
                var merged: Progress
                if overwrite {
                    merged = store.progress
                } else if let base = cfg.base {
                    merged = SyncMerge.merge(base: base, local: store.progress, remote: remote)
                } else if SyncMerge.isFresh(store.progress) {
                    merged = remote
                } else {
                    let choice = await askChoice()
                    merged = choice == .remote ? remote : SyncMerge.merge(base: nil, local: store.progress, remote: remote)
                }
                // Round-trip through JSON so dates match what the gist holds (whole seconds).
                merged = try GistAPI.decode(GistAPI.encode(merged))
                // This Mac now holds everything in `remote`, so it's the right base even if the push fails.
                cfg.base = remote
                if merged != store.progress { store.applySynced(merged) }
                if merged != remote { try await GistAPI.write(cfg.token, id, merged) }
                cfg.base = merged
            } else {
                let snapshot = try GistAPI.decode(GistAPI.encode(store.progress))
                cfg.gistID = try await GistAPI.create(cfg.token, snapshot)
                cfg.base = snapshot
            }
            guard config != nil else { return false } // disconnected meanwhile
            config = cfg
            saveConfig()
            lastAuthFailed = false
            state = .idle
            lastSynced = Date()
            return true
        } catch {
            if config != nil {
                config = cfg
                saveConfig()
            }
            lastAuthFailed = (error as? SyncError)?.auth ?? false
            state = .error((error as? SyncError)?.message ?? "Sync didn't work this time 🌙")
            return false
        }
    }
}
