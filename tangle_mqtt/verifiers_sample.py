from verifier_base import Verifier


class Verifier1(Verifier):
    def __init__(self, id, iota_host, seed, push=False):
        super(Verifier1, self).__init__(id, iota_host, seed, push)

    def verification(self, topic, value):
        # Write any logic here to verify value for topic.
        # What is returned from here will be saved in DB, with this class ID
        return True
