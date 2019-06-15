import math

class eleven:
    
    PLAYERS = None
    
    def __init__(self):
        
        self.starting = []
        self.second = []
        
        self.elevens = [self.starting, self.second]
        
        self.goalkeepers = []
        self.full_backs_left = []
        self.full_backs_right = []
        self.defenders_central = []
        self.defensive_midfielders = []
        self.wingers_left = []
        self.wingers_right = []
        self.attacking_midfielders_central = []
        self.strikers = []
        
        self.matrix = [self.goalkeepers, self.full_backs_left, self.full_backs_right, self.defenders_central, self.defenders_central, self.defensive_midfielders, self.wingers_left, self.wingers_right, self.attacking_midfielders_central, self.strikers, self.strikers]
        
    def set_players(self, players):
        self.PLAYERS = players.copy()
        for p in self.PLAYERS:
            if "goalkeeper" in p.positions:
                self.goalkeepers.append(p)
            if "full_back_left" in p.positions or "wing_back_left" in p.positions:
                self.full_backs_left.append(p)
            if "full_back_right" in p.positions or "wing_back_right" in p.positions:
                self.full_backs_right.append(p)
            if "sweeper" in p.positions or "defender_central" in p.positions:
                self.defenders_central.append(p)
            if "defensive_midfielder" in p.positions:
                self.defensive_midfielders.append(p)
            if "midfielder_left" in p.positions or "attacking_midfielder_left" in p.positions:
                self.wingers_left.append(p)
            if "midfielder_right" in p.positions or "attacking_midfielder_right" in p.positions:
                self.wingers_right.append(p)
            if "midfielder_central" in p.positions or "attacking_midfielder_central" in p.positions:
                self.attacking_midfielders_central.append(p)
            if "striker" in p.positions:
                self.strikers.append(p)
                
        self.goalkeepers.sort(key=lambda x: x.total + x.goalkeeper_total * 4, reverse = True)
        self.full_backs_left.sort(key=lambda x: x.total + x.full_back_total * 4, reverse = True)
        self.full_backs_right.sort(key=lambda x: x.total + x.full_back_total * 4, reverse = True)
        self.defenders_central.sort(key=lambda x: x.total + x.defender_central_total * 4, reverse = True)
        self.defensive_midfielders.sort(key=lambda x: x.total + x.defensive_midfielder_total * 4, reverse = True)
        self.wingers_left.sort(key=lambda x: x.total + x.winger_total * 4, reverse = True)
        self.wingers_right.sort(key=lambda x: x.total + x.winger_total * 4, reverse = True)
        self.attacking_midfielders_central.sort(key=lambda x: x.total + x.attacking_midfielder_total * 4, reverse = True)
        self.strikers.sort(key=lambda x: x.total + x.striker_total * 4, reverse = True)
        
    def get_eleven(self):
        
        self.starting = []
        self.second = []
        
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
        
        print(self.list_to_string(self.starting))
        print('\n')
        print(self.list_to_string(self.second))
        
    def list_to_string(self, lis):
        s = ""
        first = True
        for p in lis:
            if first:
                first = False
            else:
                s = s + "\n"
            s = s + p.to_string()
        return s

    def prune_matrix(self):
        for i in range(22):
            p = self.elevens[math.floor(i/11)][i%11]
            for j in range(11):
                if p in self.matrix[j]:
                    self.matrix[j].remove(p)
        
    def prune_elevens(self):
        
    def repopulate_elevens(self):
        
        added_player = False
        
        for i in range(11):
            if (self.elevens[0][i] is None) and (len(self.matrix[i]) > 0):
                self.elevens[0][i] = self.matrix[i][0]
                added_player = True
            if (self.elevens[1][i] is None) and (len(self.matrix[i]) > 1):
                self.elevens[1][i] = self.matrix[i][1]
        
        return not added_player