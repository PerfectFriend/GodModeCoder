[Environment]::SetEnvironmentVariable('KOTLIN_HOME', 'C:\kotlinc', 'User')
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike '*C:\kotlinc\bin*') {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';C:\kotlinc\bin', 'User')
    Write-Host 'Added Kotlin to PATH'
} else {
    Write-Host 'Kotlin already in PATH'
}