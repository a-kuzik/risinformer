import json
import time


class ReadInTime:
    def __init__(self, time, file):
        self.time = time
        self.file = file

    def read(self):
        while True:
            if time.strftime("%H.%M.%S", time.localtime()) == self.time:
                with open(self.file) as json_file:
                    prefixes = json.load(json_file)
                    print("Timestamp")
                    return prefixes
