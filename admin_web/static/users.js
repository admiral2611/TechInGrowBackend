const usersTableBody =
    document.getElementById(
        "usersTableBody"
    );

const searchInput =
    document.getElementById(
        "searchInput"
    );

const usersCount =
    document.getElementById(
        "usersCount"
    );

const refreshButton =
    document.getElementById(
        "refreshButton"
    );

const logoutButton =
    document.getElementById(
        "logoutButton"
    );

const usersError =
    document.getElementById(
        "usersError"
    );

const previousPageButton =
    document.getElementById(
        "previousPageButton"
    );

const nextPageButton =
    document.getElementById(
        "nextPageButton"
    );

const paginationInfo =
    document.getElementById(
        "paginationInfo"
    );

const pageSizeSelect =
    document.getElementById(
        "pageSizeSelect"
    );


let currentPage = 1;

let pageSize = Number(
    pageSizeSelect.value
);

let totalPages = 0;

let searchValue = "";

let searchTimer = null;


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

    usersError.textContent =
        message;

    usersError.classList.remove(
        "hidden"
    );
}


function hideError() {

    usersError.classList.add(
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

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        value ?? "";

    return div.innerHTML;
}


function getStatus(user) {

    if (user.course_completed) {

        return {
            text: "Completed",
            className:
                "status-completed"
        };
    }


    if (
        user.completed_lessons > 0
    ) {

        return {
            text: "Learning",
            className:
                "status-learning"
        };
    }


    return {
        text: "Not started",
        className:
            "status-not-started"
    };
}


function createUserRow(user) {

    const status =
        getStatus(
            user
        );

    const percent =
        Math.max(
            0,
            Math.min(
                100,
                user.progress_percent
            )
        );


    return `
        <tr>

            <td>

                <div class="user-cell">

                    <div class="user-avatar">
                        ${escapeHtml(user.username.charAt(0).toUpperCase())}
                    </div>

                    <div class="user-details">

                        <strong>
                            ${escapeHtml(user.username)}
                        </strong>

                        <span>
                            ID ${user.id}
                        </span>

                    </div>

                </div>

            </td>


            <td class="muted-text">
                ${escapeHtml(user.email)}
            </td>


            <td class="muted-text">
                ${formatDate(user.created_at)}
            </td>


            <td class="muted-text">
                ${formatDate(user.last_active_at)}
            </td>


            <td>

                <div class="user-progress">

                    <div class="user-progress-info">

                        <strong>
                            ${user.progress_percent}%
                        </strong>

                        <span>
                            ${user.completed_lessons}/${user.total_lessons}
                        </span>

                    </div>

                    <div class="user-progress-track">

                        <div
                            class="user-progress-fill"
                            style="width: ${percent}%"
                        ></div>

                    </div>

                </div>

            </td>


            <td>

                <span
                    class="status-badge ${status.className}"
                >
                    ${status.text}
                </span>

            </td>


            <td>

                <div class="action-buttons">

                    <a
                        href="/admin/users/${user.id}"
                        class="view-user-button"
                    >
                        View
                    </a>

                    <button
                        class="delete-user-button"
                        data-user-id="${user.id}"
                        data-username="${escapeHtml(user.username)}"
                    >
                        Delete
                    </button>

                </div>

            </td>

        </tr>
    `;
}


function renderUsers(users) {

    if (
        users.length === 0
    ) {

        usersTableBody.innerHTML =
            `
                <tr>

                    <td
                        colspan="7"
                        class="empty-table"
                    >
                        User topilmadi.
                    </td>

                </tr>
            `;

        return;
    }


    usersTableBody.innerHTML =
        users
            .map(
                createUserRow
            )
            .join("");


    document
        .querySelectorAll(
            ".delete-user-button"
        )
        .forEach(
            (button) => {

                button.addEventListener(
                    "click",
                    async () => {

                        await deleteUser(
                            Number(
                                button.dataset.userId
                            ),
                            button.dataset.username,
                            button
                        );
                    }
                );
            }
        );
}


function updatePagination(data) {

    totalPages =
        data.total_pages;

    usersCount.textContent =
        `${data.total} ta user`;


    if (
        totalPages === 0
    ) {

        paginationInfo.textContent =
            "Page 0 / 0";

    } else {

        paginationInfo.textContent =
            `Page ${data.page} / ${totalPages}`;
    }


    previousPageButton.disabled =
        currentPage <= 1;


    nextPageButton.disabled =
        totalPages === 0
        ||
        currentPage >= totalPages;
}


async function loadUsers() {

    hideError();

    refreshButton.disabled =
        true;


    const params =
        new URLSearchParams();


    params.set(
        "page",
        currentPage
    );

    params.set(
        "page_size",
        pageSize
    );


    if (searchValue) {

        params.set(
            "search",
            searchValue
        );
    }


    try {

        const response =
            await apiFetch(
                `/api/v1/admin/users?${params.toString()}`
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
                "Userlar ma'lumotini olishda xatolik."
            );

            return;
        }


        const data =
            await response.json();


        renderUsers(
            data.users || []
        );


        updatePagination(
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


async function deleteUser(
    userId,
    username,
    button
) {

    const confirmed =
        window.confirm(
            `${username} userini o'chirishni tasdiqlaysizmi?`
        );


    if (!confirmed) {
        return;
    }


    button.disabled =
        true;


    try {

        const response =
            await apiFetch(
                `/api/v1/admin/users/${userId}`,
                {
                    method: "DELETE"
                }
            );


        if (!response) {
            return;
        }


        if (!response.ok) {

            showError(
                "Userni o'chirishda xatolik."
            );

            return;
        }


        await loadUsers();


    } finally {

        button.disabled =
            false;
    }
}


searchInput.addEventListener(
    "input",
    () => {

        clearTimeout(
            searchTimer
        );


        searchTimer =
            setTimeout(
                () => {

                    searchValue =
                        searchInput
                            .value
                            .trim();

                    currentPage = 1;

                    loadUsers();

                },
                350
            );
    }
);


pageSizeSelect.addEventListener(
    "change",
    () => {

        pageSize =
            Number(
                pageSizeSelect.value
            );

        currentPage = 1;

        loadUsers();
    }
);


previousPageButton.addEventListener(
    "click",
    () => {

        if (
            currentPage > 1
        ) {

            currentPage--;

            loadUsers();
        }
    }
);


nextPageButton.addEventListener(
    "click",
    () => {

        if (
            currentPage < totalPages
        ) {

            currentPage++;

            loadUsers();
        }
    }
);


refreshButton.addEventListener(
    "click",
    loadUsers
);


logoutButton.addEventListener(
    "click",
    () => {

        clearTokens();

        window.location.href =
            "/admin";
    }
);


if (!getAccessToken()) {

    goToLogin();

} else {

    loadUsers();
}