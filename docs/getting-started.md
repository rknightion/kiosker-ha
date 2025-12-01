---
title: Getting Started
description: A short guide to install the Kiosker integration, enable the Kiosker API, and connect your kiosk to Home Assistant.
---

# Getting Started

This guide walks through prerequisites, installing the integration, and completing the first-time configuration wizard in Home Assistant.

## Prerequisites

- Home Assistant 2024.6 or newer.
- The **Kiosker** app installed on your iPad/iPhone with API access enabled.
- The device reachable from Home Assistant on your local network (default API port: `8081`).
- An **Access Token** generated in the Kiosker app.


## Enable the Kiosker API

1. Open the Kiosker app on the device.
2. Go to **Settings → Remote Admin / API** (wording may vary by Kiosker version).
3. Enable the **API/Remote admin** toggle.
4. Note the **Base URL** shown (for example `http://tablet-office:8081/api/v1`).
5. Generate or copy the **Access Token**.

Keep the Base URL and token handy—you will paste them into Home Assistant during setup.

## Install the integration

- **HACS**: Add the repository `https://github.com/rknightion/kiosker-ha` as an Integration, install, then restart Home Assistant.
- **Manual**: Copy `custom_components/kiosker` into your Home Assistant `custom_components` directory and restart.

See [Installation](installation.md) for detailed steps.

## Add Kiosker in Home Assistant

1. In Home Assistant, go to **Settings → Devices & Services → + Add Integration**.
2. Search for **Kiosker**.
3. Enter the **API Base URL** and **Access Token** you copied from the app. Optionally set a friendly name.
4. Submit to validate the connection. The integration tests the API and fetches the device ID.
5. Finish; your kiosk appears as a device with sensors, binary sensors, and action buttons.

If you have multiple kiosks, repeat the flow for each device.

## Next steps

- Review the [Configuration](configuration.md) guide for options like the update interval.
- Explore [Entities](entities.md) to see what each sensor, binary sensor, button, and service does.
- Check [Troubleshooting](faq.md) if the wizard reports connection or authentication errors.
