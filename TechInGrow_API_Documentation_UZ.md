# TechInGrow API Documentation — O‘zbekcha

**Base URL (local):** `http://127.0.0.1:8000`  
**API prefix:** `/api/v1`  
**Swagger:** `/docs`

> Ushbu hujjat joriy Backend V1 + Admin Web V1 checkpointiga tegishli. `Forgot Password` va `Google Sign-In` hali API tarkibiga kiritilmagan.

## 1. Autentifikatsiya qoidalari

Protected endpointlarda header:

```http
Authorization: Bearer <access_token>
```

Tokenlar:
- **Access token:** qisqa muddatli (~15 daqiqa), protected endpointlar uchun.
- **Refresh token:** uzoqroq muddatli (~30 kun), yangi token juftligini olish uchun.
- Refresh muvaffaqiyatli ishlatilganda rotate qilinadi; eski refresh token qayta ishlatilmaydi.
- Password change va logout refresh tokenlarni revoke qiladi.

## 2. Umumiy HTTP statuslar

| Status | Ma’nosi |
|---|---|
| 200 | Request muvaffaqiyatli |
| 201 | Resource yaratildi (implementationga qarab register response 200/201 bo‘lishi mumkin) |
| 400 | Biznes qoida xatosi / noto‘g‘ri request |
| 401 | Login/token yaroqsiz yoki token tugagan |
| 403 | Ruxsat yo‘q; masalan locked lesson yoki admin bo‘lmagan user |
| 404 | Resource topilmadi |
| 409 | Username/email conflict |
| 422 | Pydantic/form validation xatosi |
| 500 | Server yoki lesson content xatosi |

---

# 3. Auth API

## POST `/api/v1/auth/register`
**Vazifa:** yangi TechInGrow account yaratish.  
**Auth:** Public  
**Content-Type:** `application/json`

Request:
```json
{
  "username": "azizbek",
  "email": "azizbek@example.com",
  "password": "StrongPassword123"
}
```

Asosiy tekshiruvlar:
- username unique;
- email unique;
- password policy bajarilishi;
- common/zaif parol bloklanishi mumkin.

Response: yaratilgan user ma’lumotlari (password/hash qaytarilmaydi).

Ko‘p uchraydigan xatolar:
- `409` — username yoki email mavjud;
- `422` — request formati noto‘g‘ri.

## POST `/api/v1/auth/login`
**Vazifa:** username/password orqali login va JWT tokenlar olish.  
**Auth:** Public  
**Content-Type:** `application/x-www-form-urlencoded`

Body:
```text
username=azizbek
password=StrongPassword123
```

Response namunasi:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

Xatolar:
- `400/401` — username yoki password noto‘g‘ri.

## GET `/api/v1/auth/me`
**Vazifa:** access token egasi bo‘lgan joriy userni qaytaradi.  
**Auth:** Access JWT

Response odatda:
```json
{
  "id": 1,
  "username": "azizbek",
  "email": "azizbek@example.com"
}
```

Xatolar: `401` — token yaroqsiz/tugagan.

## POST `/api/v1/auth/refresh`
**Vazifa:** refresh token orqali yangi access + refresh token juftligini olish.  
**Auth:** body’dagi Refresh token

Request:
```json
{
  "refresh_token": "OLD_REFRESH_TOKEN"
}
```

Response:
```json
{
  "access_token": "NEW_ACCESS_TOKEN",
  "refresh_token": "NEW_REFRESH_TOKEN",
  "token_type": "bearer"
}
```

Muhim: eski refresh token rotate/revoke qilinadi va qayta ishlatilmasligi kerak.

Xatolar: `400/401` — invalid, expired yoki revoked refresh token.

## POST `/api/v1/auth/logout`
**Vazifa:** sessiondan chiqish va berilgan refresh tokenni revoke qilish.  
**Auth:** Access JWT

Header:
```http
Authorization: Bearer <access_token>
```

Body:
```json
{
  "refresh_token": "..."
}
```

Natija: refresh token endi `/refresh` uchun ishlamaydi.

---

# 4. Profile API

## GET `/api/v1/profile`
**Vazifa:** joriy user profilini olish.  
**Auth:** Access JWT

Response:
```json
{
  "id": 1,
  "username": "azizbek",
  "email": "azizbek@example.com"
}
```

## PATCH `/api/v1/profile`
**Vazifa:** username va/yoki emailni yangilash.  
**Auth:** Access JWT

Request (hammasi optional, lekin kamida bittasi bo‘lishi kerak):
```json
{
  "username": "new_name",
  "email": "new_email@example.com"
}
```

Qoidalar:
- bo‘sh `{}` → `400 No changes provided`;
- duplicate username/email → conflict/business validation error.

