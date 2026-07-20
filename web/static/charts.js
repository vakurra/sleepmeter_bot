import {
    formatDate,
    formatDuration,
    chartValueToTime,
    timeToChartValue,
} from "./utils.js";

const durationChartCanvas =
    document.getElementById("duration-chart");

const sleepStartChartCanvas =
    document.getElementById("sleep-start-chart");
    
const ratingChartCanvas =
    document.getElementById("rating-chart");

const CHART_Y_AXIS_WIDTH = 50;


let ratingChart = null;
let sleepStartChart = null;
let durationChart = null;


function getCssVariable(name) {
    return getComputedStyle(document.body)
        .getPropertyValue(name)
        .trim();
}


function getChartColors() {
    return {
        text: getCssVariable("--muted"),
        grid: getCssVariable("--grid"),
        accent: getCssVariable("--accent"),
        accentDeep: getCssVariable("--accent-deep"),
    };
}


function applyChartTheme(chart) {
    const colors = getChartColors();

    chart.options.scales.x.ticks.color = colors.text;
    chart.options.scales.y.ticks.color = colors.text;

    chart.options.scales.x.grid.color = colors.grid;
    chart.options.scales.y.grid.color = colors.grid;

    if (
        chart === sleepStartChart ||
        chart === ratingChart
    ) {
        chart.data.datasets[0].borderColor =
            colors.accent;

        chart.data.datasets[0].backgroundColor =
            colors.accent;

        chart.data.datasets[0].pointBackgroundColor =
            colors.accent;

        chart.data.datasets[0].pointBorderColor =
            colors.accent;
    }

    chart.update("none");
}


export function updateChartsTheme() {

    if (durationChart) {
        applyChartTheme(durationChart);
    }

    if (sleepStartChart) {
        applyChartTheme(sleepStartChart);
    }

    if (ratingChart) {
        applyChartTheme(ratingChart);
    }

}


function createBarGradient(
    context,
    colors,
) {

    const {
        ctx,
        chartArea,
    } = context.chart;

    if (!chartArea) {
        return colors.accent;
    }

    const gradient =
        ctx.createLinearGradient(
            0,
            chartArea.top,
            0,
            chartArea.bottom,
        );

    gradient.addColorStop(
        0,
        colors.accent,
    );

    gradient.addColorStop(
        1,
        colors.accentDeep,
    );

    return gradient;

}


function renderSleepStartChart(records) {
    const colors = getChartColors();

    const labels = records.map((record) =>
        formatDate(record.date)
    );

    const sleepStartValues = records.map((record) =>
        timeToChartValue(record.sleep_start)
    );

    if (sleepStartChart) {
        sleepStartChart.destroy();
    }

    sleepStartChart = new Chart(
        sleepStartChartCanvas,
        {
            type: "line",

            data: {
                labels: labels,

                datasets: [
                    {
                        data: sleepStartValues,

                        borderColor: colors.accent,
                        backgroundColor: colors.accent,

                        tension: 0.3,
                        fill: false,

                        pointRadius: 4,
                        pointHoverRadius: 7,
                        pointHitRadius: 16,

                        pointBackgroundColor:
                            colors.accent,

                        pointBorderColor:
                            colors.accent,
                    },
                ],
            },

            options: {
                responsive: true,

                animation: {
                    duration: 450,
                    easing: "easeOutQuart",
                },

                interaction: {
                    mode: "nearest",
                    intersect: false,
                },

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return chartValueToTime(
                                    context.raw
                                );
                            },
                        },
                    },
                },

                scales: {
                    y: {
                        afterFit(scale) {
                            scale.width = CHART_Y_AXIS_WIDTH;
                        },
                        ticks: {
                            color: colors.text,

                            callback: function (value) {
                                return chartValueToTime(
                                    value
                                );
                            },
                        },

                        grid: {
                            color: colors.grid,
                        },
                    },

                    x: {
                        ticks: {
                            color: colors.text,
                            autoSkip: true,
                            maxTicksLimit: 7,
                        },

                        grid: {
                            color: colors.grid,
                        },
                    },
                },
            },
        },
    );
}


function renderDurationChart(records) {
    const colors = getChartColors();

    const labels = records.map((record) =>
        formatDate(record.date)
    );

    const durations = records.map((record) =>
        record.sleep_duration
    );

    if (durationChart) {
        durationChart.destroy();
    }

    durationChart = new Chart(
        durationChartCanvas,
        {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        data: durations,

                        backgroundColor: (context) =>
                            createBarGradient(
                                context,
                                colors,
                            ),

                        borderRadius: 6,
                        borderSkipped: false,
                    },
                ],
            },

            options: {
                responsive: true,

                animation: {
                    duration: 450,
                    easing: "easeOutQuart",
                },

                interaction: {
                    mode: "nearest",
                    intersect: false,
                },

                plugins: {
                    legend: {
                        display: false,
                    },

                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return formatDuration(
                                    context.raw
                                );
                            },
                        },
                    },
                },

                scales: {
                    y: {
                        afterFit(scale) {
                            scale.width = CHART_Y_AXIS_WIDTH;
                        },
                        min: 120,

                        ticks: {
                            color: colors.text,

                            callback: function (value) {
                                return formatDuration(
                                    value
                                );
                            },
                        },

                        grid: {
                            color: colors.grid,
                        },
                    },

                    x: {
                        ticks: {
                            color: colors.text,
                            autoSkip: true,
                            maxTicksLimit: 7,
                        },

                        grid: {
                            color: colors.grid,
                        },
                    },
                },
            },
        },
    );
}


function renderRatingChart(records) {
    const colors = getChartColors();

    const labels = records.map(record =>
        formatDate(record.date)
    );

    const ratings = records.map(record =>
        record.sleep_rating
    );

    if (ratingChart) {
        ratingChart.destroy();
    }

    ratingChart = new Chart(ratingChartCanvas, {
        type: "bar",

        data: {
            labels,

            datasets: [{
                data: ratings,
                backgroundColor: (context) =>
                    createBarGradient(
                        context,
                        colors,
                    ),
                borderRadius: 6,
            }],
        },

        options: {
            responsive: true,

            plugins: {
                legend: {
                    display: false,
                },
            },

            scales: {
                y: {
                    afterFit(scale) {
                    scale.width = CHART_Y_AXIS_WIDTH;
                    },
                    min: 0,
                    max: 5,

                    ticks: {
                        stepSize: 1,
                        color: colors.text,
                    },

                    grid: {
                        color: colors.grid,
                    },
                },

                x: {
                    ticks: {
                        color: colors.text,
                    },

                    grid: {
                        display: false,
                    },
                },
            },
        },
    });
}


export function renderCharts(records) {

    renderSleepStartChart(records);

    renderDurationChart(records);

    renderRatingChart(records);

}