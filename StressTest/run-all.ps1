$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
Set-Location $Root

$Pass = 0
$Fail = 0

function Write-Header($Text) {
    Write-Host ""
    Write-Host "========================================"
    Write-Host $Text
    Write-Host "========================================"
}

function Add-Pass {
    param([string]$Name)
    $script:Pass += 1
    Write-Host "PASS: $Name" -ForegroundColor Green
}

function Add-Fail {
    param([string]$Name)
    $script:Fail += 1
    Write-Host "FAIL: $Name" -ForegroundColor Red
}

function Run-Positive {
    param([string]$File)

    Write-Host ""
    Write-Host "[CHECK] $File" -ForegroundColor Cyan
    & ixx check $File
    if ($LASTEXITCODE -ne 0) {
        Add-Fail "$File check"
        return
    }

    Write-Host "[RUN] $File" -ForegroundColor Cyan
    & ixx $File
    if ($LASTEXITCODE -ne 0) {
        Add-Fail "$File run"
    } else {
        Add-Pass $File
    }
}

function Run-ExpectedFail {
    param([string]$File)

    Write-Host ""
    Write-Host "[EXPECTED FAIL] $File" -ForegroundColor Yellow
    & ixx $File
    if ($LASTEXITCODE -ne 0) {
        Add-Pass "$File expected failure"
    } else {
        Add-Fail "$File should have failed"
    }
}

if (-not (Get-Command ixx -ErrorAction SilentlyContinue)) {
    Write-Host "IXX CLI not found. Install with: pip install --upgrade ixx" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path "StressTest\tmp" | Out-Null

[System.IO.File]::WriteAllText(
    (Join-Path $Root "StressTest\tmp\readlines-fixture.txt"),
    "alpha`r`nbeta`r`ngamma`r`n",
    (New-Object System.Text.UTF8Encoding($false))
)

Write-Header "IXX StressTest"

& ixx version
& ixx StressTest\main.ixx

$Positive = @(
    "StressTest\01-basics.ixx",
    "StressTest\02-functions.ixx",
    "StressTest\03-builtins-text.ixx",
    "StressTest\04-builtins-math.ixx",
    "StressTest\05-builtins-lists.ixx",
    "StressTest\06-files.ixx",
    "StressTest\07-try-catch.ixx",
    "StressTest\08-scope.ixx",
    "StressTest\09-color.ixx"
)

foreach ($File in $Positive) {
    Run-Positive $File
}

$ExpectedFailures = @(
    "StressTest\ExpectedFailures\bad-syntax-missing-value.ixx",
    "StressTest\ExpectedFailures\bad-return-outside-function.ixx",
    "StressTest\ExpectedFailures\bad-bool-math.ixx",
    "StressTest\ExpectedFailures\bad-number-conversion.ixx",
    "StressTest\ExpectedFailures\bad-undefined-variable.ixx",
    "StressTest\ExpectedFailures\bad-file-read.ixx"
)

foreach ($File in $ExpectedFailures) {
    Run-ExpectedFail $File
}

Write-Host ""
Write-Host "========================================"
Write-Host "StressTest complete"
Write-Host "PASS: $Pass" -ForegroundColor Green
Write-Host "FAIL: $Fail" -ForegroundColor Red
Write-Host "========================================"

if ($Fail -gt 0) {
    exit 1
}

exit 0