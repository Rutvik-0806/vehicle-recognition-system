# Install / repair Tesseract OCR on Windows (run PowerShell as Administrator)
$ErrorActionPreference = "Stop"

Write-Host "Checking Tesseract OCR..." -ForegroundColor Cyan

$brokenPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $brokenPath) {
    $item = Get-Item $brokenPath
    if ($item.PSIsContainer) {
        Write-Host "Broken install found: tesseract.exe is a folder, not the program." -ForegroundColor Yellow
        Write-Host "Removing broken folder: C:\Program Files\Tesseract-OCR" -ForegroundColor Yellow
        Remove-Item "C:\Program Files\Tesseract-OCR" -Recurse -Force
    }
}

Write-Host "Installing Tesseract via winget..." -ForegroundColor Cyan
winget install --id UB-Mannheim.TesseractOCR -e --accept-package-agreements --accept-source-agreements

$exe = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $exe -PathType Leaf) {
    & $exe --version
    Write-Host ""
    Write-Host "Success! Add this to your .env file:" -ForegroundColor Green
    Write-Host "TESSERACT_CMD=$exe"
} else {
    Write-Host "Install finished but executable not found." -ForegroundColor Red
    Write-Host "Download manually: https://github.com/UB-Mannheim/tesseract/wiki"
}
