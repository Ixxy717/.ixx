# Probe every available WMI namespace for temperature data

Write-Host "=== root\OpenHardwareMonitor classes ==="
try {
    $classes = Get-WmiObject -Namespace root/OpenHardwareMonitor -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
    Write-Host "  Classes:" ($classes -join ', ')
    Write-Host ""
    Write-Host "  Querying Sensor class..."
    $sensors = Get-WmiObject -Namespace root/OpenHardwareMonitor -Class Sensor -ErrorAction SilentlyContinue
    Write-Host "  Sensor count:" @($sensors).Count
    if ($sensors) {
        $sensors | Where-Object { $_.SensorType -eq 'Temperature' } | ForEach-Object {
            Write-Host "   " $_.Name $_.Value "C  (parent:" $_.Parent ")"
        }
    }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== root\Hardware classes ==="
try {
    $classes = Get-WmiObject -Namespace root/Hardware -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
    Write-Host "  Classes:" ($classes -join ', ')
    $sensors = Get-WmiObject -Namespace root/Hardware -Class Sensor -ErrorAction SilentlyContinue
    if ($sensors) {
        Write-Host "  Sensor count:" @($sensors).Count
        $sensors | Where-Object { $_.SensorType -eq 'Temperature' } | ForEach-Object {
            Write-Host "   " $_.Name $_.Value "C"
        }
    }
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== root\cfos ==="
try {
    $classes = Get-WmiObject -Namespace root/cfos -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
    Write-Host "  Classes:" ($classes -join ', ')
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== root\Intel_ME ==="
try {
    $classes = Get-WmiObject -Namespace root/Intel_ME -List -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name
    Write-Host "  Classes:" ($classes -join ', ')
} catch { Write-Host "  error: $_" }

Write-Host ""
Write-Host "=== Ryzen: check AMD WMI provider ==="
try {
    $amd = Get-WmiObject -Namespace root/CIMV2 -Class AMD_Processor -ErrorAction SilentlyContinue
    Write-Host "  AMD_Processor:" @($amd).Count
} catch {}
try {
    $ns = Get-WmiObject -Namespace root -List -ErrorAction SilentlyContinue | Where-Object { $_.Name -match -join('AMD','|','Ryzen','|','cpu','|','temp') }
    Write-Host "  AMD namespaces found:" ($ns.Name -join ', ')
} catch {}

Write-Host ""
Write-Host "=== ASUS WMI (common on ASUS boards) ==="
try {
    $asus = Get-WmiObject -Namespace root/WMI -Class ASUS_HDD_SMART_INFO -ErrorAction SilentlyContinue
    Write-Host "  ASUS:" @($asus).Count
} catch {}
try {
    $wmi = Get-WmiObject -Namespace root/WMI -List | Where-Object { $_.Name -match 'ASUS|Asus|sensor|temp' } | Select-Object Name
    Write-Host "  root\WMI matching classes:" ($wmi.Name -join ', ')
} catch {}
