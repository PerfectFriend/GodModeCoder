---
title: Telegram Bot API Quick Reference
category: reference
---

# Telegram Bot API Quick Reference

## Base URL
```
https://api.telegram.org/bot<TOKEN>/
```

## Core Methods

| Method | HTTP | Description |
|--------|------|-------------|
| `getMe` | GET | Verify token, get bot info |
| `sendMessage` | POST | Send text message |
| `sendDocument` | POST (multipart) | Send file/document |
| `sendPhoto` | POST (multipart) | Send photo |
| `sendVideo` | POST (multipart) | Send video |
| `sendAudio` | POST (multipart) | Send audio |
| `sendVoice` | POST (multipart) | Send voice message |
| `editMessageText` | POST | Edit text of sent message |
| `deleteMessage` | POST | Delete message |
| `answerCallbackQuery` | POST | Answer inline button callback |
| `setMyCommands` | POST | Set bot command menu |
| `getUpdates` | GET | Long-polling (conflicts with gateway) |
| `setWebhook` | POST | Switch to webhook mode |

## sendMessage Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chat_id` | Integer/String | Yes | Target chat ID |
| `text` | String | Yes | Message text (1-4096 chars) |
| `parse_mode` | String | No | `MarkdownV2`, `HTML`, `Markdown` |
| `disable_web_page_preview` | Boolean | No | Disable link previews |
| `reply_to_message_id` | Integer | No | Reply to specific message |
| `reply_markup` | Object | No | Inline keyboard, etc. |

## sendDocument Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chat_id` | Integer/String | Yes | Target chat ID |
| `document` | InputFile/String | Yes | File to send (multipart) or file_id |
| `caption` | String | No | Caption (0-1024 chars) |
| `parse_mode` | String | No | `MarkdownV2`, `HTML`, `Markdown` |
| `disable_content_type_detection` | Boolean | No | Ignore MIME type |

## File Upload (multipart/form-data)

```python
files = {
    "document": ("filename.md", open("file.md", "rb"), "text/markdown")
}
# MIME types: text/markdown, text/plain, application/pdf, image/png, etc.
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request (encoding, invalid params) |
| 401 | Unauthorized (invalid token) |
| 404 | Not Found (chat_id, file_id) |
| 409 | Conflict (two getUpdates pollers) |
| 429 | Too Many Requests (rate limit) |
| 500 | Server Error |

## Rate Limits

- 30 messages/second to same chat
- 20 messages/minute to groups
- 1 message/second to same user (bot-initiated)
- 30 messages/second globally per bot

## Webhook vs Long-polling

| Mode | Pros | Cons |
|------|------|------|
| Long-polling | Simple, no public URL needed | Conflicts if multiple processes |
| Webhook | No conflicts, real-time | Needs HTTPS, public IP/domain |

**Hermes gateway uses long-polling by default**. For scripts/cron, use separate bot token.