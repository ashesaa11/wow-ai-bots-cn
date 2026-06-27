$auth = Start-Process -FilePath "D:\WOW\build\bin\RelWithDebInfo\authserver.exe" -WorkingDirectory "D:\WOW\build\bin\RelWithDebInfo" -PassThru
Write-Host "Authserver PID: $($auth.Id)"
Start-Sleep 8
$world = Start-Process -FilePath "D:\WOW\build\bin\RelWithDebInfo\worldserver.exe" -WorkingDirectory "D:\WOW\build\bin\RelWithDebInfo" -PassThru
Write-Host "Worldserver PID: $($world.Id)"
Start-Sleep 5
if ($world.HasExited) { Write-Host "Worldserver EXITED: $($world.ExitCode)" } else { Write-Host "Worldserver RUNNING" }
