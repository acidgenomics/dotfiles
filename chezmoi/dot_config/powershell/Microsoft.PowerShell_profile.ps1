# Koopa activation for PowerShell.
$koopaDataHome = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME '.local/share' }
$koopaActivate = Join-Path $koopaDataHome 'koopa/activate.ps1'
if (Test-Path $koopaActivate) {
    . $koopaActivate
}
Remove-Variable koopaDataHome, koopaActivate -ErrorAction SilentlyContinue
