from . import helper

class PCIeDevice(object):

    def __init__(self, bus, device, func, name, rwe):
     
        self.rwe = rwe
        self.bus = helper.hexstr_to_int(bus) if type(bus) == str else bus    
        self.device = helper.hexstr_to_int(device) if type(device) == str else device
        self.function = helper.hexstr_to_int(func) if type(func) == str else func
        self.name = name

        self._config_space = None
        
        self.upstream = None
        self.downstream = []
    
    def print_tree(self, indent=0) -> None:
        indent_str = " " * indent
        print(indent_str + str(self))
        for device in self.downstream:
            device.print_tree(indent+4)

    def find_device(self, bus:int, device:int, func:int):
        '''
        Returns the PCIeDevice under the current device, returns none if not found
        '''
        if(self.bus == bus and self.device == device and self.function == func):
            return self
        else:
            for port in self.downstream:
                
                d = port.find_device(bus, device, func)
                if(d is not None):
                    return d

    def get_flat_device_list(self):
        '''
        Return a list of all device under the current device including itself
        '''
        
        l = [self]
        for device in self.downstream:
            l += device.get_flat_device_list()
            
        return l 
    
    def __str__(self) -> str:
        if self.bus < 0:
            return f"Bus: {self.bus} Device:{self.device} Function:{self.function} - {self.name}"
        else:
            bus = helper.int_to_hexstr(self.bus)
            device = helper.int_to_hexstr(self.device)
            function = helper.int_to_hexstr(self.function)

            return f"Bus: 0x{bus} Device: 0x{device} Function: 0x{function} - {self.name}"


    def get_config_space_data(self) -> bytes:
        '''
        Use this to read the config space, this is more efficient than reading per byte
        '''
        
        if(self._config_space is None): #no need to initialize the rc object
            self._config_space = self.rwe.read_PCI_space(self.bus, self.device, self.function)
        
        return self._config_space 


    def set_config_space_data(self, data:bytes) -> None:
        '''
        Recommend not using this unless absolutely needed
        '''
        
        if(len(data) != 4096):
            raise Exception("data is not 4096 bytes long")

        return self.rwe.wirte_PCI_space(self.bus, self.device, self.function, data)
  
    
    def read_config_space_bytes(self, offset:int, size:int) -> bytes:
        return self.rwe.read_bytes(self.bus, self.device, self.function, offset, size)

    
    def write_config_space_bytes(self, offset:int, data:bytes) -> None:
        return self.rwe.write_bytes(self.bus, self.device, self.function, offset, data)
   
    
    def print_cap_registers(self) -> None:
        '''
        Shows all PCI/PCIe cap registers in the first 256 bytes of the space
        '''

        data = self.get_config_space_data()

        first_pointer = 0x34
        
        next_pointer = int.from_bytes(helper.read_bytes(data, first_pointer, 1), 'big')
        while next_pointer != 0x00:
            
            cap_id = helper.bytes_to_hexstr(helper.read_bytes(data, next_pointer, 1))
            next_ptr = helper.bytes_to_hexstr(helper.read_bytes(data, next_pointer+1, 1))
            cur_ptr = helper.int_to_hexstr(next_pointer)
            print(f"Cur ptr: {cur_ptr} | Cap ID: {cap_id} | Next ptr: {next_ptr}")

            next_pointer = int.from_bytes(helper.read_bytes(data, next_pointer+1, 1), 'big')


    def print_extended_cap_registers(self) -> None:
        '''
        Shows all PCI/PCIe extended cap registers after the 256 bytes of the space
        '''

        data = self.get_config_space_data()

        next_pointer = 0x0100
        while next_pointer != 0x0000:

            cap_id = helper.bytes_to_hexstr(helper.read_bytes(data, next_pointer, 2))
            next_ptr = helper.bytes_to_hexstr(helper.read_bits(helper.read_bytes(data, next_pointer+2, 2), 4, 15) )
            cur_ptr = helper.int_to_hexstr(next_pointer)
            print(f"Cur ptr: {cur_ptr} | Cap ID: {cap_id} | Next ptr: {next_ptr}")

            next_pointer = int.from_bytes( helper.read_bits(helper.read_bytes(data, next_pointer+2, 2), 4, 15) , 'big')
    
    
    def find_cap_register_offset(self, cap_id:int) -> int:
        data = self.get_config_space_data()
        first_pointer = 0x34
        
        next_pointer = int.from_bytes(helper.read_bytes(data, first_pointer, 1), 'big')
        while next_pointer != 0x00:
            cur_cap_id = int.from_bytes(helper.read_bytes(data, next_pointer, 1), 'big')
            
            if(cur_cap_id == cap_id):
                return next_pointer

            next_pointer = int.from_bytes(helper.read_bytes(data, next_pointer+1, 1), 'big')


    def find_extended_cap_register_offset(self, cap_id:int) -> int:
        data = self.get_config_space_data()

        next_pointer = 0x0100
        while next_pointer != 0x0000:

            cur_cap_id = int.from_bytes(helper.read_bytes(data, next_pointer, 2), 'big')
            if(cur_cap_id == cap_id):
                return next_pointer

            next_pointer = int.from_bytes( helper.read_bits(helper.read_bytes(data, next_pointer+2, 2), 4, 15) , 'big')
    