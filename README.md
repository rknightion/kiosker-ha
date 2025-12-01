<div align="center">
  <img src="docs/assets/kiosker-logo.webp" alt="Kiosker Logo" width="120">
  <h1>Kiosker Home Assistant Integration</h1>
  <p>Monitor and control iOS kiosks running <a href="https://www.kiosker.io">Kiosker</a> directly from Home Assistant</p>

  [![GitHub Release](https://img.shields.io/github/v/release/rknightion/kiosker-ha?style=flat-square)](https://github.com/rknightion/kiosker-ha/releases)
  [![License](https://img.shields.io/github/license/rknightion/kiosker-ha?style=flat-square)](LICENSE)
  [![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square)](https://hacs.xyz)
  [![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025.8.0+-blue.svg?style=flat-square)](https://www.home-assistant.io)
</div>

---

Keep your wall-mounted dashboards and tablets in sync with Home Assistant. This custom integration communicates with the Kiosker app API to surface live device status, expose remote navigation controls, and manage screensaver/blackout behavior without picking up the tablet.

## Features

- **Live Status Monitoring**: Ambient light, battery level/state, app/OS versions, last interaction and motion timestamps
- **Remote Navigation**: Navigate home/forward/back, refresh the page, print, clear cache/cookies, or dismiss the screensaver
- **Display Management**: Toggle the Kiosker blackout overlay, adjust its text/colors, or fully enable/disable the screensaver
- **Multi-Device Support**: Add multiple kiosks with individual polling intervals and device profiles
- **Troubleshooting Friendly**: Diagnostics export, detailed logging, and service calls for recovery actions

## Installation

### HACS (Recommended)

1. Open **HACS** > **Integrations** > **...** > **Custom repositories**
2. Add `https://github.com/rknightion/kiosker-ha` with category **Integration**
3. Find **Kiosker** in HACS and click **Install**
4. Restart Home Assistant
5. Add the integration via **Settings** > **Devices & Services**

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/rknightion/kiosker-ha/releases)
2. Copy the `custom_components/kiosker` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Add the integration via **Settings** > **Devices & Services**

## Quick Start

1. In the **Kiosker app**, enable the API under **Settings** > **Remote Admin / API**
2. Copy the **Base URL** and **Access Token** from the app
3. In Home Assistant, go to **Settings** > **Devices & Services** > **Add Integration**
4. Search for **Kiosker** and enter your credentials
5. Use the provided buttons and services to control your kiosk

## Documentation

Full documentation is available at **[m7kni.io/kiosker-ha](https://m7kni.io/kiosker-ha/)**

- [Getting Started](https://m7kni.io/kiosker-ha/getting-started/)
- [Configuration](https://m7kni.io/kiosker-ha/configuration/)
- [Entity Reference](https://m7kni.io/kiosker-ha/entities/)
- [FAQ & Troubleshooting](https://m7kni.io/kiosker-ha/faq/)

## Requirements

- Home Assistant 2025.8.0 or newer
- Kiosker app with API access enabled
- Device reachable from Home Assistant on your local network (default API port: `8081`)

## Services

The integration exposes several services under the `kiosker` domain:

| Service | Description |
| ------- | ----------- |
| `kiosker.navigate_url` | Navigate the kiosk browser to a specific URL |
| `kiosker.set_blackout` | Show or hide the blackout overlay |
| `kiosker.set_screensaver` | Enable/disable the screensaver |
| `kiosker.set_start_url` | Update the kiosk start page URL |

## Contributing

Contributions are welcome! Please see the [contributing guidelines](https://m7kni.io/kiosker-ha/contributing/) for more information.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with :heart: for the Home Assistant community</sub>
</div>
