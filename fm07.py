import psutil
import json

from ctypes import *
from ctypes.wintypes import *

from util.player import player
from util.eleven import Eleven

NAME_OF_PROCESS = "fm.exe"
PROCESS_ID = None

PLAYERS_START_ADDR = None

PLAYER_ADDR_STRLEN = 4

PROCESS_VM_READ = 0x0010

PLAYER_CLASS_ID = 0x0133f1a80133ec44

CURRENT_DATE = None # (year, days)

PLAYERS = []
CLUBS = {}

KNOWN_PLAYERS_FILE_NAME = "./shortlists/known.slf"
INTERESTED_PLAYERS_FILE_NAME = "./shortlists/interested.slf"

PLAYER_SEARCH_JSONS_PATH = "./player_search_jsons/"

POSITIONS = ["GK", "DL", "DR", "DC", "DC", "DM", "ML", "MR", "AM", "ST", "ST"]

k32 = WinDLL('kernel32')
k32.OpenProcess.argtypes = DWORD,BOOL,DWORD
k32.OpenProcess.restype = HANDLE
k32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
k32.ReadProcessMemory.restype = BOOL


def set_pid():
    global NAME_OF_PROCESS
    global PROCESS_ID
    for proc in psutil.process_iter():
        if proc.name() == NAME_OF_PROCESS:
            PROCESS_ID = proc.pid
            break
    if PROCESS_ID is None:
        print(NAME_OF_PROCESS + " not found!")


def set_current_date():
    
    global CURRENT_DATE
    global PROCESS_VM_READ
    global PROCESS_ID
    
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
        
    player_uid_list = []
    for p in PLAYERS:
        player_uid_list.append(p.uid)

    hexdata_known = None
    # Not full-proof as file may be deleted between check and open
    try:
        with open(KNOWN_PLAYERS_FILE_NAME, 'rb') as f:
            hexdata_known = f.read().hex()
    except Exception as e:
        print("File " + KNOWN_PLAYERS_FILE_NAME + " does not exist \n")

    if hexdata_known is not None:
        
        offset = 0
        l = len(hexdata_known)
        
        while True:
            
            known_players_uid = []
            
            if offset >= 8:
                break
            
            end = l - offset
            start = end - 8
    
            while True:
                hex_string = hexdata_known[start:end]
                hex_string_reversed = reverse_hex_string(hex_string)
                known_players_uid.append(int(hex_string_reversed, 16))
        
                start -= 8
                end -= 8
        
                if start < 0:
                    break
                
            intersect = list(set(player_uid_list) & set(known_players_uid))
            len_intersect = len(intersect)
            
            if len_intersect > (len(known_players_uid) / 2):
                break
            else:
                offset += 2
            
        for p in PLAYERS:
            if p.uid in known_players_uid:
                p.is_known = True
            else:
                p.is_known = False

    hexdata_interested = None
    # Not full-proof as file may be deleted between check and open
    try:
        with open(INTERESTED_PLAYERS_FILE_NAME, 'rb') as f:
            hexdata_interested = f.read().hex()
    except Exception as e:
        print("File " + INTERESTED_PLAYERS_FILE_NAME + " does not exist \n")

    if hexdata_interested is not None:
    
        offset = 0
        l = len(hexdata_interested)
        
        while True:
            
            interested_players_uid = []
            
            if offset >= 8:
                break
            
            end = l - offset
            start = end - 8
            
            while True:
                hex_string = hexdata_interested[start:end]
                hex_string_reversed = reverse_hex_string(hex_string)
                interested_players_uid.append(int(hex_string_reversed, 16))
        
                start -= 8
                end -= 8
        
                if start < 0:
                    break
            
            intersect = list(set(player_uid_list) & set(interested_players_uid))
            len_intersect = len(intersect)
            
            if len_intersect > (len(interested_players_uid) / 2):
                break
            else:
                offset += 2
    
        for p in PLAYERS:
            if p.uid in interested_players_uid:
                p.is_interested = True
            else:
                p.is_interested = False

    print("Number of player loaded: " + str(number_of_players) +"\n")


def populate_clubs():
        
    global CLUBS
    global PLAYERS
    CLUBS = {}
        
    for p in PLAYERS:
        if not p.club_uid in CLUBS:
            CLUBS[p.club_uid] = p.club_name


