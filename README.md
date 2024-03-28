# python-rwe
Simple python ReadWriteEverything wrapper

Example script to disable completion_timeout

```python
from rwepy.rwe import RWE
import rwepy.helper as h
from rwepy.PCIeRegisters import PCIeRegisters

rwe = RWE()
device = rwe.find_device(0x10DE, 0x2484) # Device Upstream port
start_device = device.upstream

for device in start_device.get_flat_device_list():

    express_cap_offset = device.find_cap_register_offset(PCIeRegisters.pcie_express_capability.value)
    device2_offset = express_cap_offset + 0x28

    device2_data = device.read_config_space_bytes(device2_offset, 2)
    device2_data = h.set_bit(device2_data, 4, 1)
    device.write_config_space_bytes(device2_offset, device2_data)
```
