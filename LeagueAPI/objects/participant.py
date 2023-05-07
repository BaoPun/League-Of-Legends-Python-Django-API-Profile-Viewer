class Participant:
    def __init__(self):
        self.assists = None
        self.championName = None
        self.deaths = None
        self.items = [None, None, None, None, None, None, None]
        self.kills = None
        self.teamPosition = None
        self.summonerSpells = [None, None]
        self.summonerName = None
        self.totalDamage = None
        self.minionsKilled = None
        self.team = None
        self.win = None

    # Setters
    def set_assists(self, assists):
        self.assists = assists

    def set_championName(self, championName):
        self.championName = championName

    def set_deaths(self, deaths):
        self.deaths = deaths

    def set_kills(self, kills):
        self.kills = kills

    def set_teamPosition(self, teamPosition):
        self.teamPosition = teamPosition

    def set_summonerName(self, summonerName):
        self.summonerName = summonerName

    def set_totalDamage(self, totalDamage):
        self.totalDamage = totalDamage

    def set_minionsKilled(self, minionsKilled):
        self.minionsKilled = minionsKilled

    def set_teamSide(self, team):
        self.team = team

    def set_win(self, win):
        self.win = win

    def set_items(self, item_list):
        for i in range(0, len(item_list)):
            self.items[i] = item_list[i]

    def set_summonerSpells(self, summonerSpells):
        for i in range(0, len(summonerSpells)):
            self.summonerSpells[i] = summonerSpells[i]

    # Getters
    def get_assists(self):
        return self.assists

    def get_championName(self):
        return self.championName

    def get_deaths(self):
        return self.deaths

    def get_kills(self):
        return self.kills

    def get_teamPosition(self):
        return self.teamPosition

    def get_summonerName(self):
        return self.summonerName

    def get_totalDamage(self):
        return self.totalDamage

    def get_minionsKilled(self):
        return self.minionsKilled

    def get_teamSide(self):
        return self.team

    def get_win(self):
        return self.win

    def get_items(self):
        return self.items

    def get_summonerSpells(self):
        return self.summonerSpells

    # String output
    def __repr__(self):
        return '{name} - {position}'.format(name=self.get_summonerName(), position=self.get_teamPosition())