## PATCH `/api/v1/profile/password`
**Vazifa:** joriy parolni tekshirib yangi parol o‘rnatish.  
**Auth:** Access JWT

Request:
```json
{
  "current_password": "OldPassword",
  "new_password": "NewPassword123"
}
```

Natija:
- password hash yangilanadi;
- userning refresh tokenlari revoke qilinadi;
- keyingi sessionlar yangi password bilan login qiladi.

---

# 5. Lessons API

## GET `/api/v1/lessons`
**Vazifa:** 30 ta lessonning summary ro‘yxatini user holati bilan qaytarish.  
**Auth:** Access JWT

Har element:
```json
{
  "id": 1,
  "day": 1,
  "title": "Dasturlash qanday fikrlaydi?",
  "description": "...",
  "level": "beginner",
  "category": "programming_thinking",
  "duration_minutes": 45,
  "completed": false,
  "locked": false
}
```

`completed` — user lessonni tugatganmi.  
`locked` — prerequisite hali bajarilmaganmi.

## GET `/api/v1/lessons/{day}`
**Vazifa:** bitta lessonning to‘liq public contentini olish.  
**Auth:** Access JWT  
**Path:** `day` — 1..30.

Response tarkibi:
- id/day/title/description;
- level/category/duration;
- objectives/prerequisites;
- sections;
- practice va hints;
- challenge va hints;
- assessment questions va options.

**Security:** public response `correct_answer`ni hech qachon qaytarmaydi.

Xatolar:
- `403` — lesson locked;
- `404` — day mavjud emas;
- `500` — lesson JSON invalid bo‘lsa controlled content error.

---

# 6. Progress API

## GET `/api/v1/progress`
**Vazifa:** joriy userning lesson progress recordlarini olish.  
**Auth:** Access JWT

Progress DB recordlari `completed` va `completed_at` kabi holatlarni beradi.

## GET `/api/v1/progress/summary`
**Vazifa:** course dashboard uchun umumiy progress va joriy lesson holatini olish.  
**Auth:** Access JWT

Response namunasi:
```json
{
  "total_lessons": 30,
  "completed_lessons": 1,
  "progress_percent": 3.3,
  "current_day": 2,
  "current_lesson_id": 2,
  "current_title": "O'zgaruvchilar bilan tanishuv",
  "current_lesson_attempts": 0,
  "current_lesson_best_score": 0,
  "last_completed_day": 1,
  "last_completed_at": "2026-09-29T10:00:00",
  "course_completed": false
}
```

Kurs 30/30 bo‘lganda `current_day/current_lesson_id/current_title` `null`, `course_completed=true` bo‘ladi.

---

# 7. Assessment API

## POST `/api/v1/assessments/{lesson_id}/submit`
**Vazifa:** assessment javoblarini tekshirish, attempt saqlash va pass bo‘lsa lessonni complete qilish.  
**Auth:** Access JWT

Request:
```json
{
  "answers": [
    {"question_id": 1, "selected_answer": 0},
    {"question_id": 2, "selected_answer": 1}
  ]
}
```

Response namunasi:
```json
{
  "lesson_id": 1,
  "attempt_number": 2,
  "score": 100,
  "correct_answers": 5,
  "total_questions": 5,
  "passed": true,
  "completed": true
}
```

Backend internal lesson JSONdagi `correct_answer` bilan solishtiradi. Client correct answer indekslarini oldindan olmaydi.

Xatolar:
- `403` — lesson locked;
- `404` — lesson topilmadi;
- `422` — `question_id/selected_answer` formatida xato.

## GET `/api/v1/assessments/{lesson_id}/attempts`
**Vazifa:** joriy userning shu lesson bo‘yicha barcha attemptlarini olish.  
**Auth:** Access JWT

Har attempt odatda: `attempt_number`, `score`, `correct_answers`, `total_questions`, `passed`, `created_at`.

## GET `/api/v1/assessments/{lesson_id}/summary`
**Vazifa:** bitta lesson bo‘yicha user assessment summarysini olish.  
**Auth:** Access JWT

UI uchun attempt count, best score, pass holati kabi aggregat ma’lumotlar qaytariladi.

---

# 8. Admin API

Barcha endpointlar **Access JWT + `is_admin=true`** talab qiladi. Oddiy user `403 Admin access required` oladi. Adminlar normal user analyticsidan chiqarilgan.

## GET `/api/v1/admin/dashboard`
**Vazifa:** Admin Dashboard yuqori darajadagi user statistikasi.

Response:
```json
{
  "total_users": 7,
  "active_today": 2,
  "active_7_days": 5,
  "active_30_days": 7,
  "new_users_today": 1,
  "new_users_7_days": 3
}
```

