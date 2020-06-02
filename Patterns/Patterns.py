# -*- coding: utf-8 -*-
import traversal


class Pattern(object):


    def __init__(self):
        pass

    def check(self, expr, ctx):
        pass


class AnyPattern(Pattern):

    def check(self, expr, ctx):
        return True


class NoPattern(Pattern):

    def check(self, expr, ctx):
        return False

class OrPattern(Pattern):

    def __init__(self, *args):
        self.children = args

    def check(self, expr, ctx):
        return any([c.check(expr, ctx) for c in self.children])


class BinaryExpr(Pattern):

    def __init__(self, left, right, simmetric=False):
        super(BinaryExpr, self).__init__()
        self.left = left
        self.right = right
        self.simmetric = simmetric

    def check(self, expr, ctx):
        left_x_right_y = self.left.check(expr.x, ctx) and self.right.check(expr.y, ctx)
        if self.simmetric:
            left_y_right_x = self.left.check(expr.y, ctx) and self.right.check(expr.x, ctx)
            return left_x_right_y or left_y_right_x
        else:
            return left_x_right_y


class UnaryExpr(Pattern):

    def __init__(self, operand):
        super(UnaryExpr, self).__init__()
        self.op = operand

    def check(self, expr, ctx):
        return self.op.check(expr, ctx)


class ChainPattern(object):

    def __init__(self, array, make_mod=True):
        self._list = array
        self.pos = 0
        self.make_mod = make_mod

    def check(self, inst, ctx):
        ret_val = self._list[self.pos].check(inst, ctx)
        if ret_val:
            if self.pos + 1 == len(self._list):
                ctx.save_cnt(self.pos + 1)
                self.pos = 0
            else:
                self.pos += 1
        else:
            self.pos = 0
        return ret_val


class DeepExprPattern(object):

    def __init__(self, expression):
        self._expr = expression

    def check(self, inst, ctx):
        if self._expr.check(inst, ctx):
            return True
        exprs = traversal.get_inner_expr_to_check(inst)
        for i in exprs:
            if self._expr.check(i, ctx):
                return True
        return False

class GreedyPattern(object):
    """This class matches several instructions ended by stopper"""

    def __init__(self, stopper):
        self.stopper = stopper

    def check_greedy(self, inst, ctx):
        if self.stopper.check(inst, ctx):
            return True
        else:
            return False
