import SwiftUI
import LeetlingShared

// Leetlings are the app's own collectible critters (original names, emoji art).
// Solve problems → earn packs → open packs → collect & evolve Leetlings.

enum Element: String, Codable, CaseIterable {
    case blossom, splash, ember, breeze, cocoa, frost, dream, starry

    var name: String { rawValue.capitalized }

    var icon: String {
        switch self {
        case .blossom: return "🌸"
        case .splash: return "💧"
        case .ember: return "🔥"
        case .breeze: return "🍃"
        case .cocoa: return "🍫"
        case .frost: return "❄️"
        case .dream: return "🌙"
        case .starry: return "✨"
        }
    }

    var colors: [Color] {
        switch self {
        case .blossom: return [Color(hex: 0xFFD1E1), Color(hex: 0xFFB0CB)]
        case .splash: return [Color(hex: 0xCDEBFF), Color(hex: 0x9FD3FA)]
        case .ember: return [Color(hex: 0xFFE0C2), Color(hex: 0xFFB38A)]
        case .breeze: return [Color(hex: 0xD8F5E3), Color(hex: 0xA9E5C3)]
        case .cocoa: return [Color(hex: 0xF3E1CF), Color(hex: 0xDDBB9A)]
        case .frost: return [Color(hex: 0xE6F4FF), Color(hex: 0xC4E1F7)]
        case .dream: return [Color(hex: 0xE6DCFF), Color(hex: 0xC2AEF5)]
        case .starry: return [Color(hex: 0xFFF5C7), Color(hex: 0xF8D97A)]
        }
    }
}

enum Rarity: Int, Codable, CaseIterable, Comparable {
    case common = 1, uncommon, rare, legendary

    static func < (a: Rarity, b: Rarity) -> Bool { a.rawValue < b.rawValue }

    var name: String {
        switch self {
        case .common: return "Common"
        case .uncommon: return "Uncommon"
        case .rare: return "Rare"
        case .legendary: return "Legendary"
        }
    }

    var stars: String { String(repeating: "★", count: rawValue) }

    var color: Color {
        switch self {
        case .common: return Theme.mauve
        case .uncommon: return Theme.mintDeep
        case .rare: return Color(hex: 0x7B6CF6)
        case .legendary: return Color(hex: 0xE89B3C)
        }
    }
}

struct Leetling: Identifiable, Hashable {
    let id: String
    let name: String
    let emoji: String
    let accessory: String?       // little overlay emoji for evolved forms (🎀, 👑, ✨…)
    let element: Element
    let stage: Int               // 1–3 for evolution lines, 0 for legendaries
    let evolvesTo: String?
    let rarity: Rarity
    let flavor: String
    let dexNumber: Int
}

enum Dex {
    static let all: [Leetling] = build()
    static let byID: [String: Leetling] = Dictionary(uniqueKeysWithValues: all.map { ($0.id, $0) })

    static func of(_ id: String) -> Leetling? { byID[id] }
    static func with(_ rarity: Rarity) -> [Leetling] { all.filter { $0.rarity == rarity } }

    static let copiesToEvolve = 3

    private typealias Form = (id: String, name: String, emoji: String, accessory: String?, flavor: String)

