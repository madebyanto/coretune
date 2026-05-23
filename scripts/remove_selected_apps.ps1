# Script per la rimozione selettiva di Appx Packages

foreach ($app in $args) {
    Write-Host "Rimozione in corso: $app..."
    # Rimuove l'app per l'utente corrente e per tutti gli utenti
    Get-AppxPackage -Name $app -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
    
    # Rimuove il pacchetto provisioned (impedisce la reinstallazione automatica al nuovo login)
    Get-AppxProvisionedPackage -Online | Where-Object { $_.PackageName -like "*$app*" } | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue
}
Write-Host "Operazione di pulizia completata."