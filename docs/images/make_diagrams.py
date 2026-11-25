from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

out = Path(__file__).resolve().parent
out.mkdir(parents=True, exist_ok=True)


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for c in candidates:
        p = Path(c)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def rounded_box(draw, xy, fill, outline, width=2, radius=16):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def center_text(draw, box, text, f, fill):
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((x0 + x1 - tw) / 2, (y0 + y1 - th) / 2), text, font=f, fill=fill)


title = font(36, True)
body = font(22)
small = font(18)

# 1) Install flow
img = Image.new("RGB", (1400, 520), "#F7F8FA")
d = ImageDraw.Draw(img)
d.text((48, 28), "I-01 Install flow (RTX workstation)", font=title, fill="#0F2744")
steps = [
    ("1", "GPU driver\nnvidia-smi"),
    ("2", "Isaac Sim\ninstall + sample"),
    ("3", "Isaac Lab\nenv + demo"),
    ("4", "MuJoCo\nvenv + humanoid"),
    ("5", "SETUP_LOG\n+ checklist"),
]
colors = ["#1F6FEB", "#0E8A6A", "#0E8A6A", "#C47A00", "#5B6577"]
x = 48
for i, ((num, label), col) in enumerate(zip(steps, colors)):
    box = (x, 120, x + 220, 320)
    rounded_box(d, box, "#FFFFFF", col, 3, 18)
    d.ellipse((x + 85, 145, x + 135, 195), fill=col)
    center_text(d, (x + 85, 145, x + 135, 195), num, font(28, True), "#FFFFFF")
    lines = label.split("\n")
    yy = 220
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=body)
        tw = bbox[2] - bbox[0]
        d.text((x + (220 - tw) / 2, yy), line, font=body, fill="#132238")
        yy += 32
    if i < len(steps) - 1:
        d.polygon([(x + 230, 210), (x + 255, 225), (x + 230, 240)], fill="#9AA3AF")
    x += 270
d.text((48, 380), "Pass each smoke test before moving to the next step.", font=small, fill="#5B6577")
img.save(out / "sim-install-flow.png")

# 2) Folder layout
img = Image.new("RGB", (1200, 700), "#F7F8FA")
d = ImageDraw.Draw(img)
d.text((48, 28), "Suggested folder layout", font=title, fill="#0F2744")
tree = [
    (0, "C:/Users/<you>/sim/"),
    (1, "isaac/                 # Isaac Sim notes / shortcuts"),
    (1, "isaac_lab/"),
    (2, "IsaacLab/            # git clone"),
    (1, "mujoco/"),
    (2, ".venv/               # Python environment"),
    (2, "mujoco_menagerie/    # sample humanoids"),
    (1, "notes/"),
    (2, "SETUP_LOG.md         # versions + who installed"),
]
y = 110
mono = font(22)
for indent, text in tree:
    xx = 70 + indent * 36
    fill = "#0F2744" if indent == 0 else "#243447"
    d.text((xx, y), ("▸ " if indent else "") + text, font=mono, fill=fill)
    y += 54
rounded_box(d, (48, 620, 1150, 670), "#E8EEF7", "#1F6FEB", 2, 12)
d.text(
    (70, 632),
    "Keep paths short. Record GPU driver + software versions in SETUP_LOG.md",
    font=small,
    fill="#1F6FEB",
)
img.save(out / "sim-folder-layout.png")

# 3) Stack diagram
img = Image.new("RGB", (1200, 620), "#F7F8FA")
d = ImageDraw.Draw(img)
d.text((48, 24), "Simulation stack for HR", font=title, fill="#0F2744")
layers = [
    ("AI / control experiments / RL", "#D9E8FF", "#1F6FEB"),
    ("Isaac Lab", "#D9F3EA", "#0E8A6A"),
    ("Isaac Sim  (GPU robotics sim)", "#FFF0D6", "#C47A00"),
    ("MuJoCo  (fast physics / humanoid models)", "#E8EEF7", "#5B6577"),
    ("NVIDIA RTX driver  ·  Windows workstation", "#E6E9EE", "#5B6577"),
]
y = 100
for text, bg, edge in layers:
    box = (80, y, 1120, y + 80)
    rounded_box(d, box, bg, edge, 3, 14)
    center_text(d, box, text, font(26, True), "#132238")
    y += 95
img.save(out / "sim-stack.png")

# 4) Checklist
img = Image.new("RGB", (1200, 720), "#F7F8FA")
d = ImageDraw.Draw(img)
d.text((48, 24), "I-01 acceptance smoke tests", font=title, fill="#0F2744")
checks = [
    ("A", "nvidia-smi shows RTX GPU"),
    ("B", "Isaac Sim launches"),
    ("C", "Isaac sample humanoid runs >= 30 s"),
    ("D", "Isaac Lab demo starts"),
    ("E", "MuJoCo humanoid opens in viewer"),
    ("F", "SETUP_LOG.md completed"),
]
y = 100
for code, text in checks:
    box = (70, y, 1130, y + 80)
    rounded_box(d, box, "#FFFFFF", "#CFD6DE", 2, 14)
    d.rounded_rectangle((90, y + 18, 150, y + 62), radius=10, fill="#0E8A6A")
    center_text(d, (90, y + 18, 150, y + 62), code, font(24, True), "#FFFFFF")
    d.text((180, y + 26), text, font=font(26), fill="#132238")
    y += 95
img.save(out / "sim-checklist.png")

print("ok", sorted(p.name for p in out.glob("sim-*")))
