const tg =
    window.Telegram.WebApp;


const apiHeaders = {
    Authorization: `tma ${tg.initData}`,
    "Content-Type": "application/json",
};


export async function apiRequest(
    url,
    options = {},
) {

    const response = await fetch(
        url,
        {
            headers: apiHeaders,
            ...options,
        },
    );

    if (!response.ok) {
        throw new Error(
            `${response.status} ${response.statusText}`,
        );
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