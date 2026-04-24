# Probe root\Hardware NumericSensor and try admin-requiring methods

Write-Host "=== root\Hardware NumericSensor ==="
try {
    $sensors = Get-WmiObject -Namespace root/Hardware -Class NumericSensor -ErrorAction SilentlyContinue
    Write-Host "  NumericSensor count:" @($sensors).Count
    if ($sensors) {
        $sensors | ForEach-Object { Write-Host "  " $_.Name $_.CurrentReading $_.BaseUnits $_.UnitModifier }
    }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== root\Hardware Sensor ==="
try {
    $sensors = Get-WmiObject -Namespace root/Hardware -Class Sensor -ErrorAction SilentlyContinue
    Write-Host "  Sensor count:" @($sensors).Count
    if ($sensors) { $sensors | ForEach-Object { Write-Host "  " $_ } }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== root\Hardware ComputerSystem ==="
try {
    $cs = Get-WmiObject -Namespace root/Hardware -Class ComputerSystem -ErrorAction SilentlyContinue
    Write-Host "  ComputerSystem count:" @($cs).Count
    if ($cs) { $cs | ForEach-Object { Write-Host "  " $_ } }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== Try running OHM inline via .NET ==="
try {
    $code = @'
using System;
using OpenHardwareMonitor.Hardware;
'@
    Write-Host "  OHM .NET not directly available via PS"
} catch {}

Write-Host ""
Write-Host "=== Is OpenHardwareMonitor.exe or LibreHardwareMonitor.exe running? ==="
$procs = Get-Process | Where-Object { $_.Name -match 'Hardware|OpenHardware|LibreHardware|HWiNFO|HWMonitor|Ryzen' }
if ($procs) {
    $procs | ForEach-Object { Write-Host "  Running:" $_.Name $_.Id }
} else {
    Write-Host "  None of those processes are running"
}

Write-Host ""
Write-Host "=== Ryzen Master check ==="
$ryzen = Get-Process | Where-Object { $_.Name -match 'Ryzen' }
if ($ryzen) { $ryzen | ForEach-Object { Write-Host "  " $_.Name } }
else { Write-Host "  Ryzen Master not running" }

$ryzenPath = "C:\Program Files\AMD\RyzenMaster"
Write-Host "  Ryzen Master installed:" (Test-Path $ryzenPath)

Write-Host ""
Write-Host "=== CPU package temp via PDH counter ==="
try {
    $counter = Get-Counter '\Processor Information(_Total)\% Processor Time' -ErrorAction SilentlyContinue
    Write-Host "  Processor counter works:" ($null -ne $counter)
    # Try thermal
    $tCounters = Get-Counter -ListSet "Thermal*" -ErrorAction SilentlyContinue
    Write-Host "  Thermal counter sets:" ($tCounters.CounterSetName -join ', ')
} catch { Write-Host "  error: $_" }