def player_search(json_data):
    
    filters = json_data["filter"]
    filter_keys = filters.keys()
    
    filtered_players = PLAYERS
    
    filtered_players = list(filter(lambda x: x.is_known, filtered_players))
    
    if "age" in filter_keys:
        age_dict = filters["age"]
        if "max" in age_dict.keys():
            filtered_players = list(filter(lambda x: x.age[0] <= age_dict["max"], filtered_players))
        if "min" in age_dict.keys():
            filtered_players = list(filter(lambda x: x.age[0] >= age_dict["min"], filtered_players))

    if "value" in filter_keys:
        value_dict = filters["value"]
        if "max" in value_dict.keys():
            filtered_players = list(filter(lambda x: x.value <= value_dict["max"], filtered_players))
        if "min" in value_dict.keys():
            filtered_players = list(filter(lambda x: x.value >= value_dict["min"], filtered_players))
            
    if "positions" in filter_keys:
        positions = filters["positions"]
        if not "all" in positions:
            if "all_outfield" in positions:
                filtered_players = list(filter(lambda x: not "goalkeeper" in x.positions, filtered_players))
            else:
                filtered_players = list(filter(lambda x: len(list(set(positions) & set(x.positions))) > 0, filtered_players))
    
    if "interested" in filter_keys:
        interested = filters["interested"]
        filtered_players = list(filter(lambda x: x.is_interested == interested, filtered_players))
        
    if "free" in filter_keys:
        free = filters["free"]
        if free:
            filtered_players = list(filter(lambda x: x.club_uid == -1, filtered_players))
        else:
            filtered_players = list(filter(lambda x: not x.club_uid == -1, filtered_players))
    
    if json_data["sort_by"] == "total":
        filtered_players.sort(key=lambda x: x.total, reverse = True)
    elif json_data["sort_by"] == "goalkeeper_total":
        filtered_players.sort(key=lambda x: x.goalkeeper_total, reverse = True)
    elif json_data["sort_by"] == "full_back_total":
        filtered_players.sort(key=lambda x: x.full_back_total, reverse = True)
    elif json_data["sort_by"] == "defender_central_total":
        filtered_players.sort(key=lambda x: x.defender_central_total, reverse = True)
    elif json_data["sort_by"] == "defensive_midfielder_total":
        filtered_players.sort(key=lambda x: x.defensive_midfielder_total, reverse = True)
    elif json_data["sort_by"] == "winger_total":
        filtered_players.sort(key=lambda x: x.winger_total, reverse = True)
    elif json_data["sort_by"] == "attacking_midfielder_total":
        filtered_players.sort(key=lambda x: x.attacking_midfielder_total, reverse = True)
    elif json_data["sort_by"] == "striker_total":
        filtered_players.sort(key=lambda x: x.striker_total, reverse = True)
    elif json_data["sort_by"] == "goalkeeper_compare":
        filtered_players.sort(key=lambda x: x.goalkeeper_compare, reverse = True)
    elif json_data["sort_by"] == "full_back_compare":
        filtered_players.sort(key=lambda x: x.full_back_compare, reverse = True)
    elif json_data["sort_by"] == "defender_central_compare":
        filtered_players.sort(key=lambda x: x.defender_central_compare, reverse = True)
    elif json_data["sort_by"] == "defensive_midfielder_compare":
        filtered_players.sort(key=lambda x: x.defensive_midfielder_compare, reverse = True)
    elif json_data["sort_by"] == "winger_compare":
        filtered_players.sort(key=lambda x: x.winger_compare, reverse = True)
    elif json_data["sort_by"] == "attacking_midfielder_compare":
        filtered_players.sort(key=lambda x: x.attacking_midfielder_compare, reverse = True)
    elif json_data["sort_by"] == "striker_compare":
        filtered_players.sort(key=lambda x: x.striker_compare, reverse = True)
    
    max_return = json_data["max_return"]
    if not max_return == -1:
        filtered_players = filtered_players[0 : max_return]
    
    return filtered_players


# noinspection PyBroadException
def set_config(c_name=None):
    if c_name is None:
        return
    j_data = None
    f_name = "config.json"
    try:
        with open(f_name, 'r') as j_file:
            j_data = json.load(j_file)
    except Exception:
        print("File config.json could not be loaded.")
    if j_data is None:
        return
    j_data["club_name"] = c_name
    try:
        with open(f_name, 'w') as j_file:
            json.dump(j_data, j_file)
    except Exception:
        print("File config.json could not be saved.")


