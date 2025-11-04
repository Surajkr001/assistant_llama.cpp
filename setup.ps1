# Quick Setup Script for AI Assistant
# Run this script to set up your environment quickly

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AI Assistant - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Python installation
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.9 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`n[2/6] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "`n[3/6] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install basic dependencies
Write-Host "`n[4/6] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check for CUDA
Write-Host "`n[5/6] Checking for GPU support..." -ForegroundColor Yellow
$cudaCheck = nvidia-smi 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ NVIDIA GPU detected!" -ForegroundColor Green
    Write-Host "`nWould you like to install GPU-accelerated llama-cpp-python? (y/n)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Installing GPU-accelerated version..." -ForegroundColor Yellow
        $env:CMAKE_ARGS = "-DLLAMA_CUBLAS=on"
        pip install llama-cpp-python --force-reinstall --no-cache-dir
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ GPU-accelerated llama-cpp-python installed" -ForegroundColor Green
        } else {
            Write-Host "✗ Failed to install GPU version, continuing with CPU version" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "⚠ No NVIDIA GPU detected, using CPU mode" -ForegroundColor Yellow
}

# Create models directory
Write-Host "`n[6/6] Setting up directories..." -ForegroundColor Yellow
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "✓ Created models directory" -ForegroundColor Green
} else {
    Write-Host "✓ Models directory already exists" -ForegroundColor Green
}

# Final instructions
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Download a GGUF model file (see README.md for links)"
Write-Host "  2. Place the model in the 'models' folder"
Write-Host "  3. Update config.json with your model path"
Write-Host "  4. Run: python run_assistant.py`n"

Write-Host "Quick Start Commands:" -ForegroundColor Yellow
Write-Host "  • Interactive Mode: python run_assistant.py"
Write-Host "  • Text Chat:        python text_assistant.py"
Write-Host "  • Voice Mode:       python voice_assistant.py`n"

Write-Host "Documentation:" -ForegroundColor Yellow
Write-Host "  • Full Guide:    README.md"
Write-Host "  • Quick Setup:   SETUP.md"
Write-Host "  • Architecture:  PROJECT_STRUCTURE.md`n"

Write-Host "Recommended Models:" -ForegroundColor Yellow
Write-Host "  • Llama-2-7B-Chat-GGUF (Q4_K_M) - ~4GB"
Write-Host "  • Mistral-7B-Instruct-GGUF (Q4_K_M) - ~4GB"
Write-Host "  • OpenHermes-2.5-Mistral-7B (Q4_K_M) - ~4GB`n"

Write-Host "Download from: https://huggingface.co/TheBloke`n" -ForegroundColor Cyan

Write-Host "Happy assisting! 🚀`n" -ForegroundColor Green
