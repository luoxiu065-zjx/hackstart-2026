# 把本机的 ORCHESTRA 开成一个公网链接，到点自动关。
#   用法:  powershell -File share.ps1
#   停止:  关掉这个窗口，或者等它自己到点
#
# 两道保险：
#   1. 应用自己在 60 分钟后整站返回 410（app/guard.py 的 OPEN_MINUTES）
#   2. 这个脚本在 60 分钟后杀掉隧道，链接直接失效
param([int]$Minutes = 60)

$exe = "D:\apps\cloudflared\cloudflared.exe"
if (-not (Test-Path $exe)) { Write-Host "找不到 cloudflared"; exit 1 }

Write-Host "正在开隧道…（链接出现后会显示在下面）"
$log = Join-Path $env:TEMP "orchestra-tunnel.log"
if (Test-Path $log) { Remove-Item $log -Force }

$p = Start-Process $exe -ArgumentList "tunnel","--url","http://localhost:8001","--no-autoupdate" `
     -RedirectStandardError $log -RedirectStandardOutput "$log.out" -PassThru -WindowStyle Hidden

$url = $null
for ($i = 0; $i -lt 40; $i++) {
  Start-Sleep -Milliseconds 800
  if (Test-Path $log) {
    $m = Select-String -Path $log -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" -ErrorAction SilentlyContinue |
         Select-Object -First 1
    if ($m) { $url = $m.Matches[0].Value; break }
  }
}

if (-not $url) { Write-Host "隧道没起来，看日志: $log"; exit 1 }

Write-Host ""
Write-Host "  公网地址:  $url"
Write-Host "  有效期:    $Minutes 分钟（到点后链接和应用同时失效）"
Write-Host ""
$url | Set-Clipboard
Write-Host "  （已复制到剪贴板）"

Start-Sleep -Seconds ($Minutes * 60)
Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
Write-Host "已到期，隧道已关闭。"
