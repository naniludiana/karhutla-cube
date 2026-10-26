import math

ASPECT = 16 / 9
SIZE_K = 1.35      # cube size relative to thumb-index distance
SWAP_HANDS = True # set True if MediaPipe left/right labels are mirrored

def _ch(n, name):
    c = n[name]
    return None if c is None else c.eval()

def _pt(n, h, name):
    x = _ch(n, f'{h}:{name}:x')
    y = _ch(n, f'{h}:{name}:y')
    if x is None or y is None:
        return None
    return (x * ASPECT, y)

def _d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def _right_hand(n, hp):
    lh = me.fetch('l_hand', None)
    if lh:
        return lh
    return _right_hand_label(n, hp)

def _right_hand_label(n, hp):
    best = None
    for h in ('h1', 'h2'):
        act = hp[f'{h}:hand_active']
        if act is None or act.eval() < 0.5:
            continue
        r = _ch(n, f'{h}:Rightness') or 0
        l = _ch(n, f'{h}:Leftness') or 0
        if SWAP_HANDS:
            r, l = l, r
        if r > l:
            best = h
    return best

def _is_L(n, h):
    w = _pt(n, h, 'wrist')
    pts = {}
    for f in ('thumb_tip', 'index_finger_tip', 'index_finger_pip', 'index_finger_mcp',
              'middle_finger_tip', 'middle_finger_pip', 'middle_finger_mcp',
              'ring_finger_tip', 'ring_finger_pip', 'pinky_tip', 'pinky_pip'):
        pts[f] = _pt(n, h, f)
    if w is None or any(v is None for v in pts.values()):
        return False, None, None
    palm = _d(w, pts['middle_finger_mcp']) + 1e-6
    def ext(tip, pip):
        return _d(pts[tip], w) > _d(pts[pip], w) * 1.12
    index_ext = ext('index_finger_tip', 'index_finger_pip')
    curled = (not ext('middle_finger_tip', 'middle_finger_pip')) and              (not ext('ring_finger_tip', 'ring_finger_pip')) and              (not ext('pinky_tip', 'pinky_pip'))
    thumb_out = _d(pts['thumb_tip'], pts['index_finger_mcp']) > 0.55 * palm
    return (index_ext and thumb_out and curled), pts['thumb_tip'], pts['index_finger_tip']

def onFrameStart(frame):
    op('/project1/skel/bones').cook(force=True)
    _r = op('/project1/recorder')
    if _r is not None and _r.par.record.eval():
        _r.cook(force=True)
    n = op('/project1/null9')
    hp = op('/project1/hand_tracking/helpers')
    ctl = op('/project1/cubectl')
    # _ANY_HAND_L: whichever hand makes the L controls the cube (works with any camera / mirroring)
    h = None; isL = False; t = i = None
    for cand in ('h1', 'h2'):
        act = hp[f'{cand}:hand_active']
        if act is None or act.eval() < 0.5:
            continue
        ok, tt, ii = _is_L(n, cand)
        if ok:
            h, isL, t, i = cand, ok, tt, ii
            break
    if h:
        me.store('l_hand', h)
    # L_HOLD_FRAMES: the L must be held steadily (and fingers spread wide enough) before the cube opens
    L_HOLD_FRAMES = 4
    MIN_SPREAD = 0.06
    if h and t is not None and i is not None and _d(t, i) / ASPECT < MIN_SPREAD:
        h = None
    cnt = me.fetch('l_cnt', 0)
    cnt = cnt + 1 if h else 0
    me.store('l_cnt', cnt)
    if me.fetch('was_show', 0) == 0 and cnt < L_HOLD_FRAMES:
        h = None
    show = 0
    if h:
        if isL:
            mx = (t[0] + i[0]) / 2 / ASPECT
            my = (t[1] + i[1]) / 2
            dist = _d(t, i) / ASPECT
            ctl.par.value0 = (mx - 0.5) * 4.1
            ctl.par.value1 = (0.5 - my) * 2.3
            ctl.par.value2 = dist * 4.1 * SIZE_K
            ang = math.degrees(math.atan2(i[0] - t[0], -(i[1] - t[1])))
            ctl.par.value4 = max(-30, min(30, -(ang - 45) * 0.5))
            show = 1
    ctl.par.value3 = show
    _reset_check(show)
    return

RESET_AFTER = 0.5   # seconds the L must be gone before the story restarts

def _reset_check(show):
    import time
    now = time.time()
    was = me.fetch('was_show', 0)
    if show and not was:
        gone = now - me.fetch('off_since', now)
        if gone >= RESET_AFTER:
            M = op('/project1/trmod').module
            M._clear()
            tr = op('/project1/trans')
            tr.par.value1 = -1
            tr.par.value0 = absTime.seconds - M.DUR * M.SPLIT
            op('/project1/scene').par.value0 = 0
            op('/project1/fistsm').store('state', 'open')
    if not show and was:
        me.store('off_since', now)
        M2 = op('/project1/trmod').module
        M2._clear()
    me.store('was_show', show)

