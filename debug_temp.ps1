$zones = Get-WmiObject -Namespace root/wmi -Class MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue
Write-Host "MSAcpi zones:" @($zones).Count
if ($zones) {
    $zones | ForEach-Object { Write-Host "  zone:" $_.InstanceName "temp:" $_.CurrentTemperature }
} else {
    Write-Host "  MSAcpi: no data"
}

Write-Host ""
Write-Host "Trying Win32_TemperatureProbe..."
$probes = Get-CimInstance -Class Win32_TemperatureProbe -ErrorAction SilentlyContinue
Write-Host "  probes:" @($probes).Count
if ($probes) { $probes | ForEach-Object { Write-Host "  " $_.Name $_.CurrentReading } }

Write-Host ""
Write-Host "Trying OpenHardwareMonitor namespace..."
try {
    $hwm = Get-WmiObject -Namespace root/OpenHardwareMonitor -Class Sensor -ErrorAction SilentlyContinue | Where-Object { $_.SensorType -eq "Temperature" }
    Write-Host "  OHM sensors:" @($hwm).Count
    if ($hwm) { $hwm | ForEach-Object { Write-Host "  " $_.Name $_.Value } }
} catch { Write-Host "  OHM not available" }

Write-Host ""
Write-Host "Trying LibreHardwareMonitor namespace..."
try {
    $lhm = Get-WmiObject -Namespace root/LibreHardwareMonitor -Class Sensor -ErrorAction SilentlyContinue | Where-Object { $_.SensorType -eq "Temperature" }
    Write-Host "  LHM sensors:" @($lhm).Count
    if ($lhm) { $lhm | ForEach-Object { Write-Host "  " $_.Name $_.Value } }
} catch { Write-Host "  LHM not available" }

Write-Host ""
Write-Host "Checking available WMI namespaces under root/wmi..."
try {
    Get-WmiObject -Namespace root/wmi -Class __Namespace | Select-Object Name | ForEach-Object { Write-Host "  " $_.Name }
} catch { Write-Host "  Could not list namespaces" }
