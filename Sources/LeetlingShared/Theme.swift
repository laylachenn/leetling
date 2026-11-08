import SwiftUI

/// Cozy pastel palette shared by the app and the widget.
public enum Theme {
    public static let rose = Color(hex: 0xFF8FB1)       // primary pink
    public static let roseDeep = Color(hex: 0xE8638F)   // pressed / emphasis
    public static let blush = Color(hex: 0xFFD6E2)
    public static let lavender = Color(hex: 0xC8B6FF)
    public static let lilac = Color(hex: 0xEEE6FF)
    public static let cream = Color(hex: 0xFFF8F1)
    public static let paper = Color(hex: 0xFFFDFB)
    public static let mint = Color(hex: 0xBDEFD9)
    public static let mintDeep = Color(hex: 0x4FB892)
    public static let peach = Color(hex: 0xFFD6A5)
    public static let butter = Color(hex: 0xFFF3B0)
    public static let sky = Color(hex: 0xBDE0FE)
    public static let plum = Color(hex: 0x4B2942)       // main text
    public static let mauve = Color(hex: 0x9A7A90)      // secondary text
    public static let berry = Color(hex: 0xD94F70)      // errors, gently

    public static let easy = Color(hex: 0x4FB892)
    public static let medium = Color(hex: 0xE89B3C)
    public static let hard = Color(hex: 0xE8638F)

    public static let backdrop = LinearGradient(
        colors: [Color(hex: 0xFFF1F5), Color(hex: 0xF6F0FF)],
        startPoint: .topLeading, endPoint: .bottomTrailing)

    public static let pinkGlow = LinearGradient(
        colors: [Color(hex: 0xFFB3C9), Color(hex: 0xD9C6FF)],
        startPoint: .topLeading, endPoint: .bottomTrailing)

    public static func difficultyColor(_ difficulty: String) -> Color {
        switch difficulty {
        case "Easy": return easy
        case "Medium": return medium
        default: return hard
        }
    }

    public static func rounded(_ style: Font.TextStyle, weight: Font.Weight = .regular) -> Font {
        .system(style, design: .rounded).weight(weight)
    }
}

public extension Color {
    init(hex: UInt32, opacity: Double = 1) {
        self.init(.sRGB,
                  red: Double((hex >> 16) & 0xFF) / 255,
                  green: Double((hex >> 8) & 0xFF) / 255,
                  blue: Double(hex & 0xFF) / 255,
                  opacity: opacity)
    }
}
