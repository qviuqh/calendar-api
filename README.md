# Calendar API

Hệ thống Calendar API với authentication, JWT tokens, và conflict detection.

## Tính năng

- ✅ Đăng ký & đăng nhập người dùng
- ✅ JWT Access Token (30 phút) + Refresh Token (7 ngày)
- ✅ Quản lý nhiều calendars
- ✅ CRUD events với conflict detection
- ✅ Query events theo thời gian
- ✅ Soft delete (cancel) events
- ✅ Database indexes để tối ưu performance

## Công nghệ

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL/SQLite** - Database
- **JWT** - Authentication
- **Bcrypt** - Password hashing

## Cài đặt

### 1. Clone và setup môi trường

```bash
cd calendar-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Cấu hình database

Sao chép `.env.example` thành `.env`:

```bash
cp .env.example .env
```

Chỉnh sửa `.env`:

**Cho SQLite (demo nhanh):**
```env
DATABASE_URL=sqlite:///./calendar.db
SECRET_KEY=your-secret-key-change-this
```

**Cho PostgreSQL (production):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/calendar_db
SECRET_KEY=your-secret-key-change-this
```

### 3. Tạo SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Paste kết quả vào `SECRET_KEY` trong `.env`.

### 4. Chạy server

```bash
chmod +x run.sh
./run.sh
```

Hoặc:

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại: **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

## Sử dụng API

### 1. Đăng ký user

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Đăng nhập

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "expires_in": 1800,
  "refresh_token": "abc123...",
  "token_type": "bearer"
}
```

### 3. Test token (GET /me)

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Tạo calendar

```bash
curl -X POST http://localhost:8000/calendars \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Work Calendar",
    "timezone": "Asia/Bangkok"
  }'
```

### 5. Tạo event

```bash
curl -X POST http://localhost:8000/events \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "calendar_id": "CALENDAR_UUID",
    "title": "Team Meeting",
    "description": "Weekly sync",
    "start_at": "2026-02-10T10:00:00Z",
    "end_at": "2026-02-10T11:00:00Z",
    "location": "Zoom"
  }'
```

### 6. Lấy danh sách events

```bash
# Tất cả events
curl -X GET http://localhost:8000/events \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter theo calendar
curl -X GET "http://localhost:8000/events?calendar_id=CALENDAR_UUID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter theo thời gian
curl -X GET "http://localhost:8000/events?from=2026-02-01T00:00:00Z&to=2026-02-28T23:59:59Z" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Refresh token

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### 8. Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## Database Schema

### users
- `id` (UUID, PK)
- `email` (unique)
- `password_hash`
- `created_at`

### refresh_tokens
- `id` (UUID, PK)
- `user_id` (FK → users)
- `token_hash`
- `expires_at`
- `revoked_at`
- `created_at`

### calendars
- `id` (UUID, PK)
- `user_id` (FK → users)
- `name`
- `timezone`
- `created_at`

### events
- `id` (UUID, PK)
- `calendar_id` (FK → calendars)
- `title`
- `description`
- `start_at`
- `end_at`
- `location`
- `is_all_day`
- `status` (confirmed/cancelled)
- `created_at`, `updated_at`

## Conflict Detection

API tự động kiểm tra conflict khi tạo/update event. Conflict xảy ra nếu:

```
new_start < existing_end AND new_end > existing_start
```

Tắt conflict check:
```bash
curl -X POST "http://localhost:8000/events?check_conflicts=false" ...
```

## Testing

Sử dụng Swagger UI tại `http://localhost:8000/docs` để test API interactively.

## Production Checklist

- [ ] Đổi `SECRET_KEY` trong `.env`
- [ ] Sử dụng PostgreSQL thay vì SQLite
- [ ] Cấu hình CORS cho domain cụ thể
- [ ] Enable HTTPS
- [ ] Setup Alembic migrations
- [ ] Add rate limiting
- [ ] Setup logging
- [ ] Add monitoring

## Troubleshooting

**Lỗi "database is locked" (SQLite):**
- SQLite không tốt cho concurrent writes. Chuyển sang PostgreSQL.

**Lỗi 401 Unauthorized:**
- Kiểm tra token có đúng không
- Token có thể đã hết hạn (30 phút)
- Dùng refresh token để lấy token mới

**Lỗi 409 Conflict:**
- Event bị trùng thời gian với event khác
- Kiểm tra lại start_at và end_at
