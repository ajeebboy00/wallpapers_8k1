# Wallpapers_8k1 (W8K1)

> **Production-Grade Full-Stack 8K Wallpaper Discovery & Distribution Platform**

Wallpapers_8k1 is a high-performance commercial wallpaper ecosystem featuring a Flutter mobile client (Android first, iOS extensible), a high-throughput Python FastAPI REST API, a normalized PostgreSQL 15+ database with Alembic migrations, a React 18 / TypeScript / Vite Admin Panel, and an extensible image processing and storage abstraction layer.

---

## Architecture Overview

```
Flutter Mobile App (Android)      Admin Web Panel (React + TS)
         │                                    │
         ▼                                    ▼
       REST API Gateway (/api/v1/) [FastAPI + Pydantic v2]
         │
         ├── Authentication & RBAC (Argon2 / bcrypt + JWT)
         ├── Service Layer (Wallpaper, Categories, Collections, Reports)
         ├── Image Processing Pipeline (Pillow: 8K -> 2K Preview -> 600px WebP Thumb)
         ├── Repository Layer (SQLAlchemy 2.0 Async Session)
         │
         ├── Database: PostgreSQL 15+ (Alembic Migrations)
         └── Storage Engine: Local File System / S3-Compatible Object Storage
```

---

## Project Structure

```
/Wallpapers_8k1
├── backend/          # FastAPI Backend (Python 3.11+, SQLAlchemy 2.0, Alembic)
│   ├── app/          # Application core, models, schemas, repositories, services, api
│   ├── storage/      # Local image storage provider mount
│   └── tests/        # Pytest unit and integration test suite
├── mobile/           # Flutter Mobile Application (Dart, BLoC, Clean Architecture)
│   ├── lib/          # Core, features, shared widgets, theme, router
│   └── android/      # Android native configurations and manifests
├── admin/            # Admin Panel (React 18, Vite, TypeScript, Tailwind CSS)
│   └── src/          # Pages, components, hooks, API client
├── alembic/          # Database migration revisions
├── docs/             # Technical specifications & architecture blueprints
├── docker-compose.yml# Container orchestration for Postgres, Backend, Admin
└── .env.example      # Environment variables template
```

---

## Quick Start (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20+ recommended)
- Flutter SDK (for mobile development)
- PostgreSQL 15+ or Docker

### 1. Backend Setup
```bash
# Copy environment configuration
cp .env.example .env

# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Admin Panel Setup
```bash
cd admin
npm install
npm run dev
```
The Admin Panel will be available at: `http://localhost:5173`

### 3. Mobile App Setup (Flutter)
```bash
cd mobile
flutter pub get
flutter run
```

---

## Key Features

- **8K Resolution Support:** Streamlined multi-tier processing pipeline to guarantee mobile UI smoothness and prevent OOM exceptions.
- **Native Android Wallpaper Engine:** Direct setting of Home screen, Lock screen, or both via Android WallpaperManager.
- **Authentic Metrics:** Algorithmic trending score, real view/download tracking, duplicate prevention for user favorites.
- **Content Moderation:** In-app reporting workflow with review queue and audit logging.
- **RBAC:** Secure role-based authorization (`USER`, `ADMIN`, `SUPER_ADMIN`).

---

## License & Attribution
Proprietary commercial software. Designed and architected for Wallpapers_8k1.
