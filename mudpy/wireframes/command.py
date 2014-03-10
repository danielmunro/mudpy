from .. import wireframe

class Command(wireframe.Blueprint):

    yaml_tag = "command"

    def __init__(self, publisher):
        self.name = ""
        self.action = ""
        self.required = []
        self.messages = {}
        self.dispatches = {}
        self.post_dispatches = {}
        self.execute = []
        self.publisher = publisher

    def run(self, actor, args):
        """Takes an actor and input arguments and runs the command."""

        handled = self._required_chain(actor)
        if handled:
            return

        self._execute_chain(actor, args)

    def _execute_chain(self, actor, args):
        handled = actor.fire('action', self.action)
        if not handled:
            actor.last_command = self
            handled = self._fire_chain(actor, self.dispatches)
            if handled:
                return
            for e in self.execute:
                eval("actor."+e)
            self._fire_chain(actor, self.post_dispatches)

    def _required_chain(self, actor):
        for req in self.required:
            req_value = req['value'] if 'value' in req else True
            req_prop = req['property']
            attr = eval('actor.'+req_prop)
            if self._did_fail(req_value, attr):
                self._fail(actor, req_value, req['fail'] if 'fail' in req else '')
                return True

    def _fire_chain(self, actor, dispatches):
        for d in dispatches:
            msg = ", '"+d['message'] % actor+"'" if "message" in d else ""
            call = d['object']+".fire('"+d['event']+"', actor"+msg+")"
            handled = eval("actor."+call)
            if handled:
                return True

    def _did_fail(self, req_value, attr):
        if isinstance(req_value, bool):
            return (req_value and not attr) or (not req_value and attr)
        else:
            return not attr in req_value
    
    def _fail(self, actor, req_value, fail):
        if '%s' in fail:
            if isinstance(req_value, list):
                fail_val = " or ".join(req_value)
            else:
                fail_val = req_value
            actor.notify((fail) % fail_val)
        elif fail:
            actor.notify(fail)
    
    def __str__(self):
        return self.name
