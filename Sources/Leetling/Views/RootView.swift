import LeetlingShared
import SwiftUI

struct RootView: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        @Bindable var store = store
        NavigationSplitView {
            Sidebar()
                .navigationSplitViewColumnWidth(min: 200, ideal: 220, max: 260)
        } detail: {
            ZStack {
                Theme.backdrop.ignoresSafeArea()
                detail
            }
        }
        .tint(Theme.rose)
        .overlay {
            if let celebration = store.celebration {
                CelebrationView(celebration: celebration)
                    .transition(.opacity.combined(with: .scale(scale: 0.96)))
            }
        }
        .animation(.spring(response: 0.4, dampingFraction: 0.8), value: store.celebration?.id)
    }

    @ViewBuilder private var detail: some View {
        if let id = store.openProblemID, let problem = store.problem(id) {
            ProblemView(problem: problem)
                .id(problem.id)
        } else {
            switch store.section {
            case .today: TodayView()
            case .problems: ProblemListView()
            case .packs: PacksView()
            case .dex: DexView()
            case .settings: SettingsView()
            }
        }
    }
}

struct Sidebar: View {
    @Environment(AppStore.self) private var store

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: 8) {
                Text(store.buddy?.emoji ?? "🥚").font(.system(size: 28))
                VStack(alignment: .leading, spacing: 0) {
                    Text("Leetling")
                        .font(.system(size: 20, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.plum)
                    Text("Blind 75, one day at a time")
                        .font(.system(size: 10.5, weight: .medium, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }
            }
            .padding(.horizontal, 16)
            .padding(.top, 8)
            .padding(.bottom, 14)

            VStack(spacing: 4) {
                ForEach(Section.allCases) { section in
                    SidebarRow(section: section, selected: store.openProblemID == nil && store.section == section,
                               badge: badge(for: section)) {
                        store.openProblemID = nil
                        store.section = section
                    }
                }
            }
            .padding(.horizontal, 10)

            Spacer()

            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 4) {
                    Image(systemName: "flame.fill").foregroundStyle(Theme.roseDeep)
                    Text("\(store.streak)-day streak")
                }
                .font(.system(size: 13, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.plum)
                CozyProgressBar(value: Double(store.solvedCount) / Double(max(1, store.problems.count)), height: 8)
                Text("\(store.solvedCount) / \(store.problems.count) solved")
                    .font(.system(size: 11, weight: .semibold, design: .rounded))
                    .foregroundStyle(Theme.mauve)
            }
            .padding(14)
            .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Theme.blush.opacity(0.35)))
            .padding(12)
        }
        .frame(maxHeight: .infinity, alignment: .top)
        .background(Theme.cream.opacity(0.6))
    }

    private func badge(for section: Section) -> String? {
        switch section {
        case .packs: return store.progress.totalPacks > 0 ? "\(store.progress.totalPacks)" : nil
        case .dex: return Dex.all.contains(where: store.canEvolve) ? "✦" : nil
        default: return nil
        }
    }
}

private struct SidebarRow: View {
    let section: Section
    let selected: Bool
    let badge: String?
    let action: () -> Void

    @Local private var hovering = false

    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                Image(systemName: section.icon)
                    .font(.system(size: 13, weight: .semibold))
                    .frame(width: 20)
                Text(section.title)
                    .font(.system(size: 14, weight: selected ? .bold : .semibold, design: .rounded))
                Spacer()
                if let badge {
                    Text(badge)
                        .font(.system(size: 11, weight: .heavy, design: .rounded))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 7).padding(.vertical, 2)
                        .background(Capsule().fill(Theme.roseDeep))
                }
            }
            .foregroundStyle(selected ? Theme.roseDeep : Theme.plum)
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(selected ? Theme.blush.opacity(0.75) : hovering ? Theme.blush.opacity(0.3) : .clear)
            )
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .onHover { hovering = $0 }
    }
}
