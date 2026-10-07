$h = @{ "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36" }
Start-Sleep -Seconds 40
$page = (Invoke-WebRequest -Uri ("https://github.com/Gorilla-Kevv?cb=" + (Get-Random)) -UseBasicParsing -Headers $h -TimeoutSec 40).Content
$m = [regex]::Matches($page, "src=.{0,160}banner[^`"'\s>]*")
$m | ForEach-Object { Write-Output ("ref: " + $_.Value) }
if ($m.Count -eq 0) { Write-Output "ref: NOT FOUND" }
