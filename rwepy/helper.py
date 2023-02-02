import binascii
from distutils.util import byte_compile
import math

def int_to_hexstr(val:int, len=2) -> str:
    '''
    Convert integer to HEX string
    Note: this string shows the value of the interger in hex, run binascii.unhexlify to get the actual bytes
    '''
    counter = 0
    remain = val
    while not remain < 1:
        remain = remain//16
        counter+=1

    counter = max(counter, len)

    return binascii.hexlify(val.to_bytes(math.ceil(counter/2), 'big')).decode().upper()

def hexstr_to_int(s:str) -> int:

    return int.from_bytes(binascii.unhexlify(s), 'big')

def bytes_to_hexstr(data:bytes) -> str:
    
    return binascii.hexlify(data).decode().upper()

def print_hex_dump(data:bytes, byte_grouping=16) -> None:

    if byte_grouping not in [1, 2, 4]:
        raise Exception("bit_grouping must be 1, 2 or 4")
    
    hexstr = binascii.hexlify(data).decode().upper()

    #make a list of bytes    
    data_list = [["00","01","02","03","04","05","06","07","08","09","0A","0B","0C","0D","0E","0F"]]

    byte_count = len(data)
    line_counter = 0
    while byte_count > 0:
        
        data_str = []
        for i in range(16):
            if(line_counter+(i*2)+2 <= len(hexstr)):
                data_str.append(hexstr[line_counter+(i*2):line_counter+(i*2)+2])
            else:
                data_str.append("  ")

        data_list.append(data_str)

        line_counter += 16
        byte_count -= 16

    # Print the hex dump list
    line_counter = 0

    for i in range(len(data_list)):
        line = ""
        for j in range(len(data_list[i])//byte_grouping):
            lst = data_list[i][j*byte_grouping:(j*byte_grouping)+byte_grouping]
            lst = lst[::-1]
            line += "".join(lst) + " "

        if(i > 0):
            print("{:<6}{:<2}".format(int_to_hexstr(line_counter, 4), line))
            line_counter += 16
        else:
            print("{:<6}{:<2}\n".format("", line))

    return

def read_bytes(data:bytes, offset:int, byte_grouping:int) -> bytes:

    if byte_grouping not in [1, 2, 4]:
        raise Exception("bit_grouping must be 1, 2 or 4")

    start_address = offset - (offset%byte_grouping)
    
    # slice the bytes object, then return the big endian version of the slice
    return data[start_address:start_address+byte_grouping][::-1]


def set_bit(data:bytes, index:int, x:int) -> bytes:
    """Set the index:th bit of v to 1 if x is truthy, else to 0, and return the new value."""

    if (index >= len(data)*8):
        raise Exception("Index greater than length of data")

    i = int.from_bytes(data, 'big')

    mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
    i &= ~mask          # Clear the bit indicated by the mask (if x is False)
    if x:
        i |= mask         # If x was True, set the bit indicated by the mask.
    
    return i.to_bytes(len(data), byteorder='big')

def int_to_bitstr(val:int) -> str:
    '''
    Outputs a string represetation of the bits from an integer or <4 len bytes 

    if the int is negative returns the 2s compliment of the int
    '''

    if type(val) == bytes:
        if (len(val) <= 4):
            val = int.from_bytes(val, 'big')
        else:
            raise Exception("bytes object greater than 4, too big")
        
    return format( (val & (0xffffffff)) , '032b')

def read_bits(val:int|bytes, start_i:int, end_i:int) -> int|bytes:
    '''
    Takes int/ <4 len bytes and gets the value of bit between start index (start_i) and end index (end_i) inclusive.
    '''
    r = val
    if type(val) == bytes:
        if (len(val) <= 4):
            r = int.from_bytes(val, 'big')
        else:
            raise Exception("bytes object greater than 4, too big")

    r = r >> start_i
    mask = ~0
    mask = (~(mask << (end_i - start_i + 1))) & (0xffffffff)
    r &= mask

    if type(val) == bytes:
        return r.to_bytes(len(val), byteorder='big')
    elif type(val) == int:
        return r


