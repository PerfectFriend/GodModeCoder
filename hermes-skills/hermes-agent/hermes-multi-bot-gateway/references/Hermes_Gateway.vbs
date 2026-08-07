' =============================================================================
' TEMPLATE: Hermes Gateway Launcher (VBS) - <BOT-NAME>
' Copy to gateways/<bot-name>/Hermes_Gateway.vbs and update paths
' =============================================================================

Option Explicit
Dim sh, env, existing_pp, target, dotenv

target = "C:\Users\tomas\AppData\Local\hermes\gateways\<bot-name>\Hermes_Gateway.cmd"
dotenv = "C:\Users\tomas\AppData\Local\hermes\gateways\<bot-name>\.env"

Set sh = CreateObject("WScript.Shell")
Set env = sh.Environment("PROCESS")

env.Item("HERMES_HOME") = "C:\Users\tomas\AppData\Local\hermes"
env.Item("DOTENV_PATH") = dotenv
env.Item("PYTHONIOENCODING") = "utf-8"
env.Item("HERMES_GATEWAY_DETACHED") = "1"
env.Item("VIRTUAL_ENV") = "C:\Users\tomas\AppData\Local\hermes\hermes-agent\venv"

existing_pp = env.Item("PYTHONPATH")
If Len(existing_pp) > 0 Then
  env.Item("PYTHONPATH") = "C:\Users\tomas\AppData\Local\hermes\hermes-agent;" & existing_pp
Else
  env.Item("PYTHONPATH") = "C:\Users\tomas\AppData\Local\hermes\hermes-agent"
End If

sh.CurrentDirectory = "C:\Users\tomas\AppData\Local\hermes"
sh.Run "wscript.exe //B " & target, 0, False