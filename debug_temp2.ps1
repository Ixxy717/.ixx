# Try every known Windows temperature path

Write-Host "=== Performance Counter: Thermal Zone ==="
try {
    $counter = Get-Counter '\Thermal Zone Information(*)\Temperature' -ErrorAction SilentlyContinue
    if ($counter) {
        $counter.CounterSamples | ForEach-Object {
            $c = [math]::Round($_.CookedValue - 273.15, 1)
            Write-Host "  $($_.Path): $c C"
        }
    } else { Write-Host "  no data" }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== Win32_Processor: some boards expose CurrentTemperature ==="
try {
    $cpus = Get-CimInstance Win32_Processor
    foreach ($cpu in $cpus) {
        Write-Host "  Name:" $cpu.Name
        Write-Host "  CurrentTemperature (raw):" $cpu.CurrentTemperature
        if ($cpu.CurrentTemperature) {
            $c = [math]::Round(($cpu.CurrentTemperature / 10) - 273.15, 1)
            Write-Host "  -> $c C"
        }
    }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== CIM MSAcpi_ThermalZoneTemperature ==="
try {
    $z = Get-CimInstance -Namespace root/WMI -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue
    Write-Host "  count:" @($z).Count
    if ($z) { $z | ForEach-Object { Write-Host "  " $_.InstanceName $_.CurrentTemperature } }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== WMIC path ==="
try {
    $raw = & wmic /namespace:"\\root\wmi" path MSAcpi_ThermalZoneTemperature get CurrentTemperature 2>&1
    Write-Host "  WMIC result: $raw"
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== root\cimv2 namespaces for temperature ==="
try {
    $ns = Get-CimInstance -Namespace root -ClassName __Namespace | Select-Object -ExpandProperty Name
    Write-Host "  root namespaces:" ($ns -join ', ')
} catch {}
