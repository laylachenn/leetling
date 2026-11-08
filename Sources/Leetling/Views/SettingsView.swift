import AppKit
import LeetlingShared
import SwiftUI

struct SettingsView: View {
    @Environment(AppStore.self) private var store
    @Local private var pythonVersion: String? = nil
    @Local private var confirmReset = false

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
            Text("This erases your solves, streak history, packs and Leetdex. It can't be undone.")
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
