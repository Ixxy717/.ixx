# IXX Language — Notepad++ User Defined Language

Adds syntax highlighting for `.ixx` (IXX) source files in Notepad++.

## Installation

1. Open **Notepad++**.
2. Go to **Language → User Defined Language → Define your language…**
3. Click **Import**.
4. Select `ixx-udl.xml` from this folder.
5. Click **OK** and close the dialog.
6. **Restart Notepad++** if the language does not appear immediately.
7. Open any `.ixx` file — it should auto-detect as **IXX**.
8. If it does not auto-detect, go to **Language → IXX** to apply it manually.

## What is highlighted

| Token                         | Color        |
|-------------------------------|--------------|
| `# comment`                   | Green        |
| `"string"`                    | Orange       |
| `if`, `else`, `loop`          | Bold blue    |
| `say`                         | Yellow-green |
| `and`, `or`, `not`            | Purple       |
| `is less than more at …`      | Light blue   |
| `YES`, `NO`, `yes`, `no`      | Bold teal    |
| `---`, `--` (block markers)   | Bold grey    |
| `=`, `+`, `-`, `*`, `/`, `,`  | White/grey   |
| Numbers (`42`, `3.14`)        | Light green  |

Colors are styled to match a dark VS Code-like theme (VS Code Dark+).
If you prefer a light theme, re-import after editing the `fgColor`/`bgColor`
attributes in `ixx-udl.xml`.

## Notes

- `.ixx` may be detected as C++ in some tools. This UDL overrides that for
  Notepad++ by registering `ixx` as the file extension for the IXX language.
- String interpolation (`{name}` inside strings) is not separately coloured in
  the Notepad++ UDL — Notepad++ UDL does not support inline sub-patterns inside
  string delimiters. The entire string is highlighted as a string.
- Notepad++ UDL does not support a language server or diagnostics. For a richer
  editing experience, use the VS Code extension.

## Future roadmap (not yet implemented)

- Snippets / AutoComplete wordlist
- Formatter
- Language Server (LSP) — via VS Code only
