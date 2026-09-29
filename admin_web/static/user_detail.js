const usernameElement =
    document.getElementById(
        "username"
    );


const emailElement =
    document.getElementById(
        "email"
    );


const userIdElement =
    document.getElementById(
        "userId"
    );


const createdAtElement =
    document.getElementById(
        "createdAt"
    );


const lastActiveElement =
    document.getElementById(
        "lastActive"
    );


const progressValue =
    document.getElementById(
        "progressValue"
    );


const progressPercent =
    document.getElementById(
        "progressPercent"
    );


const progressDays =
    document.getElementById(
        "progressDays"
    );


const mainProgressFill =
    document.getElementById(
        "mainProgressFill"
    );


const lessonProgressGrid =
    document.getElementById(
        "lessonProgressGrid"
    );


const totalAttempts =
    document.getElementById(
        "totalAttempts"
    );


const passedAttempts =
    document.getElementById(
        "passedAttempts"
    );


const failedAttempts =
    document.getElementById(
        "failedAttempts"
    );


const averageScore =
    document.getElementById(
        "averageScore"
    );


const bestScore =
    document.getElementById(
        "bestScore"
    );


const attemptTableBody =
    document.getElementById(
        "attemptTableBody"
    );


const courseStatus =
    document.getElementById(
        "courseStatus"
    );


const detailError =
    document.getElementById(
        "detailError"
    );


const logoutButton =
    document.getElementById(
        "logoutButton"
    );


function getAccessToken() {

    return sessionStorage.getItem(
        "access_token"
    );
}


function getRefreshToken() {

    return sessionStorage.getItem(
        "refresh_token"
    );
}


function clearTokens() {

    sessionStorage.removeItem(
        "access_token"
    );

    sessionStorage.removeItem(
        "refresh_token"
    );
}


function saveTokens(tokens) {

    sessionStorage.setItem(
        "access_token",
        tokens.access_token
    );

    sessionStorage.setItem(
        "refresh_token",
        tokens.refresh_token
    );
}


function goToLogin() {

    clearTokens();

    window.location.href =
        "/admin";
}


function getUserIdFromUrl() {

    const pathParts =
        window.location.pathname
            .split("/")
            .filter(Boolean);


    const lastPart =
        pathParts[
            pathParts.length - 1
        ];


    const userId =
        Number(
            lastPart
        );


    if (
        !Number.isInteger(
            userId
        )
        ||
        userId <= 0
    ) {
        return null;
    }


    return userId;
}


function showError(message) {

    detailError.textContent =
        message;

    detailError.classList.remove(
        "hidden"
    );
}


