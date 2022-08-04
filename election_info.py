class currentElection():
    election_id = None
    election_name = None
    race_id = None
    candidates = []
    poll_manager = None
    start_time = None
    end_time = None
    date = None
    precincts = None
    races = []
    race_set = False
    candidates_made = False
    election_data_added = False

    def __init__(self, election_name, election_id):
        self.election_name = election_name
        self.election_id = election_id

    def __init__(self):
        pass

    def reset(self):
        self.election_id = None
        self.election_name = None
        self.race_id = None
        self.candidates = []
        self.poll_manager = None
        self.start_time = None
        self.end_time = None
        self.date = None
        self.precincts = None
        self.races = []
        self.race_set = False
        self.candidates_made = False
        self.election_data_added = False



class currentVoter():
    current_voter_id = None
    first_race_choose = False
    current_race = None
    user_selected_race = None
    races_user_can_vote_in = []
    races_voted_in = []

    def __init__(self, current_voter_id):
        self.current_voter_id = current_voter_id

    def __init__(self):
        pass

    def clear(self):
        self.current_voter_id = None
        self.first_race_choose = False
        self.current_race = None
        self.user_selected_race = None
        self.races_user_can_vote_in = []
        self.races_voted_in = []