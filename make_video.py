#!/usr/bin/env python3
"""
Kismoe Business Services — Narrated Intro Video Generator v2
Resolution: 1280x720, 30fps, ~90 seconds
Voice: Microsoft Edge Neural TTS (en-US-JennyNeural) — natural human voice
"""

import os, subprocess, math, asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
import cv2

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
W, H    = 1280, 720
FPS     = 30
DURATIONS = [8, 10, 10, 12, 12, 12, 12, 10]   # seconds per slide

BG    = (10, 15, 30)
BLUE  = (59, 130, 246)
TEAL  = (20, 184, 166)
PURP  = (139, 92, 246)
WHITE = (255, 255, 255)
GRAY  = (148, 163, 184)
DARK  = (18, 26, 52)
CARD  = (22, 32, 62)

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

NARRATIONS = [
    "Welcome to Kismoe Business Services — your AI-powered business operating system. "
    "One platform to launch, manage, automate, protect, grow, and scale your business.",

    "Running a business means juggling legal compliance, financial planning, HR workflows, "
    "marketing, technology, and customer operations all at once. Most businesses waste "
    "thousands of dollars and countless hours doing this manually.",

    "Kismoe brings it all together. Eight core service pillars — Legal and Compliance, "
    "Finance and Operations, AI Automation, HR and Workforce, Marketing and Sales, "
    "Business Protection, Website Building, and the Expert Marketplace.",

    "Getting started is simple. Click Start My Business Journey and complete a quick "
    "five-step onboarding. Tell Kismoe about your business name, industry, stage, team "
    "size, revenue, and biggest challenges.",

    "Kismoe instantly generates your Business Health Score — nine dimensions scored from "
    "zero to one hundred. Legal compliance, financial readiness, operations, marketing, "
    "technology, HR, cybersecurity, and overall growth readiness.",

    "The AI chat assistant is your always-on business advisor. Ask about business "
    "formation, legal documents, marketing strategy, hiring, or automation. "
    "Powered by advanced AI, it gives you expert-level guidance in seconds.",

    "Browse eight service pillars and click any card to generate deliverables instantly. "
    "The document generator produces ready-to-use templates — NDAs, operating agreements, "
    "privacy policies, employment contracts, invoices, and more.",

    "Kismoe is free to start. Sign in with your email, complete your business profile, "
    "and get your personalized health score and action plan in minutes. "
    "Take control of your business today.",
]

FFMPEG      = imageio_ffmpeg.get_ffmpeg_exe()
TMP         = "/tmp/kismoe_v2"
VOICE_MODEL = "/tmp/piper_voice/en_US-lessac-high.onnx"
VOICE_CFG   = "/tmp/piper_voice/en_US-lessac-high.onnx.json"
os.makedirs(TMP, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Font + drawing helpers
# ─────────────────────────────────────────────────────────────────────────────
def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

def tsz(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]

def cx_text(draw, text, y, fnt, color=WHITE):
    """Draw text horizontally centered at y."""
    tw, th = tsz(draw, text, fnt)
    x = (W - tw) // 2
    draw.text((x + 2, y + 2), text, font=fnt, fill=(0, 0, 0, 80))
    draw.text((x, y), text, font=fnt, fill=color)
    return th

def accent(draw, y, color=BLUE, h=3):
    draw.rectangle([60, y, W - 60, y + h], fill=color)

def grad_bg(top=(10,15,30), bot=(4,6,16)):
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for r in range(H):
        t = r / H
        for c in range(3):
            arr[r, :, c] = int(top[c]*(1-t) + bot[c]*t)
    return Image.fromarray(arr, "RGB")

def wrap_text(draw, text, fnt, max_w):
    """Return list of lines that fit within max_w pixels."""
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if tsz(draw, test, fnt)[0] > max_w:
            if line:
                lines.append(line)
            line = w
        else:
            line = test
    if line:
        lines.append(line)
    return lines

def draw_card(draw, x0, y0, x1, y1, accent_color=None, radius=14):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=CARD)
    if accent_color:
        draw.rounded_rectangle([x0, y0, x0 + 5, y1], radius=4, fill=accent_color)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Brand Intro
