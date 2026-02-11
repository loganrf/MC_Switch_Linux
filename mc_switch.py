import hid
import sys
import argparse
import time

VENDOR_ID = 0x20CE
PRODUCT_ID = 0x0022

class module:
    def __init__(self, s=None):
        self.device = None
        self.serial = s

        target_path = None

        # Enumerate devices
        device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)

        if not device_list:
            raise RuntimeError("No Mini-Circuits RF Switch devices found.")

        if s:
            # Find specific serial
            found = False
            for dev in device_list:
                if dev['serial_number'] == str(s):
                    target_path = dev['path']
                    found = True
                    break
            if not found:
                raise RuntimeError(f"Device with serial number {s} not found.")
        else:
            # Pick first available
            target_path = device_list[0]['path']
            if not s:
                 s = device_list[0]['serial_number']

        self.serial = s

        try:
            self.device = hid.device()
            self.device.open_path(target_path)
        except Exception as e:
            raise RuntimeError(f"Failed to open device: {e}")

    def set(self, command):
        """
        Sets a switch state based on a command string like 'A1', 'B2', etc.
        """
        if not command or len(command) < 2:
            raise ValueError("Invalid command format. Expected format like 'A1'.")

        switch_char = command[0].upper()
        state_char = command[1:]

        # Mapping switch char to index (A=1, B=2, ..., H=8)
        if not ('A' <= switch_char <= 'H'):
            raise ValueError(f"Invalid switch '{switch_char}'. Must be between A and H.")

        switch_index = ord(switch_char) - ord('A') + 1

        try:
            port = int(state_char)
        except ValueError:
            raise ValueError(f"Invalid port '{state_char}'. Must be a number.")

        # Mapping port to state (1 -> 0, 2 -> 1)
        if port == 1:
            state = 0
        elif port == 2:
            state = 1
        else:
            raise ValueError(f"Invalid port {port}. Must be 1 or 2 for SPDT switches.")

        # Construct report
        # Report format: 64 bytes
        # Byte 0: Switch index (1-8)
        # Byte 1: State (0 or 1)
        report = [0] * 64
        report[0] = switch_index
        report[1] = state

        # Send report
        # Note: hidapi.write expects a list of integers.
        # First byte is report ID if using numbered reports, but here protocol says Byte 0 is command code.
        # However, hidapi usually requires report ID as first byte if report IDs are used.
        # If report IDs are NOT used (Report ID 0), then first byte of data is the first byte of payload.
        # But if the device expects Report ID 0, some platforms might prepend 0 automatically or require it.
        # Let's assume standard behavior: prepend 0x00 if Report IDs are used, or just send data.
        # The manual says "Transmit Array = [Byte 0][Byte 1]...". It doesn't explicitly mention Report ID.
        # Typically with hidapi, if Report ID is 0, we prepend 0. If protocol Byte 0 IS the command, it might be the Report ID itself?
        # But here Command Code is 1-8 for Setting Switch. These are likely NOT Report IDs because Report IDs are usually constant for a type of report (e.g. OUT report).
        # But here Byte 0 varies. So likely it is just data payload.
        # In hidapi, write() sends data to the Output endpoint.
        # If the device uses Report ID 0 (no report ID), we just send the 64 bytes.
        # However, on some systems (Windows), the first byte must be 0x00 (Report ID). On Linux it might not matter or might be stripped.
        # The safest way is to try sending [0] + report if report ID is required, or just report.
        # Since I can't test, I'll follow common practice.
        # The manual says "Transmit Array = [Byte 0][Byte1]...".
        # Byte 0 is the Command Code.
        # If Command Code is variable (1, 9, 40...), it suggests it's part of the payload, NOT the Report ID.
        # So I should send 64 bytes where buffer[0] is the command code.
        # For hidapi.write, we usually prepend 0x00 as Report ID if the device doesn't use numbered reports.
        # I'll prepend 0x00 just in case, making it 65 bytes.

        data = [0x00] + report
        self.device.write(data)

    def close(self):
        if self.device:
            self.device.close()

def main():
    parser = argparse.ArgumentParser(description="Control Mini-Circuits RF Switches via USB")
    parser.add_argument('-s', '--serial', type=str, help='Serial number of the device')
    parser.add_argument('commands', nargs='*', help='Switch commands (e.g., A1 B2)')

    args = parser.parse_args()

    try:
        sw = module(s=args.serial)

        if not args.commands:
            print(f"Connected to Mini-Circuits RF Switch (Serial: {sw.serial})")

        for cmd in args.commands:
            try:
                sw.set(cmd)
            except ValueError as e:
                print(f"Error processing command '{cmd}': {e}", file=sys.stderr)

        sw.close()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
