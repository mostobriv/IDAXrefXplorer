# -*- coding: utf-8 -*-

import ida_hexrays
import idaapi

TAB_SPACES = 4
BLOCK_TYPES = [
    "casm", "cblock", "cdo", "cexpr", "cfor", "cgoto", "cif", "creturn",
    "cswitch", "cwhile",
]


class FuncProcessor(object):

    def __init__(self, fcn):
        self.expression_pattern = None
        self.pattern = None
        self.replacer = None
        self.fcn = fcn
        self.curr_cblock = []
        self.DEBUG = False

    def process_inst_and_get_next(self, node, shift):
        #TODO: refactor return values
        opname = node.opname
        if opname == "block":
            return node.cblock
        elif opname == "expr":
            self.traverse_expr(node.cexpr, shift + 1)
            return []
        elif opname == "if":
            retval = []
            self.traverse_expr(node.cif.expr, shift + 1)
            if node.cif.ithen is not None:
                retval.append(node.cif.ithen)
            if node.cif.ielse is not None:
                retval.append(node.cif.ielse)
            return retval
        elif opname == "do":
            self.traverse_expr(node.cdo.expr, shift + 1)
            return [node.cdo.body]
        elif opname == "return":
            self.traverse_expr(node.creturn.expr, shift + 1)
            return []
        elif opname == "goto":
            if self.DEBUG:
                print "{}[+]Goto to label num {}".format(" " * ((shift + 1) * TAB_SPACES), node.cgoto.label_num)
        elif opname == "while":
            self.traverse_expr(node.cwhile.expr, shift + 1)
            return [node.cwhile.body]
        elif opname == "break":
            return []
        elif opname == "switch":
            self.traverse_expr(node.cswitch.expr, shift + 1)
            for i in node.cswitch.cases:
                self.process_case(i, shift + 1)
            return []
        elif opname == "for":
            self.traverse_expr(node.cfor.init, shift + 1)
            self.traverse_expr(node.cfor.expr, shift + 1)
            self.traverse_expr(node.cfor.step, shift + 1)
            return [node.cfor.body]
        elif opname == "empty":
            return None
        elif opname == "continue":
            return None
        elif opname == "asm":
            return None
        else:
            print "[-] Got unexpected opname {}".format(node.opname)
            raise Exception('Got unexpected opname {}'.format(node.opname))

    def process_case(self, cas, shift):
        if type(cas) != ida_hexrays.ccase_t:
            print "[-] Not an case!"
            return
        vals = []
        """TODO: When decompiling 32bit binaries values is not iterable"""
        #for i in cas.values:
        #    vals.append(i)
        #if not vals:
        #    vals = "default"
        if self.DEBUG:
            print "{}[+]Got case {} num {}".format(" " * (shift * TAB_SPACES), cas.opname, str(vals))
        fields = self.process_inst_and_get_next(cas, shift)
        if fields is None:
            return
        for i in fields:
            self.traverse_node(i, shift + 1)

    def traverse_function(self):
        fcnbody = self.fcn.body
        if type(fcnbody) != ida_hexrays.cinsn_t:
            print "[-] Function body not an instruction!"
            return
        self.traverse_node(fcnbody)

    def traverse_node(self, node, shift=0):
        fired = False
        if type(node) != ida_hexrays.cinsn_t:
            print "{}[-] Got not an instruction {}".format(" " * (shift * TAB_SPACES), node.opname)
            return
        if self.DEBUG:
            print "{}[+]Got instruction {}".format(" " * (shift * TAB_SPACES), node.opname)
        if node.opname == "block":
            self.curr_cblock.append(node)
            self.need_reanalyze_cblock = False
        if self.pattern is not None:
            if self.pattern.is_chain():
                if self.pattern.check_chain(node):
                    # TODO: possible inner hiding?
                    if self.pattern.is_finished():
                        print "[+] Found pattern chain {}".format(node.opname)
                        self.pattern.set_cblk_and_node(self.curr_cblock[-1], node)
                        self.pattern.replace_if_need()
                        if not self.pattern.is_chain_observer():
                            # This variable need to overcome situation with deleting instructions from
                            # cblock. I guess fields list are actually some kind of pointers
                            # which can be invalidated during cblock body replacement process
                            self.need_reanalyze_cblock = True
                    """If we don't modify anything in current node we can process next fields"""
                    if not self.pattern.is_chain_observer():
                        return
            else:
                if self.pattern.check(node):
                    print "[+] Found pattern!"
                    self.pattern.set_node(node)
                    if self.pattern.replace_if_need() == True:
                        return
        fields = self.process_inst_and_get_next(node, shift)
        if fields is None:
            return
        for i in fields:
            self.traverse_node(i, shift + 1)
            if node.opname == "block" and self.need_reanalyze_cblock:
                break
        if node.opname == "block":
            self.curr_cblock.pop()
            if self.pattern is not None:
                self.pattern.finish_cblock()
        if self.need_reanalyze_cblock:
            if self.DEBUG:
                print "{}[+] Reanalyzing cblock after replacement".format(" " * (shift * TAB_SPACES))
            self.traverse_node(node, shift)

    TWO_OP = [
        'asg', 'idx', 'sub', 'mul', 'add', 'land', 'lor', 'ult', 'ule', 'ugt',
        'uge', 'sle', 'slt', 'sgt', 'sge', 'eq', 'comma', 'sshr', 'ushr', 'bor',
        'asgushr', 'smod', 'xor', 'asgadd', 'asgsub', 'band', 'asgmul', 'asgbor',
        'asgband', 'ne', 'shl', 'fdiv', 'fmul', 'sdiv', 'udiv', 'asgshl',
        'asgmul', 'asgxor', 'fsub', 'asgsshr', 'asgsdiv', 'asgudiv', 'asgumod', 'asgsmod',
        'umod', 'fadd'
    ]

    ONE_OP = [
        'preinc', 'predec', 'lnot', 'ref', 'bnot', 'postinc', 'postdec', 'neg', 'fneg'
    ]

    def process_expr(self, exp, shift):
        opname = exp.opname
        if opname == "var":
            if self.DEBUG:
                print "{}[+] Varname: {}".format(" " * ((shift + 1) * TAB_SPACES), self.fcn.lvars[exp.v.idx].name)
        elif opname == "memptr":
            self.traverse_expr(exp.x, shift + 1)
            if self.DEBUG:
                print "{}[+] Offset: {}".format(" " * ((shift + 1) * TAB_SPACES), exp.m)
                print "{}[+] Size: {}".format(" " * ((shift + 1) * TAB_SPACES), exp.ptrsize)
        elif opname == "memref":
            self.traverse_expr(exp.x, shift + 1)
            if self.DEBUG:
                print "{}[+] Offset: {}".format(" " * ((shift + 1) * TAB_SPACES), exp.m)
        elif opname == "ptr":
            self.traverse_expr(exp.x, shift + 1)
            if self.DEBUG:
                print "{}[+] Size: {}".format(" " * ((shift + 1) * TAB_SPACES), exp.ptrsize)
        elif opname in FuncProcessor.TWO_OP:
            self.traverse_expr(exp.x, shift + 1)
            self.traverse_expr(exp.y, shift + 1)
        elif opname in FuncProcessor.ONE_OP:
            self.traverse_expr(exp.x, shift + 1)
        elif opname == "tern":
            self.traverse_expr(exp.x, shift + 1)
            self.traverse_expr(exp.y, shift + 1)
            self.traverse_expr(exp.z, shift + 1)
        elif opname == "call":
            self.traverse_expr(exp.x, shift + 1)
            for i in exp.a:
                self.traverse_args(i, shift + 1)
        elif opname == "helper":
            if self.DEBUG:
                print "{}[+] Helper: {}".format(" " * ((shift + 1) * TAB_SPACES), exp.helper)
        elif opname == "str":
            if self.DEBUG:
                print "{}[+] String: {}".format(" " * ((shift + 1) * TAB_SPACES), exp.string)
        elif opname == "obj":
            if self.DEBUG:
                print "{}[+] EA: {:x}".format(" " * ((shift + 1) * TAB_SPACES), exp.obj_ea)
        elif opname == "num":
            if self.DEBUG:
                print "{}[+] Number: {:x}".format(" " * ((shift + 1) * TAB_SPACES), exp.n._value)
        elif opname == "fnum":
            if self.DEBUG:
                print "{}[+] Float number {}".format(" "* ((shift+1) * TAB_SPACES), ["{:x}".format(x) for x in exp.fpc.fnum])
        elif opname == "cast":
            if self.DEBUG:
                print "{}[+] CastTo: {}".format(" " * ((shift + 1) * TAB_SPACES), exp.type.dstr())
            self.traverse_expr(exp.x, shift + 1)
        elif opname == "empty":
            pass
        elif opname == "sizeof":
            if self.DEBUG:
                print "{}[+] sizeof".format(" " * ((shift + 1) * TAB_SPACES))
            pass
        else:
            print "[-] Got unknown expr {}".format(opname)
            raise Exception('Got unknown expr {}'.format(opname))

    def traverse_args(self, arg, shift):
        if type(arg) != ida_hexrays.carg_t:
            print "{}[-] Got not an argument. Fail ;[".format(" " * (shift * TAB_SPACES))
            print type(arg)
        if self.DEBUG:
            print "{}[+] Got {} arg".format(" " * (shift * TAB_SPACES), arg.opname)
        if self.expression_pattern is not None:
            if self.expression_pattern.check(arg):
                print "[+] Found args pattern"
        self.process_expr(arg, shift)

    def traverse_expr(self, exp, shift):
        if type(exp) != ida_hexrays.cexpr_t:
            print "{}[-] Got not expression. Fail ;[".format(" " * (shift * TAB_SPACES))
            print type(exp)
        if self.DEBUG:
            print "{}[+] Got {} expr".format(" " * (shift * TAB_SPACES), exp.opname)
        if self.expression_pattern is not None:
            if self.expression_pattern.check(exp):
                print "[+] Found expr pattern"
        self.process_expr(exp, shift)