# ─────────────────────────────────────────────────────────────────────────────
def make_slide1():
    img = grad_bg((12, 18, 38), (5, 8, 20))
    draw = ImageDraw.Draw(img)

    # Soft glow blobs
    for (bx, by, br, bc) in [(220, 160, 180, (25,45,90)), (1060, 560, 200, (45,15,75))]:
        blob = Image.new("RGBA", (W, H), (0,0,0,0))
        bd   = ImageDraw.Draw(blob)
        bd.ellipse([bx-br, by-br, bx+br, by+br], fill=bc+(50,))
        img  = Image.alpha_composite(img.convert("RGBA"), blob).convert("RGB")
    draw = ImageDraw.Draw(img)

    # "K" badge circle
    bcx, bcy, br = W//2, 200, 80
    draw.ellipse([bcx-br, bcy-br, bcx+br, bcy+br], fill=(28,38,78))
    draw.ellipse([bcx-br+3, bcy-br+3, bcx+br-3, bcy+br-3], outline=BLUE, width=3)
    fK = font(88)
    tw, th = tsz(draw, "K", fK)
    draw.text((bcx - tw//2 + 2, bcy - th//2 + 2), "K", font=fK, fill=(10,15,40))
    draw.text((bcx - tw//2,     bcy - th//2),     "K", font=fK, fill=BLUE)

    # Brand name
    cx_text(draw, "KISMOE", 300, font(74), WHITE)
    cx_text(draw, "Business Services", 390, font(28, False), TEAL)
    cx_text(draw, "AI-Powered Business Operating System", 440, font(20, False), GRAY)

    # Double accent
    accent(draw, 500, BLUE, 3)
    accent(draw, 504, PURP, 3)

    cx_text(draw, "Launch  ·  Manage  ·  Automate  ·  Protect  ·  Grow  ·  Scale",
            525, font(18, False), GRAY)

    # Bottom domain
    cx_text(draw, "ksg93rd.github.io/ksg93rd", 620, font(16, False), (80,100,160))

    return img

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — The Challenge
# ─────────────────────────────────────────────────────────────────────────────
def make_slide2():
    img = grad_bg()
    draw = ImageDraw.Draw(img)

    cx_text(draw, "The Business Challenge", 30, font(44), WHITE)
    accent(draw, 92, BLUE, 2)

    problems = [
        ("Legal Chaos",       "Compliance, contracts & formation are overwhelming",           BLUE),
        ("Finance Confusion", "Budgeting, cash flow & taxes feel out of control",              TEAL),
        ("No Automation",     "Manual processes eat hours every single day",                   PURP),
        ("Manual HR",         "Hiring, payroll & onboarding are all disconnected",             (234,179,8)),
    ]

    # 4 cards across full width with margin
    margin = 50
    gap    = 16
    card_w = (W - 2*margin - 3*gap) // 4   # ~279px
    card_h = 200
    card_y = 120

    for i, (title, desc, color) in enumerate(problems):
        x0 = margin + i*(card_w + gap)
        x1 = x0 + card_w
        y0 = card_y
        y1 = y0 + card_h
        draw.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=CARD)
        # top accent bar
        draw.rounded_rectangle([x0, y0, x1, y0+5], radius=4, fill=color)

        # Number badge
        draw.ellipse([x0+16, y0+18, x0+50, y0+52], fill=color)
        fn = font(18)
        nw, nh = tsz(draw, str(i+1), fn)
        draw.text((x0+33 - nw//2, y0+35 - nh//2), str(i+1), font=fn, fill=WHITE)

        # Title
        ft = font(17)
        draw.text((x0+14, y0+62), title, font=ft, fill=WHITE)

        # Desc word-wrapped
        fd  = font(13, False)
        lines = wrap_text(draw, desc, fd, card_w - 28)
        for li, ln in enumerate(lines):
            draw.text((x0+14, y0+92 + li*22), ln, font=fd, fill=GRAY)

    # Bottom message
    cx_text(draw, "Most businesses waste thousands of dollars doing this manually.",
            365, font(20, False), (210,210,210))
    cx_text(draw, "There is a smarter way.", 405, font(22), TEAL)

    # Stats row
    stats = [("$47K", "Avg annual waste"), ("23 hrs", "Lost per week"), ("68%", "Businesses fail yr 5")]
    sw = 280
    total_sw = len(stats)*sw + (len(stats)-1)*20
    sx = (W - total_sw) // 2
    sy = 460
    for i, (val, lbl) in enumerate(stats):
        bx = sx + i*(sw+20)
        draw.rounded_rectangle([bx, sy, bx+sw, sy+90], radius=12, fill=(28,38,72))
        fv = font(32)
        vw, _ = tsz(draw, val, fv)
        draw.text((bx + (sw-vw)//2, sy+10), val, font=fv, fill=BLUE)
        fl = font(13, False)
        lw, _ = tsz(draw, lbl, fl)
        draw.text((bx + (sw-lw)//2, sy+55), lbl, font=fl, fill=GRAY)

    accent(draw, 600, TEAL, 2)
    cx_text(draw, "Kismoe solves all of this — in one place.", 618, font(20, False), WHITE)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — 8 Pillars Hub
# ─────────────────────────────────────────────────────────────────────────────
def make_slide3():
    img = grad_bg()
    draw = ImageDraw.Draw(img)

    cx_text(draw, "One Platform. Eight Pillars.", 28, font(44), WHITE)
    accent(draw, 90, TEAL, 2)

    pillars = [
        ("Legal & Compliance",   BLUE),
        ("Finance & Operations", TEAL),
        ("AI & Automation",      PURP),
        ("HR & Workforce",       (234,179,8)),
        ("Marketing & Sales",    (239,68,68)),
        ("Business Protection",  (16,185,129)),
        ("Website Builder",      (14,165,233)),
        ("Expert Marketplace",   (249,115,22)),
    ]

    hub_cx, hub_cy = W//2, 400
    hub_r   = 62
    spoke_r = 240   # distance from hub center to pillar node center
    node_r  = 50    # pillar node radius

    # Hub circle
    draw.ellipse([hub_cx-hub_r, hub_cy-hub_r, hub_cx+hub_r, hub_cy+hub_r],
                 fill=(28,42,90), outline=TEAL, width=3)
    fhub1 = font(15)
    hw1, hh1 = tsz(draw, "Kismoe", fhub1)
    draw.text((hub_cx - hw1//2, hub_cy - 20), "Kismoe", font=fhub1, fill=TEAL)
    fhub2 = font(20)
    hw2, hh2 = tsz(draw, "AI", fhub2)
    draw.text((hub_cx - hw2//2, hub_cy + 4), "AI", font=fhub2, fill=WHITE)

    n = len(pillars)
    for i, (name, color) in enumerate(pillars):
        angle = math.radians(-90 + i * 360 / n)
        px = int(hub_cx + spoke_r * math.cos(angle))
        py = int(hub_cy + spoke_r * math.sin(angle))

        # Spoke line (from hub edge to node edge)
        lx0 = int(hub_cx + hub_r * math.cos(angle))
        ly0 = int(hub_cy + hub_r * math.sin(angle))
        lx1 = int(hub_cx + (spoke_r - node_r) * math.cos(angle))
        ly1 = int(hub_cy + (spoke_r - node_r) * math.sin(angle))
        draw.line([(lx0, ly0), (lx1, ly1)], fill=color, width=2)

        # Node
        draw.ellipse([px-node_r, py-node_r, px+node_r, py+node_r],
                     fill=(20,30,60), outline=color, width=2)

        # Pillar number inside node
        fn_num = font(16)
        nw, nh = tsz(draw, str(i+1), fn_num)
        draw.text((px - nw//2, py - nh//2), str(i+1), font=fn_num, fill=color)

        # Name label OUTSIDE node (avoid overlap)
        fn_lbl = font(12, False)
        # Determine label position based on angle quadrant
        label_dist = node_r + 14
        lbx = int(hub_cx + (spoke_r + label_dist) * math.cos(angle))
        lby = int(hub_cy + (spoke_r + label_dist) * math.sin(angle))

        # Split long names to 2 lines
        words = name.split()
        if len(words) > 2:
            mid = len(words)//2
            lns = [" ".join(words[:mid]), " ".join(words[mid:])]
        else:
            lns = [name]

        total_lbl_h = len(lns) * 16
        for li, ln in enumerate(lns):
            lw, lh = tsz(draw, ln, fn_lbl)
            draw.text((lbx - lw//2, lby - total_lbl_h//2 + li*17), ln, font=fn_lbl, fill=WHITE)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — Onboarding
# ─────────────────────────────────────────────────────────────────────────────
def make_slide4():
    img = grad_bg()
    draw = ImageDraw.Draw(img)

    cx_text(draw, "Get Started in Minutes", 28, font(44), WHITE)
    accent(draw, 90, BLUE, 2)

    # CTA Button
    btn_w, btn_h = 460, 54
    bx = (W - btn_w)//2
    draw.rounded_rectangle([bx, 114, bx+btn_w, 114+btn_h], radius=27, fill=TEAL)
    fBtn = font(20)
    btxt = "Start My Business Journey"
    bw, bh = tsz(draw, btxt, fBtn)
    draw.text((W//2 - bw//2, 114 + (btn_h-bh)//2), btxt, font=fBtn, fill=WHITE)

    # Step circles
    steps = ["Business Info", "Stage & Size", "Revenue", "Challenges", "Your Score"]
    n     = len(steps)
    sr    = 26
    spacing = (W - 120) // (n - 1)
    for i, step in enumerate(steps):
        cx_ = 60 + i * spacing
        active = (i == 0)
        fill   = BLUE if active else (32,44,80)
        draw.ellipse([cx_-sr, 196-sr, cx_+sr, 196+sr], fill=fill, outline=BLUE, width=2)
        fnum = font(16)
        nw, nh = tsz(draw, str(i+1), fnum)
        draw.text((cx_-nw//2, 196-nh//2), str(i+1), font=fnum, fill=WHITE)
        # connector
        if i < n-1:
            draw.rectangle([cx_+sr, 194, cx_+spacing-sr, 198], fill=(32,44,80))
        # label below
        fl = font(11, bold=active)
        lw, _ = tsz(draw, step, fl)
        draw.text((cx_-lw//2, 196+sr+6), step, font=fl, fill=WHITE if active else GRAY)

    # Mock form card
    fx, fy = 200, 270
    fw, fh = 880, 310
    draw.rounded_rectangle([fx, fy, fx+fw, fy+fh], radius=16, fill=DARK)
    draw.rounded_rectangle([fx, fy, fx+fw, fy+5], radius=4, fill=BLUE)

    fields = [
        ("Business Name",   "Acme Corp LLC"),
        ("Industry",        "Technology / SaaS"),
        ("Business Stage",  "Growth Stage  (1–3 years)"),
        ("Team Size",       "5–10 employees"),
    ]
    fL = font(13, False)
    fV = font(15)
    cols = 2
    field_w = (fw - 80) // cols
    for fi_, (label, val) in enumerate(fields):
        col = fi_ % cols
        row = fi_ // cols
        lx  = fx + 30 + col*(field_w + 20)
        ly  = fy + 28 + row*130
        draw.text((lx, ly), label, font=fL, fill=GRAY)
        draw.rounded_rectangle([lx, ly+22, lx+field_w-10, ly+58], radius=8, fill=(28,40,80))
        draw.text((lx+14, ly+30), val, font=fV, fill=WHITE)

    # Bottom
    cx_text(draw, "Takes less than 3 minutes  ·  No credit card required",
            628, font(18, False), GRAY)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — Health Score
# ─────────────────────────────────────────────────────────────────────────────
def make_slide5():
    img = grad_bg()
    draw = ImageDraw.Draw(img)

    cx_text(draw, "Your Business Health Score", 26, font(44), WHITE)
    accent(draw, 88, PURP, 2)

    scores = [
        ("Legal",       74, BLUE),
        ("Finance",     45, (239,68,68)),
        ("Operations",  88, TEAL),
        ("Marketing",   62, (249,115,22)),
        ("Technology",  55, PURP),
        ("HR",          79, (16,185,129)),
        ("Cybersec",    38, (239,68,68)),
        ("Growth",      91, TEAL),
        ("Overall",     67, BLUE),
    ]

    cols, rows = 3, 3
    cw = 370
    ch = 140
    pad_x = (W - cols*cw - (cols-1)*14) // 2
    pad_y = 108

    for idx, (name, score, color) in enumerate(scores):
        col = idx % cols
        row = idx // cols
        x0  = pad_x + col*(cw+14)
        y0  = pad_y + row*(ch+12)
        x1, y1 = x0+cw, y0+ch

        draw.rounded_rectangle([x0,y0,x1,y1], radius=12, fill=DARK)

        # Arc ring
        rcx, rcy, rr = x0+58, y0+ch//2, 36
        draw.arc([rcx-rr, rcy-rr, rcx+rr, rcy+rr], 0, 360, fill=(40,55,90), width=7)
        arc_end = int(360*score/100) - 90
        if arc_end > -90:
            draw.arc([rcx-rr, rcy-rr, rcx+rr, rcy+rr], -90, arc_end, fill=color, width=7)
        fs = font(20)
        sw_, sh_ = tsz(draw, str(score), fs)
        draw.text((rcx-sw_//2, rcy-sh_//2), str(score), font=fs, fill=WHITE)

        # Name
        fn = font(18)
        draw.text((x0+106, y0+18), name, font=fn, fill=WHITE)

        # Status
        if score >= 70:
            status, sc_ = "Strong", TEAL
        elif score >= 50:
            status, sc_ = "Developing", (249,115,22)
        else:
            status, sc_ = "Critical", (239,68,68)
        draw.text((x0+106, y0+46), status, font=font(13, False), fill=sc_)

        # Progress bar
        bar_x, bar_y = x0+106, y0+72
        bar_w = cw - 126
        draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+10], radius=5, fill=(40,55,90))
        fill_w = max(4, int(bar_w*score/100))
        draw.rounded_rectangle([bar_x, bar_y, bar_x+fill_w, bar_y+10], radius=5, fill=color)

        # Score label
        draw.text((bar_x, bar_y+16), f"{score}/100", font=font(11, False), fill=GRAY)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — AI Chat
# ─────────────────────────────────────────────────────────────────────────────
def make_slide6():
    img = grad_bg()
    draw = ImageDraw.Draw(img)

    cx_text(draw, "AI Chat Assistant — Always On", 26, font(44), WHITE)
    accent(draw, 88, TEAL, 2)

    # Chat window
    cw_x, cw_y = 80, 108
    cw_w, cw_h = 1120, 545
    draw.rounded_rectangle([cw_x, cw_y, cw_x+cw_w, cw_y+cw_h], radius=16, fill=(14,20,44))
    # title bar
    draw.rounded_rectangle([cw_x, cw_y, cw_x+cw_w, cw_y+46], radius=16, fill=(22,32,72))
    draw.rounded_rectangle([cw_x, cw_y+30, cw_x+cw_w, cw_y+46], radius=0, fill=(22,32,72))
    fbar = font(15)
    draw.text((cw_x+20, cw_y+14), "Kismoe AI  •  Online  •  Powered by GPT-4o", font=fbar, fill=TEAL)
    # status dot
    draw.ellipse([cw_x+cw_w-26, cw_y+18, cw_x+cw_w-14, cw_y+30], fill=(16,185,129))

    messages = [
        ("user", "How do I form an LLC for my tech startup?"),
        ("ai",   [
            "Great choice! Here is a quick roadmap to form your LLC:",
            "  1.  Choose your state of formation",
            "  2.  Pick a unique business name",
            "  3.  File Articles of Organization",
            "  4.  Draft an Operating Agreement",
            "  5.  Obtain your EIN from the IRS",
            "I can generate your Operating Agreement right now — shall I?",
        ]),
        ("user", "Yes please — generate it now."),
        ("ai",   ["✅  Operating Agreement generated!  Download it in the Documents section."]),
    ]

    fmsg  = font(14, False)
    lh    = 22
    msg_y = cw_y + 56
    max_y = cw_y + cw_h - 58

    for role, content in messages:
        if msg_y >= max_y:
            break
        is_user = (role == "user")
        lines   = [content] if isinstance(content, str) else content
        bh      = len(lines)*lh + 20
        # max bubble width is 55% of chat window
        max_bw  = int(cw_w * 0.55)

        # Measure actual width needed
        needed_w = max(tsz(draw, ln, fmsg)[0] for ln in lines) + 36
        bw = min(needed_w, max_bw)
        bw = max(bw, 200)

        if is_user:
            bx = cw_x + cw_w - bw - 20
            bc = (45, 90, 200)
        else:
            bx = cw_x + 20
            bc = (26, 40, 88)

        # Clamp to stay within chat window
        if msg_y + bh > max_y:
            break

        draw.rounded_rectangle([bx, msg_y, bx+bw, msg_y+bh], radius=12, fill=bc)
        for li, ln in enumerate(lines):
            draw.text((bx+16, msg_y+10+li*lh), ln, font=fmsg, fill=WHITE)

        msg_y += bh + 10

    # Input bar
    inp_y = cw_y + cw_h - 48
    draw.rounded_rectangle([cw_x+14, inp_y, cw_x+cw_w-76, inp_y+36], radius=18, fill=(22,34,72))
    draw.text((cw_x+30, inp_y+9), "Ask Kismoe anything about your business...", font=font(13,False), fill=GRAY)
    draw.rounded_rectangle([cw_x+cw_w-72, inp_y, cw_x+cw_w-14, inp_y+36], radius=18, fill=TEAL)
    aw, ah = tsz(draw, "Send", font(12))
    draw.text((cw_x+cw_w-72+(58-aw)//2, inp_y+(36-ah)//2), "Send", font=font(12), fill=WHITE)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — Services & Docs
# ─────────────────────────────────────────────────────────────────────────────
def make_slide7():
    img = grad_bg()
    draw = ImageDraw.Draw(img)

    cx_text(draw, "Services & Document Generator", 26, font(44), WHITE)
    accent(draw, 88, BLUE, 2)

    services = [
        ("01", "Legal & Compliance",   BLUE),
        ("02", "Finance & Ops",        TEAL),
        ("03", "AI Automation",        PURP),
        ("04", "HR & Workforce",       (234,179,8)),
        ("05", "Marketing & Sales",    (239,68,68)),
        ("06", "Protection",           (16,185,129)),
        ("07", "Website Builder",      (14,165,233)),
        ("08", "Expert Marketplace",   (249,115,22)),
    ]

    margin = 50
    gap    = 12
    cols   = 4
    sc_w   = (W - 2*margin - (cols-1)*gap) // cols   # ~287px
    sc_h   = 100
    sc_y0  = 108

    for i, (num, name, color) in enumerate(services):
        col = i % cols
        row = i // cols
        x0  = margin + col*(sc_w+gap)
        y0  = sc_y0 + row*(sc_h+gap)
        x1, y1 = x0+sc_w, y0+sc_h
        draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=CARD)
        draw.rounded_rectangle([x0, y0, x0+5, y1], radius=4, fill=color)
        # Number
        fn_ = font(13, False)
        draw.text((x0+16, y0+12), num, font=fn_, fill=color)
        # Name (word-wrap if needed)
        ft_ = font(16)
        lines_ = wrap_text(draw, name, ft_, sc_w - 30)
        for li_, ln_ in enumerate(lines_):
            draw.text((x0+16, y0+34 + li_*20), ln_, font=ft_, fill=WHITE)
        # Click hint
        fa_ = font(11, False)
        draw.text((x0+16, y0+sc_h-18), "Click to explore  →", font=fa_, fill=GRAY)

    # Document templates section
    doc_y = sc_y0 + 2*(sc_h+gap) + 18   # below service cards
    fdt = font(18)
    draw.text((margin, doc_y), "Document Templates:", font=fdt, fill=WHITE)

    docs = ["NDA", "Op. Agreement", "Privacy Policy", "Employment", "Invoice", "Handbook"]
    total_docs = len(docs)
    doc_pill_w = (W - 2*margin - (total_docs-1)*10) // total_docs
    dx_ = margin
    for doc in docs:
        draw.rounded_rectangle([dx_, doc_y+32, dx_+doc_pill_w, doc_y+72],
                                radius=10, fill=DARK, outline=BLUE, width=1)
        fw_ = font(13)
        tw_, th_ = tsz(draw, doc, fw_)
        draw.text((dx_+(doc_pill_w-tw_)//2, doc_y+32+(40-th_)//2), doc, font=fw_, fill=WHITE)
        dx_ += doc_pill_w + 10

    cx_text(draw, "Generate, customize, and download any document instantly",
            doc_y + 92, font(17, False), GRAY)

    return img

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — CTA
# ─────────────────────────────────────────────────────────────────────────────
def make_slide8():
    img = grad_bg((18, 8, 45), (5, 4, 18))
    draw = ImageDraw.Draw(img)

    # Glow blobs
    for (bx, by, br, bc) in [(320,300,280,(20,10,80,40)),(960,400,260,(10,60,100,35))]:
        blob = Image.new("RGBA", (W, H), (0,0,0,0))
        bd   = ImageDraw.Draw(blob)
        bd.ellipse([bx-br, by-br, bx+br, by+br], fill=bc)
        img  = Image.alpha_composite(img.convert("RGBA"), blob).convert("RGB")
    draw = ImageDraw.Draw(img)

    cx_text(draw, "Start Free Today", 80, font(70), WHITE)
    cx_text(draw, "No credit card required  ·  Setup in under 3 minutes", 174, font(22, False), GRAY)

    # URL badge
    url = "ksg93rd.github.io/ksg93rd"
    uw, uh = tsz(draw, url, font(22))
    ux = (W - uw - 40)//2
    draw.rounded_rectangle([ux, 218, ux+uw+40, 262], radius=22, fill=TEAL)
    draw.text((ux+20, 228), url, font=font(22), fill=WHITE)

    # Feature row
    features = ["Business Health Score", "AI Chat Assistant", "Document Generator", "8 Service Pillars"]
    fw_  = 272
    total_fw = len(features)*fw_ + (len(features)-1)*16
    fx_  = (W - total_fw)//2
    fy_  = 284
    for feat in features:
        draw.rounded_rectangle([fx_, fy_, fx_+fw_, fy_+54], radius=10, fill=(24,34,72))
        ff_ = font(14, False)
        tw_, th_ = tsz(draw, feat, ff_)
        draw.text((fx_+(fw_-tw_)//2, fy_+(54-th_)//2), feat, font=ff_, fill=WHITE)
        fx_ += fw_ + 16

    # CTA button
    btn_w, btn_h = 520, 66
    bx_ = (W - btn_w)//2
    by_ = 364
    draw.rounded_rectangle([bx_, by_, bx_+btn_w, by_+btn_h], radius=33, fill=BLUE)
    btxt = "Create My Free Account  →"
    fbt  = font(24)
    bw_, bh_ = tsz(draw, btxt, fbt)
    draw.text((W//2-bw_//2, by_+(btn_h-bh_)//2), btxt, font=fbt, fill=WHITE)

    # Divider
    accent(draw, 468, TEAL, 2)
    accent(draw, 471, PURP, 2)

    cx_text(draw, "Trusted by growing businesses  ·  AI-powered  ·  Always improving",
            488, font(16, False), GRAY)

    # Bottom brand
    cx_text(draw, "KISMOE BUSINESS SERVICES", 546, font(30), WHITE)
    cx_text(draw, "Your AI Business Operating System", 592, font(20, False), TEAL)

    return img


SLIDE_FUNCS = [
    make_slide1, make_slide2, make_slide3, make_slide4,
    make_slide5, make_slide6, make_slide7, make_slide8,
]

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Generate audio with Piper Neural TTS (offline, high quality)
#         Model: en_US-lessac-high  — natural American English male voice
# ─────────────────────────────────────────────────────────────────────────────
from piper.voice import PiperVoice
import wave as _wave, io as _io

print("Loading Piper neural TTS voice (en_US-lessac-high)...")
_piper_voice = PiperVoice.load(VOICE_MODEL, config_path=VOICE_CFG)
print("  Voice loaded.")

def gen_piper_wav(text, out_wav):
    buf = _io.BytesIO()
    wf  = _wave.open(buf, "w")
    _piper_voice.synthesize_wav(text, wf)
    wf.close()
    with open(out_wav, "wb") as f:
        f.write(buf.getvalue())

print("Generating narrations...")
for i, text in enumerate(NARRATIONS):
    out = f"{TMP}/narration_{i}.wav"
    if not os.path.exists(out):
        print(f"  Generating narration_{i}.wav...")
        gen_piper_wav(text, out)
        sz = os.path.getsize(out) // 1024
        print(f"  Saved ({sz}KB).")
    else:
        print(f"  narration_{i}.wav already exists — skipping.")

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Resample WAVs to 44100Hz mono and concatenate
# ─────────────────────────────────────────────────────────────────────────────
print("\nResampling and concatenating audio...")
resampled = []
for i in range(len(NARRATIONS)):
    src = f"{TMP}/narration_{i}.wav"
    dst = f"{TMP}/narration_{i}_44k.wav"
    subprocess.run([
        FFMPEG, "-y", "-i", src, "-ar", "44100", "-ac", "1", dst
    ], check=True, capture_output=True)
    resampled.append(dst)

concat_list = f"{TMP}/concat.txt"
with open(concat_list, "w") as f:
    for wav in resampled:
        f.write(f"file '{wav}'\n")

full_audio = f"{TMP}/narration_full.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "concat", "-safe", "0",
    "-i", concat_list, "-c", "copy", full_audio
], check=True, capture_output=True)
print(f"  Full audio ready: {full_audio}")

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Render slides → silent video
# ─────────────────────────────────────────────────────────────────────────────
silent_video = f"{TMP}/kismoe_silent.mp4"
print("\nRendering slides...")
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(silent_video, fourcc, FPS, (W, H))
for idx, (slide_fn, dur) in enumerate(zip(SLIDE_FUNCS, DURATIONS)):
    print(f"  Slide {idx+1}/{len(SLIDE_FUNCS)}  ({dur}s)...")
    pil_img = slide_fn()
    frame   = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    for _ in range(dur * FPS):
        writer.write(frame)
writer.release()
print(f"  Silent video: {silent_video}")

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Merge video + audio → final MP4
# ─────────────────────────────────────────────────────────────────────────────
OUT = "/home/user/ksg93rd/docs/kismoe_intro.mp4"
print("\nMerging video + audio...")
subprocess.run([
    FFMPEG, "-y",
    "-i", silent_video,
    "-i", full_audio,
    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
    "-c:a", "aac", "-b:a", "128k",
    "-shortest", OUT
], check=True)

size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f"\nVideo created: {OUT} — SIZE: {size_mb:.2f} MB")
