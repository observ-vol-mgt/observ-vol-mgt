
class Stage:
    def __init__(self, stage_info):
        self.name = stage_info['name']
        self.type = stage_info['type']
        self.subtype = stage_info['subtype']
        self.input_data_fields = stage_info['input_data']
        self.output_data_fields = stage_info['output_data']
        self.config = stage_info['config']
        self.follows = []
        self.followers = []
        self.latest_output_data = None
        self.scheduled = False

    def set_follows(self, stage):
        self.follows.append(stage)

    def add_follower(self, stage):
        self.followers.append(stage)

    def set_latest_output_data(self, output_data):
        self.latest_output_data = output_data

    def set_scheduled(self):
        self.scheduled = True

    def clear_scheduled(self):
        self.scheduled = False