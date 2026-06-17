# PowerShell version of run.sh
# change these variables to fit your working directory

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$SERVICES_ROOT = Join-Path $SCRIPT_DIR "services"
$NOTIFICATION = Join-Path $SERVICES_ROOT "notification-service"

$PROCESSES = @()

function Get-ServiceDir {
  param([string]$name)

  if ($name -eq 'gateway') {
    return Join-Path $SCRIPT_DIR 'gateway'
  }

  return Join-Path $SERVICES_ROOT $name
}

function Cleanup {
  Write-Host ""
  Write-Host "Stopping all services..."
  foreach ($proc in $PROCESSES) {
    try {
      Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    } catch {
      # Process already stopped
    }
  }
  exit 0
}

function Get-ServiceLabel {
  param([string]$name)
  return Split-Path $name -Leaf
}

function Get-ServiceModule {
  param([string]$dir)

  if (Test-Path (Join-Path $dir "app/main.py")) {
    return "app.main:app"
  }

  if (Test-Path (Join-Path $dir "main.py")) {
    return "main:app"
  }

  return $null
}

function Get-FlaskApp {
  param([string]$dir)

  if (Test-Path (Join-Path $dir "app/main.py")) {
    return "app.main"
  }

  if (Test-Path (Join-Path $dir "main.py")) {
    return "main"
  }

  return $null
}

function Run-Uvicorn {
  param(
    [string]$name,
    [int]$port
  )

  $dir = Get-ServiceDir $name
  $label = Get-ServiceLabel $name
  $module = Get-ServiceModule $dir

  if (-not $module) {
    Write-Host "[$label] skipping - no app/main.py or main.py"
    return
  }

  $python = Join-Path $dir ".venv\Scripts\python.exe"
  if (-not (Test-Path $python)) {
    Write-Host "[$label] skipping - no python in .venv"
    return
  }

  if (Test-Path (Join-Path $dir "requirements.txt")) {
    Write-Host "[$label] installing requirements..."
    Push-Location $dir
    & $python -m pip install --upgrade --force-reinstall -r requirements.txt -q
    Pop-Location
  }

  Write-Host "[$label] -> http://localhost:$port"
  $proc = Start-Process -FilePath $python -ArgumentList "-m", "uvicorn", $module, "--port", $port -WorkingDirectory $dir -PassThru -NoNewWindow
  $PROCESSES += $proc
}

function Run-Flask {
  param(
    [string]$name,
    [int]$port
  )

  $dir = Get-ServiceDir $name
  $label = Get-ServiceLabel $name
  $flaskApp = Get-FlaskApp $dir

  if (-not $flaskApp) {
    Write-Host "[$label] skipping - no app/main.py or main.py"
    return
  }

  $python = Join-Path $dir ".venv\Scripts\python.exe"
  if (-not (Test-Path $python)) {
    Write-Host "[$label] skipping - no python in .venv"
    return
  }

  if (Test-Path (Join-Path $dir "requirements.txt")) {
    Write-Host "[$label] installing requirements..."
    Push-Location $dir
    & $python -m pip install --upgrade --force-reinstall -r requirements.txt -q
    Pop-Location
  }

  Write-Host "[$label] -> http://localhost:$port"
  $proc = Start-Process -FilePath $python -ArgumentList "-m", "flask", "--app", $flaskApp, "run", "--port", $port -WorkingDirectory $dir -PassThru -NoNewWindow
  $PROCESSES += $proc
}

Write-Host "Starting services..."

# FastAPI / uvicorn services
Run-Uvicorn "gateway"           8000
Run-Uvicorn "user-service"      8001
Run-Uvicorn "game-service"      8002
Run-Uvicorn "activity-service"  8003
Run-Uvicorn "auth-service"      8005

# Flask / WSGI service
Run-Flask "logging-service"     8006

# Node.js service
if (Test-Path (Join-Path $NOTIFICATION "package.json")) {
  Write-Host "[notification-service] -> http://localhost:8004"
  $proc = Start-Process -FilePath "cmd" -ArgumentList "/c", "cd /d `"$NOTIFICATION`" && npm install && npm run dev" -PassThru -NoNewWindow
  $PROCESSES += $proc
} else {
  Write-Host "[notification-service] skipping - no package.json"
}

Write-Host ""
Write-Host "Press Ctrl+C to stop all services."
Write-Host ""

# Wait for all processes
try {
  $PROCESSES | ForEach-Object { $_.WaitForExit() }
} catch {
  Cleanup
}
