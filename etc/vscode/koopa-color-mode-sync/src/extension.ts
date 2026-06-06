import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import * as vscode from "vscode";

function writeColorMode(kind: vscode.ColorThemeKind): void {
    const mode =
        kind === vscode.ColorThemeKind.Light ||
        kind === vscode.ColorThemeKind.HighContrastLight
            ? "light"
            : "dark";
    const cacheDir = path.join(os.homedir(), ".cache", "koopa");
    fs.mkdirSync(cacheDir, { recursive: true });
    fs.writeFileSync(path.join(cacheDir, "color-mode"), mode + "\n");
}

export function activate(context: vscode.ExtensionContext): void {
    writeColorMode(vscode.window.activeColorTheme.kind);
    context.subscriptions.push(
        vscode.window.onDidChangeActiveColorTheme((theme) => {
            writeColorMode(theme.kind);
        }),
    );
}

export function deactivate(): void {}
