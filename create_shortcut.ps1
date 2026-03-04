$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$Desktop\Document Download.lnk")
$Shortcut.TargetPath = "C:\Users\hcrisapulli\Downloads\claudecode\webapp\start_webapp.bat"
$Shortcut.WorkingDirectory = "C:\Users\hcrisapulli\Downloads\claudecode\webapp"
$Shortcut.Description = "Launch Document Download Web Application"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop successfully!"
