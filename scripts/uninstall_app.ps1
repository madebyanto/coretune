param([string]$appId)
Write-Host "Disinstallazione di $appId..."
winget uninstall --id $appId --silent --accept-source-agreements --force

# Pulizia residui profonda (AppData)
# Cerchiamo sia sotto l'editore che sotto il nome dell'app
$parts = $appId -split '\.'
if ($parts.Count -ge 2) {
    $publisher = $parts[0]
    $appName = $parts[-1]
} else {
    $publisher = ""
    $appName = $appId
}

$paths = @(
    "$env:AppData\$appName",
    "$env:LocalAppData\$appName",
    "$env:ProgramData\$appName",
    "$env:AppData\$publisher\$appName",
    "$env:LocalAppData\$publisher\$appName"
)

foreach ($p in $paths) {
    if ($p -match "\w" -and (Test-Path $p)) {
        Write-Host "Rimozione residui in $p..."
        Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "Disinstallazione e pulizia completata."