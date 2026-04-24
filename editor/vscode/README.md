# IXX Language — VS Code Extension

Adds syntax highlighting for `.ixx` (IXX) source files in Visual Studio Code.

## What it does

- Registers `.ixx` as the **IXX** language (not C++)
- Highlights comments, strings, keywords, booleans, numbers, and operators
- Highlights string interpolation (`{name}` inside double-quoted strings)
- Configures `#` as the line comment character
- Auto-closes double quotes

## Why `.ixx`?

Some editors detect `.ixx` as a C++20 module interface file. This extension
explicitly overrides that association and registers `.ixx` as IXX.

## Installation (local / development)

### Option A — Copy to VS Code extensions folder

1. Copy the `editor/vscode/` folder to your VS Code extensions directory:
   - **Windows**: `%USERPROFILE%\.vscode\extensions\ixx-language`
   - **macOS / Linux**: `~/.vscode/extensions/ixx-language`
2. Copy the icon files (see below).
3. Restart VS Code.
4. Open any `.ixx` file — it will be highlighted as IXX.

### Option B — Install with the CLI

```
code --install-extension editor/vscode
```

### Icon setup

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

If the `icons/` folder does not exist or the icon files are missing, VS Code
will use its default generic file icon. The extension still works correctly.

## Syntax highlighting reference

| Token               | Scope                            |
|---------------------|----------------------------------|
| `# comment`         | `comment.line.number-sign.ixx`   |
| `"string"`          | `string.quoted.double.ixx`       |
| `{interpolation}`   | `variable.other.interpolated.ixx`|
| `say`               | `support.function.builtin.ixx`   |
| `if else loop`      | `keyword.control.ixx`            |
| `and or not`        | `keyword.operator.logical.ixx`   |
| `is less than …`    | `keyword.operator.comparison.ixx`|
| `YES NO yes no`     | `constant.language.boolean.ixx`  |
| `42`, `3.14`        | `constant.numeric.ixx`           |
| `=`                 | `keyword.operator.assignment.ixx`|
| `+ - * /`           | `keyword.operator.arithmetic.ixx`|
| `- -- ---`          | `punctuation.definition.block.ixx`|

## Future roadmap (not yet implemented)

- Snippets (common IXX patterns)
- Formatter
- Diagnostics / error squiggles
- Language Server Protocol (LSP)
- Hover documentation
- Command guidance inside the editor
