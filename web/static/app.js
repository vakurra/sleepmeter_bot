import {
    loadProfile,
} from "./profile.js";

import {
    loadStatistics,
} from "./statistics.js";

import {
    initSettings,
} from "./settings.js";

import {
    updateChartsTheme,
} from "./charts.js";

const tg = window.Telegram.WebApp;

const periodSelector =
    document.querySelector(".period-selector");

const periodButtons =
    document.querySelectorAll(".period-button");


tg.ready();
tg.expand();


function applyTheme() {
    document.body.classList.toggle(
        "dark",
        tg.colorScheme === "dark",
    );

    updateChartsTheme();
}


tg.onEvent(
    "themeChanged",
    applyTheme,
);


periodButtons.forEach((button) => {
    button.addEventListener(
        "click",
        async () => {

            const days = Number(
                button.dataset.days,
            );

            periodSelector.dataset.period =
                String(days);

            await loadStatistics(days);

        },
    );
});


async function initApp() {

    applyTheme();

    const results = await Promise.allSettled([
        loadProfile(),
        loadStatistics(7),
    ]);

    for (const result of results) {
        if (result.status === "rejected") {
            console.error("Не удалось загрузить данные Mini App", result.reason);
        }
    }

    initSettings();

}


initApp();
