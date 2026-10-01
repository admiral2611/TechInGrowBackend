const adminsTableBody =
    document.getElementById(
        "adminsTableBody"
    );

const searchInput =
    document.getElementById(
        "searchInput"
    );

const adminsCount =
    document.getElementById(
        "adminsCount"
    );

const refreshButton =
    document.getElementById(
        "refreshButton"
    );

const logoutButton =
    document.getElementById(
        "logoutButton"
    );

const adminsError =
    document.getElementById(
        "adminsError"
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


const adminModal =
    document.getElementById(
        "adminModal"
    );

const closeModalButton =
    document.getElementById(
        "closeModalButton"
    );

const modalCloseActionButton =
    document.getElementById(
        "modalCloseActionButton"
    );

const modalDeleteButton =
    document.getElementById(
        "modalDeleteButton"
    );

const modalAdminId =
    document.getElementById(
        "modalAdminId"
    );

const modalUsername =
    document.getElementById(
        "modalUsername"
    );

const modalEmail =
    document.getElementById(
        "modalEmail"
    );

const modalVerified =
    document.getElementById(
        "modalVerified"
    );

const modalCurrentAdmin =
    document.getElementById(
        "modalCurrentAdmin"
    );

const modalCreatedAt =
    document.getElementById(
        "modalCreatedAt"
    );

const modalLastActive =
    document.getElementById(
        "modalLastActive"
    );


let currentPage = 1;

let pageSize = Number(
    pageSizeSelect.value
);

let totalPages = 0;

let searchValue = "";

let searchTimer = null;

let selectedAdmin = null;


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


function saveTokens(
    tokens
) {

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


function showError(
    message
) {

    adminsError.textContent =
        message;

    adminsError.classList.remove(
        "hidden"
    );
}


function hideError() {

    adminsError.classList.add(
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


function formatDate(
    value
) {

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


function escapeHtml(
    value
) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        value ?? "";

    return div.innerHTML;
}


function verificationBadge(
    verified
) {

    if (verified) {

        return `
            <span
                class="
                    verification-badge
                    verification-verified
                "
            >
                Verified
            </span>
        `;
    }


    return `
        <span
            class="
                verification-badge
                verification-unverified
            "
        >
            Unverified
        </span>
    `;
}


function createAdminRow(
    admin
) {

    const currentBadge =
        admin.is_current_admin
            ? `
                <span
                    class="current-admin-badge"
                >
                    You
                </span>
            `
            : "";


    const deleteButton =
        admin.is_current_admin
            ? ""
            : `
                <button
                    class="delete-admin-button"
                    data-admin-id="${admin.id}"
                    data-username="${escapeHtml(admin.username)}"
                    type="button"
                >
                    Delete
                </button>
            `;


    return `
        <tr>

            <td>

                <div class="admin-account-cell">

                    <div class="admin-avatar">
                        ${escapeHtml(
                            admin.username
                                .charAt(0)
                                .toUpperCase()
                        )}
                    </div>

                    <div class="admin-account-info">

                        <strong>
                            ${escapeHtml(admin.username)}
                            ${currentBadge}
                        </strong>

                        <span>
                            ID ${admin.id}
                        </span>

                    </div>

                </div>

            </td>


            <td class="muted-text">
                ${escapeHtml(admin.email)}
            </td>


            <td>
                ${verificationBadge(
                    admin.is_email_verified
                )}
            </td>


            <td class="muted-text">
                ${formatDate(
                    admin.created_at
                )}
            </td>


            <td class="muted-text">
                ${formatDate(
                    admin.last_active_at
                )}
            </td>


            <td>

                <div class="action-buttons">

                    <button
                        class="view-admin-button"
                        data-admin-id="${admin.id}"
                        type="button"
                    >
                        View
                    </button>

                    ${deleteButton}

                </div>

            </td>

        </tr>
    `;
}


function renderAdmins(
    admins
) {

    if (
        admins.length === 0
    ) {

        adminsTableBody.innerHTML =
            `
                <tr>

                    <td
                        colspan="6"
                        class="empty-table"
                    >
                        Admin topilmadi.
                    </td>

                </tr>
            `;

        return;
    }


    adminsTableBody.innerHTML =
        admins
            .map(
                createAdminRow
            )
            .join("");


    document
        .querySelectorAll(
            ".view-admin-button"
        )
        .forEach(
            (button) => {

                button.addEventListener(
                    "click",
                    () => {

                        openAdminDetail(
                            Number(
                                button.dataset.adminId
                            )
                        );
                    }
                );
            }
        );


    document
        .querySelectorAll(
            ".delete-admin-button"
        )
        .forEach(
            (button) => {

                button.addEventListener(
                    "click",
                    async () => {

                        await deleteAdmin(
                            Number(
                                button.dataset.adminId
                            ),

                            button.dataset.username,

                            button
                        );
                    }
                );
            }
        );
}


function updatePagination(
    data
) {

    totalPages =
        data.total_pages;


    adminsCount.textContent =
        `${data.total} ta admin`;


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


async function loadAdmins() {

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
                `/api/v1/admin/admins?${params.toString()}`
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
                "Adminlar ma'lumotini olishda xatolik."
            );

            return;
        }


        const data =
            await response.json();


        renderAdmins(
            data.admins || []
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


async function readErrorMessage(
    response,
    fallbackMessage
) {

    try {

        const data =
            await response.json();

        return (
            data.detail
            ||
            data.message
            ||
            fallbackMessage
        );

    } catch {

        return fallbackMessage;
    }
}


async function openAdminDetail(
    adminId
) {

    hideError();


    try {

        const response =
            await apiFetch(
                `/api/v1/admin/admins/${adminId}`
            );


        if (!response) {
            return;
        }


        if (!response.ok) {

            const message =
                await readErrorMessage(
                    response,
                    "Admin ma'lumotini olishda xatolik."
                );

            showError(
                message
            );

            return;
        }


        selectedAdmin =
            await response.json();


        modalAdminId.textContent =
            selectedAdmin.id;

        modalUsername.textContent =
            selectedAdmin.username;

        modalEmail.textContent =
            selectedAdmin.email;

        modalVerified.textContent =
            selectedAdmin.is_email_verified
                ? "Ha"
                : "Yo'q";

        modalCurrentAdmin.textContent =
            selectedAdmin.is_current_admin
                ? "Ha"
                : "Yo'q";

        modalCreatedAt.textContent =
            formatDate(
                selectedAdmin.created_at
            );

        modalLastActive.textContent =
            formatDate(
                selectedAdmin.last_active_at
            );


        if (
            selectedAdmin.is_current_admin
        ) {

            modalDeleteButton.classList.add(
                "hidden"
            );

        } else {

            modalDeleteButton.classList.remove(
                "hidden"
            );
        }


        adminModal.classList.remove(
            "hidden"
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


function closeAdminModal() {

    selectedAdmin = null;

    adminModal.classList.add(
        "hidden"
    );
}


async function deleteAdmin(
    adminId,
    username,
    button = null
) {

    const confirmed =
        window.confirm(
            `${username} admin accountini o'chirishni tasdiqlaysizmi?\n\nBu amalni qaytarib bo'lmaydi.`
        );


    if (!confirmed) {
        return;
    }


    if (button) {

        button.disabled =
            true;
    }


    modalDeleteButton.disabled =
        true;


    hideError();


    try {

        const response =
            await apiFetch(
                `/api/v1/admin/admins/${adminId}`,
                {
                    method: "DELETE"
                }
            );


        if (!response) {
            return;
        }


        if (!response.ok) {

            const message =
                await readErrorMessage(
                    response,
                    "Adminni o'chirishda xatolik."
                );

            showError(
                message
            );

            return;
        }


        closeAdminModal();


        await loadAdmins();

    } catch (error) {

        console.error(
            error
        );

        showError(
            "Server bilan bog'lanishda xatolik."
        );

    } finally {

        if (button) {

            button.disabled =
                false;
        }

        modalDeleteButton.disabled =
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

                    loadAdmins();

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

        loadAdmins();
    }
);


previousPageButton.addEventListener(
    "click",
    () => {

        if (
            currentPage > 1
        ) {

            currentPage--;

            loadAdmins();
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

            loadAdmins();
        }
    }
);


refreshButton.addEventListener(
    "click",
    loadAdmins
);


logoutButton.addEventListener(
    "click",
    logout
);


closeModalButton.addEventListener(
    "click",
    closeAdminModal
);


modalCloseActionButton.addEventListener(
    "click",
    closeAdminModal
);


adminModal
    .querySelector(
        ".admin-modal-backdrop"
    )
    .addEventListener(
        "click",
        closeAdminModal
    );


modalDeleteButton.addEventListener(
    "click",
    async () => {

        if (!selectedAdmin) {
            return;
        }


        await deleteAdmin(
            selectedAdmin.id,
            selectedAdmin.username
        );
    }
);


document.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Escape"
            &&
            !adminModal.classList.contains(
                "hidden"
            )
        ) {

            closeAdminModal();
        }
    }
);


if (!getAccessToken()) {

    goToLogin();

} else {

    loadAdmins();
}