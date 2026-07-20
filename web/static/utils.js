export function formatUtcOffset(offset) {

    const moscowOffset =
        offset - 3;

    if (moscowOffset === 0) {
        return "Москва";
    }

    if (moscowOffset > 0) {
        return `Мск +${moscowOffset}`;
    }

    return `Мск ${moscowOffset}`;

}


export function formatDate(date) {

    const [
        ,
        month,
        day,
    ] = date.split("-");

    return `${day}.${month}`;

}


export function formatDuration(minutes) {

    if (minutes === null) {
        return "Нет данных";
    }

    const hours =
        Math.floor(minutes / 60);

    const remainingMinutes =
        minutes % 60;

    if (remainingMinutes === 0) {
        return `${hours}ч`;
    }

    return (
        `${hours}ч ` +
        `${remainingMinutes}м`
    );

}


export function chartValueToTime(value) {
    const totalMinutes = Math.round(value * 60);

    const hour =
        Math.floor(totalMinutes / 60) % 24;

    const minute = totalMinutes % 60;

    return (
        `${String(hour).padStart(2, "0")}:` +
        `${String(minute).padStart(2, "0")}`
    );
}


export function timeToChartValue(time) {
    const [hour, minute] = time
        .split(":")
        .map(Number);

    let value = hour + minute / 60;

    if (hour < 12) {
        value += 24;
    }

    return value;
}
