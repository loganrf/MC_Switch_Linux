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

        data = [0x00] + report
        self.device.write(data)

    def get(self, switch_char):
        """
        Gets the state of a switch.
        Returns:
            1 if state is 0 (Port 1)
            2 if state is 1 (Port 2)
            Other value if state is different.
        """
        switch_char = switch_char.upper()
        if not ('A' <= switch_char <= 'H'):
            raise ValueError(f"Invalid switch '{switch_char}'. Must be between A and H.")

        switch_index = ord(switch_char) - ord('A') + 1

        # Attempt to read status.
        # Try to read directly first
        data = self.device.read(64, timeout_ms=100)

        if not data:
            # If no data, send a query.
            # We use a command code matching switch_index but with a special state value.
            # Assuming state 2 requests status.
            report = [0] * 64
            report[0] = switch_index
            report[1] = 0x02 # Request Status
            self.device.write([0x00] + report)

            data = self.device.read(64, timeout_ms=200)

        if not data:
            raise RuntimeError("Failed to read switch status.")

        # Parse response
        # Assuming format: [switch_index, state, ...]
        if len(data) >= 2:
            resp_index = data[0]
            resp_state = data[1]

            # State mapping: 0 -> 1, 1 -> 2
            if resp_state == 0:
                return 1
            elif resp_state == 1:
                return 2
            else:
                 return resp_state # Raw state if unexpected or unsupported

        raise RuntimeError(f"Unexpected response format: {data}")

    def close(self):
        if self.device:
            self.device.close()

def main():
    parser = argparse.ArgumentParser(description="Control Mini-Circuits RF Switches via USB")
    parser.add_argument('-s', '--serial', type=str, help='Serial number of the device')
    parser.add_argument('-f', '--find', action='store_true', help='List all connected MC switches')
    parser.add_argument('-g', '--get', type=str, help='Get the state of a switch (e.g. A)')
    parser.add_argument('commands', nargs='*', help='Switch commands (e.g., A1 B2)')

    args = parser.parse_args()

    if args.find:
        # Enumerate devices
        try:
            device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)
            if not device_list:
                print("No Mini-Circuits RF Switch devices found.")
            else:
                print("Connected Mini-Circuits RF Switches:")
                for dev in device_list:
                    print(f"- Serial: {dev['serial_number']}")
        except Exception as e:
            print(f"Error enumerating devices: {e}", file=sys.stderr)
        return

    try:
        sw = module(s=args.serial)

        if args.get:
             try:
                 state = sw.get(args.get)
                 print(f"{state}")
             except Exception as e:
                 print(f"Error getting status for switch {args.get}: {e}", file=sys.stderr)

        if not args.commands and not args.get:
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
