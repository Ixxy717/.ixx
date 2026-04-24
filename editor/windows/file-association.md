# Windows File Association for `.ixx`

This document explains how to associate `.ixx` files with an editor and/or
apply the IXX file icon on Windows. All steps are **manual and optional**.
IXX does not automatically modify the Windows registry or force file associations.

---

## Background: `.ixx` and C++ conflict

The `.ixx` extension is also used by C++20 module interface files. Some tools
(Visual Studio, Windows Explorer, some shells) may detect `.ixx` as a C++ file.

Our editor integrations explicitly override this:

- **VS Code extension** (`editor/vscode/`) registers `.ixx` as IXX, not C++.
- **Notepad++ UDL** (`editor/notepad-plus-plus/ixx-udl.xml`) registers `.ixx`
  as IXX within Notepad++.

If you open a `.ixx` file in VS Code or Notepad++ with the respective support
installed, it will be highlighted as IXX regardless of what Windows thinks.

---

## Associating `.ixx` with VS Code

1. Right-click any `.ixx` file in Windows Explorer.
2. Choose **Open with → Choose another app**.
3. Select **Visual Studio Code**.
4. Check **Always use this app to open `.ixx` files**.
5. Click **OK**.

VS Code will use the IXX extension to highlight the file correctly once the
extension is installed.

---

## Associating `.ixx` with Notepad++

1. Right-click any `.ixx` file in Windows Explorer.
2. Choose **Open with → Choose another app**.
3. Select **Notepad++**.
4. Check **Always use this app to open `.ixx` files**.
5. Click **OK**.

Notepad++ will use the IXX UDL once it has been imported (see
`editor/notepad-plus-plus/README.md`).

---

## Applying the IXX file icon

Windows displays a file icon based on the program associated with the extension.
To use a custom IXX icon:

### Prerequisites

Generate the icon first:

```
pip install Pillow
python assets/generate_icons.py
```

This produces `assets/generated/ixx-icon.ico` (multi-size Windows ICO).

### Manual icon registration (advanced)

> **Warning**: Editing the Windows registry is irreversible if done incorrectly.
> Back up the registry before making any changes.

1. Open **Registry Editor** (`regedit.exe`).
2. Navigate to:
   ```
   HKEY_CLASSES_ROOT\.ixx
   ```
   If this key does not exist, create it as a String Value with data `ixx_file`.
3. Navigate to (create if missing):
   ```
   HKEY_CLASSES_ROOT\ixx_file
   ```
4. Create a subkey `DefaultIcon`.
5. Set the `(Default)` value to the full path of the ICO file:
   ```
   C:\path\to\IXX\assets\generated\ixx-icon.ico,0
   ```
6. Run the following command to refresh the icon cache:
   ```
   ie4uinit.exe -show
   ```
   or log out and log back in.

### Alternative: Use the editor's icon

If you associate `.ixx` with VS Code, Windows will use the VS Code icon for
`.ixx` files. The IXX VS Code extension can display the IXX icon in the editor
tab and file explorer, but Windows Explorer will still show the VS Code icon
unless you apply the custom icon via the registry as described above.

---

## What is NOT done automatically

- IXX does **not** modify the Windows registry during installation.
- IXX does **not** force a file association.
- IXX does **not** add `.ixx` to the Windows "Open with" list automatically.
- All of the above are intentional. File association changes are user-controlled.

---

## Icon asset locations

| File                                | Purpose                          |
|-------------------------------------|----------------------------------|
| `assets/ixx-icon-source.png`        | Source image (673×673)           |
| `assets/generated/ixx-icon-32.png`  | VS Code file icon                |
| `assets/generated/ixx-icon-128.png` | VS Code extension icon           |
| `assets/generated/ixx-icon.ico`     | Windows ICO (multi-size)         |

Run `python assets/generate_icons.py` to generate all sizes from the source.

---

## Future roadmap

- NSIS / WiX installer that optionally registers the file association
- VS Code extension published to marketplace (icon bundled)
- Automatic icon refresh after generation
