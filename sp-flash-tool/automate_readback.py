#!/usr/bin/env python3
"""
AC8227L Automated Readback System
Complete automation for backing up AC8227L device using SP Flash Tool
"""

import subprocess
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

class AC8227LBackup:
    def __init__(self, backup_dir=None, device_check=True):
        self.sp_flash_tool_dir = Path(__file__).parent / "SP_Flash_Tool_v6.2228_Linux"
        self.sp_flash_tool_bin = self.sp_flash_tool_dir / "SPFlashToolV6"
        self.backup_dir = Path(backup_dir) if backup_dir else Path.cwd() / "backups" / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.scatter_file = None
        self.readback_xml = None
        self.device_check = device_check

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def check_adb_connection(self):
        """Check if ADB device is connected"""
        print("Checking ADB connection...")
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True
        )

        if "device" not in result.stdout or result.stdout.count('\n') < 2:
            print("❌ Error: No ADB device connected")
            print("Please connect your AC8227L device via USB")
            return False

        print("✅ ADB device connected")
        return True

    def generate_scatter_file(self):
        """Generate scatter file from device"""
        print("\n" + "=" * 60)
        print("Step 1: Generating Scatter File")
        print("=" * 60)

        scatter_output = self.backup_dir / f"scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # Run scatter generator
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "generate_scatter.py")],
            cwd=self.backup_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("❌ Error generating scatter file")
            print(result.stderr)
            return None

        # Find the generated scatter file
        scatter_files = list(self.backup_dir.glob("MT8127_Android_scatter_*.txt"))
        if scatter_files:
            self.scatter_file = scatter_files[0]
            print(f"✅ Scatter file generated: {self.scatter_file}")
            return self.scatter_file
        else:
            print("❌ Error: Scatter file not found")
            return None

    def generate_readback_xml(self):
        """Generate readback XML configuration"""
        print("\n" + "=" * 60)
        print("Step 2: Generating Readback XML")
        print("=" * 60)

        if not self.scatter_file:
            print("❌ Error: No scatter file available")
            return None

        readback_xml_path = self.backup_dir / "readback_ui_bak.xml"

        # Run readback XML generator
        result = subprocess.run([
            sys.executable,
            str(Path(__file__).parent / "generate_readback_xml.py"),
            str(self.scatter_file),
            "-o", str(readback_xml_path),
            "-d", str(self.backup_dir / "images")
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Error generating readback XML")
            print(result.stderr)
            return None

        self.readback_xml = readback_xml_path
        print(f"✅ Readback XML generated: {self.readback_xml}")
        return self.readback_xml

    def prepare_sp_flash_tool(self):
        """Prepare SP Flash Tool environment"""
        print("\n" + "=" * 60)
        print("Step 3: Preparing SP Flash Tool")
        print("=" * 60)

        # Check if SP Flash Tool exists
        if not self.sp_flash_tool_bin.exists():
            print(f"❌ Error: SP Flash Tool not found at {self.sp_flash_tool_bin}")
            return False

        # Make executable
        self.sp_flash_tool_bin.chmod(0o755)

        # Copy readback XML to SP Flash Tool directory
        if self.readback_xml:
            target_xml = self.sp_flash_tool_dir / "readback_ui_bak.xml"
            subprocess.run(["cp", str(self.readback_xml), str(target_xml)])
            print(f"✅ Readback XML copied to SP Flash Tool directory")

        print(f"✅ SP Flash Tool ready at: {self.sp_flash_tool_bin}")
        return True

    def run_sp_flash_tool_gui(self):
        """Launch SP Flash Tool GUI for manual readback"""
        print("\n" + "=" * 60)
        print("Step 4: Launching SP Flash Tool")
        print("=" * 60)
        print()
        print("MANUAL STEPS:")
        print("  1. SP Flash Tool will open")
        print("  2. Go to 'Readback' tab")
        print("  3. Click 'Add' button")
        print("  4. Load scatter file if prompted")
        print("  5. Configure partitions to backup")
        print("  6. Click 'Readback' button")
        print("  7. Connect device in download mode")
        print("  8. Wait for backup to complete")
        print()
        print(f"Scatter file: {self.scatter_file}")
        print(f"Backup location: {self.backup_dir / 'images'}")
        print()
        input("Press Enter to launch SP Flash Tool...")

        # Launch SP Flash Tool
        try:
            subprocess.run(
                [str(self.sp_flash_tool_bin)],
                cwd=self.sp_flash_tool_dir
            )
        except KeyboardInterrupt:
            print("\nSP Flash Tool closed")

    def run_console_mode_readback(self):
        """Run SP Flash Tool in console mode (experimental)"""
        print("\n" + "=" * 60)
        print("Step 4: Running Console Mode Readback")
        print("=" * 60)
        print()
        print("⚠️  Console mode is experimental")
        print("Please ensure device is in download mode")
        print()
        input("Press Enter to continue or Ctrl+C to cancel...")

        # Note: Console mode readback requires specific XML format
        # This is a placeholder - actual implementation depends on SP Flash Tool version
        print("❌ Console mode not yet fully implemented")
        print("Please use GUI mode instead")

    def create_backup_summary(self):
        """Create a summary file of the backup"""
        summary_file = self.backup_dir / "BACKUP_INFO.txt"

        with open(summary_file, 'w') as f:
            f.write(f"AC8227L Backup Summary\n")
            f.write(f"=" * 60 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Backup Directory: {self.backup_dir}\n")
            f.write(f"Scatter File: {self.scatter_file.name if self.scatter_file else 'N/A'}\n")
            f.write(f"Readback XML: {self.readback_xml.name if self.readback_xml else 'N/A'}\n")
            f.write(f"\n")
            f.write(f"Files:\n")
            for file in self.backup_dir.rglob('*'):
                if file.is_file():
                    f.write(f"  - {file.relative_to(self.backup_dir)}\n")

        print(f"\n✅ Backup summary saved: {summary_file}")

    def run_full_backup(self, gui_mode=True):
        """Run complete backup process"""
        print("\n" + "=" * 80)
        print(" AC8227L AUTOMATED READBACK SYSTEM")
        print("=" * 80)
        print(f"Backup directory: {self.backup_dir}")
        print()

        # Step 1: Check ADB connection (if device check enabled)
        if self.device_check and not self.check_adb_connection():
            return False

        # Step 2: Generate scatter file
        if not self.generate_scatter_file():
            return False

        # Step 3: Generate readback XML
        if not self.generate_readback_xml():
            return False

        # Step 4: Prepare SP Flash Tool
        if not self.prepare_sp_flash_tool():
            return False

        # Step 5: Run SP Flash Tool
        if gui_mode:
            self.run_sp_flash_tool_gui()
        else:
            self.run_console_mode_readback()

        # Step 6: Create backup summary
        self.create_backup_summary()

        print("\n" + "=" * 80)
        print(" BACKUP PROCESS COMPLETE")
        print("=" * 80)
        print(f"All files saved to: {self.backup_dir}")
        print()

        return True

def main():
    parser = argparse.ArgumentParser(
        description='Automated readback system for AC8227L devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full automated backup (GUI mode)
  python3 automate_readback.py

  # Backup to specific directory
  python3 automate_readback.py -o /path/to/backup

  # Skip ADB device check (use existing scatter file)
  python3 automate_readback.py --no-device-check

  # Console mode (experimental)
  python3 automate_readback.py --console
        """
    )

    parser.add_argument(
        '-o', '--output',
        help='Output directory for backup files'
    )
    parser.add_argument(
        '--console',
        action='store_true',
        help='Use console mode instead of GUI (experimental)'
    )
    parser.add_argument(
        '--no-device-check',
        action='store_true',
        help='Skip ADB device check'
    )

    args = parser.parse_args()

    # Create backup instance
    backup = AC8227LBackup(
        backup_dir=args.output,
        device_check=not args.no_device_check
    )

    # Run backup
    try:
        success = backup.run_full_backup(gui_mode=not args.console)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nBackup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
