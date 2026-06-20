# Android SystemUI Stock Replacement

Replace Chinese head unit custom SystemUI with stock AOSP Android 8.1 SystemUI.

## Goal
Replace custom MediaTek SystemUI (MtkSystemUI.apk + OP01SystemUI.apk) and custom navbar (EasyRemind.apk) with stock AOSP Android 8.1 SystemUI on AC8227L head unit.

## Device Info
- Model: 9210B (alps manufacturer)
- SoC: AC8227L / MT8168
- Reported Android: 10.0
- Actual API Level: 27 (Android 8.1 Oreo)
- Build: 9210B_00028_V001

## Original SystemUI Components
- `/system/priv-app/MtkSystemUI/MtkSystemUI.apk` (11MB) - Status bar + notifications
- `/system/app/OP01SystemUI/OP01SystemUI.apk` (54KB) - Overlay
- `/system/app/EasyRemind/EasyRemind.apk` (10MB) - Custom navigation bar

## Stock AOSP SystemUI
- Downloaded from: `arm64-v8a-27_r01.zip` (Android 8.1 AOSP)
- Size: 6.3MB
- Location: `/system/priv-app/SystemUI/SystemUI.apk`
- Handles: Status bar + notifications + navigation bar (unified)

## Challenge
`/system` partition is read-only and cannot be remounted read-write via standard methods:
- `mount -o remount,rw /system` fails with "read-only filesystem"
- `blockdev --setrw` ineffective
- Device lacks `adb root` capability

## Solution Approach
Use SP Flash Tool to directly flash modified system partition bypassing Android mount restrictions.

## Tools Included
- **mtkclient** (v2.1.3) - CLI tool for MediaTek devices
- **sp-flash-tool** (v6.2228) - GUI/CLI flashing tool
- Helper scripts for readback and scatter generation

## Backups
Original Chinese head unit SystemUI files backed up to external storage.

## Status
In progress - awaiting SP Flash Tool implementation for system partition modification.
