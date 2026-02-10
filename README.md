# MC_Switch_Linux

# Use

This library provides command line & python interfaces to the mini ciruits RC-4SPDT-A40 quad SPDT switch.

For command line use the following command illustrates the syntax:
```
# mc_switch A1 B2 C1 D2
```
After invoking "mc_switch" the user has merely to provide the case-insensitive switch configs for the ports in consideration. By default the utility selects the first available USB switch found but the user can specify the serial number like so:
```
# mc_switch -s 02209210196 A1 B2 C1 D2
```

The python interface is very similar
```
import mc_switch as ms

# Specify a specific serial
switch = ms.module(s=02209210196)

# Sets switch A to position 1
switch.set('A1')
switch.close()
# This method of invocation grabs the first minicircuits switch found
switch2 = ms.module()
switch2.close()
```
