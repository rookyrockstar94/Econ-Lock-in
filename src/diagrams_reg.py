DIAS = {}
ORDER = []
def dia(id, title, topic, hl=False, steps=(), explain='', watch=''):
    def deco(fn):
        DIAS[id] = dict(id=id, title=title, topic=topic, hl=hl, steps=list(steps), explain=explain, watch=watch, svg=fn())
        ORDER.append(id)
        return fn
    return deco
