
DUR = 1.2
SPLIT = 0.46
N_SCENES = 4
BURSTS = ['burst_a', 'burst_b', 'burst_c']

def _t():
    st = op('/project1/trans')['start'].eval()
    return max(0.0, min(1.0, (absTime.seconds - st) / DUR))

def _ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def _back(x):
    x = max(0.0, min(1.0, x))
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def k(scenes):
    cur = int(op('/project1/scene')['v'])
    prev = int(op('/project1/trans')['prev'])
    t = _t()
    inc, inp = cur in scenes, prev in scenes
    if inc and inp:
        return 1.0
    if inc:
        return 0.0 if t < SPLIT else _back((t - SPLIT) / (1 - SPLIT))
    if inp:
        return 1.0 - _ease(t / SPLIT) if t < SPLIT else 0.0
    return 0.0

def vis(scenes):
    return k(scenes) > 0.002

def _clear():
    for b in BURSTS:
        o = op('/project1/' + b + '/particle1')
        if o is not None:
            o.par.resetpulse.pulse()

def _burst(count):
    _clear()
    for b in BURSTS:
        o = op('/project1/' + b + '/particle1')
        if o is not None:
            o.par.birthcount = count
            o.par.birthpulse.pulse()

def begin():
    """Fist closed: old model shatters, nothing shown while fist is held."""
    sc = op('/project1/scene')
    cur = int(sc.par.value0)
    if cur < 0:
        return
    me.store('pending', (cur + 1) % N_SCENES)
    tr = op('/project1/trans')
    tr.par.value1 = cur
    tr.par.value0 = absTime.seconds
    sc.par.value0 = -1
    _shape(cur)
    _burst(24000)

def finish():
    """Fist opened: new model forms out of the particles."""
    sc = op('/project1/scene')
    if int(sc.par.value0) >= 0:
        return
    nxt = me.fetch('pending', 0)
    tr = op('/project1/trans')
    tr.par.value1 = -1
    tr.par.value0 = absTime.seconds
    sc.par.value0 = nxt
    _form(nxt)
    _clear()

def go(n=None):
    begin()
    run("op('/project1/trmod').module.finish()", delayFrames=30)


SHAPES = {0: ('forest2', 1.425, 0.12, 0.095, 1.0, -0.3192), 1: ('forest2', 1.425, 0.12, 0.095, 1.0, -0.3192),
          2: ('forest2', 1.425, 0.12, 0.095, 1.0, -0.3192), 3: ('ape', 0.0, 0.0, 0.012, 1.0, -0.0036)}
COLORS = {
    0: [(0.2, 0.75, 0.25), (0.55, 0.9, 0.2), (0.55, 0.32, 0.12)],
    1: [(1.0, 0.4, 0.05), (1.0, 0.7, 0.1), (0.3, 0.75, 0.2)],
    2: [(0.25, 0.18, 0.14), (1.0, 0.35, 0.05), (0.45, 0.25, 0.15)],
    3: [(1.0, 0.45, 0.1), (0.8, 0.3, 0.08), (0.95, 0.6, 0.2)],
}

def _shape(scene):
    name, cx, cz, kk, sy, base = SHAPES.get(scene, SHAPES[0])
    for i, b in enumerate(BURSTS):
        g = op('/project1/' + b)
        g.op('shape').par.file = project.folder + '/models/' + name + '_shape.obj'
        tr = g.op('shapex')
        tr.par.tx, tr.par.ty, tr.par.tz = -cx * kk, base, -cz * kk
        tr.par.scale = kk
        tr.par.sx, tr.par.sy, tr.par.sz = 1, sy, 1
        tr.par.ry = 90 if name == 'ape' else 0
        m = op('/project1/' + b + '_mat')
        m.par.colorr, m.par.colorg, m.par.colorb = COLORS.get(scene, COLORS[0])[i]



def _form(scene):
    name, cx, cz, kk, sy, base = SHAPES.get(scene, SHAPES[0])
    g = op('/project1/form')
    g.op('shape').par.file = project.folder + '/models/' + name + '_shape.obj'
    tr = g.op('shapex')
    tr.par.tx, tr.par.ty, tr.par.tz = -cx * kk, base, -cz * kk
    tr.par.scale = kk
    tr.par.sx, tr.par.sy, tr.par.sz = 1, sy, 1
    op('/project1/form/pform').par.resetpulse.pulse()
    op('/project1/form/pform').par.birthpulse.pulse()
    m = op('/project1/form_mat')
    m.par.colorr, m.par.colorg, m.par.colorb = COLORS.get(scene, COLORS[0])[0]


_orig_form = _form
def _form(scene):
    _orig_form(scene)
    op('/project1/form/shapex').par.ry = -90 if SHAPES.get(scene, SHAPES[0])[0] == 'ape' else 0

_orig_shape = _shape
def _shape(scene):
    _orig_shape(scene)
    for b in BURSTS:
        op('/project1/' + b + '/shapex').par.ry = -90 if SHAPES.get(scene, SHAPES[0])[0] == 'ape' else 0


FORM_COLORS = {
    0: ((0.3, 0.78, 0.28), (0.55, 0.9, 0.25)),
    1: ((0.3, 0.72, 0.25), (1.0, 0.42, 0.05)),   # green trees + fire
    2: ((0.28, 0.2, 0.15), (1.0, 0.35, 0.05)),   # charcoal + embers
    3: ((1.0, 0.48, 0.12), (0.85, 0.32, 0.08)),
}
_orig_form2 = _form
def _form(scene):
    _orig_form2(scene)
    a, b = FORM_COLORS.get(scene, FORM_COLORS[0])
    m = op('/project1/form_mat'); m.par.colorr, m.par.colorg, m.par.colorb = a
    m = op('/project1/form2_mat'); m.par.colorr, m.par.colorg, m.par.colorb = b


MORPH_TIME = 1.1
def pcol(i, c):
    st = op('/project1/trans')['start'].eval()
    t = max(0.0, min(1.0, (absTime.seconds - st) / MORPH_TIME))
    t = t * t * (3 - 2 * t)
    a = COLORS.get(me.fetch('from_scene', 0), COLORS[0])[i]
    b = COLORS.get(me.fetch('pending', 0), COLORS[0])[i]
    return a[c] + (b[c] - a[c]) * t

_orig_shape2 = _shape
def _shape(scene):
    _orig_shape2(scene)
    for i, b in enumerate(BURSTS):
        m = op('/project1/' + b + '_mat')
        for c, n in enumerate(('colorr', 'colorg', 'colorb')):
            par = getattr(m.par, n)
            par.expr = "op('/project1/trmod').module.pcol(%d, %d)" % (i, c)
            par.mode = ParMode.EXPRESSION

_orig_begin = begin
def begin():
    me.store('from_scene', int(op('/project1/scene').par.value0))
    _orig_begin()
