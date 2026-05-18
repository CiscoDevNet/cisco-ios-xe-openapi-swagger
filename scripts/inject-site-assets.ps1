$pages = @('index.html','code-generator.html','yang-accountability.html','yang-accountability-compare.html','tree-compare.html','telemetry.html','exports.html')
$inject = "<link rel=`"stylesheet`" href=`"assets/css/site.css`">`r`n<script src=`"assets/js/site-chrome.js`" defer></script>`r`n"
$enc = New-Object System.Text.UTF8Encoding($false)  # UTF-8 without BOM
$root = Split-Path -Parent $PSScriptRoot
foreach ($p in $pages) {
    $full = Join-Path $root $p
    if (-not (Test-Path $full)) { Write-Host "$p : not found"; continue }
    # Read with explicit UTF-8 to avoid Windows-1252 mojibake on chars like ellipsis
    $c = [System.IO.File]::ReadAllText($full, $enc)
    if ($c -match 'assets/css/site\.css') { Write-Host "$p : already injected"; continue }
    $idx = $c.IndexOf('</head>')
    if ($idx -lt 0) { Write-Host "$p : no </head>"; continue }
    $new = $c.Substring(0,$idx) + $inject + $c.Substring($idx)
    [System.IO.File]::WriteAllText($full, $new, $enc)
    Write-Host "$p : injected"
}
