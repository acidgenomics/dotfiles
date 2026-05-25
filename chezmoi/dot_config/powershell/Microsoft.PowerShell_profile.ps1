# Koopa activation for PowerShell.
$koopaDataHome = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME '.local/share' }
$koopaActivate = Join-Path $koopaDataHome 'koopa/activate.ps1'
if (Test-Path $koopaActivate) {
    . $koopaActivate
}
Remove-Variable koopaDataHome, koopaActivate -ErrorAction SilentlyContinue

if (Get-Module -ListAvailable -Name PSReadLine) {
    Set-PSReadLineOption -Colors @{
        Command   = '#50fa7b'
        Parameter = '#ffb86c'
        String    = '#f1fa8c'
        Operator  = '#ff79c6'
        Variable  = '#bd93f9'
        Comment   = '#6272a4'
        Keyword   = '#8be9fd'
        Error     = '#ff5555'
        Type      = '#8be9fd'
        Number    = '#bd93f9'
    }
}
