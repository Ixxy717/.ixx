$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Split-Path -Parent $ScriptDir
Set-Location $Root

$FilePass = 0
$FileFail = 0
$AssertPass = 0
$AssertFail = 0
$ExpectedPass = 0
$ExpectedFail = 0
$JsonPass = 0
$JsonFail = 0

function Write-Header($Text) {
    Write-Host ""
    Write-Host "========================================"
    Write-Host $Text
    Write-Host "========================================"
}

function Count-Assertions($Output) {
    foreach ($Line in $Output) {
        $Text = [string]$Line
        if ($Text -match '^PASS ') {
            $script:AssertPass += 1
        }
        if ($Text -match '^FAIL ') {
            $script:AssertFail += 1
        }
    }
}

function Add-FilePass {
    param([string]$Name)
    $script:FilePass += 1
    Write-Host "FILE PASS: $Name" -ForegroundColor Green
}

function Add-FileFail {
    param([string]$Name)
    $script:FileFail += 1
    Write-Host "FILE FAIL: $Name" -ForegroundColor Red
}

function Add-JsonPass {
    param([string]$Name)
    $script:JsonPass += 1
    Write-Host "JSON PASS: $Name" -ForegroundColor Green
}

function Add-JsonFail {
    param([string]$Name, [string]$Why = "")
    $script:JsonFail += 1
    if ($Why) {
        Write-Host "JSON FAIL: $Name -- $Why" -ForegroundColor Red
    } else {
        Write-Host "JSON FAIL: $Name" -ForegroundColor Red
    }
}

function Run-Positive {
    param([string]$File)

    Write-Host ""
    Write-Host "[CHECK] $File" -ForegroundColor Cyan
    $checkOut = & ixx check $File 2>&1
    $checkCode = $LASTEXITCODE
    $checkOut | ForEach-Object { Write-Host $_ }

    if ($checkCode -ne 0) {
        Add-FileFail "$File check"
        return
    }

    Write-Host "[RUN] $File" -ForegroundColor Cyan
    $runOut = & ixx $File 2>&1
    $runCode = $LASTEXITCODE
    $runOut | ForEach-Object { Write-Host $_ }
    Count-Assertions $runOut

    if ($runCode -ne 0) {
        Add-FileFail "$File run"
    } else {
        Add-FilePass $File
    }
}

function Run-ExpectedFail {
    param([string]$File)

    Write-Host ""
    Write-Host "[EXPECTED FAIL] $File" -ForegroundColor Yellow
    $out = & ixx $File 2>&1
    $code = $LASTEXITCODE
    $out | ForEach-Object { Write-Host $_ }

    if ($code -ne 0) {
        $script:ExpectedPass += 1
        Write-Host "EXPECTED PASS: $File failed as expected" -ForegroundColor Green
    } else {
        $script:ExpectedFail += 1
        Write-Host "EXPECTED FAIL: $File should have failed" -ForegroundColor Red
    }
}

function Run-JsonCheck {
    param(
        [string]$Name,
        [string]$File,
        [bool]$ShouldPass,
        [string]$MessageContains = ""
    )

    Write-Host ""
    Write-Host "[CHECK JSON] $Name" -ForegroundColor Magenta
    $out = & ixx check $File --json 2>&1
    $code = $LASTEXITCODE
    $text = ($out | Out-String).Trim()
    Write-Host $text

    try {
        $json = $text | ConvertFrom-Json
    } catch {
        Add-JsonFail $Name "output was not valid JSON"
        return
    }

    if ($null -eq $json.ok) {
        Add-JsonFail $Name "missing ok field"
        return
    }

    if ($null -eq $json.errors) {
        Add-JsonFail $Name "missing errors field"
        return
    }

    if ($ShouldPass) {
        if ($code -ne 0) {
            Add-JsonFail $Name "expected exit 0, got $code"
            return
        }
        if ($json.ok -ne $true) {
            Add-JsonFail $Name "expected ok true"
            return
        }
        if ($json.errors.Count -ne 0) {
            Add-JsonFail $Name "expected no errors"
            return
        }
        Add-JsonPass $Name
        return
    }

    if ($code -eq 0) {
        Add-JsonFail $Name "expected nonzero exit"
        return
    }
    if ($json.ok -ne $false) {
        Add-JsonFail $Name "expected ok false"
        return
    }
    if ($json.errors.Count -lt 1) {
        Add-JsonFail $Name "expected at least one error"
        return
    }

    $msg = [string]$json.errors[0].message
    if ($MessageContains -and $msg -notlike "*$MessageContains*") {
        Add-JsonFail $Name "message did not contain '$MessageContains'"
        return
    }

    Add-JsonPass $Name
}