    private static func build() -> [Leetling] {
        let lines: [(Element, [Form])] = [
            (.breeze, [("peepip", "Peepip", "🐣", nil, "Hatched mid-semester. Peeps encouragingly whenever you open your laptop."),
                       ("chirpette", "Chirpette", "🐥", "🎀", "Hums little tunes while you trace through a for-loop."),
                       ("cloudove", "Cloudove", "🕊️", nil, "Glides above your code and spots off-by-one errors from the sky.")]),
            (.splash, [("finnie", "Finnie", "🐟", nil, "Swims in circles. Surprisingly good at detecting cycles."),
                       ("coralette", "Coralette", "🐠", nil, "Keeps a tidy reef sorted in ascending order."),
                       ("tidalumi", "Tidalumi", "🐳", "✨", "A gentle giant who can hold an entire hash map in one breath.")]),
            (.ember, [("sizzlet", "Sizzlet", "🦎", nil, "Its tail glows warmer each day of your streak."),
                      ("drakelet", "Drakelet", "🐲", nil, "Breathes tiny sparks that light up the right data structure."),
                      ("emberwyrm", "Emberwyrm", "🐉", "🔥", "Legends say it once solved Merge k Sorted Lists in its sleep.")]),
            (.blossom, [("nibblet", "Nibblet", "🐛", nil, "Munches through arrays one element at a time."),
                        ("flutterine", "Flutterine", "🦋", nil, "Flutters between two pointers until they meet."),
                        ("petalfae", "Petalfae", "🧚", "🌸", "Sprinkles petals on every Accepted submission.")]),
            (.dream, [("mochikit", "Mochikit", "🐱", nil, "Naps on your keyboard. Occasionally types valid Python."),
                      ("velvetail", "Velvetail", "🐈", "🎀", "Knocks bugs off the table, one by one."),
                      ("nocturna", "Nocturna", "🐈‍⬛", "🌙", "Only appears to those who practice late at night.")]),
            (.cocoa, [("pudgeon", "Pudgeon", "🐹", nil, "Stuffs its cheeks with memoized results for later."),
                      ("nutkin", "Nutkin", "🐿️", nil, "Buries acorns in a perfectly balanced tree."),
                      ("timberbelle", "Timberbelle", "🦫", "🎀", "Builds dams out of well-placed base cases.")]),
            (.frost, [("snowpip", "Snowpip", "🐧", nil, "Waddles through linked lists, node by node."),
                      ("sealumi", "Sealumi", "🦭", nil, "Balances a stack on its nose — LIFO only!"),
                      ("glacierbear", "Glacierbear", "🐻‍❄️", "❄️", "Calm, cool, and never panics on a Hard problem.")]),
            (.starry, [("bunbun", "Bunbun", "🐰", nil, "Hops between recursion levels without ever getting lost."),
                       ("hopsy", "Hopsy", "🐇", nil, "Can jump to any index in O(1)."),
                       ("cloverqueen", "Queen Clover", "🐇", "👑", "Rules the meadow with a lucky, logarithmic hop.")]),
            (.splash, [("ribbit", "Ribbit", "🐸", nil, "Hops lily pad to lily pad — a natural at Jump Game."),
                       ("croakette", "Croakette", "🐸", "🎀", "Sings a little song for every passing test case."),
                       ("froggington", "Sir Froggington", "🐸", "👑", "A distinguished gentleman of dynamic programming.")]),
            (.breeze, [("puppuff", "Puppuff", "🐶", nil, "Fetches your hints. Very good dog."),
                       ("barkley", "Barkley", "🐕", nil, "Sniffs out the shortest path in any graph."),
                       ("moonhowl", "Moonhowl", "🐺", "🌙", "Howls once for each day of your streak.")]),
            (.cocoa, [("honeybun", "Honeybun", "🐻", nil, "Sticky-sweet and stubbornly persistent."),
                      ("teddiette", "Teddiette", "🧸", "🎀", "Gives the best hugs after a Wrong Answer."),
                      ("pandarling", "Pandarling", "🐼", "✨", "Balances everything: work, rest, and red-black trees.")]),
            (.ember, [("foxling", "Foxling", "🦊", nil, "Clever and curious — always asks \"what's the edge case?\""),
                      ("vixette", "Vixette", "🦊", "🎀", "Outfoxes brute force with a single hash set."),
                      ("kitsunova", "Kitsunova", "🦊", "✨", "Each of its tails holds a different sorting algorithm.")]),
            (.dream, [("fluffle", "Fluffle", "🐑", nil, "Counting it helps you fall asleep. Counting with it helps you pass interviews."),
                      ("cumulamb", "Cumulamb", "🐏", "☁️", "Floats on clouds of cozy, well-commented code."),
                      ("dreamllama", "Dreamllama", "🦙", "💤", "Dreams in Big-O notation.")]),
        ]
        let legendaries: [(Element, Form)] = [
            (.starry, ("aurorabelle", "Aurorabelle", "🦄", "🌈", "Appears only to coders who keep their promises to themselves.")),
            (.blossom, ("peacora", "Peacora", "🦚", nil, "Its tail fans out into a perfect binary tree.")),
            (.splash, ("flamingala", "Flamingala", "🦩", nil, "Stands on one leg for hours debugging. Very graceful.")),
            (.dream, ("jellumina", "Jellumina", "🪼", "✨", "Glows softly in the deep end of the call stack.")),
            (.frost, ("swanelle", "Swanelle", "🦢", "❄️", "Serene on the surface, furiously paddling recursion underneath.")),
            (.ember, ("pyrabelle", "Pyrabelle", "🐦‍🔥", nil, "Rises from every broken streak, stronger than before.")),
            (.cocoa, ("bramblequill", "Bramblequill", "🦔", "🍂", "Curls into a ball around your hardest bugs until they give up.")),
        ]

        var result: [Leetling] = []
        var number = 1
        for (element, forms) in lines {
            for (i, form) in forms.enumerated() {
                result.append(Leetling(
                    id: form.id, name: form.name, emoji: form.emoji, accessory: form.accessory, element: element,
                    stage: i + 1, evolvesTo: i + 1 < forms.count ? forms[i + 1].id : nil,
                    rarity: [Rarity.common, .uncommon, .rare][i], flavor: form.flavor, dexNumber: number))
                number += 1
            }
        }
        for (element, form) in legendaries {
            result.append(Leetling(
                id: form.id, name: form.name, emoji: form.emoji, accessory: form.accessory, element: element,
                stage: 0, evolvesTo: nil, rarity: .legendary, flavor: form.flavor, dexNumber: number))
            number += 1
        }
        return result
    }
}