`last_active_at` authenticated activityda taxminan har 5 daqiqada ko‘pi bilan bir marta yangilanadi.

## GET `/api/v1/admin/users`
**Vazifa:** userlar ro‘yxatini server-side search va pagination bilan olish.

Query params:
| Param | Default | Qoida |
|---|---:|---|
| `page` | 1 | `>=1` |
| `page_size` | 20 | `5..100` |
| `search` | null | username/email bo‘yicha, max 100 char |

Misol:
```http
GET /api/v1/admin/users?page=2&page_size=20&search=aziz
```

Response:
```json
{
  "page": 1,
  "page_size": 20,
  "total": 57,
  "total_pages": 3,
  "users": [
    {
      "id": 1,
      "username": "azizbek",
      "email": "azizbek@example.com",
      "created_at": "...",
      "last_active_at": "...",
      "completed_lessons": 4,
      "total_lessons": 30,
      "progress_percent": 13,
      "course_completed": false
    }
  ]
}
```

## GET `/api/v1/admin/users/{user_id}`
**Vazifa:** bitta userning batafsil profili, course progressi va assessment tarixini olish.

Response asosiy qismlari:
```json
{
  "id": 1,
  "username": "azizbek",
  "email": "azizbek@example.com",
  "created_at": "...",
  "last_active_at": "...",
  "completed_lessons": 3,
  "total_lessons": 30,
  "progress_percent": 10,
  "course_completed": false,
  "progress": [],
  "assessment_summary": {
    "total_attempts": 5,
    "passed_attempts": 3,
    "failed_attempts": 2,
    "average_score": 76.4,
    "best_score": 100
  },
  "recent_attempts": []
}
```

`recent_attempts` joriy implementatsiyada oxirgi 20 tagacha attemptni beradi.

## DELETE `/api/v1/admin/users/{user_id}`
**Vazifa:** keraksiz/test userni tegishli ma’lumotlari bilan xavfsiz o‘chirish.

Transaction ichida o‘chiriladi:
1. `RefreshToken`
2. `AssessmentAttempt`
3. `UserProgress`
4. `User`

Admin userni delete qilish bloklangan (`403`).

Muvaffaqiyatli response:
```json
{
  "message": "User deleted successfully",
  "user_id": 11,
  "username": "catest"
}
```

Manually verified natija:
```text
user: 0
progress: 0
attempts: 0
tokens: 0
```

## GET `/api/v1/admin/course/stats`
**Vazifa:** 30 bosqichli course funnel va drop-off analytics.

Response tarkibi:
- `total_users`
- `total_lessons`
- `started_users`
- `completed_course_users`
- `completion_rate`
- `average_completed_lessons`
- `average_progress_percent`
- `largest_drop`
- `lessons[]`: har Day bo‘yicha completed users, completion %, previous Daydan drop.

## GET `/api/v1/admin/assessments/stats`
**Vazifa:** global va Day kesimida assessment analytics.

Response tarkibi:
- total attempts;
- unique users;
- passed / failed attempts;
- pass rate;
- average score;
- average attempts per user;
- `lessons[]` bo‘yicha shu metrikalar.

---

# 9. Admin Web route’lari (API emas)

| URL | Vazifa |
|---|---|
| `/admin` | Admin login |
| `/admin/dashboard` | User activity va registrations |
| `/admin/users` | Search/pagination/View/Delete |
| `/admin/users/{id}` | User detail |
| `/admin/course` | Course analytics |
| `/admin/assessments` | Assessment analytics |

---

# 10. Lesson lock va course completion qoidalari

- Day 1 unlocked.
- Day N odatda Day N-1 completionga bog‘liq.
- Locked lessonni GET qilish → `403`.
- Locked lesson assessmentini submit qilish → `403`.
- Lesson faqat assessment passing score’dan o‘tilganda complete bo‘ladi.
- Manual completion endpoint olib tashlangan.
- 30/30 complete bo‘lganda course completed hisoblanadi.

# 11. Client integratsiya uchun tavsiya etilgan flow

```text
Register / Login
      ↓
JWT pair saqlash
      ↓
GET /lessons + GET /progress/summary
      ↓
GET /lessons/{day}
      ↓
Practice + hints
      ↓
POST /assessments/{lesson_id}/submit
      ↓
GET /progress/summary
      ↓
Next unlocked lesson
```

Access token `401` bersa client refresh flow bajaradi. Refresh muvaffaqiyatsiz bo‘lsa user login sahifasiga qaytariladi.

# 12. Hali mavjud bo‘lmagan API

Quyidagilar faqat reja, joriy kodda yo‘q:
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`
- Google Sign-In endpointi

Ularni mavjud deb client kod yozmaslik kerak.
