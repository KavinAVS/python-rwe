import os
import subprocess
import sys
import re
import binascii
from . import helper
from .PCIeDevice import PCIeDevice


TMP_FILE_LOC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '__tmp.bin')


class RWE(object):

    def __init__(self):
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rwe\Rw.exe')
        self.default_args = '/Min /Nologo /Stdout'
        self.PCIeRC = None
        self.PCIeRC = self.get_pci_tree()

    def callCommand(self, cmd:str) -> str:
        fullCmd = f"\"{self.path}\" {self.default_args} /Command=\"{cmd}\""
        
        r = subprocess.Popen(fullCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out, err = r.communicate()

        if err != b'':
            print(err.decode(), file=sys.stderr)
            exit(1) 

        return out.decode()

    def get_pci_tree(self) -> PCIeDevice:
        '''
        Returns a PCIeDevice "root complex" device with all pcie devices map in a tree
        '''
        if(self.PCIeRC is not None): #no need to initialize the rc object
            return self.PCIeRC

        tree = self.callCommand("PCITree")

        root_complex = PCIeDevice(-1,0,0, "RC-Dummy", self) # just a dummy object

        cur_indent = 0
        prev_device = None
        cur_parent = root_complex
        for device in tree.split("\n"):
            indent = (len(device) - len(device.lstrip()))/2 #2 space per indentation level
            
            # Move up and down the tree based one indentation, this works since the output has the device ordered
            if(indent > cur_indent):
                cur_parent = prev_device
            elif(indent < cur_indent):
                cur_parent = cur_parent.upstream

            cur_indent = indent

            m = re.search(r'Bus (\w*), Device (\w*), Function (\w*) \- (.*)', device)
            if m is None:
                continue
            
            #print(f'Bus = {m.group(1)} Device = {m.group(2)} Function = {m.group(3)} Name = {m.group(4)}')

            device = PCIeDevice(m.group(1),m.group(2),m.group(3),m.group(4), self)
            device.upstream = cur_parent
            cur_parent.downstream.append(device)
            
            prev_device = device

        return root_complex
    
    def read_PCI_space(self, bus:int, device:int, function:int) -> bytes:
        '''
        Returns a byte object with all data from the device's pcie space
        '''

        o = self.callCommand(f'SAVE \"{TMP_FILE_LOC}\" PCI {bus} {device} {function}')

        with open(TMP_FILE_LOC, "rb") as tmp:
            b = tmp.read()
        
        os.remove(TMP_FILE_LOC)
        return b

    def wirte_PCI_space(self, bus:int, device:int, function:int, data:bytes) -> None:
        '''
        Write len 4096 byte object to the PCIe space of the device

        Note: this will replace the entire pcie space of the device, but ignores the read only bits 
        '''
        with open(TMP_FILE_LOC, "wb") as tmp:
            tmp.write(data)

        o = self.callCommand(f'LOAD \"{TMP_FILE_LOC}\" PCI {bus} {device} {function}')
        
        os.remove(TMP_FILE_LOC)

        return

    def find_device(self, vendorid=0xFFFF, deviceid=0xFFFF, instance=0x0) -> PCIeDevice:
        dev_ven_str = helper.int_to_hexstr(deviceid, 4) + helper.int_to_hexstr(vendorid, 4)
        inst_str = helper.int_to_hexstr(instance)

        o = self.callCommand(f'FPCI 0x{dev_ven_str} 0x{inst_str}')

        m = re.search(f'Find PCI Device: 0x{dev_ven_str} Index 0x(\w*) = 0x(\w*)', o)
        if(m is None):
            return None

        bdf = binascii.unhexlify(m.group(2))
        bus = int.from_bytes(bdf, 'big') // 0x100
        device = (int.from_bytes(bdf, 'big')%0x100) // 0x8
        function = (int.from_bytes(bdf, 'big')%0x100) % 0x8

        return self.get_pci_tree().find_device(bus, device, function)

    def find_device_with_bdf(self, bus:int, device:int, function:int) -> PCIeDevice:
        return self.get_pci_tree().find_device(bus, device, function) 

    def read_bytes(self, bus:int, device:int, function:int, offset:int, byte_grouping:int) -> bytes:
        
        if byte_grouping not in [1, 2, 4]:
            raise Exception("bit_grouping must be 1, 2 or 4")
        
        command = ''
        if(byte_grouping == 1):
            command = f'RPCIE'
        elif(byte_grouping == 2):
            command = f'RPCIE16'   
        elif(byte_grouping == 4):
            command = f'RPCIE32'
        
        o = self.callCommand(f'{command} {bus} {device} {function} {offset}')
        m = re.search(r'Read PCIE Bus/Dev/Fun/Offset (\w*)/(\w*)/(\w*)/(\w*) = 0x(\w*)', o)
        if m is None:
            raise Exception("No proper output from command")
        
        return binascii.unhexlify(m.group(5))
    
    def write_bytes(self, bus:int, device:int, function:int, offset:int, data:bytes) -> None:
        byte_grouping = len(data)
        if byte_grouping not in [1, 2, 4]:
            raise Exception("data must be len 1, 2 or 4")
        
        command = ''
        if(byte_grouping == 1):
            command = f'WPCIE'
        elif(byte_grouping == 2):
            command = f'WPCIE16'   
        elif(byte_grouping == 4):
            command = f'WPCIE32'
            
        self.callCommand(f'{command} {bus} {device} {function} {offset} 0x{helper.bytes_to_hexstr(data)}')
        