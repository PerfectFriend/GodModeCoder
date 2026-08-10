$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$add = @(
    'C:\Users\tomas\.cargo\bin',
    'C:\jdk-21.0.12+8\bin',
    'C:\dart-sdk\bin',
    'C:\gradle-9.1.0\bin',
    'C:\Users\tomas\develop\flutter\bin',
    'C:\Users\tomas\AppData\Local\Android\Sdk\platform-tools',
    'C:\Users\tomas\AppData\Local\Android\Sdk\cmdline-tools\latest\bin',
    'C:\Users\tomas\AppData\Local\Android\Sdk\emulator',
    'C:\Program Files\Microsoft Visual Studio\18\Insiders\MSBuild\Current\Bin',
    'C:\Program Files\Microsoft Visual Studio\18\Insiders\VC\Tools\MSVC\14.51.36231\bin\Hostx64\x64'
)
$new = $add | Where-Object { $currentPath -notlike "*$_*" }
if ($new) {
    [Environment]::SetEnvironmentVariable('Path', $currentPath + ';' + ($new -join ';'), 'User')
    Write-Host "Added: $($new -join ', ')"
} else {
    Write-Host 'All paths already in User PATH'
}