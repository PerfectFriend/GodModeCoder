#!/usr/bin/env python3
"""
Verify all Hermes gateway processes are healthy.
Run via: python verify_gateways.py
"""
import subprocess
import sys
import json

GATEWAYS = [
    "Cathedral", "Torquemada", "Nexus", "Node2Bot", "Elemental",
    "NodeBot", "Шурген420", "StonedBot", "Tomas", "Steward",
    "MyGemma", "DarkPushkin", "MasterInquisitor", "SuperGuard", "RedShredZombie"
]

def check_scheduled_tasks():
    """Check all gateway scheduled tasks exist and are Ready."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-ScheduledTask -TaskName 'Hermes-Gateway-*' | Select-Object TaskName, State | ConvertTo-Json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, f"PowerShell error: {result.stderr}"
        tasks = json.loads(result.stdout)
        if isinstance(tasks, dict):
            tasks = [tasks]
        results = {}
        for task in tasks:
            name = task.get("TaskName", "")
            state = task.get("State", "")
            results[name] = state == "Ready"
        return True, results
    except Exception as e:
        return False, str(e)

def check_gateway_processes():
    """Check running gateway python processes."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-WmiObject Win32_Process -Filter \"Name='python.exe' AND CommandLine LIKE '%gateway%'\" | Select-Object ProcessId, @{n='MemMB';e={'{0:N1}' -f ($_.WorkingSetSize/1MB)}}, @{n='PrivMB';e={'{0:N1}' -f ($_.PrivatePageCount/1MB)}}, CommandLine | ConvertTo-Json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, f"PowerShell error: {result.stderr}"
        processes = json.loads(result.stdout)
        if isinstance(processes, dict):
            processes = [processes]
        return True, processes
    except Exception as e:
        return False, str(e)

def main():
    print("=== Hermes Multi-Bot Gateway Health Check ===\n")
    
    # Check scheduled tasks
    print("1. Checking Scheduled Tasks...")
    ok, task_results = check_scheduled_tasks()
    if not ok:
        print(f"  ERROR: {task_results}")
        return 1
    for name, ready in task_results.items():
        status = "✅" if ready else "❌"
        print(f"  {status} {name}: {'Ready' if ready else 'Not Ready'}")
    
    # Check running processes
    print("\n2. Checking Running Gateway Processes...")
    ok, processes = check_gateway_processes()
    if not ok:
        print(f"  ERROR: {processes}")
        return 1
    if processes:
        if isinstance(processes, dict):
            processes = [processes]
        for proc in processes:
            pid = proc.get("ProcessId", "?")
            mem = proc.get("MemMB", "?")
            priv = proc.get("PrivMB", "?")
            cmd = proc.get("CommandLine", "")[:80]
            print(f"  PID {pid}: WS={mem}MB Private={priv}MB | {cmd}...")
    else:
        print("  ⚠️  No gateway processes found!")
    
    # Check gateway status via hermes CLI
    print("\n3. Checking Gateway Status via hermes CLI...")
    try:
        result = subprocess.run(
            ["hermes", "gateway", "status"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"  ✅ {result.stdout.strip()}")
        else:
            print(f"  ❌ {result.stderr.strip()}")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    print("\n=== Health Check Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())