---
title: API Optimization
description: Tips for keeping Kiosker API calls efficient, reliable, and polite to both the tablet and Home Assistant.
---

# API Optimization

Kiosker exposes a lightweight HTTP API, but rapid polling or unreliable networks can still cause slowdowns. Use these practices to keep updates stable.

## Choose the right update interval

- **Default**: 60 seconds is safe for most setups.
- **Faster updates**: You can lower the interval to 10–30 seconds if you rely on motion/interaction timestamps. Watch CPU usage on both the tablet and Home Assistant.
- **Multiple kiosks**: Stagger intervals across devices (for example 30s, 45s, 60s) to avoid bursts.

Adjust the interval from the integration options dialog.

## Keep traffic on the local network

- Use the tablet’s hostname or static IP in the base URL (`http://tablet-office:8081/api/v1`).
- Avoid exposing the API to the internet; the integration assumes LAN access.
- If you must traverse VLANs, allow the API port (8081) and test with `curl` from the Home Assistant host.

## Handle service calls thoughtfully

Service calls for blackout/screen changes cause immediate UI changes on the kiosk. Avoid sending rapid-fire commands; wait for the next polling cycle if you need state confirmation.

## Error handling and retries

- Each request times out after **10 seconds**.
- Authentication failures trigger a re-authentication flow.
- Connection errors are surfaced as coordinator update failures; the integration recovers automatically on the next cycle once connectivity is restored.

## Logging for troubleshooting

Enable debug logging temporarily to inspect API calls:

```yaml
logger:
  default: info
  logs:
    custom_components.kiosker: debug
    aiohttp: warning
```

Remember to revert to `info` once you have collected the necessary details.
