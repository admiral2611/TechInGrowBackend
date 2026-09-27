from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
from urllib import parse, request
from urllib.error import HTTPError, URLError


BASE_URL = os.getenv(
    "TECHINGROW_BASE_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

ROOT_DIR = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT_DIR / "data" / "lessons"

REQUEST_TIMEOUT = 15

TEST_ID = f"{int(time.time())}_{uuid.uuid4().hex[:6]}"

USERNAME = f"e2e_user_{TEST_ID}"
EMAIL = f"{USERNAME}@example.com"

SECOND_USERNAME = f"e2e_second_{TEST_ID}"
SECOND_EMAIL = f"{SECOND_USERNAME}@example.com"

UPDATED_EMAIL = f"updated_{TEST_ID}@example.com"

PASSWORD = "TestPass_12345"
NEW_PASSWORD = "NewTestPass_12345"


passed_checks = 0
failed_checks = 0


class TestFailure(Exception):
    pass


def print_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_response(status: int, body) -> None:
    print(f"HTTP {status}")

    if body is None:
        return

    try:
        print(json.dumps(body, indent=2, ensure_ascii=False))
    except TypeError:
        print(body)


def decode_response(raw: bytes):
    if not raw:
        return None

    text = raw.decode("utf-8", errors="replace")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def api_request(
    method: str,
    path: str,
    *,
    json_body: dict | list | None = None,
    form_body: dict | None = None,
    token: str | None = None,
):
    url = f"{BASE_URL}{path}"

    headers = {
        "Accept": "application/json"
    }

    body = None

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if json_body is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(json_body).encode("utf-8")

    elif form_body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = parse.urlencode(form_body).encode("utf-8")

    req = request.Request(
        url=url,
        data=body,
        headers=headers,
        method=method.upper()
    )

    try:
        with request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            status = response.status
            data = decode_response(response.read())
            return status, data

    except HTTPError as exc:
        data = decode_response(exc.read())
        return exc.code, data

    except URLError as exc:
        raise TestFailure(
            f"Backendga ulanib bo'lmadi: {BASE_URL}\n"
            f"Server ishlayotganini tekshiring.\n"
            f"Sabab: {exc}"
        )


def check(name: str, condition: bool, detail: str = "") -> bool:
    global passed_checks, failed_checks

    if condition:
        passed_checks += 1
        print(f"[PASS] {name}")
        return True

    failed_checks += 1
    print(f"[FAIL] {name}")

    if detail:
        print(f"       {detail}")

    return False


def require(name: str, condition: bool, detail: str = "") -> None:
    if not check(name, condition, detail):
        raise TestFailure(name)


def require_status(
    name: str,
    status: int,
    expected: int | tuple[int, ...] | list[int]
) -> None:

    if isinstance(expected, int):
        valid_statuses = (expected,)
    else:
        valid_statuses = tuple(expected)

    require(
        name,
        status in valid_statuses,
        f"Expected: {valid_statuses}, actual: {status}"
    )


def load_lesson(day: int) -> dict:
    path = LESSONS_DIR / f"day_{day:02d}.json"

    if not path.exists():
        raise TestFailure(f"Lesson fayli topilmadi: {path}")

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_correct_answers(lesson: dict) -> list[dict]:
    answers = []

    for question in lesson["assessment"]["questions"]:
        answers.append(
            {
                "question_id": question["id"],
                "selected_answer": question["correct_answer"]
            }
        )

    return answers


def get_wrong_answers(lesson: dict) -> list[dict]:
    answers = []

    for question in lesson["assessment"]["questions"]:
        correct_answer = question["correct_answer"]
        options = question["options"]

        wrong_answer = (correct_answer + 1) % len(options)

        answers.append(
            {
                "question_id": question["id"],
                "selected_answer": wrong_answer
            }
        )

    return answers


def login(username: str, password: str):
    return api_request(
        "POST",
        "/api/v1/auth/login",
        form_body={
            "username": username,
            "password": password
        }
    )


def register(username: str, email: str, password: str):
    return api_request(
        "POST",
        "/api/v1/auth/register",
        json_body={
            "username": username,
            "email": email,
            "password": password
        }
    )


def get_summary(token: str):
    return api_request(
        "GET",
        "/api/v1/progress/summary",
        token=token
    )


def run_tests() -> None:
    print_header("TechInGrow Backend Full E2E Test")

    print(f"Backend: {BASE_URL}")
    print(f"Test user: {USERNAME}")
    print()

    # ---------------------------------------------------------
    # 1. SERVER / OPENAPI
    # ---------------------------------------------------------

    print_header("1. Server")

    status, body = api_request(
        "GET",
        "/openapi.json"
    )

    require_status(
        "FastAPI server ishlayapti",
        status,
        200
    )

    require(
        "OpenAPI schema mavjud",
        isinstance(body, dict)
    )

    # ---------------------------------------------------------
    # 2. AUTH REGISTER
    # ---------------------------------------------------------

    print_header("2. Register")

    status, body = register(
        USERNAME,
        EMAIL,
        PASSWORD
    )

    require_status(
        "Yangi user register",
        status,
        (200, 201)
    )

    status, body = register(
        USERNAME,
        EMAIL,
        PASSWORD
    )

    require_status(
        "Duplicate user bloklandi",
        status,
        (400, 409, 422)
    )

    # ---------------------------------------------------------
    # 3. UNAUTHORIZED
    # ---------------------------------------------------------

    print_header("3. Authorization protection")

    status, body = api_request(
        "GET",
        "/api/v1/profile"
    )

    require_status(
        "Token bo'lmasa profile yopiq",
        status,
        (401, 403)
    )

    status, body = api_request(
        "GET",
        "/api/v1/profile",
        token="invalid-token"
    )

    require_status(
        "Noto'g'ri token rad etildi",
        status,
        (401, 403)
    )

    # ---------------------------------------------------------
    # 4. LOGIN
    # ---------------------------------------------------------

    print_header("4. Login")

    status, body = login(
        USERNAME,
        "WrongPassword_123"
    )

    require_status(
        "Noto'g'ri password rad etildi",
        status,
        (400, 401)
    )

    status, login_body = login(
        USERNAME,
        PASSWORD
    )

    require_status(
        "To'g'ri login",
        status,
        200
    )

    require(
        "access_token mavjud",
        isinstance(login_body, dict)
        and bool(login_body.get("access_token"))
    )

    require(
        "refresh_token mavjud",
        isinstance(login_body, dict)
        and bool(login_body.get("refresh_token"))
    )

    access_token = login_body["access_token"]
    original_refresh_token = login_body["refresh_token"]

    require(
        "token_type bearer",
        login_body.get("token_type") == "bearer"
    )

    # ---------------------------------------------------------
    # 5. AUTH /ME
    # ---------------------------------------------------------

    print_header("5. Current user")

    status, body = api_request(
        "GET",
        "/api/v1/auth/me",
        token=access_token
    )

    require_status(
        "/auth/me ishladi",
        status,
        200
    )

    if isinstance(body, dict):
        require(
            "/me username mos",
            body.get("username") == USERNAME,
            f"Response: {body}"
        )

    # ---------------------------------------------------------
    # 6. PROFILE
    # ---------------------------------------------------------

    print_header("6. Profile GET")

    status, body = api_request(
        "GET",
        "/api/v1/profile",
        token=access_token
    )

    require_status(
        "Profile GET",
        status,
        200
    )

    # ---------------------------------------------------------
    # 7. LESSON LIST INITIAL STATE
    # ---------------------------------------------------------

    print_header("7. Initial lesson state")

    status, lessons = api_request(
        "GET",
        "/api/v1/lessons",
        token=access_token
    )

    require_status(
        "Lessons list GET",
        status,
        200
    )

    require(
        "Lessons response list",
        isinstance(lessons, list)
    )

    require(
        "30 ta lesson mavjud",
        len(lessons) == 30,
        f"Actual lesson count: {len(lessons)}"
    )

    day1_summary = next(
        (
            lesson
            for lesson in lessons
            if lesson.get("day") == 1
        ),
        None
    )

    day2_summary = next(
        (
            lesson
            for lesson in lessons
            if lesson.get("day") == 2
        ),
        None
    )

    require(
        "Day 1 listda mavjud",
        day1_summary is not None
    )

    require(
        "Day 2 listda mavjud",
        day2_summary is not None
    )

    require(
        "Day 1 unlocked",
        day1_summary.get("locked") is False,
        f"Day 1: {day1_summary}"
    )

    require(
        "Day 2 locked",
        day2_summary.get("locked") is True,
        f"Day 2: {day2_summary}"
    )

    # ---------------------------------------------------------
    # 8. LOCK TEST
    # ---------------------------------------------------------

    print_header("8. Lesson lock")

    status, body = api_request(
        "GET",
        "/api/v1/lessons/2",
        token=access_token
    )

    require_status(
        "Day 2 ochilishidan oldin yopiq",
        status,
        403
    )

    day2_internal = load_lesson(2)

    status, body = api_request(
        "POST",
        f"/api/v1/assessments/{day2_internal['id']}/submit",
        token=access_token,
        json_body={
            "answers": get_correct_answers(day2_internal)
        }
    )

    require_status(
        "Locked Day 2 assessment bloklandi",
        status,
        403
    )

    # ---------------------------------------------------------
    # 9. FAIL DAY 1 ASSESSMENT
    # ---------------------------------------------------------

    print_header("9. Failed assessment")

    day1_internal = load_lesson(1)

    status, body = api_request(
        "POST",
        f"/api/v1/assessments/{day1_internal['id']}/submit",
        token=access_token,
        json_body={
            "answers": get_wrong_answers(day1_internal)
        }
    )

    require_status(
        "Day 1 noto'g'ri assessment submit",
        status,
        200
    )

    require(
        "Day 1 failed",
        body.get("passed") is False,
        f"Response: {body}"
    )

    require(
        "Failed assessment lessonni complete qilmadi",
        body.get("completed") is False,
        f"Response: {body}"
    )

    status, summary = get_summary(access_token)

    require_status(
        "Failed assessmentdan keyin summary",
        status,
        200
    )

    require(
        "Completed lessons hali 0",
        summary.get("completed_lessons") == 0,
        f"Summary: {summary}"
    )

    # ---------------------------------------------------------
    # 10. DAY 1 -> DAY 30
    # ---------------------------------------------------------

    print_header("10. Day 1 -> Day 30 full learning flow")

    for day in range(1, 31):
        internal_lesson = load_lesson(day)
        lesson_id = internal_lesson["id"]

        print()
        print(f"--- DAY {day:02d} ---")

        status, public_lesson = api_request(
            "GET",
            f"/api/v1/lessons/{day}",
            token=access_token
        )

        require_status(
            f"Day {day} lesson ochildi",
            status,
            200
        )

        require(
            f"Day {day} response day to'g'ri",
            public_lesson.get("day") == day
        )

        public_questions = (
            public_lesson
            .get("assessment", {})
            .get("questions", [])
        )

        require(
            f"Day {day} assessment savollari mavjud",
            len(public_questions) > 0
        )

        correct_answer_exposed = any(
            "correct_answer" in question
            for question in public_questions
        )

        require(
            f"Day {day} correct_answer public API da yashirilgan",
            not correct_answer_exposed
        )

        answers = get_correct_answers(internal_lesson)

        status, result = api_request(
            "POST",
            f"/api/v1/assessments/{lesson_id}/submit",
            token=access_token,
            json_body={
                "answers": answers
            }
        )

        require_status(
            f"Day {day} assessment submit",
            status,
            200
        )

        require(
            f"Day {day} assessment passed",
            result.get("passed") is True,
            f"Response: {result}"
        )

        require(
            f"Day {day} completed",
            result.get("completed") is True,
            f"Response: {result}"
        )

        require(
            f"Day {day} barcha javoblar to'g'ri",
            result.get("correct_answers")
            == result.get("total_questions"),
            f"Response: {result}"
        )

        status, attempts = api_request(
            "GET",
            f"/api/v1/assessments/{lesson_id}/attempts",
            token=access_token
        )

        require_status(
            f"Day {day} attempts GET",
            status,
            200
        )

        require(
            f"Day {day} kamida bitta attempt mavjud",
            isinstance(attempts, list)
            and len(attempts) >= 1
        )

        status, assessment_summary = api_request(
            "GET",
            f"/api/v1/assessments/{lesson_id}/summary",
            token=access_token
        )

        require_status(
            f"Day {day} assessment summary GET",
            status,
            200
        )

        status, progress_summary = get_summary(access_token)

        require_status(
            f"Day {day} progress summary",
            status,
            200
        )

        require(
            f"Day {day} completed_lessons = {day}",
            progress_summary.get("completed_lessons") == day,
            f"Summary: {progress_summary}"
        )

        if day < 30:
            status, next_lesson = api_request(
                "GET",
                f"/api/v1/lessons/{day + 1}",
                token=access_token
            )

            require_status(
                f"Day {day + 1} avtomatik unlock",
                status,
                200
            )

    # ---------------------------------------------------------
    # 11. FINAL COURSE STATE
    # ---------------------------------------------------------

    print_header("11. Final course state")

    status, summary = get_summary(access_token)

    require_status(
        "Final progress summary",
        status,
        200
    )

    require(
        "total_lessons = 30",
        summary.get("total_lessons") == 30,
        f"Summary: {summary}"
    )

    require(
        "completed_lessons = 30",
        summary.get("completed_lessons") == 30,
        f"Summary: {summary}"
    )

    require(
        "progress_percent = 100",
        float(summary.get("progress_percent", -1)) == 100.0,
        f"Summary: {summary}"
    )

    require(
        "course_completed = true",
        summary.get("course_completed") is True,
        f"Summary: {summary}"
    )

    require(
        "Final current_day null",
        summary.get("current_day") is None,
        f"Summary: {summary}"
    )

    status, progress_rows = api_request(
        "GET",
        "/api/v1/progress",
        token=access_token
    )

    require_status(
        "Progress GET final",
        status,
        200
    )

    require(
        "30 ta completed progress record",
        isinstance(progress_rows, list)
        and len(progress_rows) == 30,
        f"Progress rows: {len(progress_rows) if isinstance(progress_rows, list) else progress_rows}"
    )

    status, lessons = api_request(
        "GET",
        "/api/v1/lessons",
        token=access_token
    )

    require_status(
        "Final lessons list",
        status,
        200
    )

    require(
        "Barcha 30 lesson completed",
        all(
            lesson.get("completed") is True
            for lesson in lessons
        )
    )

    require(
        "Finalda hech qaysi lesson locked emas",
        all(
            lesson.get("locked") is False
            for lesson in lessons
        )
    )

    # ---------------------------------------------------------
    # 12. INVALID LESSON
    # ---------------------------------------------------------

    print_header("12. Invalid lesson")

    status, body = api_request(
        "GET",
        "/api/v1/lessons/999",
        token=access_token
    )

    require_status(
        "Mavjud bo'lmagan lesson 404",
        status,
        404
    )

    # ---------------------------------------------------------
    # 13. MALFORMED ASSESSMENT
    # ---------------------------------------------------------

    print_header("13. Assessment validation")

    status, body = api_request(
        "POST",
        "/api/v1/assessments/1/submit",
        token=access_token,
        json_body={
            "answers": [
                {
                    "question_id": 1
                }
            ]
        }
    )

    require_status(
        "selected_answer bo'lmasa validation error",
        status,
        422
    )

    # ---------------------------------------------------------
    # 14. SECOND USER / ISOLATION
    # ---------------------------------------------------------

    print_header("14. Multi-user isolation")

    status, body = register(
        SECOND_USERNAME,
        SECOND_EMAIL,
        PASSWORD
    )

    require_status(
        "Second user register",
        status,
        (200, 201)
    )

    status, second_login = login(
        SECOND_USERNAME,
        PASSWORD
    )

    require_status(
        "Second user login",
        status,
        200
    )

    second_access_token = second_login["access_token"]

    status, second_summary = get_summary(
        second_access_token
    )

    require_status(
        "Second user progress summary",
        status,
        200
    )

    require(
        "Second user progress 0",
        second_summary.get("completed_lessons") == 0,
        f"Summary: {second_summary}"
    )

    status, body = api_request(
        "GET",
        "/api/v1/lessons/2",
        token=second_access_token
    )

    require_status(
        "Second user Day 2 hali locked",
        status,
        403
    )

    # ---------------------------------------------------------
    # 15. REFRESH TOKEN ROTATION
    # ---------------------------------------------------------

    print_header("15. Refresh token rotation")

    status, refresh_body = api_request(
        "POST",
        "/api/v1/auth/refresh",
        json_body={
            "refresh_token": original_refresh_token
        }
    )

    require_status(
        "Refresh token ishladi",
        status,
        200
    )

    require(
        "Yangi access token qaytdi",
        bool(refresh_body.get("access_token"))
    )

    require(
        "Yangi refresh token qaytdi",
        bool(refresh_body.get("refresh_token"))
    )

    rotated_access_token = refresh_body["access_token"]
    rotated_refresh_token = refresh_body["refresh_token"]

    status, body = api_request(
        "POST",
        "/api/v1/auth/refresh",
        json_body={
            "refresh_token": original_refresh_token
        }
    )

    require_status(
        "Eski refresh token rotationdan keyin ishlamaydi",
        status,
        (400, 401)
    )

    access_token = rotated_access_token

    # ---------------------------------------------------------
    # 16. PROFILE UPDATE
    # ---------------------------------------------------------

    print_header("16. Profile update")

    status, profile = api_request(
        "PATCH",
        "/api/v1/profile",
        token=access_token,
        json_body={
            "email": UPDATED_EMAIL
        }
    )

    require_status(
        "Profile email update",
        status,
        200
    )

    require(
        "Email yangilandi",
        profile.get("email") == UPDATED_EMAIL,
        f"Profile: {profile}"
    )

    status, body = api_request(
        "PATCH",
        "/api/v1/profile",
        token=access_token,
        json_body={}
    )

    require_status(
        "Empty profile PATCH bloklandi",
        status,
        400
    )

    # ---------------------------------------------------------
    # 17. PASSWORD CHANGE
    # ---------------------------------------------------------

    print_header("17. Password change")

    status, body = api_request(
        "PATCH",
        "/api/v1/profile/password",
        token=access_token,
        json_body={
            "current_password": PASSWORD,
            "new_password": NEW_PASSWORD
        }
    )

    require_status(
        "Password change",
        status,
        200
    )

    status, body = api_request(
        "POST",
        "/api/v1/auth/refresh",
        json_body={
            "refresh_token": rotated_refresh_token
        }
    )

    require_status(
        "Password change refresh tokenlarni revoke qildi",
        status,
        (400, 401)
    )

    status, body = login(
        USERNAME,
        PASSWORD
    )

    require_status(
        "Eski password endi ishlamaydi",
        status,
        (400, 401)
    )

    status, new_login = login(
        USERNAME,
        NEW_PASSWORD
    )

    require_status(
        "Yangi password bilan login",
        status,
        200
    )

    new_access_token = new_login["access_token"]
    new_refresh_token = new_login["refresh_token"]

    # ---------------------------------------------------------
    # 18. LOGOUT
    # ---------------------------------------------------------

    print_header("18. Logout")

    status, body = api_request(
        "POST",
        "/api/v1/auth/logout",
        token=new_access_token,
        json_body={
            "refresh_token": new_refresh_token
        }
    )

    require_status(
        "Logout ishladi",
        status,
        200
    )

    status, body = api_request(
        "POST",
        "/api/v1/auth/refresh",
        json_body={
            "refresh_token": new_refresh_token
        }
    )

    require_status(
        "Logout qilingan refresh token qayta ishlamaydi",
        status,
        (400, 401)
    )

    # ---------------------------------------------------------
    # FINAL REPORT
    # ---------------------------------------------------------

    print_header("TEST COMPLETED")

    print(f"Passed checks: {passed_checks}")
    print(f"Failed checks: {failed_checks}")

    require(
        "Barcha testlar muvaffaqiyatli",
        failed_checks == 0
    )


if __name__ == "__main__":
    try:
        run_tests()

    except TestFailure as exc:
        print()
        print("=" * 70)
        print("E2E TEST FAILED")
        print("=" * 70)
        print(f"Sabab: {exc}")
        print()
        print(f"Passed checks: {passed_checks}")
        print(f"Failed checks: {failed_checks}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest to'xtatildi.")
        sys.exit(130)

    except Exception as exc:
        print()
        print("=" * 70)
        print("UNEXPECTED ERROR")
        print("=" * 70)
        print(type(exc).__name__)
        print(str(exc))
        sys.exit(1)