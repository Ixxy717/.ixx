# IXX Language — Notepad++ User Defined Language

Adds syntax highlighting for `.ixx` (IXX) source files in Notepad++.

> **Note:** Notepad++ UDL files use fixed hardcoded colors and do not
> automatically follow your editor theme. Import the file that matches
> the background you use.

## Which file to import

| Your Notepad++ theme | File to import         |
|----------------------|------------------------|
| Dark background      | `ixx-udl-dark.xml`     |
| Light background     | `ixx-udl-light.xml`    |

## Installation

1. Open **Notepad++**.
2. Go to **Language → User Defined Language → Define your language…**
3. Click **Import**.
4. Select the correct `.xml` file from this folder (dark or light).
5. Click **OK** and close the dialog.
6. **Restart Notepad++** if the language does not appear immediately.
7. Open any `.ixx` file — it should auto-detect as **IXX**.
8. If it does not auto-detect, go to **Language → IXX** to apply it manually.

## What is highlighted

| Token                                        | Dark theme     | Light theme    |
|----------------------------------------------|----------------|----------------|
| `# comment`                                  | Green          | Green          |
| `"string"`                                   | Orange         | Dark red       |
| `if`, `else`, `loop`, `function`, `return`   | Bold blue      | Bold blue      |
| `say`, `count`, `upper`, `color`, etc.       | Yellow-green   | Dark gold      |
| `and`, `or`, `not`                           | Purple         | Purple         |
| `is`, `less than`, `contains`, etc.          | Light blue     | Dark navy      |
| `YES`, `NO`, `yes`, `no`                     | Bold teal      | Bold teal      |
| `nothing`                                    | Teal           | Teal           |
| `---`, `--` (block markers)                  | Bold grey      | Bold grey      |
| `=`, `+`, `-`, `*`, `/`, `,`                 | White/grey     | Dark grey      |
| Numbers (`42`, `3.14`)                       | Light green    | Blue           |

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
