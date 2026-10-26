FINGERS = ['thumb_cmc','thumb_mcp','thumb_ip','thumb_tip',
 'index_finger_mcp','index_finger_pip','index_finger_dip','index_finger_tip',
 'middle_finger_mcp','middle_finger_pip','middle_finger_dip','middle_finger_tip',
 'ring_finger_mcp','ring_finger_pip','ring_finger_dip','ring_finger_tip',
 'pinky_mcp','pinky_pip','pinky_dip','pinky_tip']
NAMES = ['wrist'] + FINGERS
CHAINS = [[0,1,2,3,4],[0,5,6,7,8],[9,10,11,12],[13,14,15,16],[0,17,18,19,20],[5,9,13,17]]

def onCook(scriptOp):
    scriptOp.clear()
    n = op('/project1/null9'); hp = op('/project1/hand_tracking/helpers')
    lh = op('/project1/handexec').fetch('l_hand', None)
    for h in ('h1', 'h2'):
        if h == lh and op('/project1/cubectl')['show'].eval() > 0.5:
            continue
        a = hp[h + ':hand_active']
        if a is None or a.eval() < 0.5:
            continue
        pts = []
        for nm in NAMES:
            x = n[h + ':' + nm + ':x']; y = n[h + ':' + nm + ':y']
            if x is None or y is None:
                pts = []; break
            p = scriptOp.appendPoint()
            p.P = ((x.eval() - 0.5) * 4.1, (y.eval() - 0.5) * 2.3, 0.0)
            pts.append(p)
        if not pts:
            continue
        for ch in CHAINS:
            poly = scriptOp.appendPoly(len(ch), closed=False, addPoints=False)
            for k, idx in enumerate(ch):
                poly[k].point = pts[idx]
    return