function formatDate(value) {

    if (!value) {
        return "—";
    }


    const date =
        new Date(
            value
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "—";
    }


    return date.toLocaleString(
        "uz-UZ",
        {
            year: "numeric",
            month: "short",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


function escapeHtml(value) {

    const element =
        document.createElement(
            "div"
        );

    element.textContent =
        value ?? "";

    return element.innerHTML;
}


async function refreshAccessToken() {

    const refreshToken =
        getRefreshToken();


    if (!refreshToken) {
        return false;
    }


    try {

        const response =
            await fetch(
                "/api/v1/auth/refresh",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(
                        {
                            refresh_token:
                                refreshToken
                        }
                    )
                }
            );


        if (!response.ok) {
            return false;
        }


        const tokens =
            await response.json();


        saveTokens(
            tokens
        );


        return true;


    } catch (error) {

        console.error(
            error
        );

        return false;
    }
}


async function apiFetch(
    url,
    options = {},
    allowRefresh = true
) {

    const accessToken =
        getAccessToken();


    if (!accessToken) {

        goToLogin();

        return null;
    }


    const headers = {
        ...(options.headers || {}),

        "Authorization":
            `Bearer ${accessToken}`
    };


    const response =
        await fetch(
            url,
            {
                ...options,
                headers
            }
        );


    if (
        response.status === 401
        &&
        allowRefresh
    ) {

        const refreshed =
            await refreshAccessToken();


        if (!refreshed) {

            goToLogin();

            return null;
        }


        return apiFetch(
            url,
            options,
            false
        );
    }


    return response;
}


function renderProgress(data) {

    progressValue.textContent =
        `${data.completed_lessons}/${data.total_lessons}`;

    progressPercent.textContent =
        `${data.progress_percent}%`;

    progressDays.textContent =
        `${data.completed_lessons}/${data.total_lessons} Day`;


    const percent =
        Math.max(
            0,
            Math.min(
                100,
                data.progress_percent
            )
        );


    mainProgressFill.style.width =
        `${percent}%`;


    lessonProgressGrid.innerHTML =
        data.progress
            .map(
                (lesson) => {

                    const className =
                        lesson.completed
                            ? "lesson-progress-item lesson-completed"
                            : "lesson-progress-item";


                    const state =
                        lesson.completed
                            ? "Completed"
                            : "Not completed";


                    return `
                        <div class="${className}">

                            <strong>
                                Day ${lesson.day}
                            </strong>

                            <span>
                                ${escapeHtml(lesson.title)}
                            </span>

                            <span>
                                ${state}
                            </span>

                        </div>
                    `;
                }
            )
            .join("");
}


function renderAssessmentSummary(
    summary
) {

    totalAttempts.textContent =
        summary.total_attempts;

    passedAttempts.textContent =
        summary.passed_attempts;

    failedAttempts.textContent =
        summary.failed_attempts;

    averageScore.textContent =
        `${summary.average_score}%`;

    bestScore.textContent =
        `${summary.best_score}%`;
}


function renderAttempts(attempts) {

    if (
        !attempts
        ||
        attempts.length === 0
    ) {

        attemptTableBody.innerHTML =
            `
                <tr>

                    <td
                        colspan="7"
                        class="empty-attempts"
                    >
                        Assessment attempt mavjud emas.
                    </td>

                </tr>
            `;

        return;
    }


    attemptTableBody.innerHTML =
        attempts
            .map(
                (attempt) => {

                    const resultText =
                        attempt.passed
                            ? "Passed"
                            : "Failed";


                    const resultClass =
                        attempt.passed
                            ? "attempt-pass"
                            : "attempt-fail";


                    return `
                        <tr>

                            <td>
                                Day ${attempt.day}
                            </td>

                            <td>
                                ${escapeHtml(attempt.title)}
                            </td>

                            <td>
                                #${attempt.attempt_number}
                            </td>

                            <td>
                                ${attempt.score}%
                            </td>

                            <td>
                                ${attempt.correct_answers}/${attempt.total_questions}
                            </td>

                            <td class="${resultClass}">
                                ${resultText}
                            </td>

                            <td>
                                ${formatDate(attempt.created_at)}
                            </td>

                        </tr>
                    `;
                }
            )
            .join("");
}


function renderUser(data) {

    usernameElement.textContent =
        data.username;

    emailElement.textContent =
        data.email;

    userIdElement.textContent =
        data.id;

    createdAtElement.textContent =
        formatDate(
            data.created_at
        );

    lastActiveElement.textContent =
        formatDate(
            data.last_active_at
        );


    if (data.course_completed) {

        courseStatus.textContent =
            "Course Completed";

    } else if (
        data.completed_lessons > 0
    ) {

        courseStatus.textContent =
            "Learning";

    } else {

        courseStatus.textContent =
            "Not Started";
    }


    renderProgress(
        data
    );


    renderAssessmentSummary(
        data.assessment_summary
    );


    renderAttempts(
        data.recent_attempts
    );
}


async function loadUserDetail() {

    const userId =
        getUserIdFromUrl();


    if (!userId) {

        showError(
            "User ID noto'g'ri."
        );

        return;
    }


    try {

        const response =
            await apiFetch(
                `/api/v1/admin/users/${userId}`
            );


        if (!response) {
            return;
        }


        if (
            response.status === 403
        ) {

            goToLogin();

            return;
        }


        if (
            response.status === 404
        ) {

            showError(
                "User topilmadi."
            );

            return;
        }


        if (!response.ok) {

            showError(
                "User ma'lumotlarini olishda xatolik."
            );

            return;
        }


        const data =
            await response.json();


        renderUser(
            data
        );


    } catch (error) {

        console.error(
            error
        );


        showError(
            "Server bilan bog'lanishda xatolik."
        );
    }
}


async function logout() {

    const accessToken =
        getAccessToken();

    const refreshToken =
        getRefreshToken();


    try {

        if (
            accessToken
            &&
            refreshToken
        ) {

            await fetch(
                "/api/v1/auth/logout",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            `Bearer ${accessToken}`
                    },

                    body: JSON.stringify(
                        {
                            refresh_token:
                                refreshToken
                        }
                    )
                }
            );
        }

    } catch (error) {

        console.error(
            error
        );

    } finally {

        goToLogin();
    }
}


logoutButton.addEventListener(
    "click",
    logout
);


if (!getAccessToken()) {

    goToLogin();

} else {

    loadUserDetail();
}   