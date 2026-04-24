Write-Host "=== Win32_PerfFormattedData_Counters_ThermalZoneInformation ==="
try {
    $tz = Get-CimInstance -Class Win32_PerfFormattedData_Counters_ThermalZoneInformation -ErrorAction SilentlyContinue
    Write-Host "  Count:" @($tz).Count
    $tz | ForEach-Object {
        Write-Host "  Name:" $_.Name
        Write-Host "  Temperature:" $_.Temperature
        Write-Host "  HighPrecisionTemperature:" $_.HighPrecisionTemperature
        Write-Host "  PercentPassiveLimit:" $_.PercentPassiveLimit
        Write-Host "  ThrottleReasons:" $_.ThrottleReasons
        Write-Host "  ---"
    }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== Win32_PerfRawData_Counters_ThermalZoneInformation ==="
try {
    $tz2 = Get-CimInstance -Class Win32_PerfRawData_Counters_ThermalZoneInformation -ErrorAction SilentlyContinue
    Write-Host "  Count:" @($tz2).Count
    $tz2 | ForEach-Object {
        Write-Host "  Name:" $_.Name
        Write-Host "  Temperature:" $_.Temperature
        Write-Host "  HighPrecisionTemperature:" $_.HighPrecisionTemperature
        Write-Host "  ---"
    }
} catch { Write-Host "  error: $_" }
