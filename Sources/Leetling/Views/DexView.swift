import LeetlingShared
import SwiftUI

struct DexView: View {
    @Environment(AppStore.self) private var store
    @Local private var selected: Leetling? = nil
    @Local private var ownedOnly = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                HStack(alignment: .firstTextBaseline) {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Leetdex 📖")
                            .font(.system(size: 28, weight: .heavy, design: .rounded))
                            .foregroundStyle(Theme.plum)
                        Text("\(store.progress.caught.count) of \(Dex.all.count) discovered · \(shinyCount) shiny ✨ · \(store.progress.packsOpened) packs opened")
                            .font(.system(size: 14, weight: .medium, design: .rounded))
                            .foregroundStyle(Theme.mauve)
                    }
                    Spacer()
                    Toggle("Owned only", isOn: $ownedOnly)
                        .toggleStyle(.switch)
                        .controlSize(.small)
                        .font(.system(size: 12.5, weight: .semibold, design: .rounded))
                }
                CozyProgressBar(value: Double(store.progress.caught.count) / Double(Dex.all.count))

                if Dex.all.contains(where: store.canEvolve) {
                    Text("✦ Some of your Leetlings are ready to evolve! Click one with a ✦ badge.")
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.roseDeep)
                }

                LazyVGrid(columns: [GridItem(.adaptive(minimum: 140), spacing: 18)], spacing: 22) {
                    ForEach(Dex.all.filter { !ownedOnly || store.owned($0.id).count > 0 }) { critter in
                        DexCell(critter: critter)
                            .onTapGesture {
                                if store.progress.caught.contains(critter.id) { selected = critter }
                            }
                    }
                }
                .padding(.top, 6)
            }
            .padding(28)
            .frame(maxWidth: 1000)
            .frame(maxWidth: .infinity)
        }
        .sheet(item: $selected) { critter in
            LeetlingDetail(critter: critter) { selected = $0 }
                .environment(store)
        }
    }

    private var shinyCount: Int { store.progress.collection.values.reduce(0) { $0 + $1.shiny } }
}

private struct DexCell: View {
    @Environment(AppStore.self) private var store
    let critter: Leetling

    var body: some View {
        let owned = store.owned(critter.id)
        let caught = store.progress.caught.contains(critter.id)
        Group {
            if caught {
                LeetlingCardView(critter: critter, shiny: owned.shiny > 0, count: owned.count, width: 136)
                    .opacity(owned.count == 0 ? 0.55 : 1)
                    .overlay(alignment: .topTrailing) {
                        if store.canEvolve(critter) {
                            Text("✦")
                                .font(.system(size: 14, weight: .black))
                                .foregroundStyle(.white)
                                .frame(width: 26, height: 26)
                                .background(Circle().fill(Theme.roseDeep))
                                .offset(x: 8, y: -8)
                        }
                    }
                    .contentShape(Rectangle())
            } else {
                VStack(spacing: 8) {
                    Text("#\(String(format: "%03d", critter.dexNumber))")
                        .font(.system(size: 10, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                    LeetlingArt(critter: critter, size: 44, silhouette: true)
                    Text("???")
                        .font(.system(size: 14, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                    Text(critter.rarity.stars)
                        .font(.system(size: 10))
                        .foregroundStyle(Theme.mauve.opacity(0.6))
                }
                .frame(width: 136, height: 136 * 1.36)
                .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Theme.paper))
                .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .strokeBorder(Theme.blush, style: StrokeStyle(lineWidth: 2, dash: [6, 5])))
            }
        }
    }
}

private struct LeetlingDetail: View {
    @Environment(AppStore.self) private var store
    @Environment(\.dismiss) private var dismiss
    let critter: Leetling
    let show: (Leetling) -> Void
    @Local private var evolvedBanner: String? = nil

    var body: some View {
        let owned = store.owned(critter.id)
        VStack(spacing: 18) {
            if let evolvedBanner {
                Text(evolvedBanner)
                    .font(.system(size: 18, weight: .heavy, design: .rounded))
                    .foregroundStyle(Theme.roseDeep)
                    .transition(.scale.combined(with: .opacity))
            }
            HStack(alignment: .top, spacing: 24) {
                LeetlingCardView(critter: critter, shiny: owned.shiny > 0, width: 190)
                VStack(alignment: .leading, spacing: 10) {
                    Text(critter.name)
                        .font(.system(size: 26, weight: .heavy, design: .rounded))
                        .foregroundStyle(Theme.plum)
                    HStack(spacing: 6) {
                        Pill(text: "\(critter.element.icon) \(critter.element.name)", color: Color(hex: 0x8C6FE0))
                        Pill(text: critter.rarity.name, color: critter.rarity.color)
                        if critter.stage > 0 { Pill(text: "Stage \(critter.stage)", color: Theme.mauve) }
                    }
                    Text(critter.flavor)
                        .font(.system(size: 14, design: .rounded))
                        .foregroundStyle(Theme.plum)
                        .fixedSize(horizontal: false, vertical: true)
                    Text("You have \(owned.count)\(owned.shiny > 0 ? " (\(owned.shiny) shiny ✨)" : "")")
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundStyle(Theme.mauve)
                    evolutionLine
                }
                .frame(width: 300, alignment: .leading)
            }
            HStack(spacing: 10) {
                if critter.evolvesTo != nil {
                    Button(store.canEvolve(critter) ? "Evolve ✦ (uses \(Dex.copiesToEvolve))" : "Evolve at \(Dex.copiesToEvolve) copies") {
                        if let next = store.evolve(critter) {
                            withAnimation(.spring) { evolvedBanner = "✨ \(critter.name) evolved into \(next.name)! ✨" }
                            show(next)
                        }
                    }
                    .buttonStyle(.cozy(.primary))
                    .disabled(!store.canEvolve(critter))
                }
                Button(store.progress.buddy == critter.id ? "Your buddy 💖" : "Make my buddy") { store.setBuddy(critter) }
                    .buttonStyle(.cozy(.secondary))
                    .disabled(owned.count == 0 || store.progress.buddy == critter.id)
                Spacer()
                Button("Close") { dismiss() }
                    .buttonStyle(.cozy(.quiet))
                    .keyboardShortcut(.cancelAction)
            }
        }
        .padding(26)
        .frame(width: 600)
        .background(Theme.cream)
    }

    @ViewBuilder private var evolutionLine: some View {
        let line = Dex.all.filter { $0.element == critter.element && $0.stage > 0 && lineID($0) == lineID(critter) }
        if critter.stage > 0 && line.count > 1 {
            HStack(spacing: 6) {
                ForEach(Array(line.enumerated()), id: \.element.id) { i, form in
                    let caught = store.progress.caught.contains(form.id)
                    LeetlingArt(critter: form, size: 24, silhouette: !caught)
                        .padding(4)
                        .background(Circle().fill(form.id == critter.id ? Theme.blush : .clear))
                    if i < line.count - 1 { Image(systemName: "arrow.right").font(.system(size: 10, weight: .bold)).foregroundStyle(Theme.mauve) }
                }
            }
        }
    }

    /// Evolution lines are consecutive dex numbers in groups of 3.
    private func lineID(_ l: Leetling) -> Int { (l.dexNumber - 1) / 3 }
}
