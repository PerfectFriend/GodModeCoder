<#>
.SYNOPSIS
    Configure Ollama for CPU-only mode on Windows (AMD iGPU Vulkan fix)

.DESCRIPTION
    Sets environment variables and configures Ollama to run CPU-only
    to avoid Vulkan OOM errors on AMD iGPU (Radeon 780M).

.NOTES
    Run as Administrator for system-wide environment variables.
    For user-level: remove -Scope Machine from setx commands.
#>

# Set CPU-only environment variables (User scope)
$envVars = @{
    "OLLAMA_NUM_GPU"        = "0"
    "OLLAMA_GPU_LAYERS"     = "0"
    "OLLAMA_FLASH_ATTENTION" = "0"
    "OLLAMA_KV_CACHE_TYPE"  = "f16"
    "OLLAMA_NO_VULKAN"      = "1"
    "OLLAMA_CUDA"           = "0"
    "OLLAMA_ROCM"           = "0"
    "OLLAMA_METAL"          = "0"
    "OLLAMA_LOW_VRAM"       = "1"
    "OLLAMA_NUMA"           = "true"
}

Write-Host "Setting Ollama CPU-only environment variables..." -ForegroundColor Cyan

foreach ($key in $envVars.Keys) {
    $value = $envVars[$key]
    setx $key $value -Scope User
    Write-Host "  Set $key = $value"
}

# Verify
Write-Host "`nVerifying environment variables..." -ForegroundColor Cyan
foreach ($key in $envVars.Keys) {
    $value = [Environment]::GetEnvironmentVariable($key, "User")
    Write-Host "  $key = $value"
}

# Test Ollama API
Write-Host "`nTesting Ollama API..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 10
    if ($response.models) {
        Write-Host "✅ Ollama API responding" -ForegroundColor Green
        $response.models | ForEach-Object { Write-Host "  Model: $($_.name) Size: $($_.size / 1GB) GB" }
    } else {
        Write-Host "⚠️  Ollama running but no models found. Run: ollama pull qwen3:8b" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Ollama not running. Start with: ollama serve" -ForegroundColor Red
}

Write-Host "`n✅ Ollama CPU-only configuration complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Restart terminal/PowerShell to pick up new env vars"
Write-Host "  2. Run: ollama serve (or restart Ollama app)"
Write-Host "  3. Run: ollama pull qwen3:8b"
Write-Host "  4. Test: curl -X POST http://localhost:11434/api/generate -d '{\"model\":\"qwen3:8b\",\"prompt\":\"test\",\"stream\":false,\"options\":{\"num_gpu\":0}}'"