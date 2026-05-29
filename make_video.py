#!/usr/bin/env python3
"""
Kismoe Business Services — Narrated Intro Video Generator
Resolution: 1280x720, 30fps, ~86 seconds
"""

import os, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import imageio_ffmpeg

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────
W, H = 1280, 720
FPS = 30
DURATIONS = [8, 10, 10, 12, 12, 12, 12, 10]   # seconds per slide

BG    = (10, 15, 30)       # #0a0f1e
BLUE  = (59, 130, 246)     # #3b82f6
TEAL  = (20, 184, 166)     # #14b8a6
PURP  = (139, 92, 246)     # #8b5cf6
WHITE = (255, 255, 255)
GRAY  = (148, 163, 184)    # slate-400

FONT_BOLD   = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"

NARRATIONS = [
    # Slide 1
    "Welcome to Kismoe Business Services — your AI-powered business operating system. "
    "One platform to launch, manage, automate, protect, grow, and scale your business.",
    # Slide 2
    "Running a business means juggling legal compliance, financial planning, HR workflows, "
    "marketing, technology, and customer operations — all at once. Most businesses waste "
    "thousands of dollars and countless hours doing this manually.",
    # Slide 3
    "Kismoe brings it all together. Eight core service pillars — Legal and Compliance, "
    "Finance and Operations, AI Automation, HR and Workforce, Marketing and Sales, "
    "Business Protection, Website Building, and the Expert Marketplace.",
    # Slide 4
    "Getting started is simple. Click 'Start My Business Journey' and complete a quick "
    "five-step onboarding. Tell Kismoe about your business name, industry, stage, team "
    "size, revenue, and biggest challenges.",
    # Slide 5
    "Kismoe instantly generates your Business Health Score — nine dimensions scored from "
    "zero to one hundred. Legal compliance, financial readiness, operations, marketing, "
    "technology, HR, cybersecurity, and overall growth readiness. Each score tells you "
    "exactly where to focus.",
    # Slide 6
    "The AI chat assistant is your always-on business advisor. Ask about business "
    "formation, legal documents, marketing strategy, hiring, automation, or anything else. "
    "Powered by G P T 4, it gives you expert-level answers in seconds.",
    # Slide 7
    "Browse eight service pillars from the services menu. Click any card to see what's "
    "included and generate deliverables instantly. The document generator produces "
    "ready-to-use templates — NDAs, operating agreements, privacy policies, employment "
    "contracts, invoices, and more.",
    # Slide 8
    "Kismoe is free to start. Sign in with your email, complete your business profile, "
    "and get your personalized health score and action plan in minutes. Visit Kismoe "
    "Business Services and take control of your business today.",
]

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
TMP = "/tmp/kismoe"
os.makedirs(TMP, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# Font helpers
# ─────────────────────────────────────────────────────────────────────────────
def font(size, bold=True):
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size)

def text_size(draw, text, fnt):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_text_centered(draw, text, y, fnt, color=WHITE, shadow=True):
    tw, th = text_size(draw, text, fnt)
    x = (W - tw) // 2
    if shadow:
        draw.text((x+2, y+2), text, font=fnt, fill=(0,0,0,120))
    draw.text((x, y), text, font=fnt, fill=color)
    return th

def draw_rect(draw, x0, y0, x1, y1, color, radius=12):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=color)

def gradient_bg(img, top_color=BG, bottom_color=(5, 8, 20)):
    arr = np.array(img)
    for row in range(H):
        t = row / H
        for c in range(3):
            arr[row, :, c] = int(top_color[c] * (1-t) + bottom_color[c] * t)
    return Image.fromarray(arr)

def accent_line(draw, y, color=BLUE, width=3):
    draw.rectangle([80, y, W-80, y+width], fill=color)

