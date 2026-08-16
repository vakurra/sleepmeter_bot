const tg =
    window.Telegram.WebApp;


function getApiHeaders() {
    return {
        Authorization: `tma ${tg.initData}`,
        "Content-Type": "application/json",
    };
}


function delay(milliseconds) {
    return new Promise((resolve) => {
        setTimeout(resolve, milliseconds);
    });
}


export async function apiRequest(
    url,
    options = {},
) {

    let response;
    let lastError;

    for (let attempt = 0; attempt < 3; attempt++) {
        try {
            response = await fetch(
                url,
                {
                    ...options,
                    headers: {
                        ...getApiHeaders(),
                        ...(options.headers || {}),
                    },
                    // Данные профиля и статистики персональные и не должны
                    // браться из кэша Telegram WebView.
                    cache: "no-store",
                },
            );

            if (response.ok || response.status === 204) {
                break;
            }

            lastError = new Error(
                `${response.status} ${response.statusText}`,
            );
        }
        catch (error) {
            lastError = error;
        }

        await delay(250 * (attempt + 1));
    }

    if (!response || !response.ok) {
        throw lastError || new Error("API request failed");
    }

    if (response.status === 204) {
        return null;
    }

    return await response.json();

}


export async function apiPost(
    url,
    body,
) {

    return apiRequest(
        url,
        {
            method: "POST",
            body: JSON.stringify(body),
        },
    );

}


export async function getProfile() {

    return apiRequest(
        "/api/profile",
    );

}


export async function getStatistics(days) {

    return apiRequest(
        `/api/statistics?days=${days}`,
    );

}


export async function updateProfile(data) {

    return apiRequest(
        "/api/profile",
        {
            method: "PATCH",
            body: JSON.stringify(data),
        },
    );

}
