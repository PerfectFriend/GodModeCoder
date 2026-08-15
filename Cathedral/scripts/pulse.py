#!/usr/bin/env python3
"""
PULSE — сердце Графической Эволюции (Гримуар v3.0)
Проверяет здоровье узлов графа и сообщает статусы: ЖИВ / БОЛЕН / МЁРТВ.

Запуск:  python pulse.py [--quiet] [--config graph.yaml]
--quiet:  тишина при полном здоровье (для cron-воркера: тишина = здоровье)
"""

import json
import sys
import subprocess
import urllib.request
import socket
from pathlib import Path
from datetime import datetime

CONFIG = Path(__file__).parent / ".." / "configs" / "graph.yaml"
QUIET = "--quiet" in sys.argv
if "--config" in sys.argv:
    CONFIG = Path(sys.argv[sys.argv.index("--config") + 1])


def http_ok(url: str, timeout: float = 8.0) -> bool:
    """Проверка HTTP-узла."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return 200 <= r.status < 500  # 4xx — сервер жив, но что-то не так; считаем живым
    except Exception:
        return False


def port_open(port: int, host: str = "127.0.0.1", timeout: float = 2.0) -> bool:
    """Проверка TCP-порта."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def proc_alive(pattern: str) -> bool:
    """Проверка процесса по имени (Windows: tasklist, иначе pgrep).

    На Windows tasklist отдаёт OEM-кодировку (cp866), а не utf-8 —
    читаем байты и декодируем с запасом.
    Для .py-скриптов ищем python-процесс, запущенный с этим именем.
    """
    try:
        if sys.platform == "win32":
            if pattern.endswith(".py"):
                # python.exe ...\scripts\dj.py — ищем имя скрипта в командной строке
                out = subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     f"(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                     f"Where-Object {{ $_.CommandLine -match '{pattern}' }}).Count"],
                    capture_output=True, timeout=15)
                raw = out.stdout.decode("utf-8", errors="ignore").strip()
                return raw.isdigit() and int(raw) > 0
            out = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {pattern}"],
                                 capture_output=True, timeout=10)
            raw = out.stdout.decode("cp866", errors="ignore")
            return pattern.lower() in raw.lower()
        out = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True, timeout=10).stdout
        return bool(out.strip())
    except Exception:
        return False


def check_node(node: dict) -> dict:
    """Проверка одного узла по его типу и геному."""
    nid = node.get("id", "?")
    genome = node.get("genome", "")
    checks = []
    alive = None

    # SKILL-узел (skill:имя) — проверяем наличие в Hermes skills
    if genome.startswith("skill:"):
        skill_name = genome[6:]
        import os
        skill_dirs = [
            os.path.expandvars(r"%LOCALAPPDATA%\hermes\skills"),
            os.path.expanduser("~/.hermes/skills"),
        ]
        alive = any(
            Path(d).joinpath(skill_name, "SKILL.md").exists()
            or any(Path(d).glob(f"*/{skill_name}/SKILL.md"))
            for d in skill_dirs if os.path.isdir(d)
        )
        checks.append(f"skill {skill_name}")

    # URL-узел (http://...)
    elif genome.startswith("http://") or genome.startswith("https://"):
        alive = http_ok(genome)
        checks.append(f"http {genome}")

    # Порт (:8090 и т.п.)
    elif genome.startswith(":"):
        try:
            port = int(genome[1:].split("/")[0])
            alive = port_open(port)
            checks.append(f"port {port}")
        except ValueError:
            alive = False
            checks.append("bad-port-spec")

    # Процесс (имя exe)
    elif genome.endswith(".exe") or genome.endswith(".py"):
        name = Path(genome).name
        alive = proc_alive(name)
        checks.append(f"proc {name}")

    # Файл-узел (существование генома)
    else:
        p = Path(genome)
        alive = p.exists()
        checks.append(f"file {p.name if p.name else genome}")

    status = "ЖИВ" if alive else "МЁРТВ"
    return {"id": nid, "type": node.get("type"), "status": status, "checks": checks}


def main():
    import yaml
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    results = [check_node(n) for n in cfg.get("nodes", [])
               if n.get("state") == "active" and n.get("type") != "HUMAN"]

    dead = [r for r in results if r["status"] == "МЁРТВ"]
    alive_count = len(results) - len(dead)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if dead and not QUIET:
        print(f"[{ts}] PULSE: {alive_count}/{len(results)} живы")
        for r in dead:
            print(f"  ☠ {r['id']} ({r['type']}): {', '.join(r['checks'])}")
        sys.exit(1)
    elif dead and QUIET:
        # даже в тихом режиме мёртвые узлы — не тишина
        print(f"[{ts}] PULSE: МЁРТВЫЕ: " + ", ".join(r["id"] for r in dead))
        sys.exit(1)
    else:
        if not QUIET:
            print(f"[{ts}] PULSE: все {alive_count} узлов живы. Тишина = здоровье.")
        sys.exit(0)


if __name__ == "__main__":
    main()
