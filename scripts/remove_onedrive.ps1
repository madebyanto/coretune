# Script per la rimozione completa di OneDrive

Write-Host "Avvio rimozione OneDrive..."

# 1. Termina i processi OneDrive
Write-Host "Terminazione processi OneDrive..."
taskkill /f /im OneDrive.exe >$null 2>&1

# 2. Disinstalla OneDrive
Write-Host "Disinstallazione dell'applicazione OneDrive..."
$onedriveSetup = "$env:SystemRoot\SysWOW64\OneDriveSetup.exe"
if (-not (Test-Path $onedriveSetup)) {
    $onedriveSetup = "$env:SystemRoot\System32\OneDriveSetup.exe"
}

if (Test-Path $onedriveSetup) {
    & $onedriveSetup /uninstall
    Start-Sleep -Seconds 5 # Dai tempo alla disinstallazione di avviarsi
    Write-Host "Comando di disinstallazione OneDrive eseguito."
} else {
    Write-Host "OneDriveSetup.exe non trovato. Potrebbe essere già disinstallato o il percorso è diverso."
}

# 3. Rimuovi cartelle residue
Write-Host "Rimozione cartelle residue di OneDrive..."
Remove-Item "$env:LocalAppData\Microsoft\OneDrive" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:ProgramData\Microsoft OneDrive" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:SystemDrive\Users\*\OneDrive" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Rimozione OneDrive completata. Potrebbe essere necessario un riavvio per applicare tutte le modifiche."