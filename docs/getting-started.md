---
title: Getting Started
description: A short guide to install the Kiosker integration, enable the Kiosker API, and connect your kiosk to Home Assistant.
---

# Getting Started

This guide walks through prerequisites, installing the integration, and completing the first-time configuration wizard in Home Assistant.

## Prerequisites

- Home Assistant 2025.8.0 or newer.
- The **Kiosker** app installed and updated to the latest version.
- **Kiosker Pro** with API access enabled (the REST API requires Pro).
- The device reachable from Home Assistant on your local network (default API port: `8081`).
- An **Access Token** generated in the Kiosker app.


## Enable the Kiosker API

1. Open the Kiosker app on the device.
2. Go to **Settings > Remote Admin / API** (wording may vary by Kiosker version).
3. Enable the **API/Remote admin** toggle.
4. Note the **Base URL** shown (for example `http://tablet-office:8081/api/v1`).
   If the Base URL is missing, update the app and confirm you are on Kiosker Pro.
   You can also construct it with the device IP address, for example
   `http://IP_ADDRESS:8081/api/v1`.
5. Generate or copy the **Access Token** (this is always required).

Keep the access token handy; you will paste it into Home Assistant during setup.
If the kiosk is auto-discovered, you will only be asked for the token and the base URL
is filled automatically.

## Install the integration

- **HACS**: In **HACS → Integrations → Explore & Download**, search for **Kiosker** in the default list, install it, then restart Home Assistant.
- **Manual**: Copy `custom_components/kiosker` into your Home Assistant `custom_components` directory and restart.

See [Installation](installation.md) for detailed steps.

## Add Kiosker in Home Assistant

1. In Home Assistant, go to **Settings → Devices & Services → + Add Integration**.
2. Search for **Kiosker**.
3. If the device was auto-discovered, select it and enter the **Access Token** to finish setup.
   Otherwise, enter the **API Base URL** and **Access Token** you copied from the app.
   Optionally set a friendly name. After pasting into each field, click or tap out before submitting.
4. Submit to validate the connection. The integration tests the API and fetches the device ID.
5. Finish; your kiosk appears as a device with sensors, binary sensors, and action buttons.

If you have multiple kiosks, repeat the flow for each device.

## Next steps

- Review the [Configuration](configuration.md) guide for options like the update interval.
- Explore [Entities](entities.md) to see what each sensor, binary sensor, button, and service does.
- Check [Troubleshooting](faq.md) if the wizard reports connection or authentication errors.
