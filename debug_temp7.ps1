Write-Host "=== Get-Counter with explicit High Precision Temp ==="
try {
    $r = Get-Counter '\Thermal Zone Information(*)\High Precision Temperature' -ErrorAction Stop
    $r.CounterSamples | ForEach-Object {
        Write-Host "  Path:" $_.Path
        Write-Host "  CookedValue:" $_.CookedValue
        Write-Host "  -> Celsius:" ([math]::Round($_.CookedValue / 10 - 273.15, 1))
    }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== List actual thermal zone counter instances ==="
try {
    $set = Get-Counter -ListSet "Thermal Zone Information"
    Write-Host "  All PathsWithInstances:"
    $set.PathsWithInstances | ForEach-Object { Write-Host "    $_" }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== Try AMD GPU temp via OHM-style (ADLX) ==="
$gpuProcess = Get-Process | Where-Object { $_.Name -match 'RadeonSoftware|ADLX|AMDRSSrc|amddvr|CCC' }
if ($gpuProcess) { $gpuProcess | ForEach-Object { Write-Host "  AMD process:" $_.Name } }
else { Write-Host "  No AMD Radeon Software running" }

Write-Host ""
Write-Host "=== amd3dvcache service details ==="
$svc = Get-Service 'amd3dvcacheSvc' -ErrorAction SilentlyContinue
if ($svc) {
    Write-Host "  Status:" $svc.Status
    $svc | Start-Service -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    # Check if it exposed anything
    $z = Get-WmiObject -Namespace root/WMI -Class MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue
    Write-Host "  After starting: MSAcpi count:" @($z).Count
}

Write-Host ""
Write-Host "=== Check if admin would help (try wmic as admin) ==="
$id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object System.Security.Principal.WindowsPrincipal($id)
Write-Host "  Running as admin:" $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
