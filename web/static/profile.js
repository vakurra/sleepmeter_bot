import {
    getProfile,
} from "./api.js";

import {
    formatUtcOffset,
} from "./utils.js";


const profileNameElement =
    document.getElementById("profile-name");

const timezoneElement =
    document.getElementById("timezone-value");

const reminderElement =
    document.getElementById("reminder-value");

const notificationsCheckbox =
    document.getElementById("notifications-checkbox");


let profile = null;


export async function loadProfile() {

    profile = await getProfile();

    profileNameElement.textContent =
        profile.first_name;

    timezoneElement.textContent =
        formatUtcOffset(profile.utc_offset);

    reminderElement.textContent =
        profile.reminder_time;

    notificationsCheckbox.checked =
        profile.notifications_enabled;

}


export function getProfileData() {

    return profile;

}