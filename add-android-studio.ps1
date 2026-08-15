[Environment]::SetEnvironmentVariable('ANDROID_STUDIO_HOME', 'C:\Program Files\Android\Android Studio', 'User')
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$add = @(
    'C:\Program Files\Android\Android Studio\bin',
    'C:\Program Files\Android\Android Studio\jbr\bin'
)
$new = $add | Where-Object { $currentPath -notlike "*$_*" }
if ($new) {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';' + ($new -join ';'), 'User')
    Write-Host "Added Android Studio to PATH: $($new -join ', ')"
} else {
    Write-Host 'Android Studio already in PATH'
}