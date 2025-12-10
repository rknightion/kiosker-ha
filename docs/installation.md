---
title: Installation
description: Install the Kiosker custom integration via HACS or manual copy and prepare Home Assistant for the first sync.
---

# Installation

Choose the installation method that best fits your Home Assistant setup. HACS is recommended for easy updates.

## HACS installation (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rknightion&repository=kiosker-ha&category=integration)

1. Open **HACS → Integrations → Explore & Download**.
2. Search for **Kiosker** in the default list and click **Download**.
3. Restart Home Assistant when prompted.
4. Add the integration through **Settings → Devices & Services**.

## Manual installation

1. Download the latest release archive from the [GitHub releases page](https://github.com/rknightion/kiosker-ha/releases).
2. Extract and copy the `custom_components/kiosker` folder into your Home Assistant `custom_components` directory (typically `config/custom_components`).
3. Ensure file permissions allow Home Assistant to read the files.
4. Restart Home Assistant.
5. Add the integration through **Settings → Devices & Services**.

## Updating

- **HACS**: Open the integration in HACS and apply the available update, then restart Home Assistant.
- **Manual**: Replace the `custom_components/kiosker` folder with the new release contents and restart.

## Verifying installation

After restarting, go to **Settings → Devices & Services** and click **Add Integration**. If **Kiosker** appears in the list, the installation was successful.
