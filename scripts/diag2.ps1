$snake = (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Gorilla-Kevv/Gorilla-Kevv/main/dist/github-contribution-grid-snake.svg" -UseBasicParsing -TimeoutSec 40).Content
Write-Output ("len: " + $snake.Length)
Write-Output ($snake.Substring(0, [Math]::Min(1200, $snake.Length)))
Write-Output "..."
$fx = [regex]::Matches($snake, "fill[:=]""?\s*(#[0-9a-fA-F]{6}|rgb[^;""\)]+)")
$fx | ForEach-Object { $_.Groups[1].Value.ToLower() } | Group-Object | Sort-Object Count -Descending | Select-Object -First 12 | ForEach-Object { Write-Output ("color {0}: {1}" -f $_.Name, $_.Count) }
