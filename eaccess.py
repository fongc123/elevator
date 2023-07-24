"""
FILE: eaccess.py

Compile with PyInstaller: pyinstaller --onefile eaccess.py
"""
import socket
import json
import argparse
import datetime
import os

RADD_FUNC_CODE = "17500000"
QUERY_FUNC_CODE = "17200000"
START_DATE = "20100101"
END_DATE = "20291231"
USER_PASS = "000000"
FIRST_CARD = "00"
MULTI_CARD = "00"
RANDOM_BS = "0000000000000000000000000000000000000000000000000000000000000000"
SOCKET_TIMEOUT = 3

def dec2hex(num : int):
    result = hex(num).replace("0x", "")
    if len(result) % 2 != 0:
        result = "0" + result
    return result

def make_list(hex_string : str):
    return [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]

def get_floor_hex(floors : list):
    result = ""

    # floors 1 to 24
    _1to24 = 0
    for f in filter(lambda x: x < 25 and x > 0, floors):
        _1to24 += 10**(f-1)
    _1to24_hex = dec2hex(int(str(_1to24), 2))
    _1to24_hex = ''.join(make_list('0'*(6-len(_1to24_hex)) + _1to24_hex)[::-1])
    result += _1to24_hex + USER_PASS + FIRST_CARD + MULTI_CARD
    
    # floors 25 to 40
    _25to40 = 0
    for f in filter(lambda x: x > 24 and x < 41, floors):
        _25to40 += 10**(f-25)
    _25to40_hex = dec2hex(int(str(_25to40), 2))
    _25to40_hex = ''.join(make_list('0'*(4-len(_25to40_hex)) + _25to40_hex)[::-1])
    result += _25to40_hex

    return result

def space_string(string : str):
    return ' '.join(string[i:i+2] for i in range(0, len(string), 2))

def pad_zero(string : str, length : int):
    return '0'*(length-len(string)) + string

def sendPacket(ip_address : str, port : int, packet_str : str):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # udp
    s.settimeout(SOCKET_TIMEOUT)

    packet = bytes.fromhex(packet_str)

    try:
        s.connect((ip_address, port))
        s.send(packet)
    except socket.error as e:
        print("Error sending packet: " + str(e))

    try:
        response = s.recv(1024)
    except socket.timeout:
        print(f"Error: Response timed out ({SOCKET_TIMEOUT} sec).")
        response = None
    s.close()

    return response

def currentdate():
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d %H:%M:%S")

def save_file(data, file_path):
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)

    exists = os.path.isfile(file_path)
    mode = "a" if exists else "w"
    if mode == "a":
        data = "\n" + data

    with open(file_path, mode) as f:
        f.write(data)

def generate_hex_string(number : int):
    result = dec2hex(number)
    

def radd(ip_address : str, port : int, card_number : int, allow : int, floors : list, board_serial : int, start_date : int, end_date : int):
    hex_string = RADD_FUNC_CODE + ''.join(make_list(pad_zero(dec2hex(board_serial), 8))[::-1]) + ''.join(make_list(pad_zero(dec2hex(card_number), 8))[::-1])
    hex_string += str(start_date) + str(end_date) + f"0{allow}" + get_floor_hex(floors) + "00" + RANDOM_BS
    hex_string = space_string(hex_string.upper())

    response = sendPacket(ip_address, port, hex_string)

    return response

def radd1(ip_address : str, port : int, card_number : int, gates_allow : list, board_serial : int, start_date : int, end_date : int):
    hex_string = RADD_FUNC_CODE + ''.join(make_list(pad_zero(dec2hex(board_serial), 8))[::-1]) + ''.join(make_list(pad_zero(dec2hex(card_number), 8))[::-1])
    hex_string += str(start_date) + str(end_date) + ''.join([f"0{i}" for i in gates_allow])
    hex_string += USER_PASS + "00"*37
    hex_string = space_string(hex_string.upper())

    response = sendPacket(ip_address, port, hex_string)

    return response

def rdel(ip_address : str, port : int, card_number : int, board_serial : int, start_date : int, end_date : int):
    hex_string = QUERY_FUNC_CODE + ''.join(make_list(pad_zero(dec2hex(board_serial), 8))[::-1]) + ''.join(make_list(pad_zero(dec2hex(card_number), 8))[::-1])
    hex_string += str(start_date) + str(end_date) + "00" + "000000" + USER_PASS + FIRST_CARD + MULTI_CARD + "0000" + "00" + RANDOM_BS
    hex_string = space_string(hex_string.upper())

    response = sendPacket(ip_address, port, hex_string)

    return response

def getdata(ip_address : str, port : int, board_serial : int):
    hex_string = QUERY_FUNC_CODE + ''.join(make_list(dec2hex(board_serial))[::-1]) + '0'*112
    hex_string = space_string(hex_string.upper())

    response = sendPacket(ip_address, port, hex_string)

    return response

def get_floors(floor_str : str):
    if ',' in floor_str:
        return list(set(map(int, floor_str.split(','))))
    else:
        return [int(floor_str)]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-radd", nargs=9, help="Add user rights")
    parser.add_argument("-radd1", nargs=7, help="Add user rights for door")
    parser.add_argument("-rdel", nargs=7, help="Delete user rights")
    parser.add_argument("-getdata", nargs=4, help="Get recording data")
    args = parser.parse_args()

    params = None
    response = None
    path = None
    try:
        if args.radd is not None:
            # eaccess.exe -radd ip_address port card_number allow floors(csv) board_serial start_date end_date path
            params = args.radd
            if int(params[3]) > 1 or int(params[3]) < 0:
                raise Exception("Invalid allow value. Must be 0 or 1.")
            response = radd(str(params[0]), int(params[1]), int(params[2]), int(params[3]), get_floors(str(params[4])), int(params[5]), int(params[6]), int(params[7]))
            path = str(params[8])
        elif args.radd1 is not None:
            # eaccess.exe -radd1 ip_address port card_number gates_allow(csv) board_serial start_date end_date
            params = args.radd1
            if len(params[3].split(',')) != 4:
                raise Exception("Invalid gate allow values. Expected 4 values.")
            for value in params[3].split(','):
                if int(value) > 1 or int(value) < 0:
                    raise Exception("Invalid gate allow value. Must be 0 or 1.")
            response = radd1(str(params[0]), int(params[1]), int(params[2]), str(params[3]).split(','), int(params[4]), int(params[5]), int(params[6]))
        elif args.rdel is not None:
            # eaccess.exe -rdel ip_address port card_number board_serial start_date end_date path
            params = args.rdel
            response = rdel(str(params[0]), int(params[1]), int(params[2]), int(params[3]), int(params[4]), int(params[5]))
            path = str(params[6])
        elif args.getdata is not None:
            # eaccess.exe -getdata ip_address port board_serial path
            params = args.getdata
            response = getdata(str(params[0]), int(params[1]), int(params[2]))
            path = str(params[3])
        else:
            raise Exception("No arguments given.")
    except Exception as e:
        print("Error: " + str(e))
    finally:
        if response is not None and params is not None and path is not None:
            log = f"[{currentdate()}] {space_string(response.hex())}"
            save_file(log, f"{str(path)}")