[Environment]::SetEnvironmentVariable('PROTOC_HOME', 'C:\protoc', 'User')
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike '*C:\protoc\bin*') {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';C:\protoc\bin', 'User')
    Write-Host 'Added protoc to PATH'
} else {
    Write-Host 'protoc already in PATH'
}