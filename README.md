# Local Development Startup

Windows:
  scripts\dev_start.bat
  scripts\dev_stop.bat

Start will:
- create venv
- install backend deps
- run alembic migrations
- seed data
- start backend (8000)
- install frontend deps
- start frontend (5173)

Stop will:
- kill processes listening on 8000 and 5173

## Default Accounts
- admin / admin123

## Frontend Acceptance
See: FRONTEND_CHECKLIST.md

## Known Limits
- 验证码仅日志输出（开发用）
- 评论深层结构待优化
