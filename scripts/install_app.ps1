param([string]$appId)
Write-Host "Installazione di $appId in corso..."
winget install --id $appId --silent --accept-package-agreements --accept-source-agreements