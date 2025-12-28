---
title: FAQ & Troubleshooting
description: Common questions and troubleshooting steps for the Kiosker integration.
---

# FAQ & Troubleshooting

## Where do I find the Base URL and Access Token?

In the Kiosker app, open **Settings > Remote Admin / API**. Enable the API and generate/copy
the **Access Token**. The **Base URL** (includes `/api/v1`) is shown on the same screen for
manual setup or troubleshooting. The REST API requires **Kiosker Pro**.

## The Base URL is missing in the Kiosker app

- Confirm you are on **Kiosker Pro** (the REST API is Pro-only).
- Update Kiosker to the latest version, then revisit **Settings > Remote Admin / API**.
- If needed, construct the URL manually using the device IP address:
  `http://IP_ADDRESS:8081/api/v1`.

## The setup flow says "Cannot connect"

- Verify the device is online and reachable from the Home Assistant host.
- Confirm the API port (default `8081`) is allowed through any firewall/VLAN rules.
- Test with `curl http://tablet:8081/api/v1/status` from the Home Assistant machine if possible.

## The setup flow says "Invalid auth"

Regenerate the token in the Kiosker app, paste it into the re-auth dialog, and submit again.

## The setup flow keeps using the old Base URL after pasting

Home Assistant config flows can miss a pasted value if the field does not emit a change
event. Click or tap out of each field after pasting, then submit again.

## Services say I must provide a device_id

When multiple kiosks are configured, include the `device_id` (from the Devices page or entity info) in service calls so the integration knows which device to target.

## Screensaver vs. blackout—what's the difference?

- **Screensaver**: The native Kiosker screensaver. You can enable/disable it or dismiss it.
- **Blackout**: An overlay the integration can toggle with optional text/colors (useful for maintenance windows).

## How do I reduce network load?

Open the integration, click **Configure**, and raise the update interval (e.g., 45–60 seconds). Avoid sending rapid-fire blackout or navigation service calls.

## Where are logs and diagnostics?

- Enable debug logging for `custom_components.kiosker` to trace API calls.
- Download diagnostics from **Settings → Devices & Services → Kiosker → ⋯ → Download diagnostics** for a sanitized payload snapshot.

## Does the integration require internet access?

No. It communicates directly with the kiosk over your local network.