// MARK: - Packs

enum PackKind: String, Codable, CaseIterable, Identifiable {
    case sprout, bloom, starlight

    var id: String { rawValue }

    var name: String {
        switch self {
        case .sprout: return "Sprout Pack"
        case .bloom: return "Bloom Pack"
        case .starlight: return "Starlight Pack"
        }
    }

    var emoji: String {
        switch self {
        case .sprout: return "🌱"
        case .bloom: return "🌷"
        case .starlight: return "🌟"
        }
    }

    var howToEarn: String {
        switch self {
        case .sprout: return "Solve a problem for the first time"
        case .bloom: return "Hit your daily goal"
        case .starlight: return "Streak milestones & finishing a whole topic"
        }
    }

    var cardCount: Int {
        switch self {
        case .sprout: return 3
        case .bloom: return 4
        case .starlight: return 5
        }
    }

    var colors: [Color] {
        switch self {
        case .sprout: return [Color(hex: 0xC9F2DA), Color(hex: 0x8ED9B0)]
        case .bloom: return [Color(hex: 0xFFC8DA), Color(hex: 0xF58BB0)]
        case .starlight: return [Color(hex: 0xD9CCFF), Color(hex: 0x9C86F2)]
        }
    }

    /// Weights for common / uncommon / rare / legendary.
    var weights: [Double] {
        switch self {
        case .sprout: return [70, 22, 6.5, 1.5]
        case .bloom: return [62, 27, 9, 2]
        case .starlight: return [50, 30, 15, 5]
        }
    }

    /// The last card in the pack is guaranteed to be at least this rare.
    var guaranteedLast: Rarity {
        switch self {
        case .sprout: return .common
        case .bloom: return .uncommon
        case .starlight: return .rare
        }
    }

    var shinyChance: Double { self == .starlight ? 1.0 / 10 : 1.0 / 20 }
}

struct PackPull: Identifiable, Hashable {
    let id = UUID()
    let leetling: Leetling
    let shiny: Bool
    let isNew: Bool
}

enum PackOpener {
    static func roll<G: RandomNumberGenerator>(_ kind: PackKind, using rng: inout G) -> [(Leetling, Bool)] {
        (0..<kind.cardCount).map { i in
            var rarity = pickRarity(kind.weights, using: &rng)
            if i == kind.cardCount - 1, rarity < kind.guaranteedLast {
                rarity = kind == .starlight && Double.random(in: 0..<1, using: &rng) < 0.25 ? .legendary : kind.guaranteedLast
            }
            let pool = Dex.with(rarity)
            let critter = pool.randomElement(using: &rng)!
            let shiny = Double.random(in: 0..<1, using: &rng) < kind.shinyChance
            return (critter, shiny)
        }
    }

    private static func pickRarity<G: RandomNumberGenerator>(_ weights: [Double], using rng: inout G) -> Rarity {
        var x = Double.random(in: 0..<weights.reduce(0, +), using: &rng)
        for (i, w) in weights.enumerated() {
            if x < w { return Rarity(rawValue: i + 1)! }
            x -= w
        }
        return .common
    }
}
