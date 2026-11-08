import Foundation

/// Runs the user's Python code locally with Resources/runner.py.
enum CodeRunner {
    enum Mode: String { case run, submit }

    /// First working python3 we can find. GUI apps don't inherit the shell PATH, so check common spots.
    static let pythonPath: String? = {
        let candidates = [
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3",
            "/Library/Frameworks/Python.framework/Versions/Current/bin/python3",
            "/usr/bin/python3",
        ]
        return candidates.first { FileManager.default.isExecutableFile(atPath: $0) }
    }()

    static func pythonVersion() async -> String? {
        guard let python = pythonPath else { return nil }
        return try? await Task.detached {
            let p = Process()
            p.executableURL = URL(fileURLWithPath: python)
            p.arguments = ["--version"]
            let pipe = Pipe()
            p.standardOutput = pipe
            p.standardError = pipe
            try p.run()
            p.waitUntilExit()
            let out = String(data: pipe.fileHandleForReading.readDataToEndOfFile(), encoding: .utf8) ?? ""
            return out.trimmingCharacters(in: .whitespacesAndNewlines)
        }.value
    }

    static func run(problemID: Int, code: String, mode: Mode) async -> RunResult {
        guard let python = pythonPath else {
            return .setupError("I couldn't find Python 3 on this Mac. Install it from python.org or with `brew install python`, then try again. 🐍")
        }
        guard let runner = ResourceLocator.url(for: "runner.py"),
              let problems = ResourceLocator.url(for: "problems.json") else {
            return .setupError("The test runner files are missing from the app bundle. Try rebuilding with scripts/build.sh.")
        }

        return await Task.detached(priority: .userInitiated) { () -> RunResult in
            let dir = FileManager.default.temporaryDirectory
                .appendingPathComponent("leetling-\(UUID().uuidString)", isDirectory: true)
            defer { try? FileManager.default.removeItem(at: dir) }
            do {
                try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
                let solution = dir.appendingPathComponent("solution.py")
                let output = dir.appendingPathComponent("result.json")
                try code.write(to: solution, atomically: true, encoding: .utf8)

                let process = Process()
                process.executableURL = URL(fileURLWithPath: python)
                process.arguments = ["-I", runner.path, problems.path, String(problemID), solution.path, mode.rawValue, output.path]
                process.currentDirectoryURL = dir
                let errPipe = Pipe()
                process.standardOutput = FileHandle.nullDevice
                process.standardError = errPipe
                try process.run()

                // Hard stop in case something hangs outside the per-test timer.
                let killer = DispatchWorkItem { if process.isRunning { process.terminate() } }
                DispatchQueue.global().asyncAfter(deadline: .now() + 45, execute: killer)
                let errData = errPipe.fileHandleForReading.readDataToEndOfFile()
                process.waitUntilExit()
                killer.cancel()

                if let data = try? Data(contentsOf: output),
                   let result = try? JSONDecoder().decode(RunResult.self, from: data) {
                    return result
                }
                if process.terminationReason == .uncaughtSignal {
                    return RunResult(status: "time_limit", passed: 0, total: 0, results: [],
                                     message: "Your code ran for too long and was stopped. Is there an infinite loop? 🐢", runtime_ms: nil)
                }
                let err = String(data: errData, encoding: .utf8) ?? ""
                return .setupError("The runner crashed unexpectedly.\n\(err.suffix(1500))")
            } catch {
                return .setupError("Couldn't start Python: \(error.localizedDescription)")
            }
        }.value
    }
}
