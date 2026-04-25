$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StressDir = Split-Path -Parent $ScriptDir
$Root = Split-Path -Parent $StressDir
Set-Location $Root

$FilePass = 0
$FileFail = 0
$AssertPass = 0
$AssertFail = 0
$ExpectedPass = 0
$ExpectedFail = 0
$JsonPass = 0
$JsonFail = 0

function Header($Text) {
    Write-Host ""
    Write-Host "========================================"
    Write-Host $Text
    Write-Host "========================================"
}

function Count-Assertions($Output) {
    foreach ($Line in $Output) {
        $Text = [string]$Line
        if ($Text -match '^PASS ') { $script:AssertPass += 1 }
        if ($Text -match '^FAIL ') { $script:AssertFail += 1 }
    }
}

function Run-Positive {
    param([string]$File)

    Write-Host ""
    Write-Host "[HARD CHECK] $File" -ForegroundColor Cyan
    $checkTime = Measure-Command {
        $checkOut = & ixx check $File 2>&1
        $script:checkCode = $LASTEXITCODE
        $script:checkOutput = $checkOut
    }
    $script:checkOutput | ForEach-Object { Write-Host $_ }
    Write-Host ("check time: {0:n2}s" -f $checkTime.TotalSeconds) -ForegroundColor DarkGray

    if ($script:checkCode -ne 0) {
        $script:FileFail += 1
        Write-Host "FILE FAIL: $File check" -ForegroundColor Red
        return
    }

    Write-Host "[HARD RUN] $File" -ForegroundColor Cyan
    $runTime = Measure-Command {
        $runOut = & ixx $File 2>&1
        $script:runCode = $LASTEXITCODE
        $script:runOutput = $runOut
    }
    $script:runOutput | ForEach-Object { Write-Host $_ }
    Count-Assertions $script:runOutput
    Write-Host ("run time: {0:n2}s" -f $runTime.TotalSeconds) -ForegroundColor DarkGray

    if ($script:runCode -ne 0) {
        $script:FileFail += 1
        Write-Host "FILE FAIL: $File run" -ForegroundColor Red
    } else {
        $script:FilePass += 1
        Write-Host "FILE PASS: $File" -ForegroundColor Green
    }
}

