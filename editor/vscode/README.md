# IXX Language — VS Code Extension

Adds syntax highlighting and **live diagnostics** for `.ixx` (IXX) source files in Visual Studio Code.

## What it does

- Registers `.ixx` as the **IXX** language (not C++)
- Highlights comments, strings, keywords, booleans, numbers, and operators
- Highlights string interpolation (`{name}` inside double-quoted strings)
- Configures `#` as the line comment character
- Auto-closes double quotes
- **Live diagnostics** — red squiggles and Problems panel entries for syntax and semantic errors

## Diagnostics

The extension runs `ixx check <file> --json` whenever you open, save, or edit
an `.ixx` file and maps any returned errors to VS Code diagnostics.

**Diagnostics require the IXX CLI to be installed:**

```
pip install --upgrade ixx
```

After installing, `ixx` must be on your PATH. You can verify with:

```
ixx version
```

### What is checked

| Error type | Example |
|---|---|
| Syntax error | `if age less than` (missing value) |
| Wrong argument count (user function) | `add(1)` when `add` expects 2 args |
| Unknown function call | `missingfunction()` |
| Wrong argument count (built-in) | `upper("hello", "extra")` |
| Undefined variable (obvious cases) | `say ghost` |

### How triggers work

| Event | Behavior |
|---|---|
| File open | Full check runs immediately |
| File save | Full check runs immediately |
| Active editor change | Full check runs |
| Text change | Check runs after `debounceMs` (default 500ms), reads the **saved** file |

> **Note:** On text change, `ixx check` reads from disk. Unsaved edits are
> checked against the last saved version. Save the file to get current results.

## Settings

| Setting | Default | Description |
|---|---|---|
| `ixx.diagnostics.enabled` | `true` | Enable/disable IXX diagnostics |
| `ixx.diagnostics.onChange` | `true` | Re-run on text change (debounced) |
| `ixx.diagnostics.debounceMs` | `500` | Debounce delay in milliseconds |
| `ixx.diagnostics.command` | `"ixx"` | Path to IXX CLI (override if not on PATH) |

### Custom CLI path example

If `ixx` is not on PATH (e.g., installed in a virtual environment):

```json
{
  "ixx.diagnostics.command": "C:\\Python312\\Scripts\\ixx.exe"
}
```

## Installation (local / development)

### Option A — Copy to VS Code extensions folder

1. Build the extension first (see below).
2. Copy the `editor/vscode/` folder to your VS Code extensions directory:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\ixx-language`
   - **macOS / Linux**: `~/.vscode/extensions/ixx-language`
3. Restart VS Code.

### Option B — Install VSIX

```
code --install-extension ixx-language-0.6.0.vsix
```

### Building from source

```
cd editor/vscode
npm install
npm run compile
```

To package as a VSIX (requires `vsce`):

```
npm install -g @vscode/vsce
vsce package
```

## Icon setup

The extension expects icons at `editor/vscode/icons/`:

```
editor/vscode/icons/
  ixx-icon-32.png   (used for file icon in the editor tab / explorer)
  ixx-icon-128.png  (used as the extension icon)
```

To generate these icons:

1. Place your source image at `assets/ixx-icon-source.png` (673x673 PNG).
2. Install Pillow: `pip install Pillow`
3. Run: `python assets/generate_icons.py`
4. Copy the generated files:

```
copy assets\generated\ixx-icon-32.png  editor\vscode\icons\ixx-icon-32.png
copy assets\generated\ixx-icon-128.png editor\vscode\icons\ixx-icon-128.png
```

## Syntax highlighting reference

| Token               | Scope                             |
|---------------------|-----------------------------------|
| `# comment`         | `comment.line.number-sign.ixx`    |
| `"string"`          | `string.quoted.double.ixx`        |
| `{interpolation}`   | `variable.other.interpolated.ixx` |
| `say`               | `support.function.builtin.ixx`    |
| `if else loop`      | `keyword.control.ixx`             |
| `and or not`        | `keyword.operator.logical.ixx`    |
| `is less than …`    | `keyword.operator.comparison.ixx` |
| `YES NO yes no`     | `constant.language.boolean.ixx`   |
| `42`, `3.14`        | `constant.numeric.ixx`            |
| `=`                 | `keyword.operator.assignment.ixx` |
| `+ - * /`           | `keyword.operator.arithmetic.ixx` |
| `- -- ---`          | `punctuation.definition.block.ixx`|
