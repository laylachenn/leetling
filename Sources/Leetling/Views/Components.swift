import LeetlingShared
import SwiftUI

// MARK: - Cards & pills

struct CozyCard: ViewModifier {
    var padding: CGFloat = 20
    var fill: Color = Theme.paper

    func body(content: Content) -> some View {
        content
            .padding(padding)
            .background(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .fill(fill)
                    .shadow(color: Theme.rose.opacity(0.18), radius: 14, x: 0, y: 6)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .strokeBorder(Theme.blush.opacity(0.9), lineWidth: 1)
            )
    }
}

extension View {
    func cozyCard(padding: CGFloat = 20, fill: Color = Theme.paper) -> some View {
        modifier(CozyCard(padding: padding, fill: fill))
    }
}

struct Pill: View {
    let text: String
    var color: Color = Theme.rose
    var filled = false

    var body: some View {
        Text(text)
            .font(.system(size: 11.5, weight: .bold, design: .rounded))
            .padding(.horizontal, 9)
            .padding(.vertical, 4)
            .foregroundStyle(filled ? .white : color)
            .background(Capsule().fill(filled ? color : color.opacity(0.14)))
    }
}

struct DifficultyPill: View {
    let difficulty: String
    var body: some View { Pill(text: difficulty, color: Theme.difficultyColor(difficulty)) }
}

struct SectionTitle: View {
    let title: String
    var emoji: String? = nil

    var body: some View {
        HStack(spacing: 6) {
            if let emoji { Text(emoji) }
            Text(title)
        }
        .font(.system(size: 15, weight: .bold, design: .rounded))
        .foregroundStyle(Theme.plum)
    }
}

// MARK: - Buttons

struct CozyButtonStyle: ButtonStyle {
    enum Kind { case primary, secondary, mint, quiet }
    var kind: Kind = .primary
    var compact = false

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.system(size: compact ? 12.5 : 14, weight: .bold, design: .rounded))
            .padding(.horizontal, compact ? 12 : 18)
            .padding(.vertical, compact ? 6 : 10)
            .foregroundStyle(foreground)
            .background(Capsule().fill(background))
            .overlay(Capsule().strokeBorder(kind == .secondary || kind == .quiet ? Theme.rose.opacity(0.45) : .clear, lineWidth: 1.2))
            .scaleEffect(configuration.isPressed ? 0.96 : 1)
            .brightness(configuration.isPressed ? -0.04 : 0)
            .animation(.spring(response: 0.25, dampingFraction: 0.6), value: configuration.isPressed)
            .contentShape(Capsule())
    }

    private var foreground: Color {
        switch kind {
        case .primary, .mint: return .white
        case .secondary, .quiet: return Theme.roseDeep
        }
    }

    private var background: AnyShapeStyle {
        switch kind {
        case .primary: return AnyShapeStyle(LinearGradient(colors: [Theme.rose, Theme.roseDeep], startPoint: .top, endPoint: .bottom))
        case .mint: return AnyShapeStyle(LinearGradient(colors: [Color(hex: 0x7ED6B0), Theme.mintDeep], startPoint: .top, endPoint: .bottom))
        case .secondary: return AnyShapeStyle(Color.white)
        case .quiet: return AnyShapeStyle(Theme.blush.opacity(0.35))
        }
    }
}

extension ButtonStyle where Self == CozyButtonStyle {
    static var cozy: CozyButtonStyle { CozyButtonStyle() }
    static func cozy(_ kind: CozyButtonStyle.Kind, compact: Bool = false) -> CozyButtonStyle {
        CozyButtonStyle(kind: kind, compact: compact)
    }
}

// MARK: - Progress bar

struct CozyProgressBar: View {
    let value: Double   // 0…1
    var height: CGFloat = 10
    var colors: [Color] = [Theme.rose, Theme.lavender]

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule().fill(Theme.blush.opacity(0.45))
                Capsule()
                    .fill(LinearGradient(colors: colors, startPoint: .leading, endPoint: .trailing))
                    .frame(width: max(value > 0 ? height : 0, geo.size.width * min(1, max(0, value))))
            }
        }
        .frame(height: height)
        .animation(.spring(response: 0.5, dampingFraction: 0.8), value: value)
    }
}

// MARK: - Leetling card art

struct LeetlingArt: View {
    let critter: Leetling
    var size: CGFloat = 54
    var silhouette = false

    var body: some View {
        ZStack(alignment: .topTrailing) {
            Text(critter.emoji)
                .font(.system(size: size))
                .colorMultiply(silhouette ? .black : .white)
                .opacity(silhouette ? 0.18 : 1)
            if let acc = critter.accessory, !silhouette {
                Text(acc)
                    .font(.system(size: size * 0.42))
                    .offset(x: size * 0.18, y: -size * 0.12)
            }
        }
    }
}

struct LeetlingCardView: View {
    let critter: Leetling
    var shiny = false
    var isNew = false
    var count: Int? = nil
    var width: CGFloat = 150

