# TechInGrow Backend — O‘zbekcha hujjat

**TechInGrow** — dasturlashni endi boshlayotgan foydalanuvchilar uchun 30 bosqichli o‘quv kursi, assessment, progress kuzatuvi, JWT autentifikatsiya va browser orqali ishlaydigan Admin Analytics paneliga ega FastAPI backend.

> **Joriy checkpoint:** Backend V1 + Admin Web V1 ishlayapti va test qilingan. Email orqali parolni tiklash va Google Sign-In keyingi bosqich uchun rejalashtirilgan, lekin **hali implementatsiya qilinmagan**.

## Hozir ishlaydigan funksiyalar

- User register va login
- JWT access + refresh tokenlar
- Refresh token rotation va revoke
- Logout
- Parolni account ichidan almashtirish
- Profilni ko‘rish va yangilash
- 30 ta lesson JSON (`day_01.json` ... `day_30.json`)
- Lesson prerequisite va lock/unlock
- Practice/challenge uchun progressiv hintlar
- Assessment submit, attempt history, summary, pass/fail
- Assessmentdan o‘tganda lesson avtomatik complete bo‘lishi
- Har bir user progressining alohida saqlanishi
- Lesson validator
- Full backend E2E test
- Admin-only authorization
- Admin dashboard analytics
- Backend qidiruv + pagination bilan userlar ro‘yxati
- User Detail sahifasi
- Userni progress/assessment/tokenlari bilan xavfsiz o‘chirish
- Course analytics va drop-off ko‘rsatkichlari
- Assessment analytics

## Texnologiyalar

- Python 3.14 (joriy development muhiti)
- FastAPI
- SQLAlchemy
- SQLite (`techingrow.db`)
- Alembic
- PyJWT
- pwdlib / Argon2
- Pydantic
- Admin Web uchun Vanilla HTML/CSS/JavaScript

## Local ishga tushirish

### 1. Virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Dependencylarni o‘rnatish

```powershell
pip install -r requirements.txt
```

### 3. `.env` yaratish

```env
DATABASE_URL=sqlite:///./techingrow.db
JWT_SECRET_KEY=YOUR_PRIVATE_RANDOM_SECRET
```

Secret generatsiya qilish:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Haqiqiy `.env` faylini Git’ga commit qilmang.

### 4. Migration

```powershell
alembic upgrade head
```

### 5. 30 ta lessonni tekshirish

```powershell
python -m scripts.validate_lessons
```

Kutiladigan natija:

```text
Course progress: 30/30 (100%)
Remaining lessons: 0
```

### 6. Server

```powershell
uvicorn app.main:app --reload
```

- Swagger: `http://127.0.0.1:8000/docs`
- Admin login: `http://127.0.0.1:8000/admin`

## Asosiy project strukturasi

```text
TechInGrowBackend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── lessons.py
│   │   ├── progress.py
│   │   ├── assessment.py
│   │   ├── admin.py
│   │   └── admin_web.py
│   ├── core/
│   ├── database/
│   ├── dependencies/
│   ├── models/
│   ├── schemas/
│   └── services/
├── admin_web/
├── data/lessons/day_01.json ... day_30.json
├── scripts/
│   ├── validate_lessons.py
│   ├── full_backend_test.py
│   └── make_admin.py
├── alembic/
├── alembic.ini
├── .env
└── techingrow.db
```

## Auth qisqacha

### Register
`POST /api/v1/auth/register`

```json
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "StrongPassword123"
}
```

### Login
`POST /api/v1/auth/login` — `application/x-www-form-urlencoded`

```text
username=user1
password=StrongPassword123
```

Response access token va refresh token qaytaradi.

### Refresh
`POST /api/v1/auth/refresh`

```json
{"refresh_token":"..."}
```

Refresh token rotate qilinadi; eski refresh token qayta ishlamasligi kerak.

### Logout
`POST /api/v1/auth/logout` — access JWT + body’da refresh token.

### Profile
- `GET /api/v1/profile`
- `PATCH /api/v1/profile`
- `PATCH /api/v1/profile/password`

Parol almashtirilganda userning refresh tokenlari revoke qilinadi.

## O‘quv flow

```text
Register/Login
    ↓
Day 1 unlocked
    ↓
Lesson + Practice + Hints
    ↓
Assessment
    ↓
Pass
    ↓
UserProgress.completed = true
    ↓
Keyingi prerequisite lesson unlocked
```

“30 Day” hozir 30 ta ketma-ket o‘quv bosqichini anglatadi; 30 kalendar kun majburiy emas.

## Admin Web

Admin route’lari `is_admin = true` bilan himoyalangan.

Sahifalar:
- `/admin`
- `/admin/dashboard`
- `/admin/users`
- `/admin/users/{user_id}`
- `/admin/course`
- `/admin/assessments`

Admin API:
- `GET /api/v1/admin/dashboard`
- `GET /api/v1/admin/users?page=1&page_size=20&search=...`
- `GET /api/v1/admin/users/{user_id}`
- `DELETE /api/v1/admin/users/{user_id}`
- `GET /api/v1/admin/course/stats`
- `GET /api/v1/admin/assessments/stats`

Admin accountlar oddiy user analyticsiga kiritilmaydi va adminni delete qilish bloklangan.

Admin qilish:

```powershell
python -m scripts.make_admin <username>
```

## Test

```powershell
python -m scripts.validate_lessons
python -m scripts.full_backend_test
```

E2E test auth, refresh rotation, logout, profile, lesson locking, Day 1→30 flow, progress, assessment va multi-user isolationni tekshiradi.

## Git xavfsizlik

Pushdan oldin:

```powershell
git status
git check-ignore -v .env
git check-ignore -v techingrow.db
```

Kamida quyidagilar ignore qilinsin:

```gitignore
.env
.venv/
__pycache__/
*.pyc
techingrow.db
*.db-journal
*.db-shm
*.db-wal
.idea/
```

JWT secret, haqiqiy login/parollar va local DB Git’ga chiqmasligi kerak.

## Keyingi reja — hali implementatsiya qilinmagan

1. Email orqali Forgot Password / reset code
2. Google Sign-In (Android Credential Manager + backend Google ID token verification)
3. Production security va deployment
4. Launchga yaqin hosting/production DB tanlash
5. Kelajakda Admin Android app

Batafsil arxitektura uchun `TechInGrow_Backend_Developer_Documentation_UZ.docx`, barcha endpointlar uchun `TechInGrow_API_Documentation_UZ.md` fayllariga qarang.
