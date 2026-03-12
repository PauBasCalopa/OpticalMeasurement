"""Generate application icon for Optical Measurement Tool.

Run once:  python generate_icon.py
Produces:  assets/icon.ico  (multi-resolution: 16, 32, 48, 64, 128, 256)
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

def draw_icon(size: int) -> Image.Image:
    """Draw the OM-tool icon at the given pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size  # shorthand
    cx, cy = s / 2, s / 2
    margin = s * 0.06

    # --- background: rounded dark-blue circle ---
    bg_r = s / 2 - margin
    d.ellipse(
        [cx - bg_r, cy - bg_r, cx + bg_r, cy + bg_r],
        fill=(25, 42, 86),        # deep navy
        outline=(60, 130, 230),   # bright blue ring
        width=max(1, int(s * 0.03)),
    )

    # --- crosshair ---
    ch_color = (60, 200, 255, 220)  # cyan
    lw = max(1, int(s * 0.025))
    gap = s * 0.10  # gap around centre

    # horizontal arms
    d.line([(margin + s * 0.12, cy), (cx - gap, cy)], fill=ch_color, width=lw)
    d.line([(cx + gap, cy), (s - margin - s * 0.12, cy)], fill=ch_color, width=lw)
    # vertical arms
    d.line([(cx, margin + s * 0.12), (cx, cy - gap)], fill=ch_color, width=lw)
    d.line([(cx, cy + gap), (cx, s - margin - s * 0.12)], fill=ch_color, width=lw)

    # --- small centre dot ---
    dot_r = max(1.5, s * 0.03)
    d.ellipse(
        [cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r],
        fill=(255, 80, 80),  # red dot
    )

    # --- ruler ticks along bottom-right quadrant arc ---
    tick_color = (200, 220, 255, 200)
    arc_r = bg_r * 0.72
    n_ticks = 7
    for i in range(n_ticks):
        # angle from 0° to 90° (bottom-right quadrant)
        angle = math.radians(i * 90 / (n_ticks - 1))
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        inner = arc_r * 0.85 if i % 2 == 0 else arc_r * 0.90
        outer = arc_r

        x1 = cx + cos_a * inner
        y1 = cy + sin_a * inner
        x2 = cx + cos_a * outer
        y2 = cy + sin_a * outer
        tw = max(1, int(s * 0.02)) if i % 2 == 0 else max(1, int(s * 0.015))
        d.line([(x1, y1), (x2, y2)], fill=tick_color, width=tw)

    # --- angle arc indicator (top-left area) ---
    arc_inner = bg_r * 0.38
    arc_box = [
        cx - arc_inner, cy - arc_inner,
        cx + arc_inner, cy + arc_inner,
    ]
    d.arc(arc_box, start=200, end=290, fill=(100, 255, 160, 200),
          width=max(1, int(s * 0.025)))

    # --- subtle "distance" line from bottom-left to top-right with endpoints ---
    lx1, ly1 = cx - bg_r * 0.45, cy + bg_r * 0.45
    lx2, ly2 = cx + bg_r * 0.45, cy - bg_r * 0.45
    d.line([(lx1, ly1), (lx2, ly2)], fill=(255, 200, 60, 180),
           width=max(1, int(s * 0.02)))
    ep_r = max(1.5, s * 0.025)
    for px, py in [(lx1, ly1), (lx2, ly2)]:
        d.ellipse([px - ep_r, py - ep_r, px + ep_r, py + ep_r],
                  fill=(255, 200, 60))

    return img


def main():
    os.makedirs("assets", exist_ok=True)
    sizes = [16, 32, 48, 64, 128, 256]
    images = [draw_icon(sz) for sz in sizes]

    # Save as multi-resolution .ico
    ico_path = os.path.join("assets", "icon.ico")
    images[-1].save(
        ico_path,
        format="ICO",
        sizes=[(sz, sz) for sz in sizes],
        append_images=images[:-1],
    )
    print(f"Icon saved to {ico_path}  ({', '.join(str(s) for s in sizes)} px)")

    # Also save a 256px PNG for reference
    png_path = os.path.join("assets", "icon.png")
    images[-1].save(png_path)
    print(f"PNG preview saved to {png_path}")


if __name__ == "__main__":
    main()