if (-not (Get-Command ixx -ErrorAction SilentlyContinue)) {
    Write-Host "IXX CLI not found. Install with: pip install --upgrade ixx" -ForegroundColor Red
    exit 1
}

if (Test-Path "StressTest\tmp") {
    Remove-Item "StressTest\tmp" -Recurse -Force
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

$Positive = Get-ChildItem "StressTest" -Filter "*.ixx" |
    Where-Object { $_.Name -match '^\d\d-.+\.ixx$' } |
    Sort-Object Name

foreach ($Item in $Positive) {
    Run-Positive $Item.FullName
}

$ExpectedFailures = Get-ChildItem "StressTest\ExpectedFailures" -Filter "*.ixx" |
    Sort-Object Name

foreach ($Item in $ExpectedFailures) {
    Run-ExpectedFail $Item.FullName
}

Run-JsonCheck "json good file" "StressTest\CheckJson\good.ixx" $true
Run-JsonCheck "json syntax error" "StressTest\CheckJson\bad-syntax.ixx" $false "Expected a value"
Run-JsonCheck "json wrong user arg count" "StressTest\CheckJson\bad-wrong-arg-count.ixx" $false "expects 2"
Run-JsonCheck "json unknown function" "StressTest\CheckJson\bad-unknown-function.ixx" $false "missingfunction"
Run-JsonCheck "json undefined variable" "StressTest\CheckJson\bad-undefined-variable.ixx" $false "ghost"
Run-JsonCheck "json builtin arity" "StressTest\CheckJson\bad-builtin-arity.ixx" $false "do"
Run-JsonCheck "json invalid color literal" "StressTest\ExpectedFailures\bad-color-name.ixx" $false "Unknown color"
Run-JsonCheck "json missing read literal" "StressTest\ExpectedFailures\bad-file-read.ixx" $false "File not found"
Run-JsonCheck "json invalid number literal" "StressTest\ExpectedFailures\bad-number-conversion.ixx" $false "Cannot convert"
Run-JsonCheck "json empty do literal" "StressTest\ExpectedFailures\bad-do-empty.ixx" $false "empty command"
Run-JsonCheck "json nontext do literal" "StressTest\ExpectedFailures\bad-do-nontext.ixx" $false "expects a shell command"

Write-Host ""
Write-Host "========================================"
Write-Host "StressTest complete"
Write-Host "FILE PASS: $FilePass" -ForegroundColor Green
Write-Host "FILE FAIL: $FileFail" -ForegroundColor Red
Write-Host "ASSERT PASS: $AssertPass" -ForegroundColor Green
Write-Host "ASSERT FAIL: $AssertFail" -ForegroundColor Red
Write-Host "EXPECTED FAIL PASS: $ExpectedPass" -ForegroundColor Green
Write-Host "EXPECTED FAIL FAIL: $ExpectedFail" -ForegroundColor Red
Write-Host "JSON PASS: $JsonPass" -ForegroundColor Green
Write-Host "JSON FAIL: $JsonFail" -ForegroundColor Red
Write-Host "========================================"

if ($FileFail -gt 0 -or $AssertFail -gt 0 -or $ExpectedFail -gt 0 -or $JsonFail -gt 0) {
    exit 1
}

exit 0