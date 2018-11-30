import IDAXrefXplorer.actions as actions

class IDAXrefXplorer(idaapi.plugin_t):
    flags = 0
    comment = "Advanced XREF exploring tool"
    help = ""
    wanted_name = "IDAXrefXplorer"
    wanted_hotkey = ""


    def init(self):
        if idaapi.init_hexrays_plugin():
            idaapi.msg('IDAXrefXplorer: [ERROR] error during init_hexrays_plugin [ERROR]\n')
            return idaapi.PLUGIN_KEEP


        return idaapi.PLUGIN_SKIP

    def run(self, arg):
        pass

    def term(self):
        #idaapi.remove_hexrays_callback(/* callback */)




def PLUGIN_ENTRY():
    return IDAXrefXplorer()
