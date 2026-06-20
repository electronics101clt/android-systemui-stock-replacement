#!/usr/bin/env python3
"""
AC8227L Scatter File Generator
Generates scatter file from ADB partition information
"""

import subprocess
import re
import sys
from datetime import datetime

def run_adb_command(command):
    """Execute ADB command and return output"""
    try:
        result = subprocess.run(
            f"adb shell {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("Error: ADB command timed out")
        return None
    except Exception as e:
        print(f"Error executing ADB command: {e}")
        return None

def get_partition_info():
    """Get partition information from device"""
    print("Getting partition information from device...")

    # Get partition list
    partitions_output = run_adb_command("cat /proc/partitions")
    if not partitions_output:
        print("Error: Could not get partition information")
        return None

    # Get block device mappings
    by_name_output = run_adb_command("ls -la /dev/block/platform/*/by-name/")

    partitions = []

    # Parse /proc/partitions
    for line in partitions_output.split('\n'):
        # Look for mmcblk0pXX entries
        match = re.search(r'(\d+)\s+(\d+)\s+(\d+)\s+(mmcblk0p\d+)', line)
        if match:
            major, minor, blocks, device = match.groups()
            size_bytes = int(blocks) * 1024  # Convert 1K blocks to bytes

            # Try to find partition name from by-name mapping
            partition_name = None
            if by_name_output:
                for by_name_line in by_name_output.split('\n'):
                    if device in by_name_line:
                        # Extract symlink name
                        name_match = re.search(r'(\S+)\s+->\s+.*' + device, by_name_line)
                        if name_match:
                            partition_name = name_match.group(1).split('/')[-1]
                            break

            if not partition_name:
                partition_name = device

            partitions.append({
                'name': partition_name,
                'device': device,
                'size': size_bytes,
                'blocks': int(blocks)
            })

    return partitions

def calculate_partition_addresses(partitions):
    """Calculate physical start addresses for partitions"""
    # Start address after MBR/GPT header (typically 512KB or 1MB)
    current_address = 0x0

    for partition in partitions:
        partition['physical_start_addr'] = f"0x{current_address:08x}"
        partition['linear_start_addr'] = partition['physical_start_addr']
        partition['partition_size'] = f"0x{partition['size']:08x}"

        # Move to next partition (align to 512 byte boundary)
        current_address += partition['size']
        if current_address % 512 != 0:
            current_address = ((current_address // 512) + 1) * 512

    return partitions

def generate_scatter_file(partitions, output_file="MT8127_Android_scatter.txt"):
    """Generate scatter file from partition information"""

    scatter_content = f"""############################################################################################################
#
#  General Setting
#
############################################################################################################
- general: MTK_PLATFORM_CFG
  info:
    - config_version: V1.1.2
      platform: MT8127
      project: 8227L_demo
      storage: EMMC
      boot_channel: MSDC_0
      block_size: 0x20000
############################################################################################################
#
#  Layout Setting
#
############################################################################################################
"""

    # Add each partition
    for idx, part in enumerate(partitions):
        # Determine partition type based on name
        if part['name'] in ['boot', 'recovery']:
            partition_type = 'NORMAL_ROM'
            file_name = f"{part['name']}.img"
            is_download = 'true'
        elif part['name'] in ['system', 'vendor', 'userdata', 'cache']:
            partition_type = 'EXT4_IMG'
            file_name = f"{part['name']}.img"
            is_download = 'true'
        else:
            partition_type = 'NORMAL_ROM'
            file_name = 'NONE'
            is_download = 'false'

        scatter_content += f"""- partition_index: SYS{idx}
  partition_name: {part['name']}
  file_name: {file_name}
  is_download: {is_download}
  type: {partition_type}
  linear_start_addr: {part['linear_start_addr']}
  physical_start_addr: {part['physical_start_addr']}
  partition_size: {part['partition_size']}
  region: EMMC_USER
  storage: HW_STORAGE_EMMC
  boundary_check: true
  is_reserved: false
  operation_type: UPDATE
  is_upgradable: false
  empty_boot_needed: false
  reserve: 0x00

"""

    # Write to file
    with open(output_file, 'w') as f:
        f.write(scatter_content)

    print(f"Scatter file generated: {output_file}")
    return output_file

def main():
    """Main function"""
    print("=" * 60)
    print("AC8227L Scatter File Generator")
    print("=" * 60)
    print()

    # Check if device is connected
    check_device = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
    if "device" not in check_device.stdout:
        print("Error: No ADB device connected")
        print("Please connect your AC8227L device via USB")
        sys.exit(1)

    # Get partition information
    partitions = get_partition_info()
    if not partitions:
        sys.exit(1)

    print(f"Found {len(partitions)} partitions")

    # Calculate addresses
    partitions = calculate_partition_addresses(partitions)

    # Display partition info
    print("\nPartition Layout:")
    print("-" * 60)
    for part in partitions:
        print(f"{part['name']:20s} {part['device']:15s} {part['partition_size']:12s} ({part['size'] // (1024*1024):4d} MB)")
    print("-" * 60)

    # Generate scatter file
    output_file = f"MT8127_Android_scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    generate_scatter_file(partitions, output_file)

    print()
    print("Success! Scatter file created.")
    print(f"Next step: Use this scatter file with readbackbackup tool")
    print()

if __name__ == "__main__":
    main()
