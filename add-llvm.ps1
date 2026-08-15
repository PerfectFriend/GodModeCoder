[Environment]::SetEnvironmentVariable('LLVM_HOME', 'C:\LLVM', 'User')
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike '*C:\LLVM\bin*') {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';C:\LLVM\bin', 'User')
    Write-Host 'Added LLVM to PATH'
} else {
    Write-Host 'LLVM already in PATH'
}