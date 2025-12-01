---
title: Entity Reference
description: Reference for all sensors, binary sensors, buttons, and services exposed by the Kiosker integration.
---

# Entity Reference

This page lists every entity and service exposed by the Kiosker integration and how to use them.

## Sensors

| Name | Description | Device class | Unit | Category |
| ---- | ----------- | ------------ | ---- | -------- |
| Ambient Light | Ambient light level reported by the device. | Illuminance | lux | Primary |
| Battery Level | Battery percentage. | Battery | % | Measurement |
| Battery State | Charging state string (Charging/Unplugged/etc.). | Enum | — | Diagnostic |
| Last Interaction | Timestamp of the last touch/interaction. | Timestamp | — | Diagnostic |
| Last Motion | Timestamp of the last detected motion. | Timestamp | — | Diagnostic |
| App Version | Version of the Kiosker app. | — | — | Diagnostic |
| OS Version | iOS/iPadOS version. | — | — | Diagnostic |
| Device Model | Apple device model. | — | — | Diagnostic |

## Binary sensors

| Name | Description | Icon | Category |
| ---- | ----------- | ---- | -------- |
| Screensaver Active | On when the screensaver is visible. | `mdi:sleep` | Primary |
| Screensaver Disabled | On when the screensaver is disabled. | `mdi:sleep-off` | Diagnostic |
| Blackout Active | On when the blackout overlay is visible. | `mdi:cancel` | Primary |

## Buttons (one-shot actions)

| Name | Action | Category |
| ---- | ------ | -------- |
| Ping | Verify connectivity with the kiosk. | Diagnostic |
| Refresh Page | Reload the current page. | Primary |
| Go Home | Navigate to the configured start page. | Primary |
| Go Forward | Navigate forward in history. | Primary |
| Go Back | Navigate backward in history. | Primary |
| Print Page | Trigger a print of the current page. | Primary |
| Clear Cache | Clear browser cache and data. | Configuration |
| Clear Cookies | Clear cookies. | Configuration |
| Dismiss Screensaver | Simulate an interaction to clear the screensaver. | Primary |

## Services

All services live under the `kiosker` domain. Include `device_id` when more than one kiosk is configured.

### `kiosker.navigate_url`

Navigate the kiosk browser to a specific URL.

Fields:

- `device_id` (optional): Target kiosk device.
- `url` (required): Destination URL.

Example:

```yaml
service: kiosker.navigate_url
data:
  device_id: 1234567890abcdef
  url: https://dashboards.example.com/office
```

### `kiosker.set_blackout`

Show or hide the blackout overlay.

Fields:

- `device_id` (optional)
- `visible` (required): `true` to show, `false` to hide.
- `text` (optional): Overlay text.
- `background` (optional): Background color hex (e.g., `#000000`).
- `foreground` (optional): Text color hex (e.g., `#FFFFFF`).
- `icon` (optional): Icon/SF Symbol name.
- `expire` (optional): Seconds before clearing.

Example:

```yaml
service: kiosker.set_blackout
data:
  visible: true
  text: "Updating dashboard"
  background: "#111827"
  foreground: "#F9FAFB"
  expire: 120
```

### `kiosker.set_screensaver`

Enable/disable the screensaver and optionally force its visibility.

Fields:

- `device_id` (optional)
- `disabled` (required): `true` to disable, `false` to enable.
- `visible` (optional): Force visibility on/off.

Example:

```yaml
service: kiosker.set_screensaver
data:
  disabled: false
  visible: false
```

### `kiosker.set_start_url`

Update the kiosk start page URL used on launch or reset.

Fields:

- `device_id` (optional)
- `url` (required): URL to set as the home/start page.

Example:

```yaml
service: kiosker.set_start_url
data:
  url: https://dashboards.example.com/wallpanel
```

## Diagnostics

Use **Settings → Devices & Services → Kiosker → ⋯ → Download diagnostics** to export a sanitized snapshot of the latest payloads (access token is redacted) for support or debugging.
