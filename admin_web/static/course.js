const totalUsers =
    document.getElementById(
        "totalUsers"
    );


const startedUsers =
    document.getElementById(
        "startedUsers"
    );


const completedUsers =
    document.getElementById(
        "completedUsers"
    );


const completionRate =
    document.getElementById(
        "completionRate"
    );


const averageProgress =
    document.getElementById(
        "averageProgress"
    );


const averageProgressDescription =
    document.getElementById(
        "averageProgressDescription"
    );


const largestDropTitle =
    document.getElementById(
        "largestDropTitle"
    );


const largestDropDescription =
    document.getElementById(
        "largestDropDescription"
    );


const courseTableBody =
    document.getElementById(
        "courseTableBody"
    );


const courseError =
    document.getElementById(
        "courseError"
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

    courseError.textContent =
        message;

    courseError.classList.remove(
        "hidden"
    );
}


function hideError() {

    courseError.classList.add(
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

    totalUsers.textContent =
        data.total_users;

    startedUsers.textContent =
        data.started_users;

    completedUsers.textContent =
        data.completed_course_users;

    completionRate.textContent =
        `${data.completion_rate}%`;

    averageProgress.textContent =
        `${data.average_progress_percent}%`;

    averageProgressDescription.textContent =
        `${data.average_completed_lessons}/${data.total_lessons} Day o'rtacha`;


    if (data.largest_drop) {

        largestDropTitle.textContent =
            `Day ${data.largest_drop.from_day} → Day ${data.largest_drop.to_day}`;

        largestDropDescription.textContent =
            `${data.largest_drop.dropped_users} ta user davom etmagan — ${data.largest_drop.drop_percent}% drop.`;

    } else {

        largestDropTitle.textContent =
            "Hozircha drop aniqlanmadi";

        largestDropDescription.textContent =
            "Yetarli progress ma'lumoti yig'ilgach bu yerda eng katta pasayish ko'rinadi.";
    }


    const now =
        new Date();

    lastUpdated.textContent =
        `Yangilandi: ${now.toLocaleTimeString()}`;
}


function createLessonRow(
    lesson,
    totalUsersCount
) {

    const percent =
        Math.max(
            0,
            Math.min(
                100,
                lesson.completion_percent
            )
        );


    const title =
        escapeHtml(
            lesson.title
        );


    const dropText =
        lesson.drop_from_previous > 0
            ? `-${lesson.drop_from_previous}`
            : "—";


    const dropClass =
        lesson.drop_from_previous > 0
            ? "drop-negative"
            : "drop-zero";


    return `
        <tr>

            <td>
                <span class="day-badge">
                    Day ${lesson.day}
                </span>
            </td>


            <td>
                <span class="lesson-title">
                    ${title}
                </span>
            </td>


            <td>
                <span class="completed-count">
                    ${lesson.completed_users}
                </span>
            </td>


            <td>

                <div class="completion-cell">

                    <div class="completion-info">

                        <strong>
                            ${lesson.completion_percent}%
                        </strong>

                        <span>
                            ${lesson.completed_users}/${totalUsersCount} user
                        </span>

                    </div>

                    <div class="completion-track">

                        <div
                            class="completion-fill"
                            style="width: ${percent}%"
                        ></div>

                    </div>

                </div>

            </td>


            <td>
                <span class="${dropClass}">
                    ${dropText}
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

        courseTableBody.innerHTML =
            `
                <tr>

                    <td
                        colspan="5"
                        class="course-empty"
                    >
                        Lesson ma'lumoti topilmadi.
                    </td>

                </tr>
            `;

        return;
    }


    courseTableBody.innerHTML =
        data.lessons
            .map(
                (lesson) =>
                    createLessonRow(
                        lesson,
                        data.total_users
                    )
            )
            .join("");
}


async function loadCourseStats() {

    hideError();

    refreshButton.disabled =
        true;


    try {

        const response =
            await apiFetch(
                "/api/v1/admin/course/stats"
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
                "Course analytics ma'lumotlarini olishda xatolik."
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
    loadCourseStats
);


logoutButton.addEventListener(
    "click",
    logout
);


if (!getAccessToken()) {

    goToLogin();

} else {

    loadCourseStats();
}