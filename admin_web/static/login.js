const loginForm = document.getElementById("loginForm");
const loginButton = document.getElementById("loginButton");
const loginError = document.getElementById("loginError");


function showError(message) {
    loginError.textContent = message;
    loginError.classList.remove("hidden");
}


function hideError() {
    loginError.textContent = "";
    loginError.classList.add("hidden");
}


function clearTokens() {
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("refresh_token");
}


async function verifyAdmin(accessToken) {
    const response = await fetch(
        "/api/v1/admin/dashboard",
        {
            headers: {
                "Authorization": `Bearer ${accessToken}`
            }
        }
    );

    return response;
}


async function redirectIfAlreadyLoggedIn() {

    const accessToken =
        sessionStorage.getItem("access_token");

    if (!accessToken) {
        return;
    }

    try {

        const response =
            await verifyAdmin(accessToken);

        if (response.ok) {

            window.location.href =
                "/admin/dashboard";

            return;
        }

        clearTokens();

    } catch (error) {
        console.error(error);
    }
}


loginForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        hideError();

        loginButton.disabled = true;
        loginButton.textContent = "Kirilmoqda...";

        const username =
            document
                .getElementById("username")
                .value
                .trim();

        const password =
            document
                .getElementById("password")
                .value;

        const formData =
            new URLSearchParams();

        formData.append(
            "username",
            username
        );

        formData.append(
            "password",
            password
        );

        try {

            const loginResponse =
                await fetch(
                    "/api/v1/auth/login",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/x-www-form-urlencoded"
                        },

                        body: formData
                    }
                );

            if (!loginResponse.ok) {

                showError(
                    "Username yoki password noto'g'ri."
                );

                return;
            }

            const tokens =
                await loginResponse.json();

            sessionStorage.setItem(
                "access_token",
                tokens.access_token
            );

            sessionStorage.setItem(
                "refresh_token",
                tokens.refresh_token
            );

            const adminResponse =
                await verifyAdmin(
                    tokens.access_token
                );

            if (adminResponse.status === 403) {

                clearTokens();

                showError(
                    "Bu account admin huquqiga ega emas."
                );

                return;
            }

            if (!adminResponse.ok) {

                clearTokens();

                showError(
                    "Admin huquqini tekshirib bo'lmadi."
                );

                return;
            }

            window.location.href =
                "/admin/dashboard";

        } catch (error) {

            console.error(error);

            showError(
                "Server bilan bog'lanishda xatolik."
            );

        } finally {

            loginButton.disabled = false;

            loginButton.textContent =
                "Kirish";
        }
    }
);


redirectIfAlreadyLoggedIn();