Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "D:\05_Çé±¨\AI-Tools\dumate-checkin"
sh.Run "cmd /c node daily-checkin.js --once --only=dumate >> dumate_checkin.log 2>&1", 0, False
