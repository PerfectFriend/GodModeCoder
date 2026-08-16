---
type: dashboard
tags: ["#evolution/graph", "#dashboard"]
---

# 📊 Evolution Graph — Dashboard

> [!abstract] Живой дашборд эволюционного графа Гримуара v3.0
> Автообновляется при каждом пульсе (каждые 6ч). Данные из `[[INDEX]]` + frontmatter узлов.

## 🎯 Быстрые фильтры

```dataview
TABLE WITHOUT ID
  "🟢 ЖИВ" AS "Статус", length(filter(nodes, (n) => n.status = "ЖИВ")) AS "Кол-во"
  UNION ALL
  "🟡 БОЛЕН" AS "Статус", length(filter(nodes, (n) => n.status = "БОЛЕН")) AS "Кол-во"
  UNION ALL
  "🔴 МЁРТВ" AS "Статус", length(filter(nodes, (n) => n.status = "МЁРТВ")) AS "Кол-во"
FROM "#evolution/graph"
WHERE type != "index" AND type != "dashboard"
```

## 📋 Все узлы (интерактивная таблица)

```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  type AS "Тип",
  status AS "Статус",
  role AS "Роль",
  links AS "Связей",
  genome AS "Геном",
  state AS "Состояние"
FROM "#evolution/graph"
WHERE type != "index" AND type != "dashboard"
SORT status DESC, type ASC, file.name ASC
```

## 🔴 Мёртвые узлы — кандидаты на экстинкцию/реанимацию

```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  type AS "Тип",
  role AS "Роль",
  genome AS "Геном",
  state AS "Состояние",
  file.mtime AS "Последний экспорт"
FROM "#evolution/graph"
WHERE status = "МЁРТВ" AND type != "MEMORY"
SORT file.mtime ASC
```

## 🧠 Агенты и пайплайны под контролем Gardener

```dataview
TABLE WITHOUT ID
  file.link AS "Узел",
  type AS "Тип",
  status AS "Статус",
  role AS "Роль",
  genome AS "Геном"
FROM "#evolution/graph"
WHERE (type = "AGENT" OR type = "PIPELINE") AND type != "MEMORY"
SORT status DESC, file.name ASC
```

## 📡 Рёбра графа (связи)

```dataviewjs
const pages = dv.pages('"Evolution"').where(p => p.type && p.type !== "index" && p.type !== "dashboard");
const edges = [];
for (const p of pages) {
  const content = await dv.io.load(p.file.path);
  const outMatch = content.match(/## Питает \(исходящие рёбра\)([\s\S]*?)(?=##|\Z)/);
  const inMatch = content.match(/## Кормит \(входящие рёбра\)([\s\S]*?)(?=##|\Z)/);
  if (outMatch) {
    const lines = outMatch[1].match(/^- .*→ \[\[([^\]]+)\]\]/gm) || [];
    for (const l of lines) {
      const m = l.match(/^- .*?(\w+) → \[\[([^\]]+)\]\]/);
      if (m) edges.push({from: p.file.name, type: m[1], to: m[2]});
    }
  }
  if (inMatch) {
    const lines = inMatch[1].match(/^- .*← \[\[([^\]]+)\]\]/gm) || [];
    for (const l of lines) {
      const m = l.match(/^- .*?(\w+) ← \[\[([^\]]+)\]\]/);
      if (m) edges.push({from: m[2], type: m[1], to: p.file.name});
    }
  }
}
dv.table(["От", "Тип", "К"], edges.map(e => [e.from, e.type, e.to]));
```

## ⚙️ Fitness-критерии (из graph.yaml)

```dataviewjs
const index = dv.pages('"Evolution"').where(p => p.file.name === "INDEX").first();
if (index) {
  const content = await dv.io.load(index.file.path);
  const fitMatch = content.match(/## Критерии fitness([\s\S]*?)(?=\*Обновлено|\Z)/);
  if (fitMatch) {
    dv.paragraph(fitMatch[1].trim());
  }
}
```

## 📈 Статистика графа

```dataviewjs
const pages = dv.pages('"Evolution"').where(p => p.type && p.type !== "index" && p.type !== "dashboard");
const nodes = pages.array();
const total = nodes.length;
const byType = {};
const byStatus = {};
let totalLinks = 0;
for (const n of nodes) {
  byType[n.type] = (byType[n.type] || 0) + 1;
  byStatus[n.status] = (byStatus[n.status] || 0) + 1;
  totalLinks += (n.links || 0);
}
const stats = [
  ["Всего узлов", total],
  ["Всего связей (сумма degree)", totalLinks],
  ["Средняя степень", (totalLinks / total).toFixed(1)],
];
for (const [t, c] of Object.entries(byType)) stats.push([`Тип: ${t}`, c]);
for (const [s, c] of Object.entries(byStatus)) stats.push([`Статус: ${s}`, c]);
dv.table(["Метрика", "Значение"], stats);
```

---

*Обновляется автоматически при каждом запуске `export_graph_to_obsidian.py` (крон каждые 6ч).*