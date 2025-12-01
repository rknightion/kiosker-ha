---
title: Kiosker Home Assistant Integration
description: Monitor and control iOS kiosks running Kiosker directly from Home Assistant with status sensors, remote navigation, and kiosk management tools.
---

<div align="center">
  <img src="assets/kiosker-logo.webp" alt="Kiosker Logo" width="120">
</div>

# Kiosker Home Assistant Integration

Keep your wall-mounted dashboards and tablets in sync with Home Assistant. This custom integration talks to the Kiosker app API to surface live device status, expose remote navigation controls, and let you manage screensaver/blackout behavior without picking up the tablet.

## What you can do

- **Live status**: Ambient light, battery level/state, app/OS versions, last interaction and motion timestamps.
- **Remote controls**: Navigate home/forward/back, refresh the page, print, clear cache/cookies, or dismiss the screensaver.
- **Display management**: Toggle the Kiosker blackout overlay, adjust its text/colors, or fully enable/disable the screensaver.
- **Multi-device ready**: Add multiple kiosks; each keeps its own polling interval and device profile.
- **Troubleshooting friendly**: Diagnostics export, detailed logging, and service calls for recovery actions.

## Quick start

1. Install the integration via HACS (recommended) or manually.
2. In the Kiosker app, enable the API and copy the **Base URL** and **Access Token**.
3. In Home Assistant, add the **Kiosker** integration and paste the values.
4. Use the provided buttons and services to control the kiosk; sensors and binary sensors update automatically.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Ready to install?**

    ---

    Start with the quick setup checklist.

    [:octicons-arrow-right-24: Getting Started](getting-started.md)

-   :material-shield-home:{ .lg .middle } **Configuration help**

    ---

    Field-by-field guidance and common options.

    [:octicons-arrow-right-24: Configuration](configuration.md)

-   :material-cog:{ .lg .middle } **Developer docs**

    ---

    Run the dev stack, lint, and test locally.

    [:octicons-arrow-right-24: Development](development.md)

-   :material-book-open-page-variant:{ .lg .middle } **Entity reference**

    ---

    Everything exposed by the integration.

    [:octicons-arrow-right-24: Entities](entities.md)

</div>
