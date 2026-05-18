$enc = New-Object System.Text.UTF8Encoding($false)
$root = Split-Path -Parent $PSScriptRoot
$pages = Get-ChildItem -Path $root -Filter 'index.html' -Recurse | Where-Object {
    $_.Directory.Name -like 'swagger-*-model'
}
$inject = "<link rel=`"stylesheet`" href=`"../assets/css/site.css`">`r`n<link rel=`"stylesheet`" href=`"../assets/css/viewer.css`">`r`n<script src=`"../assets/js/site-chrome.js`" defer></script>`r`n"
foreach ($p in $pages) {
    $full = $p.FullName
    $rel = $p.Directory.Name + '/' + $p.Name
    $c = [System.IO.File]::ReadAllText($full, $enc)
    if ($c -match 'assets/css/site\.css') { Write-Host "$rel : already injected"; continue }
    $idx = $c.IndexOf('</head>')
    if ($idx -lt 0) { Write-Host "$rel : no </head>"; continue }
    $new = $c.Substring(0,$idx) + $inject + $c.Substring($idx)
    [System.IO.File]::WriteAllText($full, $new, $enc)
    Write-Host "$rel : injected"
}
