$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StressDir = Split-Path -Parent $ScriptDir
$Root = Split-Path -Parent $StressDir
Set-Location $Root

$ScenarioPass = 0
$ScenarioFail = 0
$AssertPass = 0
$AssertFail = 0

function Count-Assertions($Output) {
    foreach ($Line in $Output) {
        $Text = [string]$Line
        if ($Text -match '^PASS ') { $script:AssertPass += 1 }
        if ($Text -match '^FAIL ') { $script:AssertFail += 1 }
    }
}

function Run-Scenario {
    param([string]$File)

    Write-Host ""
    Write-Host "[SCENARIO CHECK] $File" -ForegroundColor Cyan
    $checkTime = Measure-Command {
        $checkOut = & ixx check $File 2>&1
        $script:checkCode = $LASTEXITCODE
        $script:checkOutput = $checkOut
    }
    $script:checkOutput | ForEach-Object { Write-Host $_ }
    Write-Host ("check time: {0:n2}s" -f $checkTime.TotalSeconds) -ForegroundColor DarkGray

    if ($script:checkCode -ne 0) {
        $script:ScenarioFail += 1
        Write-Host "SCENARIO FAIL: $File check" -ForegroundColor Red
        return
    }

    Write-Host "[SCENARIO RUN] $File" -ForegroundColor Cyan
    $runTime = Measure-Command {
        $runOut = & ixx $File 2>&1
        $script:runCode = $LASTEXITCODE
        $script:runOutput = $runOut
    }
    $script:runOutput | ForEach-Object { Write-Host $_ }
    Count-Assertions $script:runOutput
    Write-Host ("run time: {0:n2}s" -f $runTime.TotalSeconds) -ForegroundColor DarkGray

    if ($script:runCode -ne 0) {
        $script:ScenarioFail += 1
        Write-Host "SCENARIO FAIL: $File run" -ForegroundColor Red
    } else {
        $script:ScenarioPass += 1
        Write-Host "SCENARIO PASS: $File" -ForegroundColor Green
    }
}

if (-not (Get-Command ixx -ErrorAction SilentlyContinue)) {
    Write-Host "IXX CLI not found. Install with: pip install --upgrade ixx" -ForegroundColor Red
    exit 1
}

if (Test-Path "StressTest\tmp") {
    Remove-Item "StressTest\tmp" -Recurse -Force
}
New-Item -ItemType Directory -Force -Path "StressTest\tmp" | Out-Null

Write-Host ""
Write-Host "========================================"
Write-Host "IXX Real-World Scenario Suite"
Write-Host "========================================"

& ixx version

$Scenarios = Get-ChildItem "StressTest\Scenario" -Filter "*.ixx" |
    Where-Object {
        $_.DirectoryName -notlike "*\Modules*" -and
        $_.Name -match '^\d\d-.+\.ixx$'
    } |
    Sort-Object Name

foreach ($Item in $Scenarios) {
    Run-Scenario $Item.FullName
}

$TotalPass = $ScenarioPass
$TotalFail = $ScenarioFail + $AssertFail

Write-Host ""
Write-Host "========================================"
Write-Host "Scenario Suite complete"
Write-Host "SCENARIO PASS: $ScenarioPass" -ForegroundColor Green
Write-Host "SCENARIO FAIL: $ScenarioFail" -ForegroundColor Red
Write-Host "ASSERT PASS: $AssertPass" -ForegroundColor Green
Write-Host "ASSERT FAIL: $AssertFail" -ForegroundColor Red
Write-Host "----------------------------------------"
Write-Host "TOTAL PASS: $TotalPass" -ForegroundColor Green
Write-Host "TOTAL FAIL: $TotalFail" -ForegroundColor Red
Write-Host "========================================"

if ($TotalFail -gt 0) {
    exit 1
}
exit 0