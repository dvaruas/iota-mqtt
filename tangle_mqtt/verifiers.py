from verifier_base import Verifier


class Verifier1(Verifier):
    def __init__(self, id, iota_host, seed, push=False):
        super(Verifier1, self).__init__(id, iota_host, seed, push)

    def verification(self, topic, value):
        _ans = False
        try:
            _ans = (value % 2 == 0)
        except:
            pass
        return str(_ans)

class Verifier2(Verifier):
    def __init__(self, id, iota_host, seed, push=False):
        super(Verifier2, self).__init__(id, iota_host, seed, push)

    def verification(self, topic, value):
        _ans = False
        try:
            _ans = (value % 3 == 0)
        except:
            pass
        return str(_ans)

def Verifier3(Verifier):
    def __init__(self, id, iota_host, seed, push=False):
        super(Verifier3, self).__init__(id, iota_host, seed, push)

    def verification(self, topic, value):
        _ans = False
        try:
            _ans = (value % 5 == 0)
        except:
            pass
        return str(_ans)
