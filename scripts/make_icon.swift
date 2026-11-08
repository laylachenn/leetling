// Renders Resources/AppIcon.icns. Run: swift scripts/make_icon.swift  (only needed if you change the icon)
import AppKit
import SwiftUI

struct Icon: View {
    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 230, style: .continuous)
                .fill(LinearGradient(colors: [Color(red: 1, green: 0.78, blue: 0.86), Color(red: 0.84, green: 0.77, blue: 1)],
                                     startPoint: .topLeading, endPoint: .bottomTrailing))
                .frame(width: 824, height: 824)
                .shadow(color: .black.opacity(0.18), radius: 24, y: 12)
            Circle().fill(.white.opacity(0.55)).frame(width: 560, height: 560)
            Text("🐰").font(.system(size: 400)).offset(y: 10)
            Text("</>")
                .font(.system(size: 120, weight: .black, design: .rounded))
                .foregroundStyle(.white)
                .padding(.horizontal, 34).padding(.vertical, 8)
                .background(Capsule().fill(Color(red: 0.91, green: 0.39, blue: 0.56)))
                .offset(x: 230, y: 270)
            Text("✨").font(.system(size: 130)).offset(x: -270, y: -260)
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
