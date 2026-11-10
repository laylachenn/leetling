// Leetlings: original collectible critters (emoji art). Mirrors Sources/Leetling/Models/Leetlings.swift —
// keep the two in sync (same ids, order and dex numbers) so progress files move between the apps.

export const ELEMENTS = {
  blossom: { name: "Blossom", icon: "🌸", colors: ["#FFD1E1", "#FFB0CB"] },
  splash: { name: "Splash", icon: "💧", colors: ["#CDEBFF", "#9FD3FA"] },
  ember: { name: "Ember", icon: "🔥", colors: ["#FFE0C2", "#FFB38A"] },
  breeze: { name: "Breeze", icon: "🍃", colors: ["#D8F5E3", "#A9E5C3"] },
  cocoa: { name: "Cocoa", icon: "🍫", colors: ["#F3E1CF", "#DDBB9A"] },
  frost: { name: "Frost", icon: "❄️", colors: ["#E6F4FF", "#C4E1F7"] },
  dream: { name: "Dream", icon: "🌙", colors: ["#E6DCFF", "#C2AEF5"] },
  starry: { name: "Starry", icon: "✨", colors: ["#FFF5C7", "#F8D97A"] },
};

// rarity: 1 common, 2 uncommon, 3 rare, 4 legendary
export const RARITIES = {
  1: { name: "Common", color: "#9A7A90" },
  2: { name: "Uncommon", color: "#4FB892" },
  3: { name: "Rare", color: "#7B6CF6" },
  4: { name: "Legendary", color: "#E89B3C" },
};
export const stars = (r) => "★".repeat(r);

const LINES = [
  ["breeze", [["peepip", "Peepip", "🐣", null, "Hatched mid-semester. Peeps encouragingly whenever you open your laptop."],
              ["chirpette", "Chirpette", "🐥", "🎀", "Hums little tunes while you trace through a for-loop."],
              ["cloudove", "Cloudove", "🕊️", null, "Glides above your code and spots off-by-one errors from the sky."]]],
  ["splash", [["finnie", "Finnie", "🐟", null, "Swims in circles. Surprisingly good at detecting cycles."],
              ["coralette", "Coralette", "🐠", null, "Keeps a tidy reef sorted in ascending order."],
              ["tidalumi", "Tidalumi", "🐳", "✨", "A gentle giant who can hold an entire hash map in one breath."]]],
  ["ember", [["sizzlet", "Sizzlet", "🦎", null, "Its tail glows warmer each day of your streak."],
             ["drakelet", "Drakelet", "🐲", null, "Breathes tiny sparks that light up the right data structure."],
             ["emberwyrm", "Emberwyrm", "🐉", "🔥", "Legends say it once solved Merge k Sorted Lists in its sleep."]]],
  ["blossom", [["nibblet", "Nibblet", "🐛", null, "Munches through arrays one element at a time."],
               ["flutterine", "Flutterine", "🦋", null, "Flutters between two pointers until they meet."],
               ["petalfae", "Petalfae", "🧚", "🌸", "Sprinkles petals on every Accepted submission."]]],
  ["dream", [["mochikit", "Mochikit", "🐱", null, "Naps on your keyboard. Occasionally types valid Python."],
             ["velvetail", "Velvetail", "🐈", "🎀", "Knocks bugs off the table, one by one."],
             ["nocturna", "Nocturna", "🐈‍⬛", "🌙", "Only appears to those who practice late at night."]]],
  ["cocoa", [["pudgeon", "Pudgeon", "🐹", null, "Stuffs its cheeks with memoized results for later."],
             ["nutkin", "Nutkin", "🐿️", null, "Buries acorns in a perfectly balanced tree."],
             ["timberbelle", "Timberbelle", "🦫", "🎀", "Builds dams out of well-placed base cases."]]],
  ["frost", [["snowpip", "Snowpip", "🐧", null, "Waddles through linked lists, node by node."],
             ["sealumi", "Sealumi", "🦭", null, "Balances a stack on its nose — LIFO only!"],
             ["glacierbear", "Glacierbear", "🐻‍❄️", "❄️", "Calm, cool, and never panics on a Hard problem."]]],
  ["starry", [["bunbun", "Bunbun", "🐰", null, "Hops between recursion levels without ever getting lost."],
              ["hopsy", "Hopsy", "🐇", null, "Can jump to any index in O(1)."],
              ["cloverqueen", "Queen Clover", "🐇", "👑", "Rules the meadow with a lucky, logarithmic hop."]]],
  ["splash", [["ribbit", "Ribbit", "🐸", null, "Hops lily pad to lily pad — a natural at Jump Game."],
              ["croakette", "Croakette", "🐸", "🎀", "Sings a little song for every passing test case."],
              ["froggington", "Sir Froggington", "🐸", "👑", "A distinguished gentleman of dynamic programming."]]],
  ["breeze", [["puppuff", "Puppuff", "🐶", null, "Fetches your hints. Very good dog."],
              ["barkley", "Barkley", "🐕", null, "Sniffs out the shortest path in any graph."],
              ["moonhowl", "Moonhowl", "🐺", "🌙", "Howls once for each day of your streak."]]],
  ["cocoa", [["honeybun", "Honeybun", "🐻", null, "Sticky-sweet and stubbornly persistent."],
             ["teddiette", "Teddiette", "🧸", "🎀", "Gives the best hugs after a Wrong Answer."],
             ["pandarling", "Pandarling", "🐼", "✨", "Balances everything: work, rest, and red-black trees."]]],
  ["ember", [["foxling", "Foxling", "🦊", null, "Clever and curious — always asks \"what's the edge case?\""],
             ["vixette", "Vixette", "🦊", "🎀", "Outfoxes brute force with a single hash set."],
             ["kitsunova", "Kitsunova", "🦊", "✨", "Each of its tails holds a different sorting algorithm."]]],
  ["dream", [["fluffle", "Fluffle", "🐑", null, "Counting it helps you fall asleep. Counting with it helps you pass interviews."],
             ["cumulamb", "Cumulamb", "🐏", "☁️", "Floats on clouds of cozy, well-commented code."],
             ["dreamllama", "Dreamllama", "🦙", "💤", "Dreams in Big-O notation."]]],
];

const LEGENDARIES = [
  ["starry", ["aurorabelle", "Aurorabelle", "🦄", "🌈", "Appears only to coders who keep their promises to themselves."]],
  ["blossom", ["peacora", "Peacora", "🦚", null, "Its tail fans out into a perfect binary tree."]],
  ["splash", ["flamingala", "Flamingala", "🦩", null, "Stands on one leg for hours debugging. Very graceful."]],
  ["dream", ["jellumina", "Jellumina", "🪼", "✨", "Glows softly in the deep end of the call stack."]],
  ["frost", ["swanelle", "Swanelle", "🦢", "❄️", "Serene on the surface, furiously paddling recursion underneath."]],
  ["ember", ["pyrabelle", "Pyrabelle", "🐦‍🔥", null, "Rises from every broken streak, stronger than before."]],
  ["cocoa", ["bramblequill", "Bramblequill", "🦔", "🍂", "Curls into a ball around your hardest bugs until they give up."]],
];

function build() {
  const out = [];
  let n = 1;
  for (const [element, forms] of LINES) {
    forms.forEach(([id, name, emoji, accessory, flavor], i) => {
      out.push({ id, name, emoji, accessory, element, stage: i + 1, evolvesTo: forms[i + 1]?.[0] ?? null,
                 rarity: i + 1, flavor, dexNumber: n++ });
    });
  }
  for (const [element, [id, name, emoji, accessory, flavor]] of LEGENDARIES) {
    out.push({ id, name, emoji, accessory, element, stage: 0, evolvesTo: null, rarity: 4, flavor, dexNumber: n++ });
  }
  return out;
}

export const DEX = build();
export const DEX_BY_ID = Object.fromEntries(DEX.map((c) => [c.id, c]));
export const COPIES_TO_EVOLVE = 3;

/** Evolution lines are consecutive dex numbers in groups of 3; legendaries stand alone. */
export function lineOf(critter) {
  if (critter.stage === 0) return [critter];
  const start = Math.floor((critter.dexNumber - 1) / 3) * 3;
  return DEX.slice(start, start + 3);
}

// ---------------------------------------------------------------- packs

export const PACKS = {
  sprout: { name: "Sprout Pack", emoji: "🌱", howToEarn: "Solve a problem for the first time", cards: 3,
            colors: ["#C9F2DA", "#8ED9B0"], weights: [70, 22, 6.5, 1.5], guaranteedLast: 1, shiny: 1 / 20 },
  bloom: { name: "Bloom Pack", emoji: "🌷", howToEarn: "Hit your daily goal", cards: 4,
           colors: ["#FFC8DA", "#F58BB0"], weights: [62, 27, 9, 2], guaranteedLast: 2, shiny: 1 / 20 },
  starlight: { name: "Starlight Pack", emoji: "🌟", howToEarn: "Streak milestones & finishing a whole topic", cards: 5,
               colors: ["#D9CCFF", "#9C86F2"], weights: [50, 30, 15, 5], guaranteedLast: 3, shiny: 1 / 10 },
};
export const PACK_KINDS = ["sprout", "bloom", "starlight"];

function pickRarity(weights) {
  let x = Math.random() * weights.reduce((a, b) => a + b, 0);
  for (let i = 0; i < weights.length; i++) {
    if (x < weights[i]) return i + 1;
    x -= weights[i];
  }
  return 1;
}

const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

export function rollPack(kind) {
  const pack = PACKS[kind];
  return Array.from({ length: pack.cards }, (_, i) => {
    let rarity = pickRarity(pack.weights);
    if (i === pack.cards - 1 && rarity < pack.guaranteedLast) {
      rarity = kind === "starlight" && Math.random() < 0.25 ? 4 : pack.guaranteedLast;
    }
    const critter = pick(DEX.filter((c) => c.rarity === rarity));
    return { critter, shiny: Math.random() < pack.shiny };
  });
}
