import AppKit
import LeetlingShared
import SwiftUI
import UniformTypeIdentifiers

struct SettingsView: View {
    @Environment(AppStore.self) private var store
    @Local private var pythonVersion: String? = nil
    @Local private var confirmReset = false
    @Local private var confirmDisconnect = false
    @Local private var confirmImport: URL? = nil
    @Local private var token = ""
    @Local private var connecting = false
    @Local private var dataNote: String? = nil

    var body: some View {
        @Bindable var store = store
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Settings ⚙️")
                    .font(.system(size: 28, weight: .heavy, design: .rounded))
                    .foregroundStyle(Theme.plum)

                card(title: "You", emoji: "🎀") {
                    row("What should I call you?") {
                        TextField(store.displayName, text: Binding(
                            get: { store.progress.name ?? "" },
                            set: { store.progress.name = $0 }))
                            .textFieldStyle(.roundedBorder)
                            .frame(width: 200)
                    }
                    row("Daily goal (problems per day)") {
                        Picker("", selection: Binding(get: { store.progress.dailyGoal }, set: { store.setGoal($0) })) {
                            ForEach(1...4, id: \.self) { Text("\($0)").tag($0) }
                        }
                        .pickerStyle(.segmented)
                        .frame(width: 200)
                    }
                    Text("Hitting your goal earns a Bloom Pack 🌷 each day. Your streak only needs 1 problem a day.")
                        .font(.system(size: 12, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }

                card(title: "Desktop widget", emoji: "🗓️") {
                    Text("**Real macOS widget:** right-click your desktop → **Edit Widgets…** → search **Leetling** → drag the small or medium streak widget onto your desktop.")
                        .font(.system(size: 13, design: .rounded))
                        .foregroundStyle(Theme.plum)
                        .fixedSize(horizontal: false, vertical: true)
                    row("Floating desktop buddy (backup option)") {
                        Toggle("", isOn: Binding(
                            get: { store.progress.showDesktopBuddy },
                            set: { on in
                                store.progress.showDesktopBuddy = on
                                DesktopBuddy.shared.setVisible(on)
                            }))
                        .toggleStyle(.switch)
                    }
                    Text("Pins the streak card to your desktop, behind your windows. Drag it wherever you like. Leetling stays running while it's on.")
                        .font(.system(size: 12, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }

                syncCard

                card(title: "Python", emoji: "🐍") {
                    if let path = CodeRunner.pythonPath {
                        Text("Running your code with **\(pythonVersion ?? "Python 3")** at `\(path)`")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.plum)
                    } else {
                        Text("Python 3 wasn't found. Install it from python.org or with `brew install python`.")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.berry)
                    }
                    Text("Your code runs locally on your Mac — nothing is sent anywhere. Each test gets 4 seconds.")
                        .font(.system(size: 12, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }

                card(title: "Your data", emoji: "💾") {
                    HStack {
                        Text("Progress is saved in Application Support/Leetling.")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        Spacer()
                        Button("Show in Finder") {
                            NSWorkspace.shared.activateFileViewerSelecting([LeetlingSnapshot.supportDirectory.appendingPathComponent("progress.json")])
                        }
                        .buttonStyle(.cozy(.secondary, compact: true))
                    }
                    HStack {
                        Text("Back up your progress, or move it by hand. Same format as the web app's export.")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        Spacer()
                        Button("⬇︎ Export…") { exportData() }
                            .buttonStyle(.cozy(.secondary, compact: true))
                        Button("⬆︎ Import…") { pickImport() }
                            .buttonStyle(.cozy(.secondary, compact: true))
                    }
                    if let dataNote {
                        Text(dataNote)
                            .font(.system(size: 12.5, weight: .semibold, design: .rounded))
                            .foregroundStyle(Theme.plum)
                    }
                    HStack {
                        Text("Start completely fresh (solves, streak, packs and Leetlings).")
                            .font(.system(size: 13, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        Spacer()
                        Button("Reset everything…") { confirmReset = true }
                            .buttonStyle(.cozy(.quiet, compact: true))
                    }
                }
            }
            .padding(28)
            .frame(maxWidth: 760)
            .frame(maxWidth: .infinity)
        }
        .task { pythonVersion = await CodeRunner.pythonVersion() }
        .alert("Reset all progress?", isPresented: $confirmReset) {
            Button("Reset everything", role: .destructive) { store.resetAllProgress() }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text(store.sync.isConnected
                 ? "This erases your solves, streak history, packs and Leetdex here and on every synced device. It can't be undone."
                 : "This erases your solves, streak history, packs and Leetdex. It can't be undone.")
        }
        .alert("Import this progress?", isPresented: Binding(get: { confirmImport != nil }, set: { if !$0 { confirmImport = nil } })) {
            Button("Import") {
                if let url = confirmImport { importData(url) }
                confirmImport = nil
            }
            Button("Cancel", role: .cancel) { confirmImport = nil }
        } message: {
            Text("It replaces the progress on this Mac (solves, streak, packs and Leetlings) with the file's."
                 + (store.sync.isConnected ? " Your synced devices will get it too." : ""))
        }
        .alert("Stop syncing this Mac?", isPresented: $confirmDisconnect) {
            Button("Stop syncing") { store.sync.disconnect() }
            Button("Keep syncing", role: .cancel) {}
        } message: {
            Text("Your progress stays on this Mac and in your gist. It just won't stay in step anymore.")
        }
    }

    // MARK: sync

    @ViewBuilder private var syncCard: some View {
        let sync = store.sync
        card(title: "Sync your devices", emoji: "☁️") {
            if sync.isConnected {
                Text(sync.statusLine)
                    .font(.system(size: 13.5, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.plum)
                Text("Leetling syncs when it opens, when you come back to it, and a few seconds after you make progress.")
                    .font(.system(size: 12, design: .rounded))
                    .foregroundStyle(Theme.mauve)
                HStack {
                    Button("🔄 Sync now") { sync.request() }
                        .buttonStyle(.cozy(.secondary, compact: true))
                        .disabled(sync.state == .syncing)
                    Button("Disconnect") { confirmDisconnect = true }
                        .buttonStyle(.cozy(.quiet, compact: true))
                }
            } else {
                Text("Keep your Mac, iPhone and browser in step. Your progress is saved to a **private gist** on your GitHub account, and solves from every device add up.")
                    .font(.system(size: 13, design: .rounded))
                    .foregroundStyle(Theme.plum)
                    .fixedSize(horizontal: false, vertical: true)
                VStack(alignment: .leading, spacing: 4) {
                    Text("1. [Make a GitHub token](https://github.com/settings/tokens/new?scopes=gist&description=Leetling%20sync) with only the **gist** box ticked. Pick “No expiration” so it keeps working.")
                    Text("2. Paste it here, then do the same in the web app (Settings → Sync your devices).")
                }
                .font(.system(size: 13, design: .rounded))
                .foregroundStyle(Theme.plum)
                .tint(Theme.rose)
                HStack {
                    SecureField("ghp_…", text: $token)
                        .textFieldStyle(.roundedBorder)
                        .onSubmit(connect)
                    Button(connecting ? "Connecting…" : "Connect", action: connect)
                        .buttonStyle(.cozy(.primary, compact: true))
                        .disabled(connecting || token.trimmingCharacters(in: .whitespaces).isEmpty)
                }
                if case .error(let message) = sync.state {
                    Text(message)
                        .font(.system(size: 12.5, weight: .semibold, design: .rounded))
                        .foregroundStyle(Theme.berry)
                }
                Text("The token stays on this Mac and is only ever sent to GitHub.")
                    .font(.system(size: 12, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
        }
    }

    private func connect() {
        let t = token.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !t.isEmpty, !connecting else { return }
        connecting = true
        Task {
            if await store.sync.connect(token: t) { token = "" }
            connecting = false
        }
    }

    // MARK: export / import

    private func exportData() {
        let panel = NSSavePanel()
        panel.allowedContentTypes = [.json]
        let day = DayKey.key()
        panel.nameFieldStringValue = "leetling-progress-\(day).json"
        guard panel.runModal() == .OK, let url = panel.url else { return }
        do {
            try store.exportProgress(to: url)
            dataNote = "Saved! 💾"
        } catch {
            dataNote = "Hmm, that didn't save: \(error.localizedDescription)"
        }
    }

    private func pickImport() {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.json]
        panel.allowsMultipleSelection = false
        guard panel.runModal() == .OK, let url = panel.url else { return }
        confirmImport = url
    }

    private func importData(_ url: URL) {
        do {
            try store.importProgress(from: url)
            dataNote = "Imported! Welcome back 💖"
        } catch {
            dataNote = "Hmm, that didn't work: \(error.localizedDescription)"
        }
    }

    private func card<Content: View>(title: String, emoji: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            SectionTitle(title: title, emoji: emoji)
            content()
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .cozyCard()
    }

    private func row<Control: View>(_ label: String, @ViewBuilder control: () -> Control) -> some View {
        HStack {
            Text(label)
                .font(.system(size: 13.5, weight: .semibold, design: .rounded))
                .foregroundStyle(Theme.plum)
            Spacer()
            control()
        }
    }
}
