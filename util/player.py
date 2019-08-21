from ctypes import *
from ctypes.wintypes import *
import numpy as np


class player:
    
    PROCESS_VM_READ = 0x0010
    PROCESS_ID = None
    
    K32 = WinDLL('kernel32')
    K32.OpenProcess.argtypes = DWORD,BOOL,DWORD
    K32.OpenProcess.restype = HANDLE
    K32.ReadProcessMemory.argtypes = HANDLE,LPVOID,LPVOID,c_size_t,POINTER(c_size_t)
    K32.ReadProcessMemory.restype = BOOL
    PROCESS = None
    
    PLAYER_CLASS_ID = 0x0133f1a80133ec44

    PLAYER_GENERAL_BYTES = 484
    PLAYER_ATTRIBUTE_BYTES = 108
    CLUB_BYTES = 336
    CONTRACT_BYTES = 112
    
    MAIN_ADDR = None
    ATTR_ADDR = 0xb4,0xb8
    CLUB_ADDR = 0x148,0x14c
    CONTRACT_LINK_ADDR = 0x16c,0x170
    
    FIRST_NAME_ADDR = 0x100,0x104
    SECOND_NAME_ADDR = 0x104,0x108
    UID_ADDR = 0xe8,0xec
    CLUB_NAME_ADDR = 0x38,0x3c
    CLUB_UID_ADDR = 0x14,0x18
    DATE_OF_BIRTH = 0x11c,0x120 # 11c - 11d = days in year, 11e - 11f year
    NATIONALIY_ADDR = 0x128,0x12c
    
    INTERNATIONAL_APPS_ADDR = 0x130,0x131
    INTERNATIONAL_GOALS_ADDR = 0x132,0x133
    UNDER_21_APPS_ADDR = 0x131,0x132
    UNDER_21_GOALS_ADDR = 0x133,0x134
    
    VALUE_ADDR = 0x24,0x28
    CONDITION_ADDR = None # Unknown
    FORM_ADDR = None # Unknown
    MORALE_ADDR = 0x48,0x49
    AVERAGE_RATING_ADDR = None # Unknown
    
    GOALKEEPER_ADDR = 0x1c,0x1d
    SWEEPER_ADDR = 0x1d,0x1e
    FULL_BACK_LEFT_ADDR = 0x28,0x29
    FULL_BACK_RIGHT_ADDR = 0x2a,0x2b
    DEFENDER_CENTRAL_ADDR = 0x29,0x2a
    WING_BACK_LEFT_ADDR = 0x33,0x34
    WING_BACK_RIGHT_ADDR = 0x34,0x35
    DEFENSIVE_MIDFIELDER_ADDR = 0x2b,0x2c
    MIDFIELDER_LEFT_ADDR = 0x2c,0x2d
    MIDFIELDER_RIGHT_ADDR = 0x2e,0x2f
    MIDFIELDER_CENTRAL_ADDR = 0x2d,0x2e
    ATTACKING_MIDFIELDER_LEFT_ADDR = 0x2f,0x30
    ATTACKING_MIDFIELDER_RIGHT_ADDR = 0x31,0x32
    ATTACKING_MIDFIELDER_CENTRAL_ADDR = 0x30,0x31
    STRIKER_ADDR = 0x32,0x33
    
    AERIAL_ABILITY_ADDR = 0x41,0x42
    COMMAND_OF_AREA_ADDR = 0x42,0x43
    COMMUNICATION_ADDR = 0x43,0x44
    ECCENTRICITY_ADDR = 0x54,0x55
    HANDLING_ADDR = 0x40,0x41
    KICKING_ADDR = 0x44,0x45
    ONE_ON_ONES_ADDR = 0x48,0x49
    REFLEXES_ADDR = 0x4a,0x4b
    RUSHING_OUT_ADDR = 0x55,0x56
    TENDENCY_TO_PUNCH_ADDR = 0x56,0x57
    THROWING_ADDR = 0x45,0x46
    
    CORNERS_ADDR = 0x50,0x51
    CROSSING_ADDR = 0x35,0x36
    DRIBBLING_ADDR = 0x36,0x37
    FINISHING_ADDR = 0x37,0x38
    FIRST_TOUCH_ADDR = 0x4b,0x4c
    FREE_KICKS_ADDR = 0x58,0x59
    HEADING_ADDR = 0x38,0x39
    LONG_SHOTS_ADDR = 0x39,0x3a
    LONG_THROWS_ADDR = 0x53,0x54
    MARKING_ADDR = 0x3a,0x3b
    PASSING_ADDR = 0x3c,0x3d
    PENALTY_TAKING_ADDR = 0x3d,0x3e
    TACKLING_ADDR = 0x3e,0x3f
    TECHNIQUE_ADDR = 0x4c,0x4d
    
    AGGRESSION_ADDR = 0x62,0x63
    ANTICIPATION_ADDR = 0x46,0x47
    BRAVERY_ADDR = 0x60,0x61
    COMPOSURE_ADDR = 0x69,0x6a
    CONCENTRATION_ADDR = 0x6a,0x6b
    CREATIVITY_ADDR = 0x3f,0x40
    DECISIONS_ADDR = 0x47,0x48
    DETERMINATION_ADDR = 0x68,0x69
    FLAIR_ADDR = 0x4f,0x50
    INFLUENCE_ADDR = 0x5d,0x5e
    OFF_THE_BALL_ADDR = 0x3b,0x3c
    POSITIONING_ADDR = 0x49,0x4a
    TEAMWORK_ADDR = 0x51,0x52
    WORK_RATE_ADDR = 0x52,0x53
    
    ACCELERATION_ADDR = 0x57,0x58
    AGILITY_ADDR = 0x63,0x64
    BALANCE_ADDR = 0x5f,0x60
    JUMPING_ADDR = 0x5c,0x5d
    NATURAL_FITNESS_ADDR = 0x67,0x68
    PACE_ADDR = 0x5b,0x5c
    STAMINA_ADDR = 0x5a,0x5b
    STRENGTH_ADDR = 0x59,0x5a
    
    LEFT_FOOT_ADDR = 0x4d,0x4e
    RIGHT_FOOT_ADDR = 0x4e,0x4f
    
    ATTR_CONVERTER = np.zeros(97)
    
    def __init__(self, process_id):
        
        self.PROCESS_ID = process_id
        self.PROCESS = self.K32.OpenProcess(self.PROCESS_VM_READ, False, self.PROCESS_ID)
        
        # General
        self.first_name = None
        self.second_name = None
        self.uid = None
        self.club_name = None
        self.club_name_long = None
        self.club_uid = None
        self.date_of_birth = None # (years, days)
        self.age = None # (years, days)
        self.is_interested = False
        self.is_known = False
        self.value = None
        
        # International
        self.international_apps = None
        self.international_goals = None
        self.under_21_apps = None
        self.under_21_goals = None
        
        # Contract
        # Transfer Statuses
        # 0 = Unattached?
        # 1 = Transfer listed, not listed for loan
        # 3 = Transfer listed, listed for loan
        # 65 = Transfer listed, not available for loan
        # 4 = Not transfer listed, not listed for loan
        # 6 = Not transfer listed, listed for loan
        # 68 = Not transfer listed, not available for loan
        # 8 = Transfer listed by request, not listed for loan
        # 10 = Transfer listed by request, listed for loan
        # 72 = Transfer listed by request, not available for loan
        # 16 = Not for sale, not listed for loan
        # 18 = Not for sale, listed for loan
        # 80 = Not for sale, not available for loan
        # Many more...
        self.transfer_status = None
        self.basic_wage = None
        self.contract_expires = None # (years, days)
        self.contract_status = None
        
        # Form
        self.condition = None
        self.form = None
        self.morale = None
        self.average_rating = None
        
        # Positions
        self.goalkeeper = None
        self.sweeper = None
        self.full_back_left = None
        self.full_back_right = None
        self.defender_central = None
        self.wing_back_left = None
        self.wing_back_right = None
        self.defensive_midfielder = None
        self.midfielder_left = None
        self.midfielder_right = None
        self.midfielder_central = None
        self.attacking_midfielder_left = None
        self.attacking_midfielder_right = None
        self.attacking_midfielder_central = None
        self.striker = None
        self.positions = []
        
        # Goalkeeping Attributes
        self.aerial_ability = None
        self.command_of_area = None
        self.communication = None
        self.eccentricity = None
        self.handling = None
        self.kicking = None
        self.one_on_ones = None
        self.reflexes = None
        self.rushing_out = None
        self.tendency_to_punch = None
        self.throwing = None
        
        # Technical Attributes
        self.corners = None
        self.crossing = None
        self.dribbling = None
        self.finishing = None
        self.first_touch = None
        self.free_kicks = None
        self.heading = None
        self.long_shots = None
        self.long_throws = None
        self.marking = None
        self.passing = None
        self.penalty_taking = None
        self.tackling = None
        self.technique = None
        
        # Mental Attributes
        self.aggression = None
        self.anticipation = None
        self.bravery = None
        self.composure = None
        self.concentration = None
        self.creativity = None
        self.decisions = None
        self.determination = None
        self.flair = None
        self.influence = None
        self.off_the_ball = None
        self.positioning = None
        self.teamwork = None
        self.work_rate = None
        
        # Physical Attributes
        self.acceleration = None
        self.agility = None
        self.balance = None
        self.jumping = None
        self.natural_fitness = None
        self.pace = None
        self.stamina = None
        self.strength = None
        
        # Other
        self.left_foot = None
        self.right_foot = None
        
        # Calculated
        self.total = None
        self.goalkeeper_total = None
        self.full_back_total = None
        self.defender_central_total = None
        self.defensive_midfielder_total = None
        self.winger_total = None
        self.attacking_midfielder_total = None
        self.striker_total = None
        self.totals = []
        self.position_totals = []

        self.goalkeeper_compare = None
        self.full_back_compare = None
        self.defender_central_compare = None
        self.defensive_midfielder_compare = None
        self.winger_compare = None
        self.attacking_midfielder_compare = None
        self.striker_compare = None
        self.compares = []
        
        self.generate_converter()
    
    def reverse_array(self, array):
        length = len(array)
        left = 0
        right = length-1
        while left < right:
            temp = array[left]
            array[left] = array[right]
            array[right] = temp
            left = left + 1
            right = right - 1
            
    def reverse_hex_string(self, st):
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
    
    def decode_player_class_id(self, addr):
            
        buf = create_string_buffer(8)
        s = c_size_t()
    
        if self.K32.ReadProcessMemory(self.PROCESS, addr, buf, 8, byref(s)):
            self.reverse_array(buf)
            value = int(buf.raw.hex(),16)
            return value
        else:
            print("player.decode_player_class_id: Access Denied!")
            return -1
        
    def attribute_100_20(self, int_value):
        if 129 > int_value > 97:
            return 20 # Seems like values can exceed 100, too high -> 1
        if int_value > 128:
            return 1
        return self.ATTR_CONVERTER[int_value - 1]
    
    def generate_converter(self):
        self.ATTR_CONVERTER[0] = 1
        self.ATTR_CONVERTER[1] = 1
        self.ATTR_CONVERTER[2] = 1
        self.ATTR_CONVERTER[3] = 1
        self.ATTR_CONVERTER[4] = 1
        self.ATTR_CONVERTER[5] = 1
        self.ATTR_CONVERTER[6] = 1
        self.ATTR_CONVERTER[7] = 2
        self.ATTR_CONVERTER[8] = 2
        self.ATTR_CONVERTER[9] = 2
        self.ATTR_CONVERTER[10] = 2
        self.ATTR_CONVERTER[11] = 2
        self.ATTR_CONVERTER[12] = 3
        self.ATTR_CONVERTER[13] = 3
        self.ATTR_CONVERTER[14] = 3
        self.ATTR_CONVERTER[15] = 3
        self.ATTR_CONVERTER[16] = 3
        self.ATTR_CONVERTER[17] = 4
        self.ATTR_CONVERTER[18] = 4
        self.ATTR_CONVERTER[19] = 4
        self.ATTR_CONVERTER[20] = 4
        self.ATTR_CONVERTER[21] = 4
        self.ATTR_CONVERTER[22] = 5
        self.ATTR_CONVERTER[23] = 5
        self.ATTR_CONVERTER[24] = 5
        self.ATTR_CONVERTER[25] = 5
        self.ATTR_CONVERTER[26] = 5
        self.ATTR_CONVERTER[27] = 6
        self.ATTR_CONVERTER[28] = 6
        self.ATTR_CONVERTER[29] = 6
        self.ATTR_CONVERTER[30] = 6
        self.ATTR_CONVERTER[31] = 6
        self.ATTR_CONVERTER[32] = 7
        self.ATTR_CONVERTER[33] = 7
        self.ATTR_CONVERTER[34] = 7
        self.ATTR_CONVERTER[35] = 7
        self.ATTR_CONVERTER[36] = 7
        self.ATTR_CONVERTER[37] = 8
        self.ATTR_CONVERTER[38] = 8
        self.ATTR_CONVERTER[39] = 8
        self.ATTR_CONVERTER[40] = 8
        self.ATTR_CONVERTER[41] = 8
        self.ATTR_CONVERTER[42] = 9
        self.ATTR_CONVERTER[43] = 9
        self.ATTR_CONVERTER[44] = 9
        self.ATTR_CONVERTER[45] = 9
        self.ATTR_CONVERTER[46] = 9
        self.ATTR_CONVERTER[47] = 10
        self.ATTR_CONVERTER[48] = 10
        self.ATTR_CONVERTER[49] = 10
        self.ATTR_CONVERTER[50] = 10
        self.ATTR_CONVERTER[51] = 10
        self.ATTR_CONVERTER[52] = 11
        self.ATTR_CONVERTER[53] = 11
        self.ATTR_CONVERTER[54] = 11
        self.ATTR_CONVERTER[55] = 11
        self.ATTR_CONVERTER[56] = 11
        self.ATTR_CONVERTER[57] = 12
        self.ATTR_CONVERTER[58] = 12
        self.ATTR_CONVERTER[59] = 12
        self.ATTR_CONVERTER[60] = 12
        self.ATTR_CONVERTER[61] = 12
        self.ATTR_CONVERTER[62] = 13
        self.ATTR_CONVERTER[63] = 13
        self.ATTR_CONVERTER[64] = 13
        self.ATTR_CONVERTER[65] = 13
        self.ATTR_CONVERTER[66] = 13
        self.ATTR_CONVERTER[67] = 14
        self.ATTR_CONVERTER[68] = 14
        self.ATTR_CONVERTER[69] = 14
        self.ATTR_CONVERTER[70] = 14
        self.ATTR_CONVERTER[71] = 14
        self.ATTR_CONVERTER[72] = 15
        self.ATTR_CONVERTER[73] = 15
        self.ATTR_CONVERTER[74] = 15
        self.ATTR_CONVERTER[75] = 15
        self.ATTR_CONVERTER[76] = 15
        self.ATTR_CONVERTER[77] = 16
        self.ATTR_CONVERTER[78] = 16
        self.ATTR_CONVERTER[79] = 16
        self.ATTR_CONVERTER[80] = 16
        self.ATTR_CONVERTER[81] = 16
        self.ATTR_CONVERTER[82] = 17
        self.ATTR_CONVERTER[83] = 17
        self.ATTR_CONVERTER[84] = 17
        self.ATTR_CONVERTER[85] = 17
        self.ATTR_CONVERTER[86] = 17
        self.ATTR_CONVERTER[87] = 18
        self.ATTR_CONVERTER[88] = 18
        self.ATTR_CONVERTER[89] = 18
        self.ATTR_CONVERTER[90] = 18
        self.ATTR_CONVERTER[91] = 18
        self.ATTR_CONVERTER[92] = 19
        self.ATTR_CONVERTER[93] = 19
        self.ATTR_CONVERTER[94] = 19
        self.ATTR_CONVERTER[95] = 19
        self.ATTR_CONVERTER[96] = 19

    def calculate_totals(self):
        if self.goalkeeper >=15:
            
            self.total = self.aerial_ability + self.command_of_area + self.communication + self.eccentricity +\
                         self.handling + self.kicking + self.one_on_ones + self.reflexes + self.rushing_out +\
                         self.tendency_to_punch + self.throwing + self.aggression + self.anticipation + self.bravery +\
                         self.composure + self.concentration + self.creativity + self.decisions + self.determination +\
                         self.flair + self.influence + self.off_the_ball + self.positioning + self.teamwork +\
                         self.work_rate + self.acceleration + self.agility + self.balance + self.jumping +\
                         self.natural_fitness + self.pace + self.stamina + self.strength
            
            self.goalkeeper_total = self.aerial_ability + self.communication + self.handling + self.kicking +\
                                    self.one_on_ones + self.reflexes + self.throwing + self.concentration +\
                                    self.decisions + self.positioning
            
            self.full_back_total = 0
            self.defender_central_total = 0
            self.defensive_midfielder_total = 0
            self.winger_total = 0
            self.attacking_midfielder_total = 0
            self.striker_total = 0
            
        else:
            
            self.total = self.corners + self.crossing + self.dribbling + self.finishing + self.first_touch +\
                         self.free_kicks + self.heading + self.long_shots + self.long_throws + self.marking +\
                         self.passing + self.penalty_taking + self.tackling + self.technique + self.aggression +\
                         self.anticipation + self.bravery + self.composure + self.concentration + self.creativity +\
                         self.decisions + self.determination + self.flair + self.influence + self.off_the_ball +\
                         self.positioning + self.teamwork + self.work_rate + self.acceleration + self.agility +\
                         self.balance + self.jumping + self.natural_fitness + self.pace + self.stamina + self.strength
            
            self.goalkeeper_total = 0
            
            self.full_back_total = self.acceleration + self.anticipation + self.concentration + self.crossing +\
                                   self.decisions + self.marking + self.pace + self.passing + self.positioning +\
                                   self.tackling
            
            self.defender_central_total = self.anticipation + self.bravery + self.concentration + self.decisions +\
                                          self.heading + self.marking + self.pace + self.positioning + self.strength\
                                          + self.tackling
        
            self.defensive_midfielder_total = self.concentration + self.creativity + self.decisions +\
                                              self.first_touch + self.marking + self.pace + self.passing +\
                                              self.positioning + self.tackling + self.work_rate
        
            self.winger_total = self.acceleration + self.creativity + self.crossing + self.dribbling + self.finishing +\
                                self.first_touch + self.off_the_ball + self.pace + self.passing + self.technique
        
            self.attacking_midfielder_total = self.anticipation + self.creativity + self.decisions + self.dribbling +\
                                              self.first_touch + self.long_shots + self.off_the_ball + self.pace +\
                                              self.passing + self.technique
        
            self.striker_total = self.acceleration + self.agility + self.anticipation + self.composure +\
                                 self.decisions + self.finishing + self.first_touch + self.off_the_ball + self.pace +\
                                 self.technique

        self.totals = [self.total, self.goalkeeper_total, self.full_back_total, self.defender_central_total,
                       self.defensive_midfielder_total, self.winger_total, self.attacking_midfielder_total,
                       self.striker_total]
        self.position_totals = [self.goalkeeper_total, self.full_back_total, self.full_back_total,
                                self.defender_central_total, self.defender_central_total,
                                self.defensive_midfielder_total, self.winger_total, self.winger_total,
                                self.attacking_midfielder_total, self.striker_total, self.striker_total]

        self.goalkeeper_compare = self.total + self.goalkeeper_total * 4
        self.full_back_compare = self.total + self.full_back_total * 4
        self.defender_central_compare = self.total + self.defender_central_total * 4
        self.defensive_midfielder_compare = self.total + self.defensive_midfielder_total * 4
        self.winger_compare = self.total + self.winger_total * 4
        self.attacking_midfielder_compare = self.total + self.attacking_midfielder_total * 4
        self.striker_compare = self.total + self.striker_total * 4
        self.compares = [self.goalkeeper_compare, self.full_back_compare, self.full_back_compare, self.defender_central_compare, self.defender_central_compare, self.defensive_midfielder_compare, self.winger_compare, self.winger_compare, self.attacking_midfielder_compare, self.striker_compare, self.striker_compare]
        
    def populate_general_from_addr(self, addr):
        
        buf = create_string_buffer(self.PLAYER_GENERAL_BYTES)
        s = c_size_t()
    
        if self.K32.ReadProcessMemory(self.PROCESS, addr, buf, self.PLAYER_GENERAL_BYTES, byref(s)):
            
            # General
            
            self.uid = int(self.reverse_hex_string(buf[self.UID_ADDR[0]:self.UID_ADDR[1]].hex()),16)
            self.first_name = self.get_name(addr + self.FIRST_NAME_ADDR[0])
            self.second_name = self.get_name(addr + self.SECOND_NAME_ADDR[0])
            self.date_of_birth = self.get_years_and_days(buf[self.DATE_OF_BIRTH[0]:self.DATE_OF_BIRTH[1]].hex())
            
            # International
            self.international_apps = int(buf[self.INTERNATIONAL_APPS_ADDR[0]:self.INTERNATIONAL_APPS_ADDR[1]].hex(),16)
            self.international_goals = int(buf[self.INTERNATIONAL_GOALS_ADDR[0]:self.INTERNATIONAL_GOALS_ADDR[1]].hex(),16)
            self.under_21_apps = int(buf[self.UNDER_21_APPS_ADDR[0]:self.UNDER_21_APPS_ADDR[1]].hex(),16)
            self.under_21_goals = int(buf[self.UNDER_21_GOALS_ADDR[0]:self.UNDER_21_GOALS_ADDR[1]].hex(),16)
            
            # Form
            self.morale = int(buf[self.MORALE_ADDR[0]:self.MORALE_ADDR[1]].hex(),16)

            # Contract
            self.value = round(int(self.reverse_hex_string(buf[self.VALUE_ADDR[0]:self.VALUE_ADDR[1]].hex()), 16) * 1.45)
            
        else:
            print("populate_general_from_addr: Access Denied!")
            
    def populate_attributes_from_addr(self, addr):
        
        buf = create_string_buffer(self.PLAYER_ATTRIBUTE_BYTES)
        s = c_size_t()
    
        if self.K32.ReadProcessMemory(self.PROCESS, addr, buf, self.PLAYER_ATTRIBUTE_BYTES, byref(s)):
            
            # Positions
            self.goalkeeper = int(buf[self.GOALKEEPER_ADDR[0]:self.GOALKEEPER_ADDR[1]].hex(),16)
            self.sweeper = int(buf[self.SWEEPER_ADDR[0]:self.SWEEPER_ADDR[1]].hex(),16)
            self.full_back_left = int(buf[self.FULL_BACK_LEFT_ADDR[0]:self.FULL_BACK_LEFT_ADDR[1]].hex(),16)
            self.full_back_right = int(buf[self.FULL_BACK_RIGHT_ADDR[0]:self.FULL_BACK_RIGHT_ADDR[1]].hex(),16)
            self.defender_central = int(buf[self.DEFENDER_CENTRAL_ADDR[0]:self.DEFENDER_CENTRAL_ADDR[1]].hex(),16)
            self.wing_back_left = int(buf[self.WING_BACK_LEFT_ADDR[0]:self.WING_BACK_LEFT_ADDR[1]].hex(),16)
            self.wing_back_right = int(buf[self.WING_BACK_RIGHT_ADDR[0]:self.WING_BACK_RIGHT_ADDR[1]].hex(),16)
            self.defensive_midfielder = int(buf[self.DEFENSIVE_MIDFIELDER_ADDR[0]:self.DEFENSIVE_MIDFIELDER_ADDR[1]].hex(),16)
            self.midfielder_left = int(buf[self.MIDFIELDER_LEFT_ADDR[0]:self.MIDFIELDER_LEFT_ADDR[1]].hex(),16)
            self.midfielder_right = int(buf[self.MIDFIELDER_RIGHT_ADDR[0]:self.MIDFIELDER_RIGHT_ADDR[1]].hex(),16)
            self.midfielder_central = int(buf[self.MIDFIELDER_CENTRAL_ADDR[0]:self.MIDFIELDER_CENTRAL_ADDR[1]].hex(),16)
            self.attacking_midfielder_left = int(buf[self.ATTACKING_MIDFIELDER_LEFT_ADDR[0]:self.ATTACKING_MIDFIELDER_LEFT_ADDR[1]].hex(),16)
            self.attacking_midfielder_right = int(buf[self.ATTACKING_MIDFIELDER_RIGHT_ADDR[0]:self.ATTACKING_MIDFIELDER_RIGHT_ADDR[1]].hex(),16)
            self.attacking_midfielder_central = int(buf[self.ATTACKING_MIDFIELDER_CENTRAL_ADDR[0]:self.ATTACKING_MIDFIELDER_CENTRAL_ADDR[1]].hex(),16)
            self.striker = int(buf[self.STRIKER_ADDR[0]:self.STRIKER_ADDR[1]].hex(),16)
            
            if self.goalkeeper > 14 :
                self.positions.append("goalkeeper")
            else:
                if self.sweeper > 14 :
                    self.positions.append("sweeper")
                if self.full_back_left > 14 :
                    self.positions.append("full_back_left")
                if self.full_back_right > 14 :
                    self.positions.append("full_back_right")
                if self.defender_central > 14 :
                    self.positions.append("defender_central")
                if self.wing_back_left > 14 :
                    self.positions.append("wing_back_left")
                if self.wing_back_right > 14 :
                    self.positions.append("wing_back_right")
                if self.defensive_midfielder > 14 :
                    self.positions.append("defensive_midfielder")
                if self.midfielder_left > 14 :
                    self.positions.append("midfielder_left")
                if self.midfielder_right > 14 :
                    self.positions.append("midfielder_right")
                if self.midfielder_central > 14 :
                    self.positions.append("midfielder_central")
                if self.attacking_midfielder_left > 14 :
                    self.positions.append("attacking_midfielder_left")
                if self.attacking_midfielder_right > 14 :
                    self.positions.append("attacking_midfielder_right")
                if self.attacking_midfielder_central > 14 :
                    self.positions.append("attacking_midfielder_central")
                if self.striker > 14 :
                    self.positions.append("striker")
        
            # Goalkeeping Attributes
            self.aerial_ability = self.attribute_100_20(int(buf[self.AERIAL_ABILITY_ADDR[0]:self.AERIAL_ABILITY_ADDR[1]].hex(),16))
            self.command_of_area = self.attribute_100_20(int(buf[self.COMMAND_OF_AREA_ADDR[0]:self.COMMAND_OF_AREA_ADDR[1]].hex(),16))
            self.communication = self.attribute_100_20(int(buf[self.COMMUNICATION_ADDR[0]:self.COMMUNICATION_ADDR[1]].hex(),16))
            self.eccentricity = self.attribute_100_20(int(buf[self.ECCENTRICITY_ADDR[0]:self.ECCENTRICITY_ADDR[1]].hex(),16))
            self.handling = self.attribute_100_20(int(buf[self.HANDLING_ADDR[0]:self.HANDLING_ADDR[1]].hex(),16))
            self.kicking = self.attribute_100_20(int(buf[self.KICKING_ADDR[0]:self.KICKING_ADDR[1]].hex(),16))
            self.one_on_ones = self.attribute_100_20(int(buf[self.ONE_ON_ONES_ADDR[0]:self.ONE_ON_ONES_ADDR[1]].hex(),16))
            self.reflexes = self.attribute_100_20(int(buf[self.REFLEXES_ADDR[0]:self.REFLEXES_ADDR[1]].hex(),16))
            self.rushing_out = self.attribute_100_20(int(buf[self.RUSHING_OUT_ADDR[0]:self.RUSHING_OUT_ADDR[1]].hex(),16))
            self.tendency_to_punch = self.attribute_100_20(int(buf[self.TENDENCY_TO_PUNCH_ADDR[0]:self.TENDENCY_TO_PUNCH_ADDR[1]].hex(),16))
            self.throwing = self.attribute_100_20(int(buf[self.THROWING_ADDR[0]:self.THROWING_ADDR[1]].hex(),16))
        
            # Technical Attributes
            self.corners = self.attribute_100_20(int(buf[self.CORNERS_ADDR[0]:self.CORNERS_ADDR[1]].hex(),16))
            self.crossing = self.attribute_100_20(int(buf[self.CROSSING_ADDR[0]:self.CROSSING_ADDR[1]].hex(),16))
            self.dribbling = self.attribute_100_20(int(buf[self.DRIBBLING_ADDR[0]:self.DRIBBLING_ADDR[1]].hex(),16))
            self.finishing = self.attribute_100_20(int(buf[self.FINISHING_ADDR[0]:self.FINISHING_ADDR[1]].hex(),16))
            self.first_touch = self.attribute_100_20(int(buf[self.FIRST_TOUCH_ADDR[0]:self.FIRST_TOUCH_ADDR[1]].hex(),16))
            self.free_kicks = self.attribute_100_20(int(buf[self.FREE_KICKS_ADDR[0]:self.FREE_KICKS_ADDR[1]].hex(),16))
            self.heading = self.attribute_100_20(int(buf[self.HEADING_ADDR[0]:self.HEADING_ADDR[1]].hex(),16))
            self.long_shots = self.attribute_100_20(int(buf[self.LONG_SHOTS_ADDR[0]:self.LONG_SHOTS_ADDR[1]].hex(),16))
            self.long_throws = self.attribute_100_20(int(buf[self.LONG_THROWS_ADDR[0]:self.LONG_THROWS_ADDR[1]].hex(),16))
            self.marking = self.attribute_100_20(int(buf[self.MARKING_ADDR[0]:self.MARKING_ADDR[1]].hex(),16))
            self.passing = self.attribute_100_20(int(buf[self.PASSING_ADDR[0]:self.PASSING_ADDR[1]].hex(),16))
            self.penalty_taking = self.attribute_100_20(int(buf[self.PENALTY_TAKING_ADDR[0]:self.PENALTY_TAKING_ADDR[1]].hex(),16))
            self.tackling = self.attribute_100_20(int(buf[self.TACKLING_ADDR[0]:self.TACKLING_ADDR[1]].hex(),16))
            self.technique = self.attribute_100_20(int(buf[self.TECHNIQUE_ADDR[0]:self.TECHNIQUE_ADDR[1]].hex(),16))
        
            # Mental Attributes
            self.aggression = self.attribute_100_20(int(buf[self.AGGRESSION_ADDR[0]:self.AGGRESSION_ADDR[1]].hex(),16))
            self.anticipation = self.attribute_100_20(int(buf[self.ANTICIPATION_ADDR[0]:self.ANTICIPATION_ADDR[1]].hex(),16))
            self.bravery = self.attribute_100_20(int(buf[self.BRAVERY_ADDR[0]:self.BRAVERY_ADDR[1]].hex(),16))
            self.composure = self.attribute_100_20(int(buf[self.COMPOSURE_ADDR[0]:self.COMPOSURE_ADDR[1]].hex(),16))
            self.concentration = self.attribute_100_20(int(buf[self.CONCENTRATION_ADDR[0]:self.CONCENTRATION_ADDR[1]].hex(),16))
            self.creativity = self.attribute_100_20(int(buf[self.CREATIVITY_ADDR[0]:self.CREATIVITY_ADDR[1]].hex(),16))
            self.decisions = self.attribute_100_20(int(buf[self.DECISIONS_ADDR[0]:self.DECISIONS_ADDR[1]].hex(),16))
            self.determination = self.attribute_100_20(int(buf[self.DETERMINATION_ADDR[0]:self.DETERMINATION_ADDR[1]].hex(),16))
            self.flair = self.attribute_100_20(int(buf[self.FLAIR_ADDR[0]:self.FLAIR_ADDR[1]].hex(),16))
            self.influence = self.attribute_100_20(int(buf[self.INFLUENCE_ADDR[0]:self.INFLUENCE_ADDR[1]].hex(),16))
            self.off_the_ball = self.attribute_100_20(int(buf[self.OFF_THE_BALL_ADDR[0]:self.OFF_THE_BALL_ADDR[1]].hex(),16))
            self.positioning = self.attribute_100_20(int(buf[self.POSITIONING_ADDR[0]:self.POSITIONING_ADDR[1]].hex(),16))
            self.teamwork = self.attribute_100_20(int(buf[self.TEAMWORK_ADDR[0]:self.TEAMWORK_ADDR[1]].hex(),16))
            self.work_rate = self.attribute_100_20(int(buf[self.WORK_RATE_ADDR[0]:self.WORK_RATE_ADDR[1]].hex(),16))
        
            # Physical Attributes
            self.acceleration = self.attribute_100_20(int(buf[self.ACCELERATION_ADDR[0]:self.ACCELERATION_ADDR[1]].hex(),16))
            self.agility = self.attribute_100_20(int(buf[self.AGILITY_ADDR[0]:self.AGILITY_ADDR[1]].hex(),16))
            self.balance = self.attribute_100_20(int(buf[self.BALANCE_ADDR[0]:self.BALANCE_ADDR[1]].hex(),16))
            self.jumping = self.attribute_100_20(int(buf[self.JUMPING_ADDR[0]:self.JUMPING_ADDR[1]].hex(),16))
            self.natural_fitness = self.attribute_100_20(int(buf[self.NATURAL_FITNESS_ADDR[0]:self.NATURAL_FITNESS_ADDR[1]].hex(),16))
            self.pace = self.attribute_100_20(int(buf[self.PACE_ADDR[0]:self.PACE_ADDR[1]].hex(),16))
            self.stamina = self.attribute_100_20(int(buf[self.STAMINA_ADDR[0]:self.STAMINA_ADDR[1]].hex(),16))
            self.strength = self.attribute_100_20(int(buf[self.STRENGTH_ADDR[0]:self.STRENGTH_ADDR[1]].hex(),16))
        
            # Other
            self.left_foot = int(buf[self.LEFT_FOOT_ADDR[0]:self.LEFT_FOOT_ADDR[1]].hex(),16)
            self.right_foot = int(buf[self.RIGHT_FOOT_ADDR[0]:self.RIGHT_FOOT_ADDR[1]].hex(),16)
            
            # Calculated
            self.calculate_totals()
            
        else:
            print("populate_attributes_from_addr: Access Denied!")
        
    def populate_player_from_addr(self, addr):
        
        self.MAIN_ADDR = addr
        class_id = self.decode_player_class_id(self.MAIN_ADDR)
        
        if not class_id == self.PLAYER_CLASS_ID:
            print("populate_general_from_addr: Incorrect class id!")
            return
        
        self.populate_general_from_addr(addr)
        
        buf = create_string_buffer(self.PLAYER_GENERAL_BYTES)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, addr, buf, self.PLAYER_GENERAL_BYTES, byref(s)):
            
            attributes_addr = int(self.reverse_hex_string(buf[self.ATTR_ADDR[0]:self.ATTR_ADDR[1]].hex()),16)
            self.populate_attributes_from_addr(attributes_addr)
            
            club_addr = int(self.reverse_hex_string(buf[self.CLUB_ADDR[0]:self.CLUB_ADDR[1]].hex()),16)
            self.populate_club_info_from_addr(club_addr)

            contract_link_addr = int(self.reverse_hex_string
                                     (buf[self.CONTRACT_LINK_ADDR[0]:self.CONTRACT_LINK_ADDR[1]].hex()), 16)
            self.populate_contract_from_addr(contract_link_addr)
            
        else:
            print("populate_player_from_addr: Access Denied!")
        
        # Form
        self.condition = None
        self.form = None
        self.average_rating = None
        
    def get_name(self, name_addr):
    
        buf = create_string_buffer(4)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, name_addr, buf, 4, byref(s)):
            self.reverse_array(buf)
            link1_addr = int(buf.raw.hex(),16) + 0x24
        else:
            print("get_name_point_1: Access Denied!")
            return
    
        buf = create_string_buffer(4)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, link1_addr, buf, 4, byref(s)):
            self.reverse_array(buf)
            link2_addr = int(buf.raw.hex(),16) + 8
        else:
            print("get_name_point_2: Access Denied!")
            return
    
        buf = create_string_buffer(4)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, link2_addr, buf, 4, byref(s)):
            self.reverse_array(buf)
            link3_addr = int(buf.raw.hex(),16)
        else:
            print("get_name_point_3: Access Denied!")
            return
        
        buf = create_string_buffer(100)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, link3_addr, buf, 100, byref(s)):
            name_100 = buf.raw.hex()
            name = self.decode_name(name_100)
            return name
        else:
            print("get_name_point_4: Access Denied!")
            return
        
    def decode_name(self, hex_string, version="normal"):

        name = ""
        start = 0
        free = version == "second"
    
        while True:
        
            hex_segment = hex_string[start:start+4]
            if hex_segment == '0000':
                if free:
                    free = False
                    name = ""
                else:
                    break
            hex_segment_reversed = self.reverse_hex_string(hex_segment)
            char = chr(int(hex_segment_reversed,16))
            name = name + char
            start += 4
            if (start + 4) > len(hex_string):
                break
        
        return name
        
    def get_years_and_days(self, hex_string):
        
        days = int(self.reverse_hex_string(hex_string[0:4]), 16)
        years = int(self.reverse_hex_string(hex_string[4:8]), 16)
        return years, days
    
    def set_age(self, current_date):
        
        years = current_date[0] - self.date_of_birth[0]
        days = current_date[1] - self.date_of_birth[1]
        if days < 0:
            days += 365
            years -= 1
        if days < 0: # Leap year, simple fix, not all edge cases covered.
            days = 0
        
        self.age = (years, days)
        
    def populate_club_info_from_addr(self, addr):
        
        if addr == 0:
            self.club_name = ""
            self.club_uid = -1
            return
        
        buf = create_string_buffer(self.CLUB_BYTES)
        s = c_size_t()
    
        if self.K32.ReadProcessMemory(self.PROCESS, addr, buf, self.CLUB_BYTES, byref(s)):
            self.club_uid = int(self.reverse_hex_string(buf[self.CLUB_UID_ADDR[0]:self.CLUB_UID_ADDR[1]].hex()),16)
            self.club_name, self.club_name_long = self.get_club_name(int(self.reverse_hex_string(buf[self.CLUB_NAME_ADDR[0]:self.CLUB_NAME_ADDR[1]].hex()),16))
        else:
            print("populate_club_info_from_addr: Access Denied!")
            
    def get_club_name(self, addr):
        
        addr += 0x28
    
        buf = create_string_buffer(4)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, addr, buf, 4, byref(s)):
            self.reverse_array(buf)
            link1_addr = int(buf.raw.hex(),16) + 8
        else:
            print("get_club_name_point_1: Access Denied!")
            return
    
        buf = create_string_buffer(4)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, link1_addr, buf, 4, byref(s)):
            self.reverse_array(buf)
            link2_addr = int(buf.raw.hex(),16)
        else:
            print("get_club_name_point_2: Access Denied!")
            return
        
        buf = create_string_buffer(100)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, link2_addr, buf, 100, byref(s)):
            name_100 = buf.raw.hex()
            name_long = self.decode_name(name_100)
            name = self.decode_name(name_100, version="second")
            return name, name_long
        else:
            print("get_club_name_point_3: Access Denied!")
            return
        
    def to_string(self, elevens=None):
        s = self.first_name + " " + self.second_name
        s = s + " (" + str(self.uid) + ")    "
        if elevens is not None:
            s = s + self.in_elevens(elevens) + "    "
        s = s + str(self.age[0]) + " years " + str(self.age[1]) + " days    " + str(self.value) + "    "
        s = s + self.list_to_string(self.positions) + "    " + self.club_name + "\n"
        s = s + str(self.total) + " " + str(self.goalkeeper_total) + " " + str(self.full_back_total) + " " + str(self.defender_central_total) + " " + str(self.defensive_midfielder_total) + " " + str(self.winger_total) + " " + str(self.attacking_midfielder_total) + " " + str(self.striker_total)
        return s

    def to_string_eleven(self, position):
        s = self.first_name + " " + self.second_name + "\t\t"
        s = s + str(self.position_totals[position]) + "/" + str(self.total)
        return s

    def to_eleven_csv(self, position):
        s = self.first_name + " " + self.second_name + ";"
        s = s + str(self.position_totals[position]) + ";" + str(self.total)
        return s
    
    def to_csv(self, elevens=None):
        s = self.first_name + " " + self.second_name + ";"
        s = s + str(self.uid) + ";"
        if elevens is not None:
            s = s + self.in_elevens(elevens) + ";"
        s = s + str(self.age[0]) + ";" + str(self.age[1]) + ";" + str(self.value) + ";"
        s = s + self.list_to_string(self.positions)  + ";" + self.club_name + ";"
        s = s + str(self.total) + ";" + str(self.goalkeeper_total) + ";" + str(self.full_back_total) + ";" + str(self.defender_central_total) + ";" + str(self.defensive_midfielder_total) + ";" + str(self.winger_total) + ";" + str(self.attacking_midfielder_total) + ";" + str(self.striker_total)
        return s

    @staticmethod
    def list_to_string(lis):
        s = ""
        first = True
        for item in lis:
            if first:
                first = False
            else:
                s = s + " "
            s = s + str(item)
        return s

    def in_elevens(self, elevens):
        e1 = elevens[0]
        e2 = elevens[1]
        for p in e1:
            if p is None:
                continue
            if p.uid == self.uid:
                return "1"
        for p in e2:
            if p is None:
                continue
            if p.uid == self.uid:
                return "2"
        return " "

    def populate_contract_from_addr(self, link_addr):

        if link_addr == 0:
            self.transfer_status = 0
            self.basic_wage = 0
            self.contract_expires = None
            return

        buf = create_string_buffer(4)
        s = c_size_t()
        if self.K32.ReadProcessMemory(self.PROCESS, link_addr, buf, 4, byref(s)):
            self.reverse_array(buf)
            contract_addr = int(buf.raw.hex(), 16)
        else:
            print("populate_contract_from_addr_1: Access Denied!")
            return

        buf = create_string_buffer(self.CONTRACT_BYTES)
        s = c_size_t()

        if self.K32.ReadProcessMemory(self.PROCESS, contract_addr, buf, self.CONTRACT_BYTES, byref(s)):
            self.transfer_status = int(buf[0x27].hex(), 16)
            self.basic_wage = round(int(self.reverse_hex_string(buf[0x10:0x14].hex()), 16) * 1.45)
            self.contract_expires = self.get_years_and_days(buf[0x20:0x24].hex())
        else:
            print("populate_contract_from_addr_2: Access Denied")

    def set_contract_status(self, current_date):
        if self.contract_expires is None:
            self.contract_status = "Unattached"
            return
        years = self.contract_expires[0] - current_date[0]
        days = self.contract_expires[1] - current_date[1]
        if years < 0:
            self.contract_status = "Expired"
        elif years == 0:
            self.contract_status = "Expiring"
            if days < 0:
                self.contract_status = "Expired"
        elif years == 1 and days < 0:
            self.contract_status = "Expiring"
        else:
            self.contract_status = "Contracted"
