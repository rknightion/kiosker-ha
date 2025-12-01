---
title: Device Data
description: Learn which data points are collected from the Kiosker API and how they map to Home Assistant entities.
---

# Device Data

The integration polls the Kiosker API for three payloads on each update cycle:

1. **Status** (`GET /status`) – core device metadata and telemetry.
2. **Screensaver state** (`GET /screensaver/state`).
3. **Blackout state** (`GET /blackout/state` or `GET /devices/blackout` on newer builds).

## Status fields

| Field | Description | Mapped entity | Notes |
| ----- | ----------- | ------------- | ----- |
| `deviceId` | Unique identifier reported by Kiosker. | Device identifier | Used as the Home Assistant unique ID. |
| `appName` | Name of the running app (Kiosker flavor). | App Version sensor | Shown in device info. |
| `appVersion` | Version of the Kiosker app. | App Version sensor | Included in device info. |
| `osVersion` | iOS/iPadOS version. | OS Version sensor | Diagnostic. |
| `model` | Apple device model. | Device Model sensor | Shown in device info. |
| `ambientLight` | Ambient light reading. | Ambient Light sensor | Unit: lux. |
| `batteryLevel` | Battery percentage. | Battery Level sensor | Unit: %. |
| `batteryState` | Charging state string (Charging/Unplugged/etc.). | Battery State sensor | Enum/diagnostic. |
| `lastInteraction` | Timestamp of the last touch/interaction. | Last Interaction sensor | Timestamp. |
| `lastMotion` | Timestamp of last motion detected. | Last Motion sensor | Timestamp. |
| `date` | Timestamp reported in the payload. | — | Used internally for diagnostics. |

## Screensaver state

| Field | Description | Mapped entity |
| ----- | ----------- | ------------- |
| `visible` | Whether the screensaver is currently on-screen. | Screensaver Active (binary sensor) |
| `disabled` | Whether the screensaver is disabled. | Screensaver Disabled (binary sensor) |

## Blackout state

| Field | Description | Mapped entity |
| ----- | ----------- | ------------- |
| `visible` | Whether the blackout overlay is shown. | Blackout Active (binary sensor) |
| `text` | Optional overlay text. | — |
| `background` | Background color (hex). | — |
| `foreground` | Text color (hex). | — |
| `icon` | Optional icon name. | — |
| `expire` | Seconds until blackout clears. | — |

## Polling cadence

- **Default**: 30 seconds between polls.
- **Minimum**: 5 seconds (enforced to protect the device and Home Assistant).
- **Timeout**: 10 seconds per request.

If the API returns an error or times out, the coordinator marks the update failed and retries on the next cycle.
