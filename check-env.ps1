Write-Host "JAVA_HOME: $([Environment]::GetEnvironmentVariable('JAVA_HOME', 'User'))"
Write-Host "ANDROID_HOME: $([Environment]::GetEnvironmentVariable('ANDROID_HOME', 'User'))"
Write-Host "ANDROID_SDK_ROOT: $([Environment]::GetEnvironmentVariable('ANDROID_SDK_ROOT', 'User'))"
Write-Host "GRADLE_HOME: $([Environment]::GetEnvironmentVariable('GRADLE_HOME', 'User'))"
Write-Host "FLUTTER_HOME: $([Environment]::GetEnvironmentVariable('FLUTTER_HOME', 'User'))"
Write-Host ""
Write-Host "PATH (User) contains:"
$path = [Environment]::GetEnvironmentVariable('Path', 'User')
$path.Split(';') | ForEach-Object { Write-Host "  $_" }