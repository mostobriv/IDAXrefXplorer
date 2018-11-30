import idaapi
import idc


def register(action, *args):
    idaapi.register_action(
        idaapi.action_desc_t(
            action.name,
            action.description,
            action(*args),
            action.hotkey
        )
    )



#Example
'''
class Constantin(idaapi.action_handler_t):
    name = "MakeIdaGreatAgain:Constantin"
    description = "Assign/remove const attribute to/from global variable"
    hotkey = "Shift+C"

    def __init__(self):
        idaapi.action_handler_t.__init__(self)


    def activate(self, ctx):
        hx_view = idaapi.get_widget_vdui(ctx.widget)
'''