function Run-ExpectedFail {
    param([string]$File)

    Write-Host ""
    Write-Host "[HARD EXPECTED FAIL] $File" -ForegroundColor Yellow
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
    Write-Host "[HARD CHECK JSON] $Name" -ForegroundColor Magenta
    $out = & ixx check $File --json 2>&1
    $code = $LASTEXITCODE
    $text = ($out | Out-String).Trim()
    Write-Host $text

    try {
        $json = $text | ConvertFrom-Json
    } catch {
        $script:JsonFail += 1
        Write-Host "JSON FAIL: $Name -- invalid JSON" -ForegroundColor Red
        return
    }

    if ($ShouldPass) {
        if ($code -eq 0 -and $json.ok -eq $true -and $json.errors.Count -eq 0) {
            $script:JsonPass += 1
            Write-Host "JSON PASS: $Name" -ForegroundColor Green
        } else {
            $script:JsonFail += 1
            Write-Host "JSON FAIL: $Name -- expected ok true" -ForegroundColor Red
        }
        return
    }

    if ($code -ne 0 -and $json.ok -eq $false -and $json.errors.Count -gt 0) {
        $msg = [string]$json.errors[0].message
        if ($MessageContains -and $msg -notlike "*$MessageContains*") {
            $script:JsonFail += 1
            Write-Host "JSON FAIL: $Name -- message did not contain '$MessageContains'" -ForegroundColor Red
            return
        }
        $script:JsonPass += 1
        Write-Host "JSON PASS: $Name" -ForegroundColor Green
    } else {
        $script:JsonFail += 1
        Write-Host "JSON FAIL: $Name -- expected ok false" -ForegroundColor Red
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

Header "IXX Hard StressTest"

& ixx version

$Positive = Get-ChildItem "StressTest\Hard" -Filter "*.ixx" |
    Where-Object {
        $_.DirectoryName -notlike "*\Modules*" -and
        $_.DirectoryName -notlike "*\ExpectedFailures*" -and
        $_.Name -match '^\d\d-.+\.ixx$'
    } |
    Sort-Object Name

foreach ($Item in $Positive) {
    Run-Positive $Item.FullName
}

$Expected = Get-ChildItem "StressTest\Hard\ExpectedFailures" -Filter "*.ixx" |
    Sort-Object Name

foreach ($Item in $Expected) {
    Run-ExpectedFail $Item.FullName
}

Run-JsonCheck "hard good deep import" "StressTest\Hard\06-hard-import-deep-chain.ixx" $true
Run-JsonCheck "hard good stdlib composition" "StressTest\Hard\08-hard-stdlib-composition.ixx" $true
Run-JsonCheck "hard good mega pipeline" "StressTest\Hard\19-hard-mega-pipeline.ixx" $true
Run-JsonCheck "hard good mega file pipeline" "StressTest\Hard\20-hard-mega-pipeline-file.ixx" $true
Run-JsonCheck "hard self cycle" "StressTest\Hard\ExpectedFailures\bad-hard-self-cycle.ixx" $false "Circular"
Run-JsonCheck "hard duplicate local" "StressTest\Hard\ExpectedFailures\bad-hard-import-duplicate-local.ixx" $false "Duplicate"
Run-JsonCheck "hard bad number literal" "StressTest\Hard\ExpectedFailures\bad-hard-top-level-builtin-literal.ixx" $false "Cannot convert"
Run-JsonCheck "hard wrong imported arity" "StressTest\Hard\ExpectedFailures\bad-hard-import-wrong-arity.ixx" $false "expects 1"
Run-JsonCheck "hard bad use nonliteral" "StressTest\Hard\ExpectedFailures\bad-hard-use-nonliteral.ixx" $false "Expected text"
Run-JsonCheck "mega cycle" "StressTest\Hard\ExpectedFailures\bad-mega-cycle.ixx" $false "Circular"
Run-JsonCheck "mega duplicate imports" "StressTest\Hard\ExpectedFailures\bad-mega-duplicate-imports.ixx" $false "Duplicate"
Run-JsonCheck "mega wrong record arity" "StressTest\Hard\ExpectedFailures\bad-mega-wrong-arity-record.ixx" $false "expects 2"
Run-JsonCheck "mega invalid color" "StressTest\Hard\ExpectedFailures\bad-mega-invalid-color.ixx" $false "Unknown color"
Run-JsonCheck "mega unknown imported" "StressTest\Hard\ExpectedFailures\bad-mega-unknown-imported.ixx" $false "not defined"

$TotalPass = $FilePass + $ExpectedPass + $JsonPass
$TotalFail = $FileFail + $AssertFail + $ExpectedFail + $JsonFail

Write-Host ""
Write-Host "========================================"
Write-Host "Hard StressTest complete"
Write-Host "FILE PASS: $FilePass" -ForegroundColor Green
Write-Host "FILE FAIL: $FileFail" -ForegroundColor Red
Write-Host "ASSERT PASS: $AssertPass" -ForegroundColor Green
Write-Host "ASSERT FAIL: $AssertFail" -ForegroundColor Red
Write-Host "EXPECTED FAIL PASS: $ExpectedPass" -ForegroundColor Green
Write-Host "EXPECTED FAIL FAIL: $ExpectedFail" -ForegroundColor Red
Write-Host "JSON PASS: $JsonPass" -ForegroundColor Green
Write-Host "JSON FAIL: $JsonFail" -ForegroundColor Red
Write-Host "----------------------------------------"
Write-Host "TOTAL PASS: $TotalPass" -ForegroundColor Green
Write-Host "TOTAL FAIL: $TotalFail" -ForegroundColor Red
Write-Host "========================================"

if ($TotalFail -gt 0) {
    exit 1
}
exit 0