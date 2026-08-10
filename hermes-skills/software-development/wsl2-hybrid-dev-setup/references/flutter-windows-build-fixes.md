# Flutter Windows Build — Common Fixes for ParanoidX Hybrid Setup

## Context
When building Flutter apps (The-Isle, Royal-Isle) on Windows in the WSL2 Hybrid setup, shared Go models are used via path dependencies (`../shared/models`). This document captures the common build errors and their fixes.

## Prerequisites
1. **Flutter 3.x** with Windows desktop support: `flutter config --enable-windows-desktop`
2. **Visual Studio 2022 Community** with "Desktop development with C++" workload
3. **Windows Developer Mode** enabled (Settings → Privacy & security → For developers)

## Shared Model Path Issues

### Problem
Flutter projects reference shared models via relative paths that break when copied from WSL2 to Windows.

### Fix
Update `pubspec.yaml` in both Flutter projects:
```yaml
dependencies:
  models:
    path: ../shared/models  # From The-Isle/ or Royal-Isle/
```
Note: From `C:\Users\tomas\The-Isle\`, the path is `..\shared\models` (one level up, not two).

## Common Build Errors & Fixes

### 1. `Unable to find suitable Visual Studio toolchain`
**Fix**: Install Visual Studio 2022 Community with "Desktop development with C++" workload.

### 2. `Building with plugins requires symlink support`
**Fix**: Enable Developer Mode in Windows Settings → Privacy & security → For developers.

### 3. Missing `encrypt` package for AES encryption
**Error**: `Type 'Key' not found` / `Encrypter` / `AES` / `IV` / `Encrypted` undefined
**Fix**: Add to `pubspec.yaml`:
```yaml
dependencies:
  encrypt: ^5.0.3
```
Then run `flutter pub get`.

### 4. `pointycastle` type errors
**Errors**:
- `The argument type 'List<int>' can't be assigned to 'Uint8List'`
- `Digest` type not assignable to `List<int>`
- `asUint8List()` not defined

**Fixes**:
```dart
// Instead of: final hash = sha256.convert(data); hex.encode(hash)
// Use:
final hash = sha256.convert(data);
hex.encode(hash.bytes)  // Use .bytes instead of implicit conversion

// For Uint8List:
Uint8List.fromList(hash.bytes)
Uint8List.fromList(utf8.encode(string))
Uint8List.fromList(xKey.privateKey!)  // instead of xKey.privateKey!.asUint8List()

// ChaCha20Poly1305 constructor:
final cipher = ChaCha20Poly1305(ChaCha7539Engine(), Poly1305());
```

### 5. Missing State classes in screen widgets
**Error**: `_LockScreenState` / `_RegistrationScreenState` / etc. not defined
**Fix**: Ensure each `StatefulWidget` has its corresponding `State` class:
```dart
class LockScreen extends StatefulWidget {
  const LockScreen({...});
  @override
  State<LockScreen> createState() => _LockScreenState();
}

class _LockScreenState extends State<LockScreen> {
  // implementation
}
```

### 6. Duplicate imports and syntax errors from sed/automated edits
**Problem**: Multiple `import` statements, duplicate class declarations, missing semicolons
**Fix**: Clean up imports and ensure proper Dart syntax:
```dart
// Single import block at top
import 'package:flutter/material.dart';
import 'package:models/models.dart' as models;
import '../services/identity_service.dart';
// ... other imports

// Single class definition
class ProfileInfo { ... }

// Single StatefulWidget
class RegistrationScreen extends StatefulWidget { ... }
class _RegistrationScreenState extends State<RegistrationScreen> { ... }
```

### 7. `flutter create --platforms=windows .` fails or creates conflicts
**Fix**: Run before building:
```bash
flutter create --platforms=windows .
flutter pub get
flutter build windows --release
```

### 8. Dependencies resolution fails due to path conflicts
**Problem**: `models` package referenced from both WSL2 and Windows paths
**Fix**: Ensure Windows Flutter projects point to Windows-side copy:
```bash
# Copy shared models to Windows
cp -r ~/shared/models /mnt/c/Users/tomas/shared
# In Flutter project pubspec.yaml:
# path: ../shared/models  (relative to C:\Users\tomas\The-Isle\)
```

## Additional Errors & Fixes (Session 2026-08-05)

### 9. ElevatedButton `label:` vs `child:`
**Error**: `No named parameter with the name 'label'`
**Fix**: Use `child:` instead of `label:`:
```dart
// WRONG
ElevatedButton(label: const Text('Click'), onPressed: ...)

// CORRECT
ElevatedButton(
  onPressed: ...,
  child: const Text('Click'),
)
```

### 10. ElevatedButton `label:` with loading state
**Error**: `No named parameter with the name 'label'`
**Fix**: Use conditional `child:`:
```dart
ElevatedButton(
  onPressed: _loading ? null : _saveProfile,
  child: _loading
      ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
      : const Text('Complete Setup'),
  style: ElevatedButton.styleFrom(
    backgroundColor: RoyalTheme.gold,
    foregroundColor: Colors.black,
    minimumSize: const Size(280, 56),
  ),
)
```

