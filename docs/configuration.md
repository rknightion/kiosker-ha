---
title: Configuration
description: Configure the Kiosker integration in Home Assistant, adjust the update interval, and learn how to target multiple kiosks.
---

# Configuration

The integration is configured entirely through the Home Assistant UI. No YAML is required.

## Fields in the setup flow

| Field | Description | Example |
| ----- | ----------- | ------- |
| **Name** (optional) | Friendly name shown for the device in Home Assistant. Defaults to the app name or device ID. | `Office Tablet` |
| **API base URL** | The Kiosker API endpoint shown in the app. Include `/api/v1`. | `http://tablet-office:8081/api/v1` |
| **Access token** | Token generated in the Kiosker app under Remote Admin/API. | `eyJhbGciOi...` |

During setup, the integration validates the connection and stores the device ID as the unique identifier.

## Options

After onboarding, open the integration, click **Configure**, and adjust:

| Option | Default | Details |
| ------ | ------- | ------- |
| **Update interval (seconds)** | 60 | How often the integration polls the kiosk. Choose between 10 seconds (fastest) and 3600 seconds (1 hour). Use higher values if you have several kiosks or want to reduce network/CPU load. |

Changes trigger a reload of the integration.

## Multiple kiosks

You can add as many kiosks as you like. Each config entry keeps its own base URL, token, and polling interval. When calling services, include `device_id` if more than one kiosk is configured so the correct device is targeted.

## Services and actions

Several actions are exposed as both UI buttons (entities) and services:

- Navigation: go home, go forward/back, refresh the page, open a specific URL.
- Maintenance: ping, print, clear cache, clear cookies.
- Display: dismiss screensaver, set blackout, enable/disable screensaver, set start URL.

See the [Entities](entities.md#services) reference for payload examples and field descriptions.

## Troubleshooting setup

- **Cannot connect**: Confirm the URL is reachable from Home Assistant and that the device is on the same network. Verify the API port (default `8081`).
- **Invalid auth**: Regenerate the token in the Kiosker app and re-run the flow.
- **Multiple entries**: If you see “Multiple Kiosker entries are configured; provide device_id”, include a `device_id` when calling services.
