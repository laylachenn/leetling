import LeetlingShared
import SwiftUI

struct CelebrationView: View {
    @Environment(AppStore.self) private var store
    let celebration: Celebration

    var body: some View {
        ZStack {
            Color.black.opacity(0.18).ignoresSafeArea()
                .onTapGesture { store.celebration = nil }
            Confetti()
            VStack(spacing: 14) {
                Text("🌸").font(.system(size: 54))
                Text("Accepted!")
                    .font(.system(size: 34, weight: .black, design: .rounded))
                    .foregroundStyle(LinearGradient(colors: [Theme.roseDeep, Color(hex: 0x9C6BF2)], startPoint: .leading, endPoint: .trailing))
                Text(celebration.firstSolve ? "You solved **\(celebration.problemTitle)** for the first time!" : "You solved **\(celebration.problemTitle)** again — that's how it sticks 🧠")
                    .font(.system(size: 15, design: .rounded))
                    .foregroundStyle(Theme.plum)
                    .multilineTextAlignment(.center)
                HStack(spacing: 18) {
                    stat("🔥", "\(celebration.streak)", "day streak")
                    stat("💖", "\(celebration.todayCount)/\(celebration.goal)", "today")
                    stat("📚", "\(store.solvedCount)/\(store.problems.count)", "solved")
                }
                .padding(.vertical, 4)

                if !celebration.rewards.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(celebration.rewards) { reward in
                            HStack(spacing: 10) {
                                Text(reward.pack.emoji).font(.system(size: 22))
                                VStack(alignment: .leading, spacing: 1) {
                                    Text("+1 \(reward.pack.name)")
                                        .font(.system(size: 14, weight: .heavy, design: .rounded))
                                        .foregroundStyle(Theme.plum)
                                    Text(reward.reason)
                                        .font(.system(size: 12, design: .rounded))
                                        .foregroundStyle(Theme.mauve)
                                }
                            }
                        }
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Theme.blush.opacity(0.45)))
                } else {
                    Text("No new packs this time, but every rep counts! 💪")
                        .font(.system(size: 13, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                }

                HStack(spacing: 10) {
                    if !celebration.rewards.isEmpty {
                        Button("Open my packs 🎁") {
                            store.celebration = nil
                            store.openProblemID = nil
                            store.section = .packs
                        }
                        .buttonStyle(.cozy(.primary))
                        .keyboardShortcut(.defaultAction)
                    }
                    Button("Keep coding") { store.celebration = nil }
                        .buttonStyle(.cozy(.secondary))
                        .keyboardShortcut(.cancelAction)
                }
                .padding(.top, 4)
            }
            .padding(30)
            .frame(width: 440)
            .background(RoundedRectangle(cornerRadius: 28, style: .continuous).fill(Theme.cream))
            .overlay(RoundedRectangle(cornerRadius: 28, style: .continuous).strokeBorder(Theme.blush, lineWidth: 2))
            .shadow(color: Theme.rose.opacity(0.35), radius: 30, y: 10)
        }
    }

    private func stat(_ emoji: String, _ value: String, _ label: String) -> some View {
        VStack(spacing: 2) {
            Text("\(emoji) \(value)")
                .font(.system(size: 18, weight: .heavy, design: .rounded))
                .foregroundStyle(Theme.plum)
            Text(label)
                .font(.system(size: 11, weight: .semibold, design: .rounded))
                .foregroundStyle(Theme.mauve)
        }
        .frame(minWidth: 90)
    }
}

private struct Confetti: View {
    private let pieces = ["🌸", "💖", "✨", "🎀", "⭐️", "🌷", "💕", "🫧"]

    var body: some View {
        GeometryReader { geo in
            ZStack {
                ForEach(0..<36, id: \.self) { i in
                    ConfettiPiece(emoji: pieces[i % pieces.count], size: geo.size)
                }
            }
        }
        .allowsHitTesting(false)
        .ignoresSafeArea()
    }
}

private struct ConfettiPiece: View {
    let emoji: String
    let size: CGSize
    @Local private var fallen = false
    @Local private var x = CGFloat.random(in: 0...1)
    @Local private var drift = CGFloat.random(in: -80...80)
    @Local private var spin = Double.random(in: -360...360)
    @Local private var delay = Double.random(in: 0...0.8)
    @Local private var duration = Double.random(in: 2.2...3.6)
    @Local private var scale = CGFloat.random(in: 0.7...1.4)

    var body: some View {
        Text(emoji)
            .font(.system(size: 22 * scale))
            .rotationEffect(.degrees(fallen ? spin : 0))
            .position(x: size.width * x + (fallen ? drift : 0), y: fallen ? size.height + 40 : -40)
            .opacity(fallen ? 0.2 : 1)
            .onAppear {
                withAnimation(.easeIn(duration: duration).delay(delay)) { fallen = true }
            }
    }
}