    @Local private var shimmer = false

    var body: some View {
        let h = width * 1.36
        VStack(spacing: width * 0.04) {
            HStack {
                Text("#\(String(format: "%03d", critter.dexNumber))")
                    .font(.system(size: width * 0.075, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.plum.opacity(0.55))
                Spacer()
                Text(critter.element.icon).font(.system(size: width * 0.09))
            }
            ZStack {
                Circle()
                    .fill(.white.opacity(0.55))
                    .frame(width: width * 0.62, height: width * 0.62)
                LeetlingArt(critter: critter, size: width * 0.36)
            }
            .frame(height: width * 0.62)
            Text(critter.name)
                .font(.system(size: width * 0.105, weight: .heavy, design: .rounded))
                .foregroundStyle(Theme.plum)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
            Text(critter.rarity.stars)
                .font(.system(size: width * 0.08, weight: .bold))
                .foregroundStyle(critter.rarity.color)
            Spacer(minLength: 0)
        }
        .padding(width * 0.07)
        .frame(width: width, height: h)
        .background(
            RoundedRectangle(cornerRadius: width * 0.12, style: .continuous)
                .fill(LinearGradient(colors: critter.element.colors, startPoint: .top, endPoint: .bottom))
        )
        .overlay {
            if shiny {
                RoundedRectangle(cornerRadius: width * 0.12, style: .continuous)
                    .fill(
                        LinearGradient(colors: [.clear, .white.opacity(0.65), Color(hex: 0xFFE6F7, opacity: 0.5), .clear],
                                       startPoint: shimmer ? .topLeading : UnitPoint(x: -1, y: -1),
                                       endPoint: shimmer ? UnitPoint(x: 2, y: 2) : .bottomTrailing)
                    )
                    .blendMode(.overlay)
                    .allowsHitTesting(false)
            }
        }
        .overlay(
            RoundedRectangle(cornerRadius: width * 0.12, style: .continuous)
                .strokeBorder(
                    shiny ? AnyShapeStyle(AngularGradient(colors: [.pink, .purple, .blue, .mint, .yellow, .pink], center: .center))
                          : AnyShapeStyle(Color.white.opacity(0.9)),
                    lineWidth: shiny ? 3 : 2.5)
        )
        .overlay(alignment: .topLeading) {
            HStack(spacing: 4) {
                if isNew { Pill(text: "NEW!", color: Theme.roseDeep, filled: true) }
                if shiny { Pill(text: "✨ Shiny", color: Color(hex: 0x9C6BF2), filled: true) }
            }
            .offset(x: -6, y: -10)
        }
        .overlay(alignment: .bottomTrailing) {
            if let count, count > 1 {
                Text("×\(count)")
                    .font(.system(size: width * 0.085, weight: .heavy, design: .rounded))
                    .foregroundStyle(.white)
                    .padding(.horizontal, 7).padding(.vertical, 3)
                    .background(Capsule().fill(Theme.plum.opacity(0.75)))
                    .padding(8)
            }
        }
        .shadow(color: critter.element.colors[1].opacity(0.55), radius: 10, y: 5)
        .onAppear {
            guard shiny else { return }
            withAnimation(.easeInOut(duration: 2.2).repeatForever(autoreverses: true)) { shimmer = true }
        }
    }
}

// MARK: - Markdown-ish text

/// Renders the problem descriptions/hints: paragraphs with inline `code`, **bold** and *italics*.
struct RichText: View {
    let text: String
    var size: CGFloat = 14

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(Array(paragraphs.enumerated()), id: \.offset) { _, para in
                if para.hasPrefix("- ") {
                    VStack(alignment: .leading, spacing: 5) {
                        ForEach(Array(para.split(separator: "\n").enumerated()), id: \.offset) { _, line in
                            HStack(alignment: .firstTextBaseline, spacing: 7) {
                                Text("•").foregroundStyle(Theme.rose)
                                inline(String(line.dropFirst(2)))
                            }
                        }
                    }
                } else {
                    inline(para)
                }
            }
        }
    }

    private var paragraphs: [String] {
        text.components(separatedBy: "\n\n").map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
    }

    private func inline(_ s: String) -> some View {
        var attributed = (try? AttributedString(markdown: s, options: .init(interpretedSyntax: .inlineOnlyPreservingWhitespace)))
            ?? AttributedString(s)
        for run in attributed.runs where run.inlinePresentationIntent?.contains(.code) == true {
            attributed[run.range].font = .system(size: size - 1, design: .monospaced)
            attributed[run.range].foregroundColor = Theme.roseDeep
            attributed[run.range].backgroundColor = Theme.blush.opacity(0.45)
        }
        return Text(attributed)
            .font(.system(size: size, design: .rounded))
            .foregroundStyle(Theme.plum)
            .lineSpacing(3)
            .fixedSize(horizontal: false, vertical: true)
            .textSelection(.enabled)
    }
}
