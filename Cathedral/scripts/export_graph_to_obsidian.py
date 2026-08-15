#!/usr/bin/env python3
"""
export_graph_to_obsidian.py — визуализация Эволюционного Графа (Гримуар v3.0)
в Obsidian: каждый узел = заметка с [[wiki-ссылками]] на соседей, фронтматтер
для Dataview, статусы ЖИВ/БОЛЕН/МЁРТВ из pulse.py. Graph View Obsidian
построит интерактивный граф автоматически из ссылок.

Запуск:  python export_graph_to_obsidian.py [--vault C:\Vault] [--config ru/configs/graph.yaml]
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

TYPE_EMOJI = {
    "HUMAN": "🧑‍🔬",
    "AGENT": "🤖",
    "SKILL": "📜",
    "PIPELINE": "⚙️",
    "MEMORY": "🗄️",
    "WATCHDOG": "🩺",
    "GATEWAY": "📡",
}
TYPE_COLOR = {
    "HUMAN": "#e67e22",
    "AGENT": "#3498db",
    "SKILL": "#9b59b6",
    "PIPELINE": "#2ecc71",
    "MEMORY": "#95a5a6",
    "WATCHDOG": "#e74c3c",
    "GATEWAY": "#f39c12",
}
EDGE_EMOJI = {
    "FEEDS": "🍽️",
    "CALLS": "🤝",
    "CONTROLS": "🧠",
    "EVALUATES": "⚖️",
    "MUTATES": "🧬",
    "BACKUPS": "🛡️",
    "VISION": "👁️",
    "APPROVAL": "✅",
}

def load_graph(config_path: Path):
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_pulse(config_path: Path) -> dict:
    """Запускаем pulse.py и парсим статусы узлов (ЖИВ/БОЛЕН/МЁРТВ).

    Формат вывода pulse.py:
      [2026-08-05 05:25:20] PULSE: 3/7 живы      <- сводка
      ☠ gardener (AGENT): http http://...        <- мёртвый
      ⚠ dj (AGENT): ...                          <- больной (если есть)
    Живые узлы НЕ выводятся (тишина = здоровье).
    """
    try:
        out = subprocess.run(
            [sys.executable, str(config_path.parent.parent / "scripts" / "pulse.py"), "--quiet"],
            capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
        text = out.stdout + "\n" + out.stderr
    except Exception as e:
        return {"_error": str(e)}

    # статусы тех, кто НЕ выведен как мёртвый/больной, но упомянут в сводке → ЖИВ
    statuses = {}
    dead_or_sick = set()
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^(☠|⚠|✓)\s+([\w\-]+)\s+\((\w+)\)", line)
        if m:
            nid = m.group(2).lower()
            sym = m.group(1)
            statuses[nid] = {"☠": "МЁРТВ", "⚠": "БОЛЕН", "✓": "ЖИВ"}.get(sym, "—")
            dead_or_sick.add(nid)
        # quiet-формат: "[timestamp] PULSE: МЁРТВЫЕ: gardener, dj, ..."
        mq = re.search(r"PULSE:\s*МЁРТВЫЕ?:\s*(.*)$", line, re.IGNORECASE)
        if mq:
            for nid in re.split(r"[,\s]+", mq.group(1)):
                nid = nid.strip().lower()
                if nid:
                    statuses[nid] = "МЁРТВ"
                    dead_or_sick.add(nid)
        # формат "PULSE: N/M живы"
        m = re.search(r"PULSE:\s*(\d+)/(\d+)", line)
        if m and not mq:
            graph = load_graph(config_path)
            node_ids = [n.get("id", "").lower() for n in graph.get("nodes", []) if n.get("id")]
            for nid in node_ids:
                if nid not in dead_or_sick:
                    statuses[nid] = "ЖИВ"
    # если ни одного формата не распознано — все узлы без явного статуса ЖИВ
    graph = load_graph(config_path)
    node_ids = [n.get("id", "").lower() for n in graph.get("nodes", []) if n.get("id")]
    for nid in node_ids:
        if nid not in statuses:
            statuses[nid] = "ЖИВ"
    return statuses


def sanitize(name: str) -> str:
    """Имя файла заметки — без спецсимволов Obsidian-файловой системы."""
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip()


def node_file(nid: str) -> str:
    return sanitize(nid)


def render_node(nid: str, node: dict, edges: list, statuses: dict) -> str:
    ntype = node.get("type", "MEMORY")
    role = node.get("role", "")
    genome = node.get("genome") or ""
    state = node.get("state", "")
    status = statuses.get(nid.lower(), "—")
    emoji = TYPE_EMOJI.get(ntype, "📦")
    color = TYPE_COLOR.get(ntype, "#888")

    out_edges = [e for e in edges if e.get("from") == nid]
    in_edges = [e for e in edges if e.get("to") == nid]

    # Tags for graph filtering and Dataview queries
    type_tag = f"#type/{ntype.lower()}"
    # Normalize status to English for tags
    status_en = {"ЖИВ": "alive", "БОЛЕН": "sick", "МЁРТВ": "dead", "—": "unknown"}.get(status, "unknown")
    status_tag = f"#status/{status_en}"
    role_slug = role.lower().replace(" ", "-").replace("—", "").replace(".", "").replace(",", "").replace("(", "").replace(")", "").replace(":", "").replace("/", "-").replace("+", "").replace("ё", "e").replace("ъ", "").replace("ь", "")
    # Keep only alphanumeric, dash, underscore, кириллицу
    import re
    role_slug = re.sub(r'[^\w\-а-яё]', '', role_slug, flags=re.IGNORECASE)
    role_slug = re.sub(r'-+', '-', role_slug).strip('-')
    role_tag = f"#role/{role_slug}" if role_slug else ""
    graph_tag = "#evolution/graph"

    tags_list = [type_tag, status_tag, graph_tag]
    if role_tag:
        tags_list.append(role_tag)

    lines = [
        "---",
        f"type: {ntype}",
        f"status: \"{status}\"",
        f"color: \"{color}\"",
        f"role: \"{role}\"",
        f"genome: \"{genome}\"",
        f"state: \"{state}\"",
        f"links: {len(out_edges) + len(in_edges)}",
        "tags:",
    ] + [f"  - \"{t}\"" for t in tags_list] + [
        "---",
        "",
        f"# {emoji} {nid.upper()}",
        "",
        f"> [!info] **{ntype}** · Пульс: **{status}**",
        "",
    ]
    if role:
        lines += [f"**Роль:** {role}", ""]
    if genome:
        lines += [f"**Геном:** `{genome}`", ""]
    if state:
        lines += [f"**Состояние:** `{state}`", ""]
    lines += [
        "",
        "## Питает (исходящие рёбра)",
    ]
    if out_edges:
        for e in out_edges:
            et = EDGE_EMOJI.get(e.get("type", ""), "🔗")
            lines.append(f"- {et} **{e.get('type')}** → [[{node_file(e['to'])}]]")
    else:
        lines.append("_нет_")
    lines += [
        "",
        "## Кормит (входящие рёбра)",
    ]
    if in_edges:
        for e in in_edges:
            et = EDGE_EMOJI.get(e.get("type", ""), "🔗")
            lines.append(f"- {et} **{e.get('type')}** ← [[{node_file(e['from'])}]]")
    else:
        lines.append("_нет_")
    lines += ["", "---", f"*Экспорт из `graph.yaml` · {datetime.now():%Y-%m-%d %H:%M}*", ""]
    return "\n".join(lines)


def render_index(graph: dict, statuses: dict, vault: Path) -> str:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    fitness = graph.get("fitness", {})
    alive = sum(1 for n in nodes if statuses.get(n.get("id", "").lower()) == "ЖИВ")
    sick = sum(1 for n in nodes if statuses.get(n.get("id", "").lower()) == "БОЛЕН")
    dead = sum(1 for n in nodes if statuses.get(n.get("id", "").lower()) == "МЁРТВ")
    unknown = len(nodes) - alive - sick - dead

    lines = [
        "---",
        "type: index",
        "---",
        "",
        "# 🧬 Эволюционный Граф — Индекс",
        "",
        "> [!abstract] Живой граф проектов Гримуара",
        f"> Узлов: **{len(nodes)}** · Рёбер: **{len(edges)}** · "
        f"🟢 ЖИВ: **{alive}** · 🟡 БОЛЕН: **{sick}** · 🔴 МЁРТВ: **{dead}** · ⚪ неизвестно: **{unknown}**",
        "",
        "## Карта узлов",
        "",
        "| Узел | Тип | Пульс | Роль |",
        "|---|---|---|---|",
    ]
    for n in nodes:
        nid = n.get("id", "")
        ntype = n.get("type", "")
        emoji = TYPE_EMOJI.get(ntype, "📦")
        st = statuses.get(nid.lower(), "—")
        marker = {"ЖИВ": "🟢", "БОЛЕН": "🟡", "МЁРТВ": "🔴"}.get(st, "⚪")
        role = (n.get("role") or "")[:50]
        lines.append(f"| {marker} [[{node_file(nid)}]] | {emoji} {ntype} | {st} | {role} |")
    lines += [
        "",
        "## Рёбра",
        "",
        "| От | Тип | К |",
        "|---|---|---|",
    ]
    for e in edges:
        et = EDGE_EMOJI.get(e.get("type", ""), "🔗")
        lines.append(
            f"| [[{node_file(e['from'])}]] | {et} {e.get('type')} | [[{node_file(e['to'])}]] |")
    lines += [
        "",
        "## Критерии fitness",
        "",
    ]
    if isinstance(fitness, dict) and fitness:
        for k, v in fitness.items():
            lines.append(f"- **{k}:** `{v}`")
    else:
        lines.append(f"```yaml\n{fitness}\n```")
    lines += ["", f"*Обновлено: {datetime.now():%Y-%m-%d %H:%M}*", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=r"C:\Vault", help="путь к хранилищу Obsidian")
    ap.add_argument("--config", default=None, help="путь к graph.yaml")
    args = ap.parse_args()

    vault = Path(args.vault)
    out_dir = vault / "Evolution"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.config:
        cfg_path = Path(args.config)
    else:
        cfg_path = Path(__file__).parent.parent / "configs" / "graph.yaml"
    graph = load_graph(cfg_path)
    statuses = run_pulse(cfg_path)

    written = []
    for node in graph.get("nodes", []):
        nid = node.get("id", "")
        if not nid:
            continue
        fname = out_dir / f"{node_file(nid)}.md"
        fname.write_text(render_node(nid, node, graph.get("edges", []), statuses), encoding="utf-8")
        written.append(fname.name)
    index = out_dir / "INDEX.md"
    index.write_text(render_index(graph, statuses, vault), encoding="utf-8")

    print(f"=== ЭКСПОРТ В OBSIDIAN: {out_dir} ===")
    print(f"Заметок: {len(written)} + INDEX.md")
    print(f"Статусы: {statuses}")
    if "_error" in statuses:
        print(f"⚠ pulse.py: {statuses['_error']}")


if __name__ == "__main__":
    main()