def draw_pill(draw, text, cx, cy, fnt, bg_color=BLUE, text_color=WHITE, pad_x=20, pad_y=8):
    tw, th = text_size(draw, text, fnt)
    x0 = cx - tw//2 - pad_x
    y0 = cy - th//2 - pad_y
    x1 = cx + tw//2 + pad_x
    y1 = cy + th//2 + pad_y
    draw.rounded_rectangle([x0, y0, x1, y1], radius=(y1-y0)//2, fill=bg_color)
    draw.text((cx - tw//2, y0 + pad_y), text, font=fnt, fill=text_color)

# ─────────────────────────────────────────────────────────────────────────────
# Slide builders
# ─────────────────────────────────────────────────────────────────────────────

def make_slide1():
    img = gradient_bg(Image.new("RGB", (W, H), BG))
    draw = ImageDraw.Draw(img)

    # Decorative blobs
    for cx, cy, r, col in [(200,150,200,(30,50,90)),(1100,580,220,(50,20,80))]:
        blob = Image.new("RGBA", (W,H), (0,0,0,0))
        bd = ImageDraw.Draw(blob)
        bd.ellipse([cx-r,cy-r,cx+r,cy+r], fill=col+(60,))
        img.paste(Image.alpha_composite(img.convert("RGBA"), blob).convert("RGB"))

    draw = ImageDraw.Draw(img)

    # Big "K" badge
    badge_cx, badge_cy = W//2, 230
    badge_r = 90
    draw.ellipse([badge_cx-badge_r, badge_cy-badge_r, badge_cx+badge_r, badge_cy+badge_r],
                 fill=(30, 40, 80))
    draw.ellipse([badge_cx-badge_r+3, badge_cy-badge_r+3, badge_cx+badge_r-3, badge_cy+badge_r-3],
                 outline=BLUE, width=3)

    fK = font(100)
    tw, th = text_size(draw, "K", fK)
    draw.text((badge_cx - tw//2 + 2, badge_cy - th//2 + 2), "K", font=fK, fill=(20,20,60))
    # gradient-ish K: draw in two layers
    draw.text((badge_cx - tw//2, badge_cy - th//2), "K", font=fK, fill=BLUE)

    # KISMOE title
    fTitle = font(80)
    draw_text_centered(draw, "KISMOE", 340, fTitle, WHITE)

    # Tagline
    fTag = font(26, bold=False)
    draw_text_centered(draw, "Business Services", 440, fTag, TEAL)

    # Subtitle
    fSub = font(20, bold=False)
    draw_text_centered(draw, "AI-Powered Business Operating System", 495, fSub, GRAY)

    # Accent
    accent_line(draw, 550, BLUE)
    accent_line(draw, 554, PURP)

    # Bottom tagline
    draw_text_centered(draw, "Launch · Manage · Automate · Protect · Grow · Scale", 580, font(18, False), GRAY)

    return img


def make_slide2():
    img = gradient_bg(Image.new("RGB", (W, H), BG))
    draw = ImageDraw.Draw(img)

    # Title
    fT = font(42)
    draw_text_centered(draw, "The Business Challenge", 40, fT, WHITE)
    accent_line(draw, 105, BLUE, 2)

    problems = [
        ("⚖", "Legal Chaos",       "Compliance, contracts, formation — overwhelming", BLUE),
        ("💰","Finance Confusion",  "Budgeting, cash flow, taxes — out of control",  TEAL),
        ("🤖","No Automation",      "Manual processes eating hours every day",        PURP),
        ("👥","Manual HR",          "Hiring, payroll, onboarding — all disconnected", (234,179,8)),
    ]

    card_w, card_h = 270, 210
    cols = 4
    total_w = cols * card_w + (cols-1)*20
    start_x = (W - total_w) // 2
    cy = 240

    for i, (icon, title, desc, color) in enumerate(problems):
        x0 = start_x + i * (card_w + 20)
        y0 = cy - card_h // 2
        x1 = x0 + card_w
        y1 = y0 + card_h
        # Card
        draw.rounded_rectangle([x0,y0,x1,y1], radius=16, fill=(20,28,55))
        draw.rounded_rectangle([x0,y0,x1,y0+4], radius=4, fill=color)

        # Icon text
        fi = font(36)
        draw.text((x0+20, y0+20), icon, font=fi, fill=color)

        # Title
        ft = font(18)
        draw.text((x0+15, y0+75), title, font=ft, fill=WHITE)

        # Desc — word wrap
        fd = font(13, False)
        words = desc.split()
        lines, line = [], ""
        for w in words:
            test = (line + " " + w).strip()
            tw, _ = text_size(draw, test, fd)
            if tw > card_w - 30:
                lines.append(line)
                line = w
            else:
                line = test
        lines.append(line)
        for li, ln in enumerate(lines):
            draw.text((x0+15, y0+105 + li*22), ln, font=fd, fill=GRAY)

    # Bottom message
    fB = font(22, False)
    draw_text_centered(draw, "Most businesses waste thousands of dollars doing this manually.", 570, fB, (200,200,200))

    accent_line(draw, 620, BLUE, 2)
    draw_text_centered(draw, "There's a better way.", 636, font(20), TEAL)

    return img


def make_slide3():
    img = gradient_bg(Image.new("RGB", (W, H), BG))
    draw = ImageDraw.Draw(img)

    fT = font(42)
    draw_text_centered(draw, "Introducing Kismoe", 40, fT, WHITE)
    accent_line(draw, 105, TEAL, 2)

    pillars = [
        ("⚖","Legal & Compliance",   BLUE),
        ("💰","Finance & Operations", TEAL),
        ("🤖","AI Automation",        PURP),
        ("👥","HR & Workforce",       (234,179,8)),
        ("📣","Marketing & Sales",    (239,68,68)),
        ("🛡","Business Protection",  (16,185,129)),
        ("🌐","Website Builder",      (14,165,233)),
        ("🤝","Expert Marketplace",   (249,115,22)),
    ]

    # Hub circle
    hub_cx, hub_cy = W//2, 390
    hub_r = 68
    draw.ellipse([hub_cx-hub_r,hub_cy-hub_r,hub_cx+hub_r,hub_cy+hub_r],
                 fill=(30,50,100), outline=TEAL, width=3)
    fHub = font(16)
    draw.text((hub_cx-32, hub_cy-20), "Kismoe", font=fHub, fill=TEAL)
    draw.text((hub_cx-14, hub_cy+2),  "AI", font=font(22), fill=WHITE)

    # Spokes
    n = len(pillars)
    spoke_r = 250
    for i, (icon, name, color) in enumerate(pillars):
        angle = math.radians(-90 + i * 360 / n)
        px = int(hub_cx + spoke_r * math.cos(angle))
        py = int(hub_cy + spoke_r * math.sin(angle))

        # Line
        draw.line([(hub_cx,hub_cy),(px,py)], fill=color+(180,) if False else color, width=2)

        # Node circle
        nr = 44
        draw.ellipse([px-nr,py-nr,px+nr,py+nr], fill=(20,28,55), outline=color, width=2)
        fi = font(20)
        tw,th = text_size(draw, icon, fi)
        draw.text((px-tw//2, py-th//2-8), icon, font=fi, fill=color)
        fn = font(10, False)
        tw,th = text_size(draw, name, fn)
        draw.text((px-tw//2, py+8), name, font=fn, fill=WHITE)

    return img


def make_slide4():
    img = gradient_bg(Image.new("RGB", (W, H), BG))
    draw = ImageDraw.Draw(img)

    fT = font(42)
    draw_text_centered(draw, "Getting Started: Onboarding", 35, fT, WHITE)
    accent_line(draw, 100, BLUE, 2)

    # Big CTA button mockup
    btn_w, btn_h = 420, 58
    bx = (W - btn_w)//2
    draw.rounded_rectangle([bx, 130, bx+btn_w, 130+btn_h], radius=29, fill=TEAL)
    fBtn = font(22)
    tw, th = text_size(draw, "▶  Start My Business Journey", fBtn)
    draw.text((W//2 - tw//2, 130 + (btn_h-th)//2), "▶  Start My Business Journey", font=fBtn, fill=WHITE)

    # Step indicators
    steps = ["Business Info", "Industry", "Team Size", "Revenue", "Challenges"]
    step_y = 230
    total = len(steps) * 130
    sx = (W - total) // 2 + 65
    for i, step in enumerate(steps):
        cx = sx + i * 130
        r = 30
        active = (i == 0)
        col = BLUE if active else (40, 55, 90)
        outline = BLUE if active else GRAY
        draw.ellipse([cx-r,step_y-r,cx+r,step_y+r], fill=col, outline=outline, width=2)
        fn = font(18) if active else font(18, False)
        draw.text((cx-8, step_y-11), str(i+1), font=fn, fill=WHITE)
        # connector
        if i < len(steps)-1:
            draw.line([(cx+r, step_y),(cx+130-r, step_y)], fill=(40,55,90), width=2)
        # label
        fl = font(12, bold=active)
        tw,_ = text_size(draw, step, fl)
        draw.text((cx-tw//2, step_y+r+8), step, font=fl, fill=WHITE if active else GRAY)

    # Mock form
    form_x, form_y = 280, 320
    form_w = 720
    draw.rounded_rectangle([form_x, form_y, form_x+form_w, form_y+270], radius=16, fill=(18,26,52))
    draw.rounded_rectangle([form_x, form_y, form_x+form_w, form_y+4], radius=4, fill=BLUE)

    fields = [
        ("Business Name", "Acme Corp LLC"),
        ("Industry",      "Technology / SaaS"),
        ("Business Stage","Growth Stage (1-3 years)"),
    ]
    fL = font(14, False)
    fV = font(16)
    for fi_, (label, val) in enumerate(fields):
        fy = form_y + 30 + fi_ * 72
        draw.text((form_x+30, fy), label, font=fL, fill=GRAY)
        draw.rounded_rectangle([form_x+30, fy+22, form_x+form_w-30, fy+54], radius=8, fill=(28,38,72))
        draw.rounded_rectangle([form_x+30, fy+22, form_x+form_w-30, fy+26], radius=4, fill=BLUE)
        draw.text((form_x+46, fy+30), val, font=fV, fill=WHITE)

    # Bottom note
    draw_text_centered(draw, "Takes less than 3 minutes · No credit card required", 650, font(18, False), GRAY)

    return img


def make_slide5():
    img = gradient_bg(Image.new("RGB", (W, H), BG))
    draw = ImageDraw.Draw(img)

    fT = font(42)
    draw_text_centered(draw, "Business Health Score", 35, fT, WHITE)
    accent_line(draw, 100, PURP, 2)

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
    card_w, card_h = 340, 145
    pad_x = (W - cols*card_w - (cols-1)*16) // 2
    pad_y = 125

    for idx, (name, score, color) in enumerate(scores):
        col = idx % cols
        row = idx // cols
        x0 = pad_x + col*(card_w+16)
        y0 = pad_y + row*(card_h+12)
        x1 = x0 + card_w
        y1 = y0 + card_h

        draw.rounded_rectangle([x0,y0,x1,y1], radius=12, fill=(18,26,52))

        # Ring arc simulation
        cx, cy, r = x0+60, y0+card_h//2, 38
        # Background ring
        draw.arc([cx-r,cy-r,cx+r,cy+r], start=0, end=360, fill=(40,55,90), width=8)
        # Score arc
        arc_end = int(360 * score / 100) - 90
        draw.arc([cx-r,cy-r,cx+r,cy+r], start=-90, end=arc_end, fill=color, width=8)
        # Score number
        fs = font(22)
        tw, th = text_size(draw, str(score), fs)
        draw.text((cx-tw//2, cy-th//2), str(score), font=fs, fill=WHITE)

        # Name + label
        fn = font(20)
        draw.text((x0+110, y0+30), name, font=fn, fill=WHITE)
        fl = font(13, False)
        status = "Good" if score>=70 else ("Needs Work" if score>=50 else "Critical")
        sc = TEAL if score>=70 else ((249,115,22) if score>=50 else (239,68,68))
        draw.text((x0+110, y0+62), status, font=fl, fill=sc)

        # Bar
        bar_x = x0+110
        bar_y = y0+90
        bar_w = card_w - 130
        draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+10], radius=5, fill=(40,55,90))
        draw.rounded_rectangle([bar_x, bar_y, bar_x+int(bar_w*score/100), bar_y+10], radius=5, fill=color)

    return img


def make_slide6():
    img = gradient_bg(Image.new("RGB", (W, H), BG))
    draw = ImageDraw.Draw(img)

    fT = font(42)
    draw_text_centered(draw, "AI Chat Assistant", 35, fT, WHITE)
    accent_line(draw, 100, TEAL, 2)

    # Chat window
    cw_x, cw_y = 120, 120
    cw_w, cw_h = 1040, 540
    draw.rounded_rectangle([cw_x,cw_y,cw_x+cw_w,cw_y+cw_h], radius=18, fill=(15,22,46))
    # Title bar
    draw.rounded_rectangle([cw_x,cw_y,cw_x+cw_w,cw_y+50], radius=18, fill=(25,35,70))
    draw.rounded_rectangle([cw_x,cw_y+36,cw_x+cw_w,cw_y+50], radius=0, fill=(25,35,70))
    fBar = font(16)
    draw.text((cw_x+20, cw_y+14), "🤖  Kismoe AI  ●  Online", font=fBar, fill=TEAL)

    messages = [
        ("user",    "How do I form an LLC for my tech startup?"),
        ("ai",      "Great question! Here's how to form an LLC:\n"
                    "1. Choose your state of formation\n"
                    "2. Pick a unique business name\n"
                    "3. File Articles of Organization\n"
                    "4. Create an Operating Agreement\n"
                    "5. Get your EIN from the IRS\n"
                    "I can generate your Operating Agreement right now — want me to?"),
        ("user",    "Yes, generate the Operating Agreement."),
        ("ai",      "✅  Operating Agreement generated! Download ready in Documents."),
    ]

    msg_y = cw_y + 65
    for role, text in messages:
        is_user = role == "user"
        lines = text.split("\n")
        fM = font(14, False)
        line_h = 22
        bubble_h = len(lines) * line_h + 20
        bubble_w = min(700, max(300, max(len(l) for l in lines)*8 + 40))

        if is_user:
            bx = cw_x + cw_w - bubble_w - 20
            bc = BLUE
        else:
            bx = cw_x + 20
            bc = (25, 40, 85)

        draw.rounded_rectangle([bx, msg_y, bx+bubble_w, msg_y+bubble_h], radius=12, fill=bc)
        for li, ln in enumerate(lines):
            draw.text((bx+14, msg_y+10+li*line_h), ln, font=fM, fill=WHITE)

        msg_y += bubble_h + 12
        if msg_y > cw_y + cw_h - 60:
            break

    # Input bar
    inp_y = cw_y + cw_h - 52
    draw.rounded_rectangle([cw_x+16, inp_y, cw_x+cw_w-80, inp_y+40], radius=20, fill=(25,35,70))
    draw.text((cw_x+34, inp_y+10), "Ask Kismoe anything about your business...", font=font(14,False), fill=GRAY)
    draw.rounded_rectangle([cw_x+cw_w-74, inp_y, cw_x+cw_w-16, inp_y+40], radius=20, fill=TEAL)
    draw.text((cw_x+cw_w-60, inp_y+10), "➤", font=font(18), fill=WHITE)

    return img


def make_slide7():
    img = gradient_bg(Image.new("RGB", (W, H), BG))
    draw = ImageDraw.Draw(img)

    fT = font(42)
    draw_text_centered(draw, "Services & Document Generator", 35, fT, WHITE)
    accent_line(draw, 100, BLUE, 2)

    services = [
        ("⚖","Legal",    BLUE),   ("💰","Finance", TEAL),
        ("🤖","AI Auto", PURP),   ("👥","HR",      (234,179,8)),
        ("📣","Marketing",(239,68,68)),("🛡","Protection",(16,185,129)),
        ("🌐","Website", (14,165,233)),("🤝","Experts",(249,115,22)),
    ]

    sc_w, sc_h = 270, 120
    cols = 4
    total_w = cols*sc_w + (cols-1)*14
    sx = (W - total_w)//2
    for i, (icon, name, color) in enumerate(services):
        col = i % cols
        row = i // cols
        x0 = sx + col*(sc_w+14)
        y0 = 125 + row*(sc_h+14)
        draw.rounded_rectangle([x0,y0,x0+sc_w,y0+sc_h], radius=12, fill=(18,26,52))
        draw.rounded_rectangle([x0,y0,x0+4,y0+sc_h], radius=4, fill=color)
        fi = font(28)
        draw.text((x0+20, y0+20), icon, font=fi, fill=color)
        fn = font(18)
        draw.text((x0+20, y0+60), name, font=fn, fill=WHITE)
        fa = font(12, False)
        draw.text((x0+20, y0+88), "Click to explore →", font=fa, fill=GRAY)

    # Document row
    doc_y = 400
    draw.text((sx, doc_y), "Document Templates:", font=font(20), fill=WHITE)
    docs = ["📄 NDA", "📋 Op. Agreement", "🔒 Privacy Policy", "👔 Employment Contract", "🧾 Invoice"]
    dx = sx
    for doc in docs:
        dw = 195
        draw.rounded_rectangle([dx, doc_y+32, dx+dw, doc_y+80], radius=10, fill=(28,38,72), outline=BLUE, width=1)
        fw = font(13)
        tw, th = text_size(draw, doc, fw)
        draw.text((dx + (dw-tw)//2, doc_y+32+(48-th)//2), doc, font=fw, fill=WHITE)
        dx += dw + 12

    draw_text_centered(draw, "Generate ready-to-use legal & business documents instantly", 625, font(18, False), GRAY)

    return img


def make_slide8():
    img = gradient_bg(Image.new("RGB", (W, H), BG), top_color=(20,10,50), bottom_color=(5,5,20))
    draw = ImageDraw.Draw(img)

    # Big headline
    fH = font(64)
    draw_text_centered(draw, "Start Free Today", 100, fH, WHITE)

    # Subhead
    fS = font(28, False)
    draw_text_centered(draw, "No credit card required · Setup in under 3 minutes", 185, fS, GRAY)

    # URL pill
    draw_pill(draw, "🌐  kismoe.com/business", W//2, 260, font(24), bg_color=TEAL)

    # Feature row
    features = ["✅ Business Health Score","✅ AI Chat Assistant","✅ Document Generator","✅ 8 Service Pillars"]
    fw = 270
    total = len(features) * fw + (len(features)-1)*20
    fx = (W - total)//2
    for feat in features:
        draw.rounded_rectangle([fx, 310, fx+fw, 370], radius=10, fill=(20,30,65))
        ff = font(14, False)
        tw, th = text_size(draw, feat, ff)
        draw.text((fx+(fw-tw)//2, 310+(60-th)//2), feat, font=ff, fill=WHITE)
        fx += fw + 20

    # Big CTA button
    btn_w, btn_h = 500, 70
    bx = (W - btn_w)//2
    by = 410
    draw.rounded_rectangle([bx, by, bx+btn_w, by+btn_h], radius=35, fill=BLUE)
    fBtn = font(26)
    tw, th = text_size(draw, "Create My Free Account →", fBtn)
    draw.text((W//2-tw//2, by+(btn_h-th)//2), "Create My Free Account →", font=fBtn, fill=WHITE)

    # Social proof
    draw_text_centered(draw, "Trusted by 10,000+ businesses · AI-powered · Always improving", 520, font(18, False), GRAY)

    accent_line(draw, 570, TEAL, 2)
    accent_line(draw, 573, PURP, 2)

    # Big KISMOE at bottom
    fK = font(32)
    draw_text_centered(draw, "KISMOE BUSINESS SERVICES", 600, fK, WHITE)
    draw_text_centered(draw, "Your AI Business Operating System", 648, font(20, False), TEAL)

    return img


SLIDE_FUNCS = [
    make_slide1, make_slide2, make_slide3, make_slide4,
    make_slide5, make_slide6, make_slide7, make_slide8,
]

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Generate audio
# ─────────────────────────────────────────────────────────────────────────────
import time as _time

def gtts_with_retry(text, out, max_retries=6, base_delay=8):
    for attempt in range(max_retries):
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(out)
            return True
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = base_delay * (attempt + 1)
                print(f"    Rate limited, waiting {wait}s...")
                _time.sleep(wait)
            else:
                raise
    return False

print("Generating narration audio (skipping if already exist)...")
for i, text in enumerate(NARRATIONS):
    out = f"{TMP}/narration_{i}.mp3"
    if not os.path.exists(out):
        print(f"  Generating narration_{i}.mp3...")
        gtts_with_retry(text, out)
        print(f"  Saved narration_{i}.mp3")
        _time.sleep(3)  # small pause between requests
        _time.sleep(5)  # longer pause between requests to avoid rate limit
    else:
        print(f"  narration_{i}.mp3 already exists")

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Concatenate audio with imageio-ffmpeg's bundled ffmpeg
# ─────────────────────────────────────────────────────────────────────────────
print("\nConcatenating audio segments...")

# Build a concat list
concat_list = f"{TMP}/concat.txt"
with open(concat_list, "w") as f:
    for i in range(len(NARRATIONS)):
        f.write(f"file '{TMP}/narration_{i}.mp3'\n")

# Convert each MP3 to WAV first, then concat
wavs = []
for i in range(len(NARRATIONS)):
    wav = f"{TMP}/narration_{i}.wav"
    subprocess.run([
        FFMPEG, "-y", "-i", f"{TMP}/narration_{i}.mp3",
        "-ar", "44100", "-ac", "1",
        wav
    ], check=True, capture_output=True)
    wavs.append(wav)

# Re-write concat list with WAV files
with open(concat_list, "w") as f:
    for wav in wavs:
        f.write(f"file '{wav}'\n")

full_audio = f"{TMP}/narration_full.wav"
subprocess.run([
    FFMPEG, "-y", "-f", "concat", "-safe", "0",
    "-i", concat_list,
    "-c", "copy",
    full_audio
], check=True, capture_output=True)
print(f"  Full audio: {full_audio}")

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Create silent video frames with OpenCV
# ─────────────────────────────────────────────────────────────────────────────
import cv2

silent_video = f"{TMP}/kismoe_silent.mp4"
print("\nRendering slides to video...")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(silent_video, fourcc, FPS, (W, H))

for idx, (slide_fn, dur) in enumerate(zip(SLIDE_FUNCS, DURATIONS)):
    print(f"  Slide {idx+1}/{len(SLIDE_FUNCS)} ({dur}s)...")
    pil_img = slide_fn()
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    for _ in range(dur * FPS):
        writer.write(frame)

writer.release()
print(f"  Silent video: {silent_video}")

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Merge video + audio using imageio-ffmpeg's bundled ffmpeg
# ─────────────────────────────────────────────────────────────────────────────
OUT = "/home/user/ksg93rd/docs/kismoe_intro.mp4"
print("\nMerging video + audio...")

subprocess.run([
    FFMPEG, "-y",
    "-i", silent_video,
    "-i", full_audio,
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "23",
    "-c:a", "aac",
    "-b:a", "128k",
    "-shortest",
    OUT
], check=True, capture_output=False)

size_mb = os.path.getsize(OUT) / 1024 / 1024
print(f"\nVideo created: {OUT} — SIZE: {size_mb:.2f} MB")
