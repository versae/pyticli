# -*- coding: utf-8 -*-
from languages import BaseQueryLanguage
from languages.gremlin import GremlinLanguage

import ast


class Program(object):

    def __init__(self, proposition):
        self.proposition = proposition
        self.temporals = ("always", "next")
        self.logics = ("&", "|", "==", "!=", "<", "<=", ">", ">=")
        self.arithmetics = ("+", "-", "*", "/", "%")
        self.opposites = {
            "==": "!=",
            "!=": "=",
            "<": ">",
            ">": "<",
            "<=": ">=",
            ">=": "<=",
        }
        self.stack = []
        self.states_count = 0
        self.states = {}
        self.always = {}
        self.next = {}
        self.parser()
        self.expand()

    def expand(self):
        # TODO: Fix "always" support
        # FIXME: self.next is not properly built.
        print self.next
        for key, value in self.next.iteritems():
            if isinstance(value, (list, tuple)):
                self.states[key] = []
                for item in value:
                    if isinstance(item, (list, tuple)):
                        self.states[key].append(["(", item, ")"])
                    else:
                        self.states[key].append(item)
            else:
                self.states[key] = value
#        for key, value in self.always.iteritems():
#            for i in xrange(key, self.states_count):
#                if i in self.states:
#                    self.states[i] = [value[1], value[0], self.states[i]]
#                else:
#                    self.states[i] = value[1]

    def query(self, language=None, verbose=False):
        if language:
            if isinstance(language, BaseQueryLanguage):
                query_language = BaseQueryLanguage(self.states,
                                                   self.states_count)
            else:
                raise NotImplemented("Language not implemented yet")
        else:
            query_language = GremlinLanguage(self.states, self.states_count)
        return query_language.generate(verbose=verbose)

    def parser(self, proposition=None):
        prop = proposition or self.proposition
        if not prop:
            return None
        prop = prop.replace("\n", "\\\n")
        expr = ast.parse(prop).body[0].value
        self.tree(expr)
        if len(self.next) > 0 and len(self.always) > 0:
            self.states_count = max(sorted(self.next.keys())[-1] + 1,
                                    sorted(self.always.keys())[-1] + 1)
        elif len(self.next) > 0:
            self.states_count = sorted(self.next.keys())[-1] + 1
        elif len(self.always) > 0:
            self.states_count = sorted(self.always.keys())[-1] + 1
        elif self.always:
            self.states_count = 1
        else:
            self.states_count = 0

    def tree(self, expr):
        if isinstance(expr, ast.BoolOp):
            self.stack.append(self.operator(expr.op))
            for value in expr.values:
                self.tree(value)
            if self.stack:
                self.stack.pop()
        if isinstance(expr, ast.Compare):
            for i, comparator in enumerate(expr.comparators):
                self.stack.append(self.operator(expr.ops[i]))
                self.tree(expr.left)
                self.tree(comparator)
                self.stack_reduce()
        elif isinstance(expr, ast.BinOp):
            self.stack.append(self.operator(expr.op))
            self.tree(expr.left)
            self.tree(expr.right)
            self.stack_reduce()
        elif isinstance(expr, ast.Call):
            self.stack.append(expr.func.id)
            for arg in expr.args:
                self.tree(arg)
        elif isinstance(expr, ast.Num):
            self.stack.append("""{#%s#}""" % expr.n)
        elif isinstance(expr, ast.Str):
            self.stack.append("""{$%s$}""" % expr.s)
        elif isinstance(expr, ast.Name):
            expr_lower = expr.id.lower()
            if expr_lower in ("true", "false"):
                self.stack.append("""{<%s>}""" % expr_lower)
            else:
                self.stack.append("""{{%s}}""" % expr.id)

    def stack_reduce(self):
        if len(self.stack) >= 3:
            left = self.stack[-2]
            right = self.stack[-1]
            if self.are_valid_comparators(left, right):
                operator = self.stack[-3]
                # if isinstance(right, (list, tuple)):
                #     right = ["(", right,")"]
                # if isinstance(left, (list, tuple)):
                #     left = ["(", left,")"]
                expr = (left, operator, right)
                if operator in self.arithmetics:
                    self.stack = self.stack[:-3]
                    self.stack.append(expr)
                    self.stack_reduce()
                elif operator in self.logics:
                    self.stack = self.stack[:-3]
                    always, next, logic = self.stack_split()
                    if always:
                        self.add_always(next, logic, expr)
                    else:
                        self.add_next(next, logic, expr)

    def are_valid_comparators(self, left, right):
        return ((self.is_atom(left) and self.is_atom(right))
                or (self.is_expr(left) and self.is_expr(right))
                or isinstance(left, (list, tuple))
                or isinstance(right, (list, tuple)))

    def stack_split(self):
        always_count = 0
        next_count = 0
        logic = None
        for item in reversed(self.stack):
            if item == "always":
                always_count += 1
            elif item == "next":
                next_count += 1
            elif item in self.logics:
                if always_count + next_count == 0:
                    pass
                else:
                    logic = item
                    break
        if not logic:
            logic = "&"
        if always_count or next_count:
            index = always_count + next_count
            self.stack = self.stack[:-index]
        return always_count, next_count, logic

    def add_always(self, from_state, logic, expr):
        if from_state not in self.always:
            self.always[from_state] = [logic, expr]
        else:
            current = self.always[from_state]
            self.always[from_state] = [current, logic, expr]

    def add_next(self, from_state, logic, expr):
        if from_state not in self.next:
            self.next[from_state] = [expr]
        else:
            current = self.next[from_state]
            self.next[from_state] = [current, logic, expr]

    def is_atom(self, value):
        return (isinstance(value, (int, float))
                or str(value).startswith("{"))

    def is_expr(self, value):
        return (filter(lambda x: x in value, self.logics + self.arithmetics))

    def operator(self, expr):
        op = None
        if isinstance(expr, (ast.And, ast.BitAnd)):
            op = "&"
        elif isinstance(expr, (ast.Or, ast.BitOr)):
            op = "|"
        elif isinstance(expr, (ast.Eq, ast.Is)):
            op = "=="
        elif isinstance(expr, (ast.NotEq, ast.IsNot)):
            op = "!="
        elif isinstance(expr, ast.Lt):
            op = "<"
        elif isinstance(expr, ast.LtE):
            op = "<="
        elif isinstance(expr, ast.Gt):
            op = ">"
        elif isinstance(expr, ast.GtE):
            op = ">="
        elif isinstance(expr, ast.Add):
            op = "+"
        elif isinstance(expr, ast.Sub):
            op = "-"
        elif isinstance(expr, ast.Mult):
            op = "*"
        elif isinstance(expr, ast.Div):
            op = "/"
        elif isinstance(expr, ast.Mod):
            op = "%"
        # elif isinstance(expr, (ast.Invert, ast.Not)):
        #    op = "not"
        # elif isinstance(expr, ast.RShift):
        #    op = "gets"
        # elif isinstance(expr, ast.LShift):
        #    op = "igets"
        #elif isinstance(expr, ast.FloorDiv):
        #    op = "equiv"
        else:
            raise SyntaxError("invalid syntax: %s" % expr)
        return op
