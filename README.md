# Calendar API

Hệ thống Calendar API quản lý sự kiện cá nhân với hệ thống xác thực Opaque Access Token an toàn và tính năng phát hiện trùng lặp lịch (conflict detection).

## Tính năng

- Đăng ký & đăng nhập người dùng.
- Xác thực bằng **Opaque Access Token** (lưu chuỗi băm trong database, an toàn hơn và hỗ trợ thu hồi token tức thì) thay thế cho JWT.
- Hỗ trợ Rotate Token và Logout an toàn.
- Quản lý sự kiện (Events) gắn trực tiếp với tài khoản người dùng.
- CRUD events với hệ thống tự động phát hiện trùng lịch (conflict detection).
- Query events theo mốc thời gian (from/to).
- Soft delete (chuyển trạng thái sang cancelled) cho events.
- Database indexes để tối ưu performance truy vấn theo thời gian.

## Công nghệ

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **PostgreSQL/SQLite** - Database
- **Opaque Tokens** - Authentication an toàn
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

Chỉnh sửa `.env` theo môi trường của bạn.

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

### 3. Chạy server (Môi trường Local)

```bash
chmod +x run.sh
./run.sh

```

Hoặc:

```bash
uvicorn app.main:app --reload

```

Server sẽ chạy tại: **http://localhost:8000**
API Documentation (Swagger UI): **http://localhost:8000/docs**

---

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

Response sẽ trả về một Access Token (Long-lived Opaque Token):

```json
{
  "access_token": "chuoi-token-dai-bao-mat...",
  "token_type": "bearer"
}

```

### 3. Xem thông tin cá nhân (Test token)

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

```

### 4. Thay mới Access Token (Rotate Token)

Đổi token hiện tại lấy một token mới an toàn hơn:

```bash
curl -X POST http://localhost:8000/auth/rotate-token \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

```

### 5. Tạo sự kiện (Event)

*Lưu ý: Không cần `calendar_id` nữa vì event được gắn trực tiếp với `user_id`.*

```bash
curl -X POST http://localhost:8000/events \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "description": "Weekly sync",
    "start_at": "2026-02-10T10:00:00Z",
    "end_at": "2026-02-10T11:00:00Z",
    "location": "Zoom",
    "is_all_day": false
  }'

```

### 6. Lấy danh sách events

```bash
# Lấy tất cả events của người dùng
curl -X GET http://localhost:8000/events \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Lọc events theo khoảng thời gian
curl -X GET "http://localhost:8000/events?from=2026-02-01T00:00:00Z&to=2026-02-28T23:59:59Z" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

```

### 7. Đăng xuất (Logout)

Hệ thống sẽ thu hồi token hiện tại bằng cách xóa mã băm khỏi database:

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

```

---

## Database Schema

### users

* `id` (UUID, PK)
* `email` (String, unique)
* `password_hash` (String)
* `access_token_hash` (String, unique) - Lưu chuỗi băm của token đang active
* `created_at` (DateTime)

### events

* `id` (UUID, PK)
* `user_id` (FK → users.id)
* `title` (String)
* `description` (String)
* `start_at` (DateTime)
* `end_at` (DateTime)
* `location` (String)
* `is_all_day` (Boolean)
* `status` (String - "confirmed" / "cancelled")
* `created_at`, `updated_at` (DateTime)

---

## Conflict Detection

API tự động kiểm tra conflict khi tạo hoặc update event đối với cùng một người dùng. Conflict xảy ra nếu:

```
new_start < existing_end AND new_end > existing_start

```

Tắt conflict check khi tạo event:

```bash
curl -X POST "http://localhost:8000/events?check_conflicts=false" ...

```

---

## Docker

*Lưu ý: File `docker-compose.yml` có khai báo mạng `shared-network` ở dạng external.*

### 1. Tạo file `.env`

```bash
cp .env.example .env

```

### 2. Khởi tạo external network cho Docker

Bạn cần tạo network này trước để các container có thể chạy được thành công:

```bash
docker network create shared-network

```

### 3. Chạy API + PostgreSQL bằng Docker Compose

```bash
docker compose up --build

```

* API chạy tại: `http://localhost:8000`
* Docs: `http://localhost:8000/docs`

### 4. Dừng container

```bash
docker compose down

```

```

```
