import time
ON, OFF = 0.45, 0.25    # gesture-model hysteresis (lower = more forgiving)
FRAMES_ON, FRAMES_OFF = 3, 4
COOLDOWN = 0.6

def _landmark_fist():
    """Fallback: left hand counts as a fist when all four fingertips are curled toward the wrist."""
    H = op('/project1/handexec').module
    n = op('/project1/null9'); hp = op('/project1/hand_tracking/helpers')
    right = H._right_hand(n, hp)
    for h in ('h1', 'h2'):
        if h == right:
            continue
        act = hp[f'{h}:hand_active']
        if act is None or act.eval() < 0.5:
            continue
        w = H._pt(n, h, 'wrist')
        if w is None:
            continue
        curled = 0
        for f in ('index_finger', 'middle_finger', 'ring_finger', 'pinky'):
            tip = H._pt(n, h, f + '_tip' if f != 'pinky' else 'pinky_tip')
            pip = H._pt(n, h, f + '_pip' if f != 'pinky' else 'pinky_pip')
            if tip and pip and H._d(tip, w) < H._d(pip, w) * 1.05:
                curled += 1
        return 1.0 if curled >= 3 else 0.0
    return 0.0

def onFrameStart(frame):
    if op('/project1/cubefilt')['show'].eval() < 0.3:   # cube closed -> ignore fists
        me.store('cnt', 0)
        return
    v = max(op('/project1/fistmax')[0].eval(), _landmark_fist())
    st = me.fetch('state', 'open'); cnt = me.fetch('cnt', 0); now = time.time()
    M = op('/project1/trmod').module
    if st == 'open':
        cnt = cnt + 1 if v > ON else 0
        if cnt >= FRAMES_ON and now - me.fetch('last', 0) > COOLDOWN:
            M.begin(); st = 'closed'; cnt = 0
    else:
        cnt = cnt + 1 if v < OFF else 0
        if cnt >= FRAMES_OFF:
            M.finish(); st = 'open'; cnt = 0; me.store('last', now)
    me.store('state', st); me.store('cnt', cnt)
    return
