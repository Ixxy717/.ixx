# IXX Language — Notepad++ User Defined Language

Adds syntax highlighting for `.ixx` (IXX) source files in Notepad++.

> **Note:** Notepad++ UDL files use fixed hardcoded colors and do not
> automatically follow your editor theme. Import the file that matches
> your Notepad++ background.

## Which file to import

| Your Notepad++ background | File to import         | UDL name registered |
|---------------------------|------------------------|---------------------|
| Default / light (recommended) | `ixx-udl.xml`     | `IXX`               |
| Light (named variant)     | `ixx-udl-light.xml`    | `IXX Light`         |
| Dark Notepad++ theme      | `ixx-udl-dark.xml`     | `IXX Dark`          |

**Recommended:** Most Notepad++ installs use a light background. Import `ixx-udl.xml`.
It registers as `IXX`, auto-detects `.ixx` files, and uses light-safe colors (no black boxes).

Only import `ixx-udl-dark.xml` if you have set Notepad++ to a dark background theme.
It registers as `IXX Dark` and does **not** claim the `.ixx` extension automatically —
apply it manually via **Language → IXX Dark** when needed.

## Installation

1. Open **Notepad++**.
2. Go to **Language → User Defined Language → Define your language…**
3. Click **Import**.
4. Select the correct `.xml` file from this folder.
5. Click **OK** and close the dialog.
6. **Restart Notepad++** if the language does not appear immediately.
7. Open any `.ixx` file — `ixx-udl.xml` and `ixx-udl-light.xml` auto-detect `.ixx`.
   For the dark UDL, go to **Language → IXX Dark** to apply manually.

## Switching between light and dark

If you want to switch from one UDL to another:

1. Go to **Language → User Defined Language → Define your language…**
2. Select the old `IXX` (or `IXX Light`) entry.
3. Click **Remove**, then close.
4. Restart Notepad++.
5. Import the new UDL file.

Do not import both `ixx-udl.xml` and `ixx-udl-light.xml` at the same time —
they both claim the `ixx` extension and will conflict.

## What is highlighted

| Token                                        | Light / default        | Dark (`IXX Dark`)  |
|----------------------------------------------|------------------------|--------------------|
| `# comment`                                  | Dark green             | Green              |
| `"string"`                                   | Dark red               | Orange             |
| `if`, `else`, `loop`, `function`, `return`   | Bold blue              | Bold blue          |
| `say`, `count`, `upper`, `color`, etc.       | Dark gold              | Yellow-green       |
| `and`, `or`, `not`                           | Purple                 | Purple             |
| `is`, `less than`, `contains`, etc.          | Dark navy              | Light blue         |
| `YES`, `NO`, `yes`, `no`                     | Bold dark teal         | Bold teal          |
| `nothing`                                    | Dark teal              | Teal               |
| `---`, `--` (block markers)                  | Bold grey              | Bold grey          |
| `=`, `+`, `-`, `*`, `/`, `,`                 | Dark grey              | White/grey         |
| Numbers (`42`, `3.14`)                       | Blue                   | Light green        |

## Notes

- `.ixx` may be detected as C++ in some tools. This UDL overrides that for
  Notepad++ by registering `ixx` as the file extension for the IXX language.
- String interpolation (`{name}` inside strings) is not separately coloured —
  Notepad++ UDL does not support inline sub-patterns inside string delimiters.
  The entire string is highlighted as a string.
- Notepad++ UDL does not support a language server or diagnostics. For a richer
  editing experience, use the VS Code extension.
- VS Code and Cursor use `editor/vscode/syntaxes/ixx.tmLanguage.json`, which is
  theme-neutral — scope colours are handled automatically by your active theme.

## Future roadmap (not yet implemented)

- Snippets / AutoComplete wordlist
- Formatter
- Language Server (LSP) — via VS Code only
