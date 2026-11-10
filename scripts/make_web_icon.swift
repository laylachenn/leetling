// Renders the web app icons (full-bleed square: iOS and Android round the corners themselves).
// Run: swift scripts/make_web_icon.swift web/icons/icon-1024.png, then resize with sips (scripts/serve_web.sh does not need this).
import AppKit
import SwiftUI

struct Icon: View {
    var body: some View {
        ZStack {
            Rectangle()
                .fill(LinearGradient(colors: [Color(red: 1, green: 0.78, blue: 0.86), Color(red: 0.84, green: 0.77, blue: 1)],
                                     startPoint: .topLeading, endPoint: .bottomTrailing))
            Circle().fill(.white.opacity(0.55)).frame(width: 640, height: 640)
            Text("🐰").font(.system(size: 440)).offset(y: 12)
            Text("</>")
                .font(.system(size: 120, weight: .black, design: .rounded))
                .foregroundStyle(.white)
                .padding(.horizontal, 34).padding(.vertical, 8)
                .background(Capsule().fill(Color(red: 0.91, green: 0.39, blue: 0.56)))
                .offset(x: 200, y: 250)
            Text("✨").font(.system(size: 130)).offset(x: -250, y: -250)
        }
        .frame(width: 1024, height: 1024)
    }
}

let out = URL(fileURLWithPath: CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "icon_1024.png")
MainActor.assumeIsolated {
    let renderer = ImageRenderer(content: Icon())
    renderer.scale = 1
    guard let cg = renderer.cgImage else { fatalError("render failed") }
    let rep = NSBitmapImageRep(cgImage: cg)
    try! rep.representation(using: .png, properties: [:])!.write(to: out)
}
print("wrote \(out.path)")
