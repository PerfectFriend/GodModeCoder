# Theory: X (Twitter) Algorithm Playbook

> **Источник:** X algorithm open-sourced (300K+ lines, анализ @AlexFinn).
> **Применение:** Максимизация охвата, защита от теневого бана, постинг-оптимизация.

## 1. Как пойти в вирал (факторы ранжирования)
| Фактор | Вес | Нюанс |
|--------|-----|-------|
| **Engagement velocity** | High | Первые 30-60 мин критичны |
| **Author reputation** | High | Verified, история вовлечённости |
| **Content type** | Medium | Video > Images > Text > **Links (пенальти)** |
| **Topic relevance** | Medium | Интерес-граф + семантика |
| **Recency** | High | Экспоненциальный decay, half-life 2-4ч |
| **Network effects** | High | КТО вовлечён важнее ЧЕМ СКОЛЬКО |

## 2. Теневой бан — реальность
- **Visibility filtering** — «low quality»/«spammy» → режут дистрибуцию
- **Account-level scoring** — новые/низкореп аккаунты подавляются
- **Content labels** — «misinformation»/«spam» режут охват
- **Нет хард-бана** — контент в профиле доступен, но не в For You/Following

### Признаки теневого бана
- Reach упал > 20% WoW без причины
- Профиль не ищется по имени
- Импрессии твита < 10% от нормы

## 3. Ranking Pipeline (упрощённо)
```
Candidate Gen (1500 tweets)
  → Ranking Model (LightGBM/Neural)
  → Heuristics & Filters
  → Final (Top 50 → For You)
```

### Ключевые фичи (из кода)
```python
features = {
  "like_count_30min": float,      # сильные сигналы
  "retweet_count_30min": float,
  "reply_count_30min": float,
  "quote_count_30min": float,
  "bookmark_count_30min": float,  # СИЛЬНЫЙ сигнал!
  "author_verified": bool,
  "has_media": bool,
  "media_type": "video|image|gif|none",
  "has_links": bool,              # NEGATIVE
  "engager_follower_count": float, # кто вовлечён = важно
}
```

## 4. Actionable (наши проекты)
| Стратегия | Реализация |
|-----------|-----------|
| **Native content** | Ссылки НЕ в основном твите → класть в reply |
| **Video first** | 15-60с демо продукта, дашборды, алерты |
| **Engagement bait** | Вопросы, опросы, «thoughts?» (реплаи = вес) |
| **Bookmark-worthy** | Треды с чек-листами, фреймворками, шаблонами |
| **Timing** | Когда твоя аудитория активна (аналитика) |
| **Consistency** | Ежедневный постинг → рост author reputation |
| **Verified** | Gold/Blue чек = буст ранжирования |
| **Engage back** | Реплаи на ВСЕ комменты в первый час |

## 5. XAlgorithmOptimizer (код)
```python
class XAlgorithmOptimizer:
    def score_draft(self, tweet: str, media_type: str = None) -> float:
        score = 0.0
        if 100 <= len(tweet) <= 280: score += 0.2
        if "?" in tweet: score += 0.15
        if any(c.isdigit() for c in tweet): score += 0.1
        if media_type == "video": score += 0.3
        elif media_type == "image": score += 0.2
        if "http" in tweet: score -= 0.4
        return min(max(score, 0), 1)

    def optimal_post_time(self, audience_tz="UTC") -> list:
        return ["08:00-09:00", "12:00-13:00", "17:00-19:00", "21:00-22:00"]

    def format_for_algorithm(self, content: str, link: str = None) -> dict:
        return {"main_tweet": content, "reply_with_link": link,
                "media": "generate_video_or_image()"}
```

## Hard Rules
- Ссылки убивают охват. Всегда в reply.
- Видео > картинка > текст. Bookmarks = топ-сигнал.
- Скорость вовлечения в первый час решает всё.
