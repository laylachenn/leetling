// swift-tools-version:5.10
// Built with the Command Line Tools only (no Xcode needed): run scripts/build.sh.
import PackageDescription

let appExtensionSafe: [SwiftSetting] = [.unsafeFlags(["-application-extension"])]

let package = Package(
    name: "Leetling",
    platforms: [.macOS(.v14)],
    targets: [
        // Code shared by the app and the widget (snapshot format, theme, streak card).
        .target(
            name: "LeetlingShared",
            path: "Sources/LeetlingShared",
            swiftSettings: appExtensionSafe
        ),
        .executableTarget(
            name: "Leetling",
            dependencies: ["LeetlingShared"],
            path: "Sources/Leetling"
        ),
        // WidgetKit extension, bundled into Leetling.app/Contents/PlugIns by scripts/build.sh.
        .executableTarget(
            name: "LeetlingWidget",
            dependencies: ["LeetlingShared"],
            path: "Sources/LeetlingWidget",
            swiftSettings: appExtensionSafe,
            // Extensions must start in Apple's _NSExtensionMain (sets up the extension context, then
            // hands off to our @main WidgetBundle). Xcode does this automatically; we must do it by hand.
            linkerSettings: [.unsafeFlags(["-Xlinker", "-application_extension", "-Xlinker", "-e", "-Xlinker", "_NSExtensionMain"])]
        ),
    ],
    swiftLanguageVersions: [.v5]
)
