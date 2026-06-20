#!/usr/bin/env python3
"""
Readback XML Generator
Converts scatter file to SP Flash Tool readback XML configuration
Based on: https://github.com/Eb43/readbackbackup
"""

import re
import sys
import argparse
from pathlib import Path

def parse_scatter_file(scatter_file):
    """Parse scatter file and extract partition information"""
    with open(scatter_file, 'r') as f:
        content = f.read()

    partitions = []
    current_partition = {}

    for line in content.split('\n'):
        line = line.strip()

        if line.startswith('- partition_index:'):
            # Save previous partition if exists
            if current_partition:
                partitions.append(current_partition)
            # Start new partition
            current_partition = {}
            match = re.search(r'SYS(\d+)', line)
            if match:
                current_partition['index'] = match.group(1)

        elif line.startswith('partition_name:'):
            current_partition['name'] = line.split(':', 1)[1].strip()

        elif line.startswith('physical_start_addr:'):
            addr = line.split(':', 1)[1].strip()
            current_partition['start_addr'] = addr

        elif line.startswith('partition_size:'):
            size = line.split(':', 1)[1].strip()
            current_partition['size'] = size

    # Add last partition
    if current_partition:
        partitions.append(current_partition)

    return partitions

def format_address(addr):
    """Format address to 16-character hex string"""
    if addr.startswith('0x'):
        addr = addr[2:]
    addr = addr.lower().zfill(16)
    return f"0x{addr}"

def generate_readback_xml(partitions, output_dir, chip_name="MT8127", storage_type="EMMC"):
    """Generate readback XML configuration"""

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    xml_header = f"""<?xml version="1.0" encoding="UTF-8" ?>
<flashtool-config version="2.0">
    <general>
        <chip-name>{chip_name}</chip-name>
        <storage-type>{storage_type}</storage-type>
    </general>
    <commands>
        <readback>
            <physical-readback is-physical-readback="false" />
            <readback-list>
"""

    xml_footer = """            </readback-list>
        </readback>
    </commands>
</flashtool-config>
"""

    readback_items = []

    for part in partitions:
        if 'index' not in part or 'name' not in part:
            continue

        start_addr = format_address(part.get('start_addr', '0x0'))
        size = part.get('size', '0x00000000')

        file_path = str(output_path / part['name'])

        readback_item = (
            f'                <readback-rom-item '
            f'readback-index="{part["index"]}" '
            f'readback-enable="true" '
            f'readback-flag="NUTL_READ_PAGE_ONLY" '
            f'start-address="{start_addr}" '
            f'readback-length="{size}" '
            f'addr-flag="NUTL_ADDR_LOGICAL" '
            f'part-id="34">{file_path}</readback-rom-item>'
        )
        readback_items.append(readback_item)

    xml_content = xml_header + '\n'.join(readback_items) + '\n' + xml_footer

    return xml_content

def main():
    parser = argparse.ArgumentParser(
        description='Generate SP Flash Tool readback XML from scatter file'
    )
    parser.add_argument(
        'scatter_file',
        help='Path to scatter file'
    )
    parser.add_argument(
        '-o', '--output',
        default='readback_ui_bak.xml',
        help='Output XML file (default: readback_ui_bak.xml)'
    )
    parser.add_argument(
        '-d', '--dir',
        default='./readback_backup',
        help='Backup directory (default: ./readback_backup)'
    )
    parser.add_argument(
        '-c', '--chip',
        default='MT8127',
        help='Chip name (default: MT8127)'
    )
    parser.add_argument(
        '-s', '--storage',
        default='EMMC',
        help='Storage type (default: EMMC)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Readback XML Generator")
    print("=" * 60)
    print()

    # Check if scatter file exists
    if not Path(args.scatter_file).exists():
        print(f"Error: Scatter file not found: {args.scatter_file}")
        sys.exit(1)

    print(f"Reading scatter file: {args.scatter_file}")

    # Parse scatter file
    partitions = parse_scatter_file(args.scatter_file)
    print(f"Found {len(partitions)} partitions")

    # Display partitions
    print("\nPartitions to backup:")
    print("-" * 60)
    for part in partitions:
        print(f"  {part.get('index', '?'):3s}: {part.get('name', 'unknown'):20s} @ {part.get('start_addr', '?'):12s} ({part.get('size', '?')})")
    print("-" * 60)

    # Generate XML
    print(f"\nGenerating readback XML...")
    xml_content = generate_readback_xml(
        partitions,
        args.dir,
        args.chip,
        args.storage
    )

    # Write XML file
    with open(args.output, 'w') as f:
        f.write(xml_content)

    print(f"Readback XML saved to: {args.output}")
    print(f"Backup directory: {args.dir}")
    print()
    print("Next steps:")
    print("  1. Copy this XML to SP Flash Tool directory")
    print("  2. Run SP Flash Tool and go to Readback tab")
    print("  3. Click 'Readback' button to start backup")
    print()

if __name__ == "__main__":
    main()
