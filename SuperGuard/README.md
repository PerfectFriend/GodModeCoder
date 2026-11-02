# SuperGuard Project

## Overview
Full-stack security monitoring system with React dashboard, FastAPI backend, and Telegram bot.

## Architecture
- **Frontend**: React + TypeScript + Vite (port 5173)
- **Backend**: FastAPI + SQLAlchemy + SQLite (port 8000)
- **Bot**: python-telegram-bot (@TotoMoto99Bot)
- **Hardware**: 2x Tuya plugs, 8x RTSP cameras, YOLOv8/InsightFace detectors

## Current Status (Post Dashboard Rewrite)
- ✅ Dashboard: Complete rewrite - working dark theme, collapsible sidebar, real API integration
- ✅ API: 34 endpoints, all functional
- ✅ Bot: Responds to commands
- 🔄 **Next**: Full functionality implementation (all buttons/actions working)

## Evolution Plan
Autonomous 50-cycle evolution with:
- Every 10 cycles: Tests + Debug + Telegram report
- End: Full audit + Telegram report

## Key Files
- Dashboard: `/home/thomas/SuperGuard/web-dashboard/src/App.tsx`
- API: `/home/thomas/SuperGuard/superguard-core/app/`
- Bot: `/home/thomas/SuperGuard/superguard-core/telegram/`

## API Endpoints (34 total)
See `API_ENDPOINTS.md` for full list.

## Credentials
- Dashboard login: `test@superguard.com` / `testpass123`
- API base: `http://127.0.0.1:8000`
- Dashboard: `http://localhost:5173`
