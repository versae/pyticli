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

    def generate(self):
        raise NotImplemented("Subclasses must implemented this method.")


class GremlinLanguage(BaseQueryLanguage):

    def generate(self, separator="\n      "):
        query = """g.v(0).outE{"initial"}"""
        for i in xrange(0, self.states_count):
            query = "%s%s" % (query, separator)
            if i in self.states:
                val = self.flatten(self.states[i])
                if i == 0:
                    query = "%s.inV{%s}.sideEffect{init=it.map(); " \
                            "prev%s=it.map()}.outE{\"next\"}" % (query, val, i)
                else:
                    query = "%s.inV{%s}.sideEffect{" \
                            "prev%s=it.map()}.outE{\"next\"}" % (query, val, i)
            else:
                if i == 0:
                    query = "%s.inV.sideEffect{init=it.map(); " \
                            "prev%s=it.map()}.outE{\"next\"}" % (query, i)
                else:
                    query = "%s.inV.sideEffect{" \
                            "prev%s=it.map()}.outE{\"next\"}" % (query, i)
        query = "%s%s.paths" % (query, separator)
        return query

    def flatten(self, expr):
        val = ""
        for excerpt in expr:
            if isinstance(excerpt, (list, tuple)):
                val += self.flatten(excerpt)
            else:
                val += self.get_representation(excerpt)
        return val

    def get_representation(self, val):
        representation = self.get_atom(val) or self.get_operator(val)
        return representation

    def get_operator(self, op):
        # The internal representation of operators in Pyticli is
        # exactly the same as in Gremlin
        return " %s " % op

    def get_atom(self, val):
        if len(val) >= 4:
            starts = val[:2]
            ends = val[-2:]
            if starts == "{<" and ends == ">}":
                # Boolean
                return val[2:-2]
            elif starts == "{#" and ends == "#}":
                # Numbers
                return val[2:-2]
            elif starts == "{$" and ends == "$}":
                # Strings
                return "\"%s\"" % val[2:-2]
            elif starts == "{{" and ends == "}}":
                # Current state
                return "it.\"%s\"" % val[2:-2]
            elif starts == "{%" and ends == "%}":
                # Previous state
                return "prev.\"%s\"" % val[2:-2]
            elif starts == "{{" and ends == "}}":
                # Initial state
                return "init.\"%s\"" % val[2:-2]
        return None
