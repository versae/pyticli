# -*- coding: utf-8 -*-


class BaseQueryLanguage(object):

    def __init__(self, states, states_count):
        self.states = states
        self.states_count = states_count
        self.temporals = ("always", "next")
        self.logics = ("&", "|", "==", "!=", "<", "<=", ">", "=>")
        self.arithmetics = ("+", "-", "*", "/", "%")
        self.opposites = {
            "==": "!=",
            "!=": "=",
            "<": ">",
            ">": "<",
            "<=": "=>",
            "=>": "<=",
        }

    def generate(self, verbose=False):
        raise NotImplemented("Subclasses must implemented this method.")
