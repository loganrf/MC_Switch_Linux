# MC_Switch_Linux

## Use

This library provides command line & python interfaces to the mini ciruits RC-4SPDT-A40 quad SPDT switch.

For command line use the following command illustrates the syntax:
```
# mc_switch A1 B2 C1 D2
```
After invoking "mc_switch" the user has merely to provide the case-insensitive switch configs for the ports in consideration. By default the utility selects the first available USB switch found but the user can specify the serial number like so:
```
# mc_switch -s 02209210196 A1 B2 C1 D2
```

To enumerate all connected Mini-Circuits switches and list their serial numbers:
```
# mc_switch -f
```

To get the current status of a switch (returns 1 or 2):
```
# mc_switch -g A
```

The python interface is very similar
```
import mc_switch as ms

# Specify a specific serial
switch = ms.module(s=02209210196)

# Sets switch A to position 1
switch.set('A1')

# Get status of switch A (returns 1 or 2)
status = switch.get('A')
print(f"Switch A is set to port {status}")

switch.close()
# This method of invocation grabs the first minicircuits switch found
switch2 = ms.module()
switch2.close()
```

## Installation

### Binary Release

You can download the latest pre-built binary for Linux from the [Releases](https://github.com/loganrf/MC_Switch_Linux/releases) page.

1. Download `mc_switch_linux_x64.tar.gz`.
2. Extract the archive:
   ```bash
   tar -xzvf mc_switch_linux_x64.tar.gz
   ```
3. Run the executable:
   ```bash
   ./mc_switch --help
   ```

### Source Installation

#### Prerequisites

Ensure you have Python 3 installed.

Install the `hidapi` Python package:

```bash
pip install hidapi
```

On Linux systems, you may also need to install `libusb` and `libudev` development packages if the pre-built wheels for `hidapi` do not work or if you are building from source:

```bash
sudo apt-get install libusb-1.0-0-dev libudev-dev
```

#### Udev Rules (Linux)

To access the USB device without root privileges, create a udev rule.

Create a file named `/etc/udev/rules.d/99-minicircuits.rules` with the following content:

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="20ce", ATTRS{idProduct}=="0022", MODE="0666"
```

Reload the udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Setup

1. Clone this repository.
2. Ensure `mc_switch.py` and the `mc_switch` script are executable:
   ```bash
   chmod +x mc_switch.py mc_switch
   ```
3. You can run the CLI utility directly:
   ```bash
   ./mc_switch A1
   ```
   Or add the directory to your PATH.
