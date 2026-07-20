import {
    getStatistics,
} from "./api.js";

import {
    formatDuration,
} from "./utils.js";

import {
    renderCharts,
} from "./charts.js";


const averageDurationElement =
    document.getElementById("average-duration");

const averageRatingElement =
    document.getElementById("average-rating");

const filledDaysElement =
    document.getElementById("filled-days");


export async function loadStatistics(days) {

    const statistics =
        await getStatistics(days);

    averageDurationElement.textContent =
        formatDuration(
            statistics.average_duration,
        );

    averageRatingElement.textContent =
        statistics.average_rating ?? "—";

    filledDaysElement.textContent =
        `${statistics.filled_days}/${days}`;

    renderCharts(
        statistics.records,
    );

}