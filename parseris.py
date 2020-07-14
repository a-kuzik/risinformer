class ParseRis:
    def __init__(self, data):
        self.data = data

    def ris_msg(self):
        type_msg = self.data["type"]
        return type_msg

    def ris_data_full(self):
        self.ris_data = self.data["data"]
        return self.ris_data

    def timestamp(self):
        timestamp = self.ris_data["timestamp"]
        return timestamp

    def peer(self):
        peer = self.ris_data["peer"]
        return peer

    def peer_asn(self):
        peer_asn = self.ris_data["peer_asn"]
        return peer_asn

    def peer_id(self):
        peer_id = self.ris_data["id"]
        return peer_id

    def host(self):
        host = self.ris_data["host"]
        return host

    def msg_type(self):
        msg_type = self.ris_data["type"]
        return msg_type

    def path(self):
        if "announcements" in self.ris_data:
            path = self.ris_data["path"]
            return path

    def community(self):
        if "announcements" in self.ris_data:
            community = self.ris_data["community"]
            return community

    def origin(self):
        if "announcements" in self.ris_data:
            origin = self.ris_data["origin"]
            return origin

    def nh(self):
        if "announcements" in self.ris_data:
            nh = self.ris_data["announcements"][0]["next_hop"]
            return nh

    def prefixes(self):
        if "announcements" in self.ris_data:
            prefixes = self.ris_data["announcements"][0]["prefixes"]
            return prefixes

    def withdrawals(self):
        if "withdrawals" in self.ris_data:
            withdrawals = self.ris_data["withdrawals"]
            return withdrawals
