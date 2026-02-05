# Quick Start Guide

## Chạy nhanh với SQLite (cho demo)

### 1. Setup môi trường

```bash
# Tạo virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Tạo file .env

Tạo file `.env` trong thư mục `calendar-api/`:

```env
DATABASE_URL=sqlite:///./calendar.db
SECRET_KEY=super-secret-key-change-in-production-abc123xyz789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
APP_NAME=Calendar API
DEBUG=True
```

### 3. Chạy server

```bash
# Cách 1: Sử dụng script
chmod +x run.sh
./run.sh

# Cách 2: Trực tiếp
uvicorn app.main:app --reload
```

Server chạy tại: **http://localhost:8000**

### 4. Test API

Mở trình duyệt: **http://localhost:8000/docs**

Hoặc chạy test script:

```bash
python test_api.py
```

## Endpoints chính

```
POST   /auth/register          - Đăng ký user mới
POST   /auth/login             - Đăng nhập
POST   /auth/refresh           - Refresh access token
POST   /auth/logout            - Đăng xuất
GET    /auth/me                - Lấy thông tin user hiện tại

POST   /calendars              - Tạo calendar
GET    /calendars              - Lấy danh sách calendars
GET    /calendars/{id}         - Lấy calendar cụ thể
PATCH  /calendars/{id}         - Update calendar
DELETE /calendars/{id}         - Xóa calendar

POST   /events                 - Tạo event
GET    /events                 - Lấy danh sách events (có filter)
GET    /events/{id}            - Lấy event cụ thể
PATCH  /events/{id}            - Update event
DELETE /events/{id}            - Xóa/Cancel event
```

## Test workflow mẫu

```bash
# 1. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Copy access_token từ response

# 3. Create calendar
TOKEN="your-access-token-here"
curl -X POST http://localhost:8000/calendars \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Work","timezone":"Asia/Bangkok"}'

# Copy calendar_id từ response

# 4. Create event
CALENDAR_ID="your-calendar-id-here"
curl -X POST http://localhost:8000/events \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "calendar_id":"'$CALENDAR_ID'",
    "title":"Team Meeting",
    "start_at":"2026-02-10T10:00:00Z",
    "end_at":"2026-02-10T11:00:00Z"
  }'
```

## Sử dụng PostgreSQL (Production)

### 1. Cài đặt PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Mac
brew install postgresql
```

### 2. Tạo database

```bash
sudo -u postgres psql

CREATE DATABASE calendar_db;
CREATE USER calendar_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE calendar_db TO calendar_user;
\q
```

### 3. Update .env

```env
DATABASE_URL=postgresql://calendar_user:your-password@localhost:5432/calendar_db
```

### 4. Restart server

Server sẽ tự động tạo tables khi khởi động.

## Troubleshooting

**Lỗi "ModuleNotFoundError":**
```bash
pip install -r requirements.txt
```

**Lỗi "SECRET_KEY not found":**
- Tạo file `.env` như hướng dẫn ở trên

**Lỗi database:**
- Xóa file `calendar.db` và restart server
- Hoặc chuyển sang PostgreSQL

**Port 8000 đã được sử dụng:**
```bash
uvicorn app.main:app --reload --port 8001
```
