[Environment]::SetEnvironmentVariable('MAVEN_HOME', 'C:\apache-maven-3.9.9', 'User')
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike '*C:\apache-maven-3.9.9\bin*') {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';C:\apache-maven-3.9.9\bin', 'User')
    Write-Host 'Added Maven to PATH'
} else {
    Write-Host 'Maven already in PATH'
}