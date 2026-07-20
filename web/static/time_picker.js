export class TimePicker {

    constructor() {

        this.overlay =
            document.getElementById(
                "time-picker-overlay",
            );

        this.hoursWheel =
            document.getElementById(
                "hours-wheel",
            );

        this.minutesWheel =
            document.getElementById(
                "minutes-wheel",
            );

        this.cancelButton =
            document.getElementById(
                "time-picker-cancel",
            );

        this.saveButton =
            document.getElementById(
                "time-picker-save",
            );

        this.onSave = null;

        this.init();

    }


    init() {

        this.createHours();

        this.createMinutes();

        this.hoursWheel.addEventListener(
            "scroll",
            () => this.snapWheel(this.hoursWheel),
        );

        this.minutesWheel.addEventListener(
            "scroll",
            () => this.snapWheel(this.minutesWheel),
        );

        this.overlay.onclick =
            (event) => {

                if (
                    event.target === this.overlay
                ) {

                    this.close();

                }

            };

        this.cancelButton.onclick =
            () => this.close();

        this.saveButton.onclick =
            () => {

                if (this.onSave) {

                    this.onSave(
                        this.getSelectedTime(),
                    );

                }

                this.close();

            };

    }


    open(
        value,
        onSave,
    ) {

        this.onSave = onSave;

        const [hour, minute] =
            value
                .split(":")
                .map(Number);

        requestAnimationFrame(
            () => {

                this.scrollToHour(hour);
                this.scrollToMinute(minute);
                this.updateWheelStyles(
                    this.hoursWheel,
                );

                this.updateWheelStyles(
                    this.minutesWheel,
                );

            },
        );

        this.overlay.classList.remove(
            "hidden",
        );

        // позже здесь выставим выбранное время

    }


    close() {

        this.overlay.classList.add(
            "hidden",
        );

    }


    createHours() {

        this.hoursWheel.innerHTML = "";

        for (
            let hour = 0;
            hour < 24;
            hour++
        ) {

            const item =
                document.createElement(
                    "div",
                );

            item.className =
                "wheel-item";

            item.textContent =
                String(hour).padStart(
                    2,
                    "0",
                );

            this.hoursWheel.appendChild(
                item,
            );

        }

    }


    createMinutes() {

        this.minutesWheel.innerHTML = "";

        for (
            let minute = 0;
            minute < 60;
            minute++
        ) {

            const item =
                document.createElement(
                    "div",
                );

            item.className =
                "wheel-item";

            item.textContent =
                String(minute).padStart(
                    2,
                    "0",
                );

            this.minutesWheel.appendChild(
                item,
            );

        }

    }

    scrollToHour(hour) {

        this.hoursWheel.scrollTop =
            hour * 44;

    }


    scrollToMinute(minute) {

        this.minutesWheel.scrollTop =
            minute * 44;

    }

    snapWheel(wheel) {

        clearTimeout(
            wheel.snapTimer,
        );

        wheel.snapTimer =
            setTimeout(
                () => {

                    const index =
                        Math.round(
                            wheel.scrollTop / 44,
                        );

                    wheel.scrollTo({

                        top: index * 44,

                        behavior: "smooth",

                    });

                    this.updateWheelStyles(
                        wheel,
                    );

                },

                100,
            );

    }

    getSelectedTime() {

        const hour =
            Math.round(
                this.hoursWheel.scrollTop / 44,
            );

        const minute =
            Math.round(
                this.minutesWheel.scrollTop / 44,
            );

        return (
            `${String(hour).padStart(2, "0")}:` +
            `${String(minute).padStart(2, "0")}`
        );

    }

    updateWheelStyles(wheel) {

        const index =
            Math.round(
                wheel.scrollTop / 44,
            );

        const items =
            wheel.children;

        for (
            let i = 0;
            i < items.length;
            i++
        ) {

            items[i].classList.remove(
                "selected",
                "near",
            );

            const distance =
                Math.abs(i - index);

            if (distance === 0) {

                items[i].classList.add(
                    "selected",
                );

            }
            else if (distance === 1) {

                items[i].classList.add(
                    "near",
                );

            }

        }

    }

}


