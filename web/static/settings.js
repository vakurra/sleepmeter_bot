import {
    formatUtcOffset,
} from "./utils.js";

import {
    updateProfile,
} from "./api.js";

import {
    loadProfile,
    getProfileData,
} from "./profile.js";

import {
    TimePicker,
} from "./time_picker.js";


const timezoneButton =
    document.getElementById("timezone-value");

const timezoneDropdown =
    document.getElementById("timezone-dropdown");

const timezoneDropdownContent =
    document.getElementById("timezone-dropdown-content");

const reminderButton =
    document.getElementById("reminder-value");

const notificationsCheckbox =
    document.getElementById("notifications-checkbox");

const timePicker =
    new TimePicker();


function toggleTimezoneDropdown() {

    const profile =
        getProfileData();

    if (!profile) {
        return;
    }


    if (
        !timezoneDropdown.classList.contains(
            "hidden",
        )
    ) {

        timezoneDropdown.classList.add(
            "hidden",
        );

        return;

    }


    timezoneDropdownContent.innerHTML = "";


    for (
        let offset = -6;
        offset <= 12;
        offset++
    ) {

        const item =
            document.createElement("div");


        item.className =
            "dropdown-item";


        if (
            offset === profile.utc_offset
        ) {

            item.classList.add(
                "selected",
            );

        }


        item.textContent =
            formatUtcOffset(offset);


        item.onclick =
            async (event) => {

                event.stopPropagation();


                await updateProfile({
                    utc_offset: offset,
                });


                timezoneDropdown.classList.add(
                    "hidden",
                );


                await loadProfile();

            };


        timezoneDropdownContent.appendChild(
            item,
        );

    }


    timezoneDropdown.classList.remove(
        "hidden",
    );

}


async function saveReminder(time) {

    await updateProfile({
        reminder_time: time,
    });

    await loadProfile();

}


function closeTimezoneDropdownOutside(
    event,
) {

    if (
        !timezoneDropdown.contains(
            event.target,
        )
        &&
        event.target !== timezoneButton
    ) {

        timezoneDropdown.classList.add(
            "hidden",
        );

    }

}



async function saveNotifications() {

    await updateProfile({
        notifications_enabled:
            notificationsCheckbox.checked,
    });

    await loadProfile();

}


export function initSettings() {


    timezoneButton.onclick =
        (event) => {

            event.stopPropagation();

            toggleTimezoneDropdown();

        };


    reminderButton.onclick =
        () => {

            const profile =
                getProfileData();

            if (!profile) {
                return;
            }

            timePicker.open(
                profile.reminder_time,
                saveReminder,
            );

        };


    notificationsCheckbox.onchange =
        saveNotifications;


    document.addEventListener(
        "click",
        closeTimezoneDropdownOutside,
    );

}