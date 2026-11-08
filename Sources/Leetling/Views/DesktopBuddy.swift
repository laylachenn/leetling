import AppKit
import LeetlingShared
import SwiftUI

/// A borderless panel that sits on the desktop (above icons, below normal windows) showing the
/// streak card. A backup for the real WidgetKit widget — works without any widget registration.
@MainActor
final class DesktopBuddy {
    static let shared = DesktopBuddy()
    private var panel: NSPanel?

    func setVisible(_ visible: Bool) {
        if visible {
            if panel == nil { panel = makePanel() }
            panel?.orderFrontRegardless()
        } else {
            panel?.orderOut(nil)
        }
    }

    private func makePanel() -> NSPanel {
        let panel = NSPanel(contentRect: NSRect(x: 0, y: 0, width: 360, height: 168),
                            styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.level = NSWindow.Level(rawValue: Int(CGWindowLevelForKey(.desktopIconWindow)) + 1)
        panel.collectionBehavior = [.canJoinAllSpaces, .stationary, .ignoresCycle]
        panel.isMovableByWindowBackground = true
        panel.backgroundColor = .clear
        panel.isOpaque = false
        panel.hasShadow = false
        panel.hidesOnDeactivate = false
        let host = NSHostingView(rootView: DesktopBuddyView().environment(AppStore.shared))
        host.frame = panel.contentRect(forFrameRect: panel.frame)
        panel.contentView = host
        if !panel.setFrameUsingName("LeetlingDesktopBuddy"), let screen = NSScreen.main {
            let f = screen.visibleFrame
            panel.setFrameOrigin(NSPoint(x: f.maxX - 380, y: f.maxY - 190))
        }
        panel.setFrameAutosaveName("LeetlingDesktopBuddy")
        return panel
    }
}

private struct DesktopBuddyView: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        StreakCard(snapshot: store.snapshot, compact: true)
            .padding(14)
            .background(
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .fill(LinearGradient(colors: [Theme.cream, Color(hex: 0xFFF0F5)], startPoint: .top, endPoint: .bottom))
                    .shadow(color: Theme.rose.opacity(0.3), radius: 10, y: 4)
            )
            .overlay(alignment: .topTrailing) {
                Text(store.buddy?.emoji ?? "🥚")
                    .font(.system(size: 26))
                    .offset(x: -6, y: -10)
            }
            .padding(10)
            .onTapGesture(count: 2) {
                NSApp.activate(ignoringOtherApps: true)
                store.openProblemID = nil
                store.section = .today
                NSApp.windows.first { $0.canBecomeMain }?.makeKeyAndOrderFront(nil)
            }
            .help("Double-click to open Leetling")
    }
}
