const totalAttempts =
    document.getElementById(
        "totalAttempts"
    );


const uniqueUsers =
    document.getElementById(
        "uniqueUsers"
    );


const passedAttempts =
    document.getElementById(
        "passedAttempts"
    );


const failedAttempts =
    document.getElementById(
        "failedAttempts"
    );


const passRate =
    document.getElementById(
        "passRate"
    );


const averageScore =
    document.getElementById(
        "averageScore"
    );


const averageAttempts =
    document.getElementById(
        "averageAttempts"
    );


const assessmentTableBody =
    document.getElementById(
        "assessmentTableBody"
    );


const assessmentError =
    document.getElementById(
        "assessmentError"
    );


const refreshButton =
    document.getElementById(
        "refreshButton"
    );


const logoutButton =
    document.getElementById(
        "logoutButton"
    );


const lastUpdated =
    document.getElementById(
        "lastUpdated"
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


function clearTokens() {

    sessionStorage.removeItem(
        "access_token"
    );

    sessionStorage.removeItem(
        "refresh_token"
    );
}


function goToLogin() {

    clearTokens();

    window.location.href =
        "/admin";
}


function showError(message) {

    assessmentError.textContent =
        message;

    assessmentError.classList.remove(
        "hidden"
    );
}


function hideError() {

    assessmentError.classList.add(
        "hidden"
    );
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


    let response =
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


function escapeHtml(value) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        value ?? "";

    return div.innerHTML;
}


function renderSummary(data) {

    totalAttempts.textContent =
        data.total_attempts;

    uniqueUsers.textContent =
        data.unique_users;

    passedAttempts.textContent =
        data.passed_attempts;

    failedAttempts.textContent =
        data.failed_attempts;

    passRate.textContent =
        `${data.pass_rate}%`;

    averageScore.textContent =
        `${data.average_score}%`;

    averageAttempts.textContent =
        data.average_attempts_per_user;


    const now =
        new Date();


    lastUpdated.textContent =
        `Yangilandi: ${now.toLocaleTimeString()}`;
}


function createLessonRow(lesson) {

    const title =
        escapeHtml(
            lesson.title
        );


    const rate =
        Math.max(
            0,
            Math.min(
                100,
                lesson.pass_rate
            )
        );


    return `
        <tr>

            <td>

                <span class="assessment-day-badge">
                    Day ${lesson.day}
                </span>

            </td>


            <td>

                <span class="assessment-title">
                    ${title}
                </span>

            </td>


            <td>

                <span class="number-value">
                    ${lesson.total_attempts}
                </span>

            </td>


            <td>

                <span class="number-value">
                    ${lesson.unique_users}
                </span>

            </td>


            <td>

                <span class="pass-value">
                    ${lesson.passed_attempts}
                </span>

            </td>


            <td>

                <span class="fail-value">
                    ${lesson.failed_attempts}
                </span>

            </td>


            <td>

                <div class="rate-wrapper">

                    <div class="rate-info">

                        <strong>
                            ${lesson.pass_rate}%
                        </strong>

                    </div>

                    <div class="rate-track">

                        <div
                            class="rate-fill"
                            style="width: ${rate}%"
                        ></div>

                    </div>

                </div>

            </td>


            <td>

                <span class="score-value">
                    ${lesson.average_score}%
                </span>

            </td>


            <td>

                <span class="muted-assessment">
                    ${lesson.average_attempts_per_user}
                </span>

            </td>

        </tr>
    `;
}


function renderLessons(data) {

    if (
        !data.lessons
        ||
        data.lessons.length === 0
    ) {

        assessmentTableBody.innerHTML =
            `
                <tr>

                    <td
                        colspan="9"
                        class="assessment-empty"
                    >
                        Assessment ma'lumoti topilmadi.
                    </td>

                </tr>
            `;

        return;
    }


    assessmentTableBody.innerHTML =
        data.lessons
            .map(
                createLessonRow
            )
            .join("");
}


async function loadAssessmentStats() {

    hideError();

    refreshButton.disabled =
        true;


    try {

        const response =
            await apiFetch(
                "/api/v1/admin/assessments/stats"
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


        if (!response.ok) {

            showError(
                "Assessment analytics ma'lumotlarini olishda xatolik."
            );

            return;
        }


        const data =
            await response.json();


        renderSummary(
            data
        );


        renderLessons(
            data
        );


    } catch (error) {

        console.error(
            error
        );


        showError(
            "Server bilan bog'lanishda xatolik."
        );


    } finally {

        refreshButton.disabled =
            false;
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


refreshButton.addEventListener(
    "click",
    loadAssessmentStats
);


logoutButton.addEventListener(
    "click",
    logout
);


if (!getAccessToken()) {

    goToLogin();

} else {

    loadAssessmentStats();
}