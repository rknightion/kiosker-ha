---
title: Changelog
description: Release notes for the Kiosker Home Assistant integration.
---

# Changelog

This project follows [Semantic Versioning](https://semver.org/). Notable user-facing changes are recorded here.

## [1.1.0](https://github.com/rknightion/kiosker-ha/releases/tag/v1.1.0) (2025-12-01)

### Features

- Add dynamic battery icon based on level and charging state
- Enhance device information with app name and serial number
- Improve sensor categorization and icons

### Bug Fixes

- Handle missing blackout object in API response

### Code Refactoring

- Remove redundant app name sensor
- Clean up import structure and service configuration

## 1.0.0

- Initial stable release of the integration
- Sensors, binary sensors, action buttons, and services for Kiosker API control
- Config flow with validation, configurable update interval, and diagnostics download support