# noinspection PyBroadException
def get_config_club():
    f_name = "config.json"
    try:
        with open(f_name) as j_file:
            j_data = json.load(j_file)
            c_name = j_data["club_name"]
            if c_name is not None:
                return c_name
            else:
                return "-"
    except Exception:
        print("File config.json could not be loaded")
        return "-"


def print_players(players, elevens=None):
    for p in players:
        print(p.to_string(elevens) + "\n")
    if len(players) == 0:
        print("No players found!\n")


def save_eleven_to_file(elevens):
    global POSITIONS
    print("")
    s_to_file = input("Do you want to save results to csv?\n> ")
    if s_to_file == "y" or s_to_file == "Y" or s_to_file == "yes" or s_to_file == "Yes":
        s_file_name = input("Enter file name\n> ")
        el1 = elevens[0]
        el2 = elevens[1]
        o = ""
        c = 0
        for p in el1:
            o = o + POSITIONS[c] + ";" + p.to_eleven_csv(c) + "\n"
            c += 1
        o = o + "\n\n\n"
        c = 0
        for p in el2:
            o = o + POSITIONS[c] + ";" + p.to_eleven_csv(c) + "\n"
            c += 1
        try:
            f = open(s_file_name, 'w', encoding='utf8')
            f.write(o)
        except Exception:
            print("File could not be saved.")
        finally:
            f.close()


def save_squad_to_file(players, elevens):
    print("")
    s_to_file = input("Do you want to save the squad to csv?\n> ")
    if s_to_file == "y" or s_to_file == "Y" or s_to_file == "yes" or s_to_file == "Yes":
        s_file_name = input("Enter file name\n> ")
        o = "Name;UID;Eleven;Years;Days;Value;Positions;Club;Total;Goalkeeper;Full Back;Defender Central;" \
            "Defensive Midfielder;Winger;Attacking Midfielder;Striker\n"
        for p in players:
            o = o + p.to_csv(elevens) + "\n"
        try:
            f = open(s_file_name, 'w', encoding='utf8')
            f.write(o)
        except Exception:
            print("File could not be saved.")
        finally:
            f.close()


set_pid()
set_players_start_address()
load_players()
populate_clubs()

print("###################################")
print("Welcome to fm07 - Type exit to quit")
print("###################################")

