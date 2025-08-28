handlers = {}

def cmd(name: str):
    def wrap(fn):
        handlers[name] = fn
        return fn
    return wrap
