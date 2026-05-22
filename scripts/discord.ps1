$paths = @(
"$env:AppData\Discord\Cache",
"$env:AppData\Discord\Code Cache",
"$env:AppData\Discord\GPUCache"
)

foreach ($p in $paths) {
    if (Test-Path $p) {
        Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
    }
}

taskkill /f /im Discord.exe >$null 2>&1
Write-Host "Discord cleaned"