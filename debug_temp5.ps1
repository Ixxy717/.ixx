# Final targeted debug

Write-Host "=== Thermal Zone Information: list all instances ==="
try {
    $set = Get-Counter -ListSet "Thermal Zone Information"
    Write-Host "  Paths sample:" ($set.PathsWithInstances | Select-Object -First 10 | ForEach-Object { "  $_" })
    Write-Host "  Counter names:" ($set.Counter -join ', ')
    Write-Host "  Instance count:" $set.PathsWithInstances.Count
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== AMD Ryzen Master service ==="
$svc = Get-Service -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'AMD|Ryzen' }
$svc | ForEach-Object { Write-Host "  Service:" $_.Name "Status:" $_.Status }

Write-Host ""
Write-Host "=== Ryzen Master: does it expose WMI when running? ==="
$ryzenExe = "C:\Program Files\AMD\RyzenMaster\AMD Ryzen Master.exe"
Write-Host "  Exe exists:" (Test-Path $ryzenExe)
$rmDir = Get-ChildItem "C:\Program Files\AMD\RyzenMaster" -ErrorAction SilentlyContinue
if ($rmDir) { $rmDir | Select-Object Name | ForEach-Object { Write-Host "  " $_.Name } }

Write-Host ""
Write-Host "=== WMI: check root\CIMV2 for AMD classes ==="
try {
    $amdClasses = Get-WmiObject -Namespace root/CIMV2 -List | Where-Object { $_.Name -match 'AMD|Temperature|Thermal|Sensor|Hardware' } | Select-Object Name
    Write-Host "  Matching classes:" ($amdClasses.Name -join ', ')
} catch {}
