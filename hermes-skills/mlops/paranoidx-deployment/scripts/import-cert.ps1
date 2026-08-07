# Import Certificate to Windows Trusted Root CA
# Run as Administrator in PowerShell

$certPath = "C:\cert.pem"

if (-not (Test-Path $certPath)) {
    Write-Error "Certificate not found at $certPath"
    Write-Host "Copy cert.pem from WSL2 first:"
    Write-Host "  wsl -- cp /mnt/c/ParanoidX-data/certs/cert.pem /mnt/c/cert.pem"
    exit 1
}

Write-Host "Importing certificate to Trusted Root CA..." -ForegroundColor Cyan

try {
    Import-Certificate -FilePath $certPath -CertStoreLocation "Cert:\LocalMachine\Root" -ErrorAction Stop
    Write-Host "Certificate imported successfully!" -ForegroundColor Green
}
catch {
    Write-Error "Failed to import: $_"
    exit 1
}

# Verify
$cert = Get-ChildItem "Cert:\LocalMachine\Root" | Where-Object { $_.Subject -like "*localhost*" }
if ($cert) {
    Write-Host "Verified in store:" -ForegroundColor Green
    Write-Host "  Subject: $($cert.Subject)"
    Write-Host "  Thumbprint: $($cert.Thumbprint)"
    Write-Host "  Expires: $($cert.NotAfter)"
}
else {
    Write-Warning "Certificate not found in store after import"
}