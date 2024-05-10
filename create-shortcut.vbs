Dim fso, currentPath
Set fso = CreateObject("Scripting.FileSystemObject")
currentPath = fso.GetParentFolderName(WScript.ScriptFullName)

Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "Gucken.LNK"
Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "C:\Windows\py.exe"
    oLink.Arguments = "-m gucken"
 '  oLink.Description = "MyProgram"   
 '  oLink.HotKey = "ALT+CTRL+F"
 '  oLink.IconLocation = "C:\Program Files\MyApp\MyProgram.EXE, 2"
 '  oLink.WindowStyle = "1"   
    oLink.WorkingDirectory = currentPath & "\src"
oLink.Save
