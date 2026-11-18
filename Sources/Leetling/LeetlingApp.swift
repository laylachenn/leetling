import AppKit
import LeetlingShared
import SwiftUI

@main
struct LeetlingApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    private let store = AppStore.shared

    var body: some Scene {
        // A single-instance `Window` (not `WindowGroup`) so leetling:// URLs from the widget reuse
        // the existing window instead of spawning a second one.
        Window("Leetling", id: "main") {
            RootView()
                .environment(store)
                .preferredColorScheme(.light)
                .frame(minWidth: 1100, minHeight: 720)
                .alert("You have progress in two places 🌷", isPresented: Binding(
                    get: { store.sync.isChoosing }, set: { _ in })) {
                    Button("Combine both") { store.sync.resolveChoice(.combine) }
                    Button("Use the synced copy") { store.sync.resolveChoice(.remote) }
                } message: {
                    Text("This Mac and your synced copy both have solves and Leetlings. Combine them into one, or replace this Mac's progress with the synced copy?")
                }
                .onOpenURL { url in
                    if url.host == "today" {
                        store.openProblemID = nil
                        store.section = .today
                    }
                }
        }
        .defaultSize(width: 1280, height: 820)
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}

@MainActor
final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.regular)
        NSApp.activate(ignoringOtherApps: true)
        AppStore.shared.ensureRandomPick()
        DesktopBuddy.shared.setVisible(AppStore.shared.progress.showDesktopBuddy)
        AppStore.shared.onDesktopBuddyChange = { DesktopBuddy.shared.setVisible($0) }
        AppStore.shared.sync.start()
    }

    func applicationWillTerminate(_ notification: Notification) {
        AppStore.shared.saveNow()
    }

    // Keep running (for the desktop buddy) after the main window closes; clicking the Dock icon reopens it.
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        !AppStore.shared.progress.showDesktopBuddy
    }
}

extension AppStore {
    static let shared = AppStore()
}
