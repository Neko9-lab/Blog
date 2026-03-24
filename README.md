# Blog Forum / 博客论坛系统

## English Introduction
Blog Forum is a full-stack discussion platform built for personal creators, small communities, and technical forums. It provides a Vue-based frontend, a FastAPI backend, PostgreSQL for persistent storage, Redis for caching and rate limiting, and Alembic for database migrations.

The project focuses on a forum-style experience instead of a pure blog layout. Users can publish posts, edit content with a Markdown editor, comment, receive notifications, like and favorite posts, and manage personal content from a dedicated center. Administrators can manage users, categories, posts, site settings, logs, and moderation actions such as banning users, pinning posts, and marking featured posts.

### Main Features
- User registration, login, token refresh, and password reset flow
- Post publishing, editing, deletion, and rich Markdown editing via Vditor
- Comments, likes, favorites, and notification center
- Personal profile and content center
- Admin dashboard for users, categories, site settings, logs, and post moderation
- Forum-style homepage with hot posts, active sorting, featured/pinned labels, and content metrics
- PostgreSQL + Redis architecture with Alembic migration support

## 中文介绍
Blog Forum 是一个面向个人创作者、小型社区和技术论坛场景的全栈讨论系统，前端基于 Vue，后端基于 FastAPI，使用 PostgreSQL 进行持久化存储，使用 Redis 做缓存和限流，并通过 Alembic 管理数据库迁移。

这个项目的定位更偏向“论坛式内容社区”，而不是传统博客首页。用户可以发帖、编辑 Markdown 正文、评论、接收通知、点赞、收藏，并在个人内容中心管理自己的帖子和收藏。管理员可以管理用户、分类、帖子、站点配置、系统日志，以及执行封号、置顶、设为精华等操作。

### 主要功能
- 用户注册、登录、Token 刷新与密码重置
- 帖子发布、编辑、删除，支持 Vditor Markdown 编辑器
- 评论、点赞、收藏与通知中心
- 个人资料与内容中心
- 管理后台支持用户、分类、站点配置、日志、帖子管理
- 首页采用论坛化展示，支持热帖、活跃排序、精华/置顶标识与互动数据展示
- 基于 PostgreSQL + Redis 的系统架构，并支持 Alembic 数据库迁移

## Project Structure / 项目结构
- `backend/`: FastAPI backend, Alembic config, app logic, models, schemas, and scripts
- `frontend/`: Vue frontend, routes, views, components, and build config
- `docker-compose.yml`: one-command Docker deployment entry
- `nginx.conf`: frontend static serving and API reverse proxy configuration
- `requirements.txt`: backend Python dependencies
- `package.json`: project package metadata

## Local Development / 本地开发
### Windows
```powershell
scripts\dev_start.bat
scripts\dev_stop.bat
```

The start script will:
- create a Python virtual environment
- install backend dependencies
- run Alembic migrations
- seed initial data
- start backend on `8000`
- install frontend dependencies
- start frontend on `5173`

停止脚本会关闭占用 `8000` 和 `5173` 端口的进程。

## Docker Deployment / Docker 一键部署
Use the following command in the project root:

```powershell
docker compose up --build -d
```

After startup:
- Frontend: `http://localhost`
- Backend API: exposed through `http://localhost/api/`
- Static uploads: exposed through `http://localhost/static/`

Stop services:
```powershell
docker compose down
```

Rebuild after code changes:
```powershell
docker compose up --build -d
```

### Deployment Notes / 部署说明
- Docker deployment uses PostgreSQL and Redis containers with named volumes
- Backend container automatically runs `alembic upgrade head` before starting the app
- Frontend is built in production mode and served by Nginx
- Environment variables are loaded from `.env.example`; in production you should replace this with a real `.env`

## Default Account / 默认账号
- `admin / admin123`

## Frontend Acceptance / 前端验收
See: `FRONTEND_CHECKLIST.md`

## Known Limits / 已知限制
- Verification codes are only printed to logs in development mode
- Deep nested comments still need further optimization
- Some frontend build chunks are still relatively large and can be further optimized later
