/**
 * IXX Language Extension — diagnostics provider.
 *
 * Runs `ixx check <file> --json` on every .ixx document and maps the
 * returned errors to VS Code Diagnostic objects (red squiggles / Problems).
 *
 * Trigger events:
 *   - document open
 *   - document save
 *   - active editor change
 *   - text change (debounced, checks saved file on disk)
 *
 * Note: `ixx check --json` always reads from disk, so onChange diagnostics
 * reflect the last saved state of the file, not the unsaved buffer.
 */

import * as vscode from 'vscode';
import { execFile } from 'child_process';

// ── module-level state ────────────────────────────────────────────────────────

let diagnosticCollection: vscode.DiagnosticCollection;
let debounceTimer: ReturnType<typeof setTimeout> | undefined;

/** Shown at most once per session to avoid spamming. */
let cliMissingWarned = false;

// ── IXX JSON output types ─────────────────────────────────────────────────────

interface IxxError {
  file:     string;
  line:     number | null;
  column:   number | null;
  severity: string;
  message:  string;
}

interface IxxCheckResult {
  ok:     boolean;
  file:   string;
  errors: IxxError[];
}

// ── extension lifecycle ───────────────────────────────────────────────────────

export function activate(context: vscode.ExtensionContext): void {
  diagnosticCollection = vscode.languages.createDiagnosticCollection('ixx');
  context.subscriptions.push(diagnosticCollection);

  // Check all already-open IXX documents immediately.
  vscode.workspace.textDocuments.forEach(doc => {
    if (doc.languageId === 'ixx') {
      runCheck(doc);
    }
  });

  // On document open.
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(doc => {
      if (doc.languageId === 'ixx') {
        runCheck(doc);
      }
    })
  );

  // On document save.
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(doc => {
      if (doc.languageId === 'ixx') {
        runCheck(doc);
      }
    })
  );

  // On active editor change.
  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(editor => {
      if (editor && editor.document.languageId === 'ixx') {
        runCheck(editor.document);
      }
    })
  );

  // On text change (debounced — checks the file as saved on disk).
  context.subscriptions.push(
    vscode.workspace.onDidChangeTextDocument(event => {
      const doc = event.document;
      if (doc.languageId !== 'ixx') {
        return;
      }
      const config = getConfig();
      if (!config.onChange) {
        return;
      }
      if (debounceTimer !== undefined) {
        clearTimeout(debounceTimer);
      }
      debounceTimer = setTimeout(() => {
        runCheck(doc);
        debounceTimer = undefined;
      }, config.debounceMs);
    })
  );

  // Clear diagnostics when a document is closed.
  context.subscriptions.push(
    vscode.workspace.onDidCloseTextDocument(doc => {
      diagnosticCollection.delete(doc.uri);
    })
  );
}

export function deactivate(): void {
  if (debounceTimer !== undefined) {
    clearTimeout(debounceTimer);
  }
}

// ── configuration helper ──────────────────────────────────────────────────────

interface IxxConfig {
  enabled:    boolean;
  onChange:   boolean;
  debounceMs: number;
  command:    string;
}

function getConfig(): IxxConfig {
  const cfg = vscode.workspace.getConfiguration('ixx');
  return {
    enabled:    cfg.get<boolean>('diagnostics.enabled',    true),
    onChange:   cfg.get<boolean>('diagnostics.onChange',   true),
    debounceMs: cfg.get<number> ('diagnostics.debounceMs', 500),
    command:    cfg.get<string> ('diagnostics.command',    'ixx'),
  };
}

// ── diagnostics runner ────────────────────────────────────────────────────────

function runCheck(document: vscode.TextDocument): void {
  const config = getConfig();

  if (!config.enabled) {
    diagnosticCollection.set(document.uri, []);
    return;
  }

  // Unsaved untitled buffers have no disk path — skip them.
  if (document.uri.scheme !== 'file') {
    return;
  }

  const filePath = document.uri.fsPath;

  // On Windows, wrappers installed by pip are .cmd scripts and require a shell.
  const useShell = process.platform === 'win32';

  execFile(
    config.command,
    ['check', filePath, '--json'],
    { timeout: 10_000, shell: useShell },
    (err, stdout, _stderr) => {

      // ENOENT means the binary wasn't found at all.
      if ((err as NodeJS.ErrnoException)?.code === 'ENOENT') {
        if (!cliMissingWarned) {
          cliMissingWarned = true;
          vscode.window.showWarningMessage(
            'IXX: CLI not found. Install with:  pip install --upgrade ixx  ' +
            '— or set ixx.diagnostics.command in your VS Code settings.'
          );
        }
        return;
      }

      // Non-zero exit with no stdout means an unexpected crash.
      const output = stdout?.trim();
      if (!output) {
        return;
      }

      let result: IxxCheckResult;
      try {
        result = JSON.parse(output) as IxxCheckResult;
      } catch {
        // Not valid JSON — ignore silently (don't spam with errors).
        return;
      }

      if (result.ok) {
        diagnosticCollection.set(document.uri, []);
        return;
      }

      const diagnostics: vscode.Diagnostic[] = [];
      for (const error of result.errors ?? []) {
        // IXX reports 1-based lines/columns; VS Code uses 0-based.
        const line   = Math.max(0, (error.line   ?? 1) - 1);
        const column = Math.max(0, (error.column ?? 1) - 1);

        const range = new vscode.Range(line, column, line, column + 1);

        const severity =
          error.severity === 'warning'
            ? vscode.DiagnosticSeverity.Warning
            : vscode.DiagnosticSeverity.Error;

        const diag    = new vscode.Diagnostic(range, error.message, severity);
        diag.source   = 'ixx';
        diagnostics.push(diag);
      }

      diagnosticCollection.set(document.uri, diagnostics);
    }
  );
}
