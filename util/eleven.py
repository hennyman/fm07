import math


class Eleven:

    PLAYERS = None
    POSITIONS = ["GK", "DL", "DR", "DC", "DC", "DM", "ML", "MR", "AM", "ST", "ST"]
    
    def __init__(self):
        self.elevens = [[], []]
        self.matrix = [[], [], [], [], [], [], [], [], [], [], []]

    def set_players(self, players):
        self.PLAYERS = players.copy()
        for p in self.PLAYERS:
            if "goalkeeper" in p.positions:
                self.matrix[0].append(p)
            if "full_back_left" in p.positions or "wing_back_left" in p.positions:
                self.matrix[1].append(p)
            if "full_back_right" in p.positions or "wing_back_right" in p.positions:
                self.matrix[2].append(p)
            if "sweeper" in p.positions or "defender_central" in p.positions:
                self.matrix[3].append(p)
                self.matrix[4].append(p)
            if "defensive_midfielder" in p.positions:
                self.matrix[5].append(p)
            if "midfielder_left" in p.positions or "attacking_midfielder_left" in p.positions:
                self.matrix[6].append(p)
            if "midfielder_right" in p.positions or "attacking_midfielder_right" in p.positions:
                self.matrix[7].append(p)
            if "midfielder_central" in p.positions or "attacking_midfielder_central" in p.positions:
                self.matrix[8].append(p)
            if "striker" in p.positions:
                self.matrix[9].append(p)
                self.matrix[10].append(p)
                
        self.matrix[0].sort(key=lambda x: x.total + x.goalkeeper_total * 4, reverse=True)
        self.matrix[1].sort(key=lambda x: x.total + x.full_back_total * 4, reverse=True)
        self.matrix[2].sort(key=lambda x: x.total + x.full_back_total * 4, reverse=True)
        self.matrix[3].sort(key=lambda x: x.total + x.defender_central_total * 4, reverse=True)
        self.matrix[4].sort(key=lambda x: x.total + x.defender_central_total * 4, reverse=True)
        self.matrix[5].sort(key=lambda x: x.total + x.defensive_midfielder_total * 4, reverse=True)
        self.matrix[6].sort(key=lambda x: x.total + x.winger_total * 4, reverse=True)
        self.matrix[7].sort(key=lambda x: x.total + x.winger_total * 4, reverse=True)
        self.matrix[8].sort(key=lambda x: x.total + x.attacking_midfielder_total * 4, reverse=True)
        self.matrix[9].sort(key=lambda x: x.total + x.striker_total * 4, reverse=True)
        self.matrix[10].sort(key=lambda x: x.total + x.striker_total * 4, reverse=True)
        
    def get_eleven(self, suppress_print=False):

        self.elevens[0] = []
        self.elevens[1] = []
        
        if self.PLAYERS is None:
            return
        
        for i in range(11):
            if len(self.matrix[i]) > 0:
                self.elevens[0].append(self.matrix[i][0])
            else:
                self.elevens[0].append(None)
            if len(self.matrix[i]) > 1:
                self.elevens[1].append(self.matrix[i][1])
            else:
                self.elevens[1].append(None)
        
        while True:
            self.prune_matrix()
            self.prune_elevens()
            is_finished = self.repopulate_elevens()
            if is_finished:
                break

        if not suppress_print:
            print("Starting eleven:")
            print(self.list_to_string(self.elevens[0]))
            print('\n')
            print("Second eleven:")
            print(self.list_to_string(self.elevens[1]))

        return self.elevens.copy()

    def list_to_string(self, lis):
        s = ""
        count = 0
        for p in lis:
            if not count == 0:
                s = s + "\n"
            if p is None:
                s = s + self.POSITIONS[count] + "\t \t" + " "
            else:
                s = s + self.POSITIONS[count] + "\t \t" + p.to_string_eleven(count)
            count += 1
        return s

    def prune_matrix(self):
        for i in range(22):
            p = self.elevens[math.floor(i/11)][i % 11]
            for j in range(11):
                if p in self.matrix[j]:
                    self.matrix[j].remove(p)
        
    def prune_elevens(self):
        for i in range(21):
            p1 = self.elevens[math.floor(i / 11)][i % 11]
            if p1 is None:
                continue
            for j in range(i+1, 22):
                p2 = self.elevens[math.floor(j / 11)][j % 11]
                if p1 == p2:
                    remove_index = self.remove_player(p1, i, j)
                    self.elevens[math.floor(remove_index / 11)][remove_index % 11] = None
                    if remove_index == i:
                        break

        for i in range(11):
            if (self.elevens[0][i] is None) and (not self.elevens[1][i] is None):
                self.elevens[0][i] = self.elevens[1][i]
                self.elevens[1][i] = None

        if (self.elevens[0][3] is None) and (not self.elevens[1][4] is None):
            self.elevens[0][3] = self.elevens[1][4]
            self.elevens[1][4] = None

        if (self.elevens[0][4] is None) and (not self.elevens[1][3] is None):
            self.elevens[0][4] = self.elevens[1][3]
            self.elevens[1][3] = None

        if (self.elevens[0][9] is None) and (not self.elevens[1][10] is None):
            self.elevens[0][9] = self.elevens[1][10]
            self.elevens[1][10] = None

        if (self.elevens[0][10] is None) and (not self.elevens[1][9] is None):
            self.elevens[0][10] = self.elevens[1][9]
            self.elevens[1][9] = None

    def repopulate_elevens(self):
        
        added_player = False
        
        for i in range(11):
            added = 0
            if (self.elevens[0][i] is None) and (len(self.matrix[i]) > 0):
                self.elevens[0][i] = self.matrix[i][0]
                added_player = True
                added = 1
            if (self.elevens[1][i] is None) and (len(self.matrix[i]) > added):
                self.elevens[1][i] = self.matrix[i][added]
                added_player = True
        
        return not added_player

    def remove_player(self, p, i, j):
        # starting vs. second
        if i < 11 <= j:
            return j

        # better position I
        position_values = [p.goalkeeper, max(p.full_back_left, p.wing_back_left),
                           max(p.full_back_right, p.wing_back_right), p.defender_central, p.defender_central,
                           p.defensive_midfielder, max(p.midfielder_left, p.attacking_midfielder_left),
                           max(p.midfielder_right, p.attacking_midfielder_right), p.attacking_midfielder_central,
                           p.striker, p.striker]
        pos_i = position_values[i % 11]
        pos_j = position_values[j % 11]
        if pos_i < 17 and pos_j > 18:
            return i
        elif pos_j < 17 and pos_i > 18:
            return j

        # better backup
        b_compare = []
        for k in range(11):
            if len(self.matrix[k]) == 0:
                b_compare.append(0)
                continue

            b = self.matrix[k][0]

            if k == 0:
                b_compare.append(b.total + b.goalkeeper_total * 4)
            elif k < 3:
                b_compare.append(b.total + b.full_back_total * 4)
            elif k < 5:
                b_compare.append(b.total + b.defender_central_total * 4)
            elif k == 5:
                b_compare.append(b.total + b.defensive_midfielder_total * 4)
            elif k < 8:
                b_compare.append(b.total + b.winger_total * 4)
            elif k == 8:
                b_compare.append(b.total + b.attacking_midfielder_total * 4)
            else:
                b_compare.append(b.total + b.striker_total * 4)

        value = (p.compares[i % 11] - p.compares[j % 11]) * 2 - (b_compare[i % 11] - b_compare[j % 11])
        if value > 0:
            return j
        elif value < 0:
            return i

        # better position II
        if pos_j < pos_i:
            return j
        else:
            return i
