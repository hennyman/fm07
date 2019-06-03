import numpy as np
import psutil
import sys

from ctypes import *
from ctypes.wintypes import *

from util.player import player

NAME_OF_PROCESS = "fm.exe"
PROCESS_ID = None

PLAYERS_START_ADDR = None

PLAYER_ADDR_STRLEN = 4

PROCESS_VM_READ = 0x0010

PLAYER_CLASS_ID = 0x0133f1a80133ec44

CURRENT_DATE = None # (year, days)

PLAYERS = []

KNOWN_PLAYERS_FILE_NAME = "known.slf"
INTERESTED_PLAYERS_FILE_NAME = "interested.slf"

k32 = WinDLL('kernel32')
k32.OpenProcess.argtypes = DWORD,BOOL,DWORD
k32.OpenProcess.restype = HANDLE
k32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
k32.ReadProcessMemory.restype = BOOL

def set_pid():
    global PROCESS_ID
    for proc in psutil.process_iter():
        if proc.name() == NAME_OF_PROCESS:
            PROCESS_ID = proc.pid
            break
        
def set_current_date():
    
    global CURRENT_DATE
    
    process = k32.OpenProcess(PROCESS_VM_READ, False, PROCESS_ID)
    buf = create_string_buffer(4)
    s = c_size_t()
    
    current_date_addr = 0x0163869c
    
    if k32.ReadProcessMemory(process, current_date_addr, buf, 4, byref(s)):
        reverse_array(buf)
        year = int(buf.raw.hex()[0:4],16)
        days = int(buf.raw.hex()[4:8],16)
        CURRENT_DATE = (year, days)
    else:
        print("set_current_date: Access Denied! \n")
        
def set_players_start_address():
    
    global PLAYERS_START_ADDRESS
    
    process = k32.OpenProcess(PROCESS_VM_READ, False, PROCESS_ID)
    buf = create_string_buffer(4)
    s = c_size_t()
    
    players_start_addr_addr = 0x0183ff10
    
    if k32.ReadProcessMemory(process, players_start_addr_addr, buf, 4, byref(s)):
        reverse_array(buf)
        PLAYERS_START_ADDRESS = int(buf.raw.hex(),16)
    else:
        print("set_players_start_address: Access Denied! \n")

def reverse_array(array):
    length = len(array)
    left = 0
    right = length-1
    while left < right:
        temp = array[left]
        array[left] = array[right]
        array[right] = temp
        left = left + 1
        right = right - 1

        
def reverse_hex_string(st):
    length = len(st)
    st = list(st)
    left = 0
    right = length
    while left < right:
        temp = st[left:left+2]
        st[left:left+2] = st[right-2:right]
        st[right-2:right] = temp
        left = left + 2
        right = right - 2
    return "".join(st)
    
def decode_player_class_id(addr):
    
    process = k32.OpenProcess(PROCESS_VM_READ, False, PROCESS_ID)
    buf = create_string_buffer(8)
    s = c_size_t()
    
    if k32.ReadProcessMemory(process, addr, buf, 8, byref(s)):
        reverse_array(buf)
        value = int(buf.raw.hex(),16)
        return value
    else:
        print("decode_player_class_id: Access Denied! \n")
        return -1

def load_players():
    
    set_current_date()
    global PLAYERS 
    PLAYERS = []
    
    global PLAYERS_START_ADDRESS
    global PLAYER_ADDR_STRLEN
    global PLAYER_CLASS_ID
    global PROCESS_ID
    global CURRENT_DATE
    global KNOWN_PLAYERS_FILE_NAME
    global INTERESTED_PLAYERS_FILE_NAME

    process = k32.OpenProcess(PROCESS_VM_READ, False, PROCESS_ID)
    buf = create_string_buffer(PLAYER_ADDR_STRLEN)
    s = c_size_t()

    addr = PLAYERS_START_ADDRESS

    number_of_players = 0

    while True:
    
        if k32.ReadProcessMemory(process, addr, buf, PLAYER_ADDR_STRLEN, byref(s)):
            reverse_array(buf)
            player_addr = int(buf.raw.hex(),16)
            if player_addr == 0:
                break
            class_id = decode_player_class_id(player_addr)
            if class_id == PLAYER_CLASS_ID:
                number_of_players += 1
                p = player(PROCESS_ID)
                p.populate_player_from_addr(player_addr)
                PLAYERS.append(p)
            elif class_id == -1:
                break
            addr = addr + PLAYER_ADDR_STRLEN
        else:
            print("load_players: Access Denied! \n")
            break
            
    for p in PLAYERS:
        p.set_age(CURRENT_DATE)
        
    known_players_uid = []
    interested_players_uid = []
    hexdata_known = None
    hexdata_interested = None

    # Not full-proof as file may be deleted between check and open
    try:
        with open(KNOWN_PLAYERS_FILE_NAME, 'rb') as f:
            hexdata_known = f.read().hex()
    except Exception as e:
        print("File " + KNOWN_PLAYERS_FILE_NAME + " does not exist \n")

    if hexdata_known is not None:
    
        l = len(hexdata_known)
        end = l - 2
        start = end - 8
    
        while True:
        
            hex_string = hexdata_known[start:end]
            if hex_string[4:8] == '0000':
                break
            hex_string_reversed = reverse_hex_string(hex_string)
            known_players_uid.append(int(hex_string_reversed, 16))
        
            start -= 8
            end -= 8
        
            if start < 0:
                break
            
        for p in PLAYERS:
            if p.uid in known_players_uid:
                p.is_known = True
            else:
                p.is_known = False

    # Not full-proof as file may be deleted between check and open
    try:
        with open(INTERESTED_PLAYERS_FILE_NAME, 'rb') as f:
            hexdata_interested = f.read().hex()
    except Exception as e:
        print("File " + INTERESTED_PLAYERS_FILE_NAME + " does not exist \n")

    if hexdata_interested is not None:
    
        l = len(hexdata_interested)
        end = l - 2
        start = end - 8
    
        while True:
        
            hex_string = hexdata_interested[start:end]
            if hex_string[4:8] == '0000':
                break
            hex_string_reversed = reverse_hex_string(hex_string)
            interested_players_uid.append(int(hex_string_reversed, 16))
        
            start -= 8
            end -= 8
        
            if start < 0:
                break
            
        for p in PLAYERS:
            if p.uid in interested_players_uid:
                p.is_interested = True
            else:
                p.is_interested = False

    print("Number of player loaded: " + str(number_of_players) +"\n")

set_pid()
set_players_start_address()
#load_players()

print("###################################")
print("Welcome to fm07 - Type exit to quit")
print("###################################")

while True:
    
    function = input("What function do you want to run? \n \n\
The options are: \n\
1 - Player search (default) \n\
2 - One player \n\
3 - Club player list \n\
4 - Reload players \n\
>")
    
    if function == "exit" or function == "Exit":
        break
    elif function == "2":
        identifier = input("Enter player UID\n>")
        if function == "exit" or function == "Exit":
            break
        else:
            try:
                uid = int(identifier)
                filtered_players = list(filter(lambda x: x.uid == uid, PLAYERS))
                if len(filtered_players) == 1:
                    print(filtered_players[0].to_string() + "\n")
                else:
                    print("UID not found\n")
            except Exception as e:
                print("Not a valid integer\n")
    elif function == "3":
        team_name = input("What is the name of your club \n>")
    elif function == "4":
        load_players()
    else:
        print("Player search")