while True:
    
    function = input("\n\nWhat function do you want to run? \n \n\
The options are: \n\
1 - One player \n\
2 - Club squad \n\
3 - Club squad - one position \n\
4 - Club squad - eleven \n\
5 - Reload players \n\
6 - Player search (default) \n\
> ")
    
    if function == "exit" or function == "Exit":
        break
    elif function == "1":
        identifier = input("Enter player name or UID\n> ")
        if identifier == "exit" or identifier == "Exit":
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
                name = identifier
                filtered_players = list(filter(lambda x: x.first_name + " " + x.second_name == name, PLAYERS))
                for p in filtered_players:
                    print(p.to_string() + "\n")
                if len(filtered_players) == 0:
                    print("No player by that name found\n")
    elif function == "2":
        club_name = get_config_club()
        identifier = input("Enter club name or UID " + "(default: " + club_name + ")" + "\n> ")
        if identifier == "exit" or identifier == "Exit":
            break
        elif identifier == "":
            filtered_players = list(filter(lambda x: x.club_name == club_name or x.club_name_long == club_name, PLAYERS))
            filtered_players.sort(key=lambda x: x.total, reverse=True)
            el = Eleven()
            el.set_players(filtered_players)
            els = el.get_eleven(suppress_print=True)
            print_players(filtered_players, elevens=els)
            save_squad_to_file(filtered_players, els)
        else:
            try:
                club_uid = int(identifier)
                filtered_players = list(filter(lambda x: x.club_uid == club_uid, PLAYERS))
                if len(filtered_players) > 0:
                    set_config(c_name = filtered_players[0].club_name)
                filtered_players.sort(key=lambda x: x.total, reverse=True)
                el = Eleven()
                el.set_players(filtered_players)
                els = el.get_eleven(suppress_print=True)
                print_players(filtered_players, elevens=els)
                save_squad_to_file(filtered_players, els)
            except Exception as e:
                club_name = identifier
                filtered_players = list(filter(lambda x: x.club_name == club_name or x.club_name_long == club_name, PLAYERS))
                if len(filtered_players) > 0:
                    set_config(c_name = filtered_players[0].club_name)
                filtered_players.sort(key=lambda x: x.total, reverse=True)
                el = Eleven()
                el.set_players(filtered_players)
                els = el.get_eleven(suppress_print=True)
                print_players(filtered_players, elevens=els)
                save_squad_to_file(filtered_players, els)
    elif function == "3":
        club_name = get_config_club()
        identifier = input("Enter club name or UID " + "(default: " + club_name + ")" + "\n> ")
        if identifier == "exit" or identifier == "Exit":
            break
        elif identifier == "":
            position = input("Enter position \n> ")
            if position == "exit" or position == "Exit":
                break
            filtered_players = list(filter(lambda x: x.club_name == club_name or x.club_name_long == club_name, PLAYERS))
            filtered_players = list(filter(lambda x: position in x.positions, filtered_players))
            filtered_players.sort(key=lambda x: x.total, reverse=True)
            print_players(filtered_players)
        else:
            position = input("Enter position \n> ")
            if position == "exit" or position == "Exit":
                break
            try:
                club_uid = int(identifier)
                filtered_players = list(filter(lambda x: x.club_uid == club_uid, PLAYERS))
                filtered_players = list(filter(lambda x: position in x.positions, filtered_players))
                if len(filtered_players) > 0:
                    set_config(c_name = filtered_players[0].club_name)
                filtered_players.sort(key=lambda x: x.total, reverse=True)
                print_players(filtered_players)
            except Exception as e:
                club_name = identifier
                filtered_players = list(filter(lambda x: x.club_name == club_name or x.club_name_long == club_name, PLAYERS))
                filtered_players = list(filter(lambda x: position in x.positions, filtered_players))
                if len(filtered_players) > 0:
                    set_config(c_name = filtered_players[0].club_name)
                filtered_players.sort(key=lambda x: x.total, reverse=True)
                print_players(filtered_players)
    elif function == "4":
        club_name = get_config_club()
        identifier = input("Enter club name or UID " + "(default: " + club_name + ")" + "\n> ")
        if identifier == "exit" or identifier == "Exit":
            break
        elif identifier == "":
            filtered_players = list(filter(lambda x: x.club_name == club_name or x.club_name_long == club_name, PLAYERS))
            if len(filtered_players) == 0:
                print("No players found!\n")
            else:
                el = Eleven()
                el.set_players(filtered_players)
                els = el.get_eleven()
                save_eleven_to_file(els)
        else:
            try:
                club_uid = int(identifier)
                filtered_players = list(filter(lambda x: x.club_uid == club_uid, PLAYERS))
                if len(filtered_players) == 0:
                    print("No players found for club with that UID\n")
                else:
                    set_config(c_name=filtered_players[0].club_name)
                    el = Eleven()
                    el.set_players(filtered_players)
                    els = el.get_eleven()
                    save_eleven_to_file(els)
            except Exception as e:
                club_name = identifier
                filtered_players = list(filter(lambda x: x.club_name == club_name or x.club_name_long == club_name, PLAYERS))
                if len(filtered_players) == 0:
                    print("No players found for club with that name\n")
                else:
                    set_config(c_name=filtered_players[0].club_name)
                    el = Eleven()
                    el.set_players(filtered_players)
                    els = el.get_eleven()
                    save_eleven_to_file(els)
    elif function == "5":
        load_players()
    else:
        file_name = input("Enter file name of json defining search \n> ")
        if file_name == "exit" or file_name == "Exit":
            break
        if not file_name[-5:] == ".json":
            file_name = file_name + ".json"
        path_file_name = PLAYER_SEARCH_JSONS_PATH + file_name
        try: 
            with open(path_file_name) as json_file:  
                json_data = json.load(json_file)
            
            filtered_players = player_search(json_data)
            print_players(filtered_players)
            
            save_to_file = input("Do you want to save results to csv?\n> ")
            if save_to_file == "exit" or save_to_file == "Exit":
                break
            elif save_to_file == "y" or save_to_file == "Y":
                save_file_name = input("Enter file name\n> ")
                if save_file_name == "exit" or save_to_file == "Exit":
                    break
            
                output = ""
                for p in filtered_players:
                    output = output + p.to_csv() + "\n"
            
                file = open(save_file_name, 'w', encoding='utf8')
                file.write(output) 
                file.close()
                
        except Exception as e:
            print(e)