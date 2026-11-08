import LeetlingShared
import SwiftUI

struct PacksView: View {
    @Environment(AppStore.self) private var store
    @Local private var opening: OpeningSession? = nil

    var body: some View {
        ZStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Your packs 🎁")
                            .font(.system(size: 28, weight: .heavy, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        Text("Every pack holds Leetlings. Collect 3 of the same one to evolve it!")
                            .font(.system(size: 14, weight: .medium, design: .rounded))
                            .foregroundStyle(Theme.mauve)
                    }
                    HStack(alignment: .top, spacing: 18) {
                        ForEach(PackKind.allCases) { kind in
                            PackTile(kind: kind, count: store.progress.packCount(kind)) {
                                if let pulls = store.openPack(kind) {
                                    opening = OpeningSession(kind: kind, pulls: pulls)
                                }
                            }
                        }
                    }
                    odds
                }
                .padding(28)
                .frame(maxWidth: 980)
                .frame(maxWidth: .infinity)
            }
            if let session = opening {
                PackOpeningView(session: session) {
                    withAnimation { opening = nil }
                }
                .transition(.opacity)
            }
        }
    }

    private var odds: some View {
        VStack(alignment: .leading, spacing: 8) {
            SectionTitle(title: "Pack guide", emoji: "📜")
            ForEach(PackKind.allCases) { kind in
                HStack(alignment: .firstTextBaseline, spacing: 8) {
                    Text(kind.emoji)
                    Text(kind.name).font(.system(size: 13, weight: .bold, design: .rounded))
                    Text("· \(kind.cardCount) cards · last card \(kind.guaranteedLast.name)+ · \(Int((kind.shinyChance * 100).rounded()))% shiny per card")
                        .font(.system(size: 12.5, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }
                .foregroundStyle(Theme.plum)
            }
            Text("Shiny Leetlings ✨ sparkle and are extra rare. Legendaries can't evolve, but they're legendary. 💅")
                .font(.system(size: 12.5, design: .rounded))
                .foregroundStyle(Theme.mauve)
        }
        .cozyCard()
    }
}

struct OpeningSession: Identifiable {
    let id = UUID()
    let kind: PackKind
    let pulls: [PackPull]
}

private struct PackArt: View {
    let kind: PackKind
    var width: CGFloat = 150

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(LinearGradient(colors: kind.colors, startPoint: .topLeading, endPoint: .bottomTrailing))
            // little zigzag "crimp" at the top & bottom
            VStack {
                Rectangle().fill(.white.opacity(0.35)).frame(height: 10)
                Spacer()
                Rectangle().fill(.white.opacity(0.35)).frame(height: 10)
            }
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            VStack(spacing: 8) {
                Text(kind.emoji).font(.system(size: width * 0.34))
                Text(kind.name.uppercased())
                    .font(.system(size: width * 0.085, weight: .black, design: .rounded))
                    .foregroundStyle(.white)
                    .shadow(color: .black.opacity(0.15), radius: 2, y: 1)
                Text("✿ LEETLINGS ✿")
                    .font(.system(size: width * 0.06, weight: .bold, design: .rounded))
                    .foregroundStyle(.white.opacity(0.85))
            }
        }
        .frame(width: width, height: width * 1.4)
        .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).strokeBorder(.white.opacity(0.8), lineWidth: 3))
        .shadow(color: kind.colors[1].opacity(0.5), radius: 12, y: 6)
    }
}

private struct PackTile: View {
    let kind: PackKind
    let count: Int
    let open: () -> Void
    @Local private var wiggle = false

    var body: some View {
        VStack(spacing: 12) {
            PackArt(kind: kind)
                .rotationEffect(.degrees(count > 0 && wiggle ? 2.5 : count > 0 ? -2.5 : 0))
                .animation(count > 0 ? .easeInOut(duration: 0.6).repeatForever(autoreverses: true) : .default, value: wiggle)
                .saturation(count > 0 ? 1 : 0.25)
                .opacity(count > 0 ? 1 : 0.6)
                .overlay(alignment: .topTrailing) {
                    if count > 0 {
                        Text("×\(count)")
                            .font(.system(size: 15, weight: .heavy, design: .rounded))
                            .foregroundStyle(.white)
                            .padding(.horizontal, 9).padding(.vertical, 4)
                            .background(Capsule().fill(Theme.roseDeep))
                            .offset(x: 10, y: -10)
                    }
                }
            Text(kind.howToEarn)
                .font(.system(size: 12, weight: .medium, design: .rounded))
                .foregroundStyle(Theme.mauve)
                .multilineTextAlignment(.center)
                .frame(height: 32)
            Button(count > 0 ? "Open ✨" : "None yet", action: open)
                .buttonStyle(.cozy(count > 0 ? .primary : .quiet))
                .disabled(count == 0)
        }
        .frame(maxWidth: .infinity)
        .cozyCard()
        .onAppear { wiggle = true }
    }
}

// MARK: - Opening animation

private struct PackOpeningView: View {
    let session: OpeningSession
    let done: () -> Void

    @Local private var torn = false
    @Local private var shake = false
    @Local private var flipped: Set<Int> = []

    var body: some View {
        ZStack {
            Rectangle().fill(.ultraThinMaterial).ignoresSafeArea()
            Theme.blush.opacity(0.35).ignoresSafeArea()

            if !torn {
                VStack(spacing: 22) {
                    Text("Tap the pack to open it!")
                        .font(.system(size: 20, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.plum)
                    PackArt(kind: session.kind, width: 210)
                        .rotationEffect(.degrees(shake ? 4 : -4))
                        .animation(.easeInOut(duration: 0.12).repeatForever(autoreverses: true), value: shake)
                        .onTapGesture {
                            withAnimation(.spring(response: 0.5, dampingFraction: 0.7)) { torn = true }
                        }
                        .onAppear { shake = true }
                }
                .transition(.scale(scale: 1.4).combined(with: .opacity))
            } else {
                VStack(spacing: 26) {
                    Text(allFlipped ? summary : "Tap each card to reveal ✨")
                        .font(.system(size: 20, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.plum)
                    HStack(spacing: 16) {
                        ForEach(Array(session.pulls.enumerated()), id: \.offset) { i, pull in
                            FlipCard(pull: pull, flipped: flipped.contains(i))
                                .onTapGesture {
                                    withAnimation(.spring(response: 0.55, dampingFraction: 0.75)) { _ = flipped.insert(i) }
                                }
                                .transition(.move(edge: .bottom).combined(with: .opacity))
                        }
                    }
                    HStack(spacing: 12) {
                        if !allFlipped {
                            Button("Reveal all") {
                                withAnimation(.spring(response: 0.55, dampingFraction: 0.75)) {
                                    flipped = Set(session.pulls.indices)
                                }
                            }
                            .buttonStyle(.cozy(.secondary))
                        }
                        Button(allFlipped ? "Add to my Leetdex 💖" : "Skip") { done() }
                            .buttonStyle(.cozy(allFlipped ? .primary : .quiet))
                            .keyboardShortcut(.return, modifiers: [])
                    }
                }
                .transition(.opacity)
            }
        }
    }

    private var allFlipped: Bool { flipped.count == session.pulls.count }

    private var summary: String {
        let new = session.pulls.filter(\.isNew).count
        let shiny = session.pulls.filter(\.shiny).count
        var parts: [String] = []
        if new > 0 { parts.append("\(new) new Leetling\(new == 1 ? "" : "s")!") }
        if shiny > 0 { parts.append("\(shiny) shiny ✨") }
        if session.pulls.contains(where: { $0.leetling.rarity == .legendary }) { parts.append("A LEGENDARY?!") }
        return parts.isEmpty ? "Nice pulls! 🎉" : parts.joined(separator: " · ")
    }
}

private struct FlipCard: View {
    let pull: PackPull
    let flipped: Bool

    var body: some View {
        ZStack {
            LeetlingCardView(critter: pull.leetling, shiny: pull.shiny, isNew: pull.isNew, width: 160)
                .opacity(flipped ? 1 : 0)
                .rotation3DEffect(.degrees(flipped ? 0 : -180), axis: (x: 0, y: 1, z: 0))
            CardBack(width: 160)
                .opacity(flipped ? 0 : 1)
                .rotation3DEffect(.degrees(flipped ? 180 : 0), axis: (x: 0, y: 1, z: 0))
        }
        .scaleEffect(flipped && pull.leetling.rarity >= .rare ? 1.06 : 1)
        .shadow(color: flipped && pull.leetling.rarity >= .rare ? pull.leetling.rarity.color.opacity(0.6) : .clear, radius: 18)
    }
}

private struct CardBack: View {
    let width: CGFloat

    var body: some View {
        RoundedRectangle(cornerRadius: width * 0.12, style: .continuous)
            .fill(LinearGradient(colors: [Theme.rose, Color(hex: 0xB59CFF)], startPoint: .topLeading, endPoint: .bottomTrailing))
            .overlay(
                VStack(spacing: 6) {
                    Text("✿").font(.system(size: width * 0.3)).foregroundStyle(.white.opacity(0.9))
                    Text("LEETLING")
                        .font(.system(size: width * 0.09, weight: .black, design: .rounded))
                        .foregroundStyle(.white)
                }
            )
            .overlay(RoundedRectangle(cornerRadius: width * 0.12, style: .continuous).strokeBorder(.white.opacity(0.85), lineWidth: 3))
            .frame(width: width, height: width * 1.36)
            .shadow(color: Theme.rose.opacity(0.4), radius: 10, y: 5)
    }
}
