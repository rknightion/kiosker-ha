---
title: Entity Naming
description: Understand how the Kiosker integration names devices and entities inside Home Assistant.
---

# Entity Naming

The integration follows Home Assistant’s standard device/entity naming rules while keeping kiosk context clear.

## Device name

- If you set a **Name** during setup, that becomes the device name.
- Otherwise the integration uses `appName` from the Kiosker API, or falls back to `Kiosker <deviceId>`.

## Entity names

All entities opt into “Use device name”. The visible entity name is the device name plus the entity label:

```
<device name>: Ambient Light
<device name>: Screensaver Active
```

Entity labels come from the integration and match the tables in [Entities](entities.md).

## Unique IDs

Unique IDs are derived from the Kiosker `deviceId` and the entity key, for example:

- `abc123_ambient_light`
- `abc123_blackout_active`

This ensures stable identifiers even if you rename the device in Home Assistant.

## Renaming

You can rename entities or the device in Home Assistant without affecting functionality. The unique IDs stay the same, so automations and dashboards keep working after renaming.
