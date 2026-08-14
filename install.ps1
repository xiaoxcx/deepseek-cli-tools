# DeepSeek CLI Tools — Windows installer (PowerShell)
# Adds dsh-poster / dsh-drama / dsh-monetize / dsh-studio commands (as .cmd shims).

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallDir = Join-Path $env:USERPROFILE ".deepseek-cli-tools"
$BinDir = Join-Path $InstallDir "bin"
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# Copy tools
Copy-Item -Recurse -Force (Join-Path $RepoRoot "poster") $InstallDir
Copy-Item -Recurse -Force (Join-Path $RepoRoot "drama") $InstallDir
Copy-Item -Recurse -Force (Join-Path $RepoRoot "book-monetize") $InstallDir
Copy-Item -Recurse -Force (Join-Path $RepoRoot "content-studio") $InstallDir

# Create .cmd shims
$tools = @{
  "dsh-poster"   = "poster\poster.py"
  "dsh-drama"    = "drama\drama.py"
  "dsh-monetize" = "book-monetize\monetize.py"
  "dsh-studio"   = "content-studio\studio.py"
}
foreach ($k in $tools.Keys) {
  $shim = Join-Path $BinDir "$k.cmd"
  "@echo off`r`npython `"$InstallDir\$($tools[$k])`" %*" | Set-Content -Encoding ASCII $shim
}

# Add to user PATH (persistent)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$BinDir*") {
  [Environment]::SetEnvironmentVariable("Path", "$userPath;$BinDir", "User")
  Write-Host "✅ Added $BinDir to user PATH"
}
$env:Path = "$env:Path;$BinDir"

Write-Host ""
Write-Host "🎉 Installed! Open a NEW terminal, then:"
Write-Host "   dsh-poster    `"AI course`" --layout portrait"
Write-Host "   dsh-drama     `"a broke student finds a magic notebook`""
Write-Host "   dsh-monetize  book.txt"
Write-Host "   dsh-studio    `"topic`" --count 5"
Write-Host ""
Write-Host "👉 Set your key: set DEEPSEEK_API_KEY=sk-xxxx"
