class Match:
    def __init__(self):
        self.gameCreationTime = None
        self.gameEndTimeMinutes = None
        self.gameEndTimeSeconds = None
        self.queueType = None
        self.platform = None;
        self.version = None;
        self.participants = []

        # For the specific user, add the image of the champion they were playing, as well as if they won or not
        self.championImageUrl = None
        self.championName = None
        self.win = None;

    # Setters
    def set_gameCreationTime(self, gameCreationTime):
        self.gameCreationTime = gameCreationTime

    def add_minutes(self, minute):
        self.gameEndTimeMinutes = minute

    def add_seconds(self, second):
        self.gameEndTimeSeconds = second

    def add_queueType(self, queueType):
        self.queueType = queueType

    def add_platform(self, platform):
        self.platform = platform;
    
    def add_version(self, version):
        self.version = version;

    def add_participant(self, participant):
        self.participants.append(participant)

    def add_championImageUrl(self, championImageUrl):
        self.championImageUrl = championImageUrl

    def add_championName(self, championName):
        self.championName = championName

    def set_isWinner(self, win):
        self.win = win;

    # Getters
    def get_gameCreationTime(self):
        return self.gameCreationTime

    def get_minutes(self):
        return self.gameEndTimeMinutes

    def get_seconds(self):
        return self.gameEndTimeSeconds

    def get_queueType(self):
        return self.queueType
    
    def get_platform(self):
        return self.platform;

    def get_version(self):
        return self.version;

    def get_participants(self):
        return self.participants

    def get_championImageUrl(self):
        return self.championImageUrl

    def get_championName(self):
        return self.championName
    
    def is_winner(self):
        return self.win;
