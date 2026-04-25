$dir = "StressTest\RealWorld"
$files = Get-ChildItem "$dir\*.ixx" | Sort-Object Name

$pass = 0
$fail = 0
$results = @()

foreach ($file in $files) {
    $output = & ixx $file.FullName 2>&1
    $ec = $LASTEXITCODE
    if ($ec -eq 0) {
        $pass++
        $results += [PSCustomObject]@{ File=$file.Name; Status="PASS"; Error="" }
    } else {
        $fail++
        $err = ($output | Out-String).Trim() -replace "`r`n","; " -replace "`n","; "
        if ($err.Length -gt 120) { $err = $err.Substring(0,120) + "..." }
        $results += [PSCustomObject]@{ File=$file.Name; Status="FAIL"; Error=$err }
    }
}

Write-Host ""
Write-Host "=== REALWORLD RESULTS ==="
foreach ($r in $results) {
    if ($r.Status -eq "PASS") {
        Write-Host "PASS  $($r.File)"
    } else {
        Write-Host "FAIL  $($r.File)"
        Write-Host "      $($r.Error)"
    }
}
Write-Host ""
Write-Host "PASSED: $pass / $($pass + $fail)"
Write-Host "FAILED: $fail / $($pass + $fail)"
