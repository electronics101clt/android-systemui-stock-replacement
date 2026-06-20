# AC8227L Automated Readback System

Complete automation for backing up AC8227L Android head units using SP Flash Tool on Linux.

## Overview

This system automates the process of creating full backups (readback) of MediaTek AC8227L devices using SP Flash Tool. It consists of three Python scripts that work together to:

1. Generate scatter files from device partition information
2. Create SP Flash Tool readback XML configurations
3. Automate the complete backup workflow

## Requirements

- **Python 3.6+**
- **ADB** (Android Debug Bridge)
- **SP Flash Tool v6.2228** (included)
- **USB connection** to AC8227L device
- **Linux** (Ubuntu 24.04 tested)

## Installation

Everything is already set up in this directory:

```bash
cd ~/sp-flash-tool
ls -la
```

**Files:**
- `generate_scatter.py` - Scatter file generator
- `generate_readback_xml.py` - Readback XML generator
- `automate_readback.py` - Main automation script
- `SP_Flash_Tool_v6.2228_Linux/` - SP Flash Tool
- `readbackbackup/` - Helper tool from GitHub

## Usage

### Quick Start - Full Automated Backup

Connect your AC8227L device via USB and run:

```bash
./automate_readback.py
```

This will:
1. Check ADB connection
2. Generate scatter file from device partitions
3. Create readback XML configuration
4. Launch SP Flash Tool GUI
5. Save all files to `backups/YYYYMMDD_HHMMSS/`

### Custom Backup Directory

```bash
./automate_readback.py -o /path/to/backup
```

### Individual Scripts

#### 1. Generate Scatter File Only

```bash
./generate_scatter.py
```

This connects to your device via ADB and creates a scatter file from the partition layout.

**Output:** `MT8127_Android_scatter_YYYYMMDD_HHMMSS.txt`

#### 2. Generate Readback XML from Scatter File

```bash
./generate_readback_xml.py MT8127_Android_scatter.txt -o readback_ui_bak.xml -d ./backup_images
```

**Options:**
- `-o, --output` - Output XML file (default: readback_ui_bak.xml)
- `-d, --dir` - Backup directory path (default: ./readback_backup)
- `-c, --chip` - Chip name (default: MT8127)
- `-s, --storage` - Storage type (default: EMMC)

#### 3. Manual SP Flash Tool Launch

```bash
cd SP_Flash_Tool_v6.2228_Linux
./SPFlashToolV6
```

## How It Works

### Step 1: Partition Discovery

The `generate_scatter.py` script:
- Connects to device via ADB
- Reads `/proc/partitions` for partition list
- Queries `/dev/block/platform/*/by-name/` for partition names
- Calculates physical addresses and sizes
- Generates MediaTek scatter file format

### Step 2: Readback Configuration

The `generate_readback_xml.py` script:
- Parses the scatter file
- Extracts partition metadata (name, address, size)
- Generates SP Flash Tool readback XML
- Configures backup file paths

### Step 3: Backup Execution

The `automate_readback.py` script:
- Orchestrates the entire workflow
- Creates organized backup directory structure
- Launches SP Flash Tool with proper configuration
- Generates backup summary documentation

## SP Flash Tool Readback Process

Once SP Flash Tool GUI launches:

1. **Readback Tab** - Click to switch to readback mode
2. **Load Scatter** - Should auto-load from readback_ui_bak.xml
3. **Select Partitions** - Choose which partitions to backup
4. **Readback Button** - Click to start
5. **Connect Device** - Put device in download mode:
   - Power off device
   - Connect USB
   - Device should be detected automatically
6. **Wait** - Backup process will run (can take 5-30 minutes)
7. **Complete** - Files saved to specified backup directory

## Download Mode

To enter download mode on AC8227L:

**Method 1: Automatic (recommended)**
- SP Flash Tool will attempt to put device in download mode
- Simply power off and connect USB when prompted

**Method 2: Manual**
- Power off device completely
- Connect 6-pin USB cable to board
- Tool should detect device

**Troubleshooting:**
- If not detected: Try different USB port
- Check `lsusb` for MediaTek device (vendor ID: 0e8d)
- Install VCOM drivers if needed (see SP_Flash_Tool_v6.2228_Linux/Driver/)

## Backup File Structure

```
backups/
└── 20260618_230500/
    ├── BACKUP_INFO.txt
    ├── MT8127_Android_scatter_20260618_230500.txt
    ├── readback_ui_bak.xml
    └── images/
        ├── preloader
        ├── lk
        ├── boot
        ├── recovery
        ├── system
        ├── vendor
        ├── userdata
        ├── cache
        └── ...
```

## Partition Information

Common AC8227L partitions:
- `preloader` - Bootloader (CRITICAL - backup first!)
- `lk` - Little Kernel bootloader
- `boot` - Android boot image
- `recovery` - Recovery partition
- `system` - Android system partition
- `vendor` - Vendor apps and libs
- `userdata` - User data and apps
- `cache` - System cache
- `nvram` - Non-volatile RAM (IMEI, calibration data)

## Important Notes

### Security
- ⚠️ Backups contain IMEI and device-specific calibration data
- Keep backups secure and private
- Do not share NVRAM/NVDATA partitions publicly

### Brick Recovery
- Always backup `preloader` partition first
- With full backup, device can be recovered from any soft brick
- Full readback can restore device to exact working state

### Time Estimates
- Scatter generation: ~5 seconds
- XML generation: <1 second
- Full readback (32GB): ~10-30 minutes depending on USB speed

## Troubleshooting

### ADB Device Not Found
```bash
adb devices
# If empty, check USB connection and enable USB debugging on device
```

### SP Flash Tool Won't Detect Device
- Check `lsusb | grep -i mediatek`
- Install VCOM drivers
- Try different USB port (prefer USB 2.0)
- Check USB cable quality

### Readback Fails
- Ensure sufficient disk space (need 32GB+ free)
- Check backup directory permissions
- Verify scatter file is correct for your device

### Python Dependencies
All scripts use standard library only, no pip packages needed.

## Advanced Usage

### Creating Scatter File Without Device

If you have partition information from another source:

```python
# Edit generate_scatter.py and manually define partitions
partitions = [
    {'name': 'boot', 'device': 'mmcblk0p10', 'size': 16777216},
    # ... add more partitions
]
```

### Custom Chip/Storage Type

```bash
./generate_readback_xml.py scatter.txt -c MT6765 -s UFS
```

### Selective Backup

Edit the generated `readback_ui_bak.xml` and set `readback-enable="false"` for partitions you want to skip.

## References

- [SP Flash Tool on GNU/Linux](https://www.rigacci.org/wiki/doku.php/doc/appunti/android/sp_flash_tool)
- [GitHub: readbackbackup tool](https://github.com/Eb43/readbackbackup)
- [XDA: MediaTek Backup Guide](https://xdaforums.com/t/guide-mediatek-android-head-units-how-to-fully-backup-or-restore-backup-with-sp-flash-tool-beginner-friendly-tutorial.4201001/)
- [Android MTK: Create Scatter File](https://androidmtk.com/create-scatter-file-for-mtk-devices)

## License

Educational use only. Use at your own risk.

## Contributing

Have improvements? Found bugs? Submit issues or pull requests.

---

**Created:** 2026-06-18
**Device:** AC8227L Android Head Unit
**Platform:** Linux (Ubuntu 24.04)
**SP Flash Tool:** v6.2228
