
class stage:
    def __init__(self, stage_info):
        self.name = stage_info['name']
        self.type = stage_info['type']
        self.subtype = stage_info['subtype']
        self.input_data_types = stage_info['input_data_types']
        self.output_data_types = stage_info['output_data_types']
        self.config = stage_info['config']
        self.follows = None
        self.followers = []

    def set_follows(self, stage):
        self.follows = stage

    def add_follower(self, stage):
        self.followers.append(stage)