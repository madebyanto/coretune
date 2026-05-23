# Recupera le app installate formattate per l'interfaccia
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Disabilita i colori ANSI per evitare caratteri invisibili che sfalsano il Substring
$env:NO_COLOR = 1 

# Esegue winget list. Usiamo --nowarn per pulire l'output da avvisi
$output = & winget list --accept-source-agreements --nowarn --source winget 2>$null
if ($null -eq $output -or $output.Count -lt 3) {
    # Fallback: riprova senza filtro sorgente se il primo fallisce
    $output = & winget list --accept-source-agreements --nowarn 2>$null
    if ($null -eq $output -or $output.Count -lt 3) { return }
}

# Cerchiamo la riga dei separatori
$sepIndex = -1
for ($i = 0; $i -lt $output.Count; $i++) {
    if ($output[$i] -match "^-+\s+-+") {
        $sepIndex = $i
        break
    }
}

if ($sepIndex -le 0) { return }

# Usiamo la riga dei separatori per capire dove inizia l'ID
$sepLine = $output[$sepIndex]
$idStart = $sepLine.IndexOf(" -") + 1
if ($idStart -le 0) { $idStart = $output[$sepIndex-1].IndexOf("ID") }

# Elaboriamo i dati
for ($i = $sepIndex + 1; $i -lt $output.Count; $i++) {
    $line = $output[$i]
    
    # Controlliamo che la riga sia lunga abbastanza e non sia una riga riassuntiva finale
    # (le righe valide avranno uno spazio in corrispondenza del break della colonna)
    if ($line.Length -gt $idStart -and $line[$idStart-1] -eq ' ') {
        $name = $line.Substring(0, $idStart).Trim()
        $id = ($line.Substring($idStart).Trim() -split "\s+")[0]
        
        if ($name -and $id -and $id -notmatch "^-+$") {
            # Usiamo Write-Output così l'interfaccia può catturare lo stream stdout più facilmente
            Write-Output "$name|$id"
        }
    }
}