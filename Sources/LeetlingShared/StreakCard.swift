import SwiftUI

/// The weekly check-in card (month + 7 days on top, a pastel row of checkmarks below).
/// Used by the medium widget, the app's Today screen and the desktop buddy.
public struct StreakCard: View {
    let snapshot: LeetlingSnapshot
    let now: Date
    let compact: Bool

    public init(snapshot: LeetlingSnapshot, now: Date = Date(), compact: Bool = false) {
        self.snapshot = snapshot
        self.now = now
        self.compact = compact
    }

    private var labelWidth: CGFloat { compact ? 74 : 96 }

    public var body: some View {
        let week = snapshot.week(now: now)
        let streak = snapshot.streak(now: now)
        VStack(spacing: compact ? 6 : 10) {
            // Header: month + day columns
            HStack(alignment: .bottom, spacing: 0) {
                Text(now.formatted(.dateTime.month(.wide)))
                    .font(.system(size: compact ? 13 : 17, weight: .bold, design: .rounded))
                    .foregroundStyle(Theme.plum)
                    .lineLimit(1)
                    // No minimumScaleFactor here: in offscreen renders (which is how widgets are drawn)
                    // it made the month name vanish entirely.
                    .fixedSize()
                    .frame(width: labelWidth, alignment: .leading)
                ForEach(week) { day in
                    VStack(spacing: 1) {
                        Text(day.dayNumber)
                            .font(.system(size: compact ? 10 : 12, weight: day.isToday ? .heavy : .medium, design: .rounded))
                        Text(day.weekdayShort)
                            .font(.system(size: compact ? 9 : 11, weight: day.isToday ? .heavy : .regular, design: .rounded))
                    }
                    .foregroundStyle(day.isToday ? Theme.roseDeep : Theme.mauve)
                    .frame(maxWidth: .infinity)
                }
            }

            // Pastel card: streak + checkmarks
            HStack(spacing: 0) {
                VStack(alignment: .leading, spacing: 2) {
                    HStack(spacing: 3) {
                        Image(systemName: "flame.fill")
                            .font(.system(size: compact ? 12 : 15, weight: .bold))
                            .foregroundStyle(streak > 0 ? Theme.roseDeep : Theme.mauve.opacity(0.6))
                        Text("\(streak)")
                            .font(.system(size: compact ? 17 : 22, weight: .heavy, design: .rounded))
                            .foregroundStyle(Theme.plum)
                            .contentTransition(.numericText())
                    }
                    Text("Leetling")
                        .font(.system(size: compact ? 11 : 13, weight: .semibold, design: .rounded))
                        .foregroundStyle(Theme.plum.opacity(0.8))
                }
                .frame(width: labelWidth - 10, alignment: .leading)
                .padding(.leading, 10)

                ForEach(week) { day in
                    DayMark(day: day, compact: compact)
                        .frame(maxWidth: .infinity)
                }
            }
            .padding(.vertical, compact ? 9 : 14)
            .background(
                RoundedRectangle(cornerRadius: compact ? 16 : 20, style: .continuous)
                    .fill(LinearGradient(colors: [Theme.blush, Theme.lilac], startPoint: .leading, endPoint: .trailing))
            )
        }
    }
}

struct DayMark: View {
    let day: DayCell
    let compact: Bool

    var body: some View {
        let size: CGFloat = compact ? 13 : 17
        Group {
            if day.goalMet {
                Image(systemName: "heart.fill")
                    .foregroundStyle(Theme.roseDeep)
            } else if day.done {
                Image(systemName: "checkmark")
                    .fontWeight(.heavy)
                    .foregroundStyle(Theme.plum)
            } else if day.mended {
                Image(systemName: "bandage.fill")
                    .foregroundStyle(Theme.rose)
            } else if day.isToday {
                Image(systemName: "circle.dashed")
                    .foregroundStyle(Theme.roseDeep.opacity(0.7))
            } else {
                Circle()
                    .fill(Theme.plum.opacity(0.15))
                    .frame(width: size * 0.35, height: size * 0.35)
            }
        }
        .font(.system(size: size))
        .frame(height: size + 2)
    }
}
