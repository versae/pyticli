# -*- coding: utf-8 -*-
import ast


class Program(object):

    def __init__(self, proposition=None):
        self.proposition = proposition
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
        self.stack = []
        self.states = 0
        self.always = {}
        self.next = {}

    def abstract(self):
        self.parser()

    def parser(self, proposition=None):
        prop = proposition or self.proposition
        if not prop:
            return None
        prop = prop.replace("\n", "\\\n")
        expr = ast.parse(prop).body[0].value
        self.tree(expr)
        if self.next:
            self.states = sorted(self.next.keys())[-1] + 1
        print self.states, self.always, self.next

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
            self.stack.append(expr.n)
        elif isinstance(expr, ast.Str):
            self.stack.append("\"%s\"" % expr.s)
        elif isinstance(expr, ast.Name):
            self.stack.append("""{{%s}}""" % expr.id)

    def stack_reduce(self):
        print self.stack
        if len(self.stack) >= 3:
            left = self.stack[-1]
            right = self.stack[-2]
            if ((self.is_atom(left) and self.is_atom(right))
                or (self.is_expr(left) and self.is_expr(right))):
                operator = self.stack[-3]
                expr = "%s %s %s" % (right, operator, left)
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
        print self.stack

    def stack_split(self):
        always_count = 0
        next_count = 0
        logic = None
        print self.stack
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
            self.always[from_state] = ['(', current, ')', logic, expr]

    def add_next(self, from_state, logic, expr):
        if from_state not in self.next:
            self.next[from_state] = [expr]
        else:
            current = self.next[from_state]
            self.next[from_state] = ['(', current, ')', logic, expr]

    def is_atom(self, value):
        return (isinstance(value, (int, float))
                or str(value).startswith("{{"))

    def is_expr(self, value):
        return (filter(lambda x: x in value, self.logics + self.arithmetics))

    def operator(self, expr):
        if isinstance(expr, (ast.And, ast.BitAnd)):
            op =  "&"
        elif isinstance(expr, (ast.Or, ast.BitOr)):
            op =  "|"
        elif isinstance(expr, (ast.Eq, ast.Is)):
            op =  "=="
        elif isinstance(expr, (ast.NotEq, ast.IsNot)):
            op =  "!="
        elif isinstance(expr, ast.Lt):
            op =  "<"
        elif isinstance(expr, ast.LtE):
            op =  "<="
        elif isinstance(expr, ast.Gt):
            op =  ">"
        elif isinstance(expr, ast.GtE):
            op =  "=>"
        elif isinstance(expr, ast.Add):
            op =  "+"
        elif isinstance(expr, ast.Sub):
            op =  "-"
        elif isinstance(expr, ast.Mult):
            op =  "*"
        elif isinstance(expr, ast.Div):
            op =  "/"
        # elif isinstance(expr, (ast.Invert, ast.Not)):
        #    op =  "not"
        # elif isinstance(expr, ast.RShift):
        #    op =  "gets"
        # elif isinstance(expr, ast.LShift):
        #    op =  "igets"
        # elif isinstance(expr, ast.FloorDiv):
        #    op =  "equiv"
        else:
            print op
        return op