### 11. `Random.shuffle()` on Random instance
**Error**: `The method 'shuffle' isn't defined for the type 'Random'`
**Fix**: Shuffle a list, not the Random object:
```dart
// WRONG
(Random()...shuffle(List.generate(24, (i) => i))).take(3).toList()

// CORRECT
final indices = List.generate(24, (i) => i);
indices.shuffle(Random());
final verifyIndices = indices.take(3).toList()
```

### 12. Animated Widget `.animate()` missing
**Error**: `The method 'animate' isn't defined for the type 'Icon'`
**Cause**: Missing `flutter_animate` import or package
**Fix**: Add to `pubspec.yaml`:
```yaml
dependencies:
  flutter_animate: ^4.5.0
```
And import:
```dart
import 'package:flutter_animate/flutter_animate.dart';
```

### 13. Identity Service Duplicate Methods
**Error**: Duplicate `getIdentity` method in `identity_service.dart`
**Fix**: Remove duplicate method, ensure single implementation with correct return type.

### 14. SecurePrefs verifyIdentity Method Missing
**Error**: `The method 'verifyIdentity' isn't defined for the type 'SecureIdentityService'`
**Fix**: Replace with direct call to `identity.verifyMnemonic()`:
```dart
// In SecurePrefs.verifyMnemonic()
final identity = await service.getIdentity(identityId);
if (identity == null) return false;
return identity.verifyMnemonic(mnemonic, passphrase: passphrase);
```

### 15. Welcome Screen Restore Identity Parameter
**Error**: `Too many positional arguments: 0 allowed, but 1 found`
**Fix**: Use named parameter:
```dart
// WRONG
await identityService.restoreIdentity(words.join(' '))

// CORRECT
await identityService.restoreIdentity(mnemonic: words.join(' '))
```

### 16. Registration Screen State Classes Missing
**Error**: `_RegistrationScreenState` / `_ProfileSelectionScreenState` not defined
**Fix**: Ensure each StatefulWidget has complete State class with all methods.

### 17. Random.shuffle() on Random instance (another occurrence)
**Error**: `The method 'shuffle' isn't defined for the type 'Random'`
**Fix**: Use list.shuffle() pattern as shown in #11.

### 18. TextField `.animate()` on Container
**Error**: `The method 'animate' isn't defined for the type 'Container'`
**Fix**: Remove `.animate()` calls or wrap in proper AnimatedWidget.

### 19. Identity Service Duplicate Methods
**Error**: Duplicate `getIdentity` method in `identity_service.dart`
**Fix**: Remove duplicate method, ensure single implementation with correct return type.

### 20. SecurePrefs verifyIdentity Method Missing
**Error**: `The method 'verifyIdentity' isn't defined for the type 'SecureIdentityService'`
**Fix**: Replace with direct call to `identity.verifyMnemonic()`:
```dart
// In SecurePrefs.verifyMnemonic()
final identity = await service.getIdentity(identityId);
if (identity == null) return false;
return identity.verifyMnemonic(mnemonic, passphrase: passphrase);
```

### 21. Welcome Screen Restore Identity Parameter
**Error**: `Too many positional arguments: 0 allowed, but 1 found`
**Fix**: Use named parameter:
```dart
// WRONG
await identityService.restoreIdentity(words.join(' '))

// CORRECT
await identityService.restoreIdentity(mnemonic: words.join(' '))
```

### 22. Registration Screen State Classes Missing
**Error**: `_RegistrationScreenState` / `_ProfileSelectionScreenState` not defined
**Fix**: Ensure each StatefulWidget has complete State class with all methods.

### 23. Random.shuffle() on Random instance (another occurrence)
**Error**: `The method 'shuffle' isn't defined for the type 'Random'`
**Fix**: Use list.shuffle() pattern as shown in #11.

### 24. TextField `.animate()` on Container
**Error**: `The method 'animate' isn't defined for the type 'Container'`
**Fix**: Remove `.animate()` calls or wrap in proper AnimatedWidget.

## Build Commands
```bash
# In each Flutter project directory (PowerShell)
cd C:\Users\tomas\The-Isle
flutter pub get
flutter create --platforms=windows .
flutter build windows --release

cd C:\Users\tomas\Royal-Isle
flutter pub get
flutter create --platforms=windows .
flutter build windows --release
```

## Output Locations
- `The-Isle`: `build/windows/x64/runner/Release/isle_app.exe`
- `Royal-Isle`: `build/windows/x64/runner/Release/royal_app.exe`

## Verification
```powershell
# Check both apps launch
Start-Process "C:\Users\tomas\The-Isle\build\windows\x64\runner\Release\isle_app.exe"
Start-Process "C:\Users\tomas\Royal-Isle\build\windows\x64\runner\Release\royal_app.exe"

# Verify processes
Get-Process isle_app, royal_app | Select-Object ProcessName, Id, WorkingSet
```

## Session Notes (2026-08-05)
- Fixed identity_service.dart: removed duplicate `getIdentity` method, fixed `asUint8List()` calls
- Fixed secure_prefs.dart: replaced `verifyIdentity` with direct `identity.verifyMnemonic()` call
- Fixed welcome_screen.dart: changed positional arg to named `mnemonic:` parameter
- Fixed screen widget State classes that were missing
- Added `encrypt: ^5.0.3` to Royal-Isle pubspec.yaml
- Regenerated 4096-bit RSA certs for SMP server
- Fixed ElevatedButton `label:` to `child:` usage
- Fixed `Random.shuffle()` pattern
- Fixed `flutter_animate` import