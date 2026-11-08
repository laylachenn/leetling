import SwiftUI

/// A stand-in for SwiftUI's `@State`.
///
/// With only the Command Line Tools installed (no Xcode), the SwiftUI macro plugin that
/// implements `@State` isn't available, so `@State` fails to compile. `@StateObject` is a
/// plain property wrapper and still works, so this wraps a value in a tiny ObservableObject.
/// Use it exactly like `@State`: `@Local private var isOn = false`, `$isOn` for a binding.
@propertyWrapper
struct Local<Value>: DynamicProperty {
    final class Box: ObservableObject {
        @Published var value: Value
        init(_ value: Value) { self.value = value }
    }

    @StateObject private var box: Box

    init(wrappedValue: Value) {
        _box = StateObject(wrappedValue: Box(wrappedValue))
    }

    var wrappedValue: Value {
        get { box.value }
        nonmutating set { box.value = newValue }
    }

    var projectedValue: Binding<Value> {
        let box = box
        return Binding(get: { box.value }, set: { box.value = $0 })
    }
}
