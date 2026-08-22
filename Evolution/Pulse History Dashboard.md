---
type: dashboard
---

# 📈 Pulse History Dashboard

> [!abstract] История пульса графа — живость системы во времени
> CSV: `Evolution/pulse-history.csv`

## 📊 Последние замеры

```dataview
TABLE WITHOUT ID
  date AS "Дата",
  time AS "Время",
  alive + "/" + total AS "Живых",
  dead_count AS "Мёртвых",
  dead_names AS "Мёртвые узлы"
FROM "Evolution"
WHERE file.name = "pulse-history"
SORT date DESC, time DESC
LIMIT 20
```

## 🔥 Heatmap — живость графа по дням

```dataviewjs
const csv = await dv.io.csv("Evolution/pulse-history.csv");
if (!csv) {
  dv.paragraph("⚠️ CSV не найден. Запустите: python pulse-history.py");
} else {
  // Group by date, get min alive count per day
  const byDate = {};
  for (const row of csv) {
    const d = row.date;
    const alive = parseInt(row.alive);
    if (!byDate[d] || byDate[d] > alive) byDate[d] = alive;
  }
  
  // Render as table
  const rows = Object.entries(byDate)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .slice(0, 30)
    .map(([date, alive]) => [date, `${alive}/21`, alive === 21 ? "🟢" : alive >= 19 ? "🟡" : "🔴"]);
  
  dv.table(["Дата", "Живых", "Статус"], rows);
}
```

## 📋 Статистика

```dataviewjs
const csv = await dv.io.csv("Evolution/pulse-history.csv");
if (csv && csv.length > 0) {
  const totalRuns = csv.length;
  const allGreen = csv.filter(r => parseInt(r.dead_count) === 0).length;
  const withDead = totalRuns - allGreen;
  const avgAlive = (csv.reduce((s, r) => s + parseInt(r.alive), 0) / totalRuns).toFixed(1);
  
  dv.paragraph(`**Всего замеров:** ${totalRuns} · **Все живы:** ${allGreen} · **С мёртвыми:** ${withDead} · **Среднее живых:** ${avgAlive}/21`);
} else {
  dv.paragraph("⚠️ CSV не найден. Запустите: python pulse-history.py");
}
```

---

*Авто-генерация: cron `pulse-history.py` каждые 6ч · Источник: `Evolution/pulse-history.csv`*
