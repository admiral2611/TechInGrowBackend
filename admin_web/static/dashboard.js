const totalUsers =
    document.getElementById("totalUsers");

const activeToday =
    document.getElementById("activeToday");

const active7Days =
    document.getElementById("active7Days");

const active30Days =
    document.getElementById("active30Days");

const newUsersToday =
    document.getElementById("newUsersToday");

const newUsers7Days =
    document.getElementById("newUsers7Days");

const dashboardError =
    document.getElementById("dashboardError");

const refreshButton =
    document.getElementById("refreshButton");

const logoutButton =
    document.getElementById("logoutButton");

const lastUpdated =
    document.getElementById("lastUpdated");

const activityTodayText =
    document.getElementById("activityTodayText");

const activity7Text =
    document.getElementById("activity7Text");

const activity30Text =
    document.getElementById("activity30Text");

const activityTodayBar =
    document.getElementById("activityTodayBar");

const activity7Bar =
    document.getElementById("activity7Bar");

const activity30Bar =
    document.getElementById("activity30Bar");


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

    dashboardError.textContent =
        message;

    dashboardError.classList.remove(
        "hidden"
    );
}


function hideError() {

    dashboardError.classList.add(
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

        saveTokens(tokens);

        return true;

    } catch (error) {

        console.error(error);

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


function calculatePercent(
    value,
    total
) {

    if (!total || total <= 0) {
        return 0;
    }

    const percent =
        (value / total) * 100;

    return Math.min(
        100,
        Math.max(
            0,
            percent
        )
    );
}


function updateActivityBars(data) {

    const total =
        data.total_users;

    activityTodayText.textContent =
        data.active_today;

    activity7Text.textContent =
        data.active_7_days;

    activity30Text.textContent =
        data.active_30_days;

    activityTodayBar.style.width =
        `${calculatePercent(
            data.active_today,
            total
        )}%`;

    activity7Bar.style.width =
        `${calculatePercent(
            data.active_7_days,
            total
        )}%`;

    activity30Bar.style.width =
        `${calculatePercent(
            data.active_30_days,
            total
        )}%`;
}


function renderDashboard(data) {

    totalUsers.textContent =
        data.total_users;

    activeToday.textContent =
        data.active_today;

    active7Days.textContent =
        data.active_7_days;

    active30Days.textContent =
        data.active_30_days;

    newUsersToday.textContent =
        data.new_users_today;

    newUsers7Days.textContent =
        data.new_users_7_days;

    updateActivityBars(data);

    const now =
        new Date();

    lastUpdated.textContent =
        `Yangilandi: ${now.toLocaleTimeString()}`;
}


async function loadDashboard() {

    hideError();

    refreshButton.disabled = true;

    try {

        const response =
            await apiFetch(
                "/api/v1/admin/dashboard"
            );

        if (!response) {
            return;
        }

        if (response.status === 403) {

            goToLogin();

            return;
        }

        if (!response.ok) {

            showError(
                "Dashboard ma'lumotlarini olishda xatolik."
            );

            return;
        }

        const data =
            await response.json();

        renderDashboard(data);

    } catch (error) {

        console.error(error);

        showError(
            "Server bilan bog'lanishda xatolik."
        );

    } finally {

        refreshButton.disabled = false;
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

        console.error(error);

    } finally {

        goToLogin();
    }
}


refreshButton.addEventListener(
    "click",
    loadDashboard
);


logoutButton.addEventListener(
    "click",
    logout
);


if (!getAccessToken()) {

    goToLogin();

} else {

    loadDashboard();
}