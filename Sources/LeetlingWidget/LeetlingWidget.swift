import LeetlingShared
import SwiftUI
import WidgetKit

struct StreakEntry: TimelineEntry {
    let date: Date
    let snapshot: LeetlingSnapshot
}

struct StreakProvider: TimelineProvider {
    func placeholder(in context: Context) -> StreakEntry {
        StreakEntry(date: Date(), snapshot: .placeholder)
    }

    func getSnapshot(in context: Context, completion: @escaping (StreakEntry) -> Void) {
        let snap = context.isPreview ? (LeetlingSnapshot.load() ?? .placeholder) : (LeetlingSnapshot.load() ?? LeetlingSnapshot())
        completion(StreakEntry(date: Date(), snapshot: snap))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<StreakEntry>) -> Void) {
        let snap = LeetlingSnapshot.load() ?? LeetlingSnapshot()
        let now = Date()
        let midnight = Calendar.current.startOfDay(for: now.addingTimeInterval(86_400))
        // Re-render right after midnight so the week shifts and the streak updates.
        let entries = [StreakEntry(date: now, snapshot: snap),
                       StreakEntry(date: midnight.addingTimeInterval(5), snapshot: snap)]
        completion(Timeline(entries: entries, policy: .after(midnight.addingTimeInterval(60))))
    }
}

struct SmallStreakView: View {
    let entry: StreakEntry

    var body: some View {
        let snap = entry.snapshot
        let streak = snap.streak(now: entry.date)
        let today = snap.todayCount(now: entry.date)
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text(snap.buddyEmoji).font(.system(size: 26))
                Spacer()
                HStack(spacing: 2) {
                    Image(systemName: "flame.fill").foregroundStyle(Theme.roseDeep)
                    Text("\(streak)").font(.system(size: 22, weight: .heavy, design: .rounded))
                }
                .foregroundStyle(Theme.plum)
            }
            Text(today >= snap.goal ? "Goal met! 💖" : "\(today)/\(snap.goal) today")
                .font(.system(size: 13, weight: .bold, design: .rounded))
                .foregroundStyle(Theme.plum)
            HStack(spacing: 4) {
                ForEach(snap.week(now: entry.date)) { day in
                    Circle()
                        .fill(day.goalMet ? Theme.roseDeep : day.done || day.mended ? Theme.rose.opacity(0.55) : Theme.plum.opacity(0.12))
                        .overlay(Circle().stroke(Theme.roseDeep, lineWidth: day.isToday ? 1.5 : 0))
                        .frame(width: 13, height: 13)
                }
            }
            Spacer(minLength: 0)
            Text(snap.packsWaiting > 0 ? "🎁 \(snap.packsWaiting) pack\(snap.packsWaiting == 1 ? "" : "s") waiting" : "\(snap.solvedTotal)/\(snap.totalProblems) solved")
                .font(.system(size: 11, weight: .semibold, design: .rounded))
                .foregroundStyle(Theme.mauve)
        }
    }
}

struct MediumStreakView: View {
    let entry: StreakEntry

    var body: some View {
        StreakCard(snapshot: entry.snapshot, now: entry.date, compact: true)
    }
}

struct LeetlingWidgetEntryView: View {
    @Environment(\.widgetFamily) var family
    let entry: StreakEntry

    var body: some View {
        Group {
            switch family {
            case .systemSmall: SmallStreakView(entry: entry)
            default: MediumStreakView(entry: entry)
            }
        }
        .widgetURL(URL(string: "leetling://today"))
        .containerBackground(for: .widget) {
            LinearGradient(colors: [Theme.cream, Color(hex: 0xFFF0F5)], startPoint: .top, endPoint: .bottom)
        }
    }
}

struct LeetlingStreakWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "LeetlingStreak", provider: StreakProvider()) { entry in
            LeetlingWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Leetling Streak")
        .description("Your daily LeetCode check-ins and streak 🔥")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

@main
struct LeetlingWidgets: WidgetBundle {
    var body: some Widget {
        LeetlingStreakWidget()
    }
}
