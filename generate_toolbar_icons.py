"""
Generate placeholder toolbar icons as PNG files.

Run this script to create basic icons in assets/icons/.
You can then edit these with Paint or replace them with your own designs.
"""

from PIL import Image, ImageDraw
from pathlib import Path


ICON_SIZE = 20  # Icon will be 20x20 pixels
OUTPUT_DIR = Path(__file__).parent / "assets" / "icons"


def create_icon(name: str, draw_func):
    """Create a PNG icon with transparent background."""
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_func(draw)
    
    output_path = OUTPUT_DIR / f"{name}.png"
    img.save(output_path, "PNG")
    print(f"✓ Created {output_path.name}")


def draw_pan(draw):
    """Four directional arrows"""
    mid = ICON_SIZE // 2
    # Vertical line
    draw.line([(mid, 2), (mid, ICON_SIZE - 2)], fill="black", width=2)
    # Horizontal line
    draw.line([(2, mid), (ICON_SIZE - 2, mid)], fill="black", width=2)
    # Arrows
    draw.polygon([(mid, 2), (mid - 3, 6), (mid + 3, 6)], fill="black")
    draw.polygon([(mid, ICON_SIZE - 2), (mid - 3, ICON_SIZE - 6), (mid + 3, ICON_SIZE - 6)], fill="black")
    draw.polygon([(2, mid), (6, mid - 3), (6, mid + 3)], fill="black")
    draw.polygon([(ICON_SIZE - 2, mid), (ICON_SIZE - 6, mid - 3), (ICON_SIZE - 6, mid + 3)], fill="black")


def draw_calibrate(draw):
    """Ruler icon"""
    draw.line([(3, ICON_SIZE - 3), (ICON_SIZE - 3, 3)], fill="blue", width=3)
    for i in range(1, 4):
        frac = i / 4
        x1 = 3 + (ICON_SIZE - 6) * frac
        y1 = ICON_SIZE - 3 - (ICON_SIZE - 6) * frac
        draw.line([(x1 - 2, y1 + 2), (x1 + 2, y1 - 2)], fill="blue", width=1)


def draw_distance(draw):
    """Line with dots at ends"""
    draw.line([(3, ICON_SIZE - 3), (ICON_SIZE - 3, 3)], fill="green", width=3)
    draw.ellipse([(1, ICON_SIZE - 5), (5, ICON_SIZE - 1)], fill="green")
    draw.ellipse([(ICON_SIZE - 5, 1), (ICON_SIZE - 1, 5)], fill="green")


def draw_radius(draw):
    """Circle with radius line"""
    mid = ICON_SIZE // 2
    r = mid - 3
    draw.ellipse([(mid - r, mid - r), (mid + r, mid + r)], outline="blue", width=2)
    draw.line([(mid, mid), (mid + r, mid)], fill="blue", width=2)
    draw.ellipse([(mid - 2, mid - 2), (mid + 2, mid + 2)], fill="blue")


def draw_angle(draw):
    """Angle icon (two lines meeting)"""
    mid = ICON_SIZE // 2
    draw.line([(mid, ICON_SIZE - 2), (2, 2)], fill="orange", width=3)
    draw.line([(mid, ICON_SIZE - 2), (ICON_SIZE - 2, 2)], fill="orange", width=3)


def draw_two_line_angle(draw):
    """Two intersecting lines"""
    mid = ICON_SIZE // 2
    draw.line([(1, mid), (ICON_SIZE - 1, mid)], fill="purple", width=2)
    draw.line([(2, ICON_SIZE - 2), (ICON_SIZE - 2, 2)], fill="purple", width=2)


def draw_polygon_area(draw):
    """Pentagon shape"""
    points = [
        (ICON_SIZE // 2, 2),
        (ICON_SIZE - 3, ICON_SIZE // 2 - 2),
        (ICON_SIZE - 4, ICON_SIZE - 2),
        (4, ICON_SIZE - 2),
        (3, ICON_SIZE // 2 - 2)
    ]
    draw.polygon(points, outline="cyan", fill=None, width=2)


def draw_coordinate(draw):
    """Crosshair with xy text"""
    mid = ICON_SIZE // 2
    cs = 5
    draw.line([(mid - cs, mid), (mid + cs, mid)], fill="red", width=2)
    draw.line([(mid, mid - cs), (mid, mid + cs)], fill="red", width=2)
    draw.text((ICON_SIZE - 6, 3), "xy", fill="red")


def draw_point_to_line(draw):
    """Horizontal line with point and perpendicular"""
    draw.line([(2, 4), (ICON_SIZE - 2, 4)], fill="brown", width=2)
    mid = ICON_SIZE // 2
    draw.ellipse([(mid - 2, ICON_SIZE - 4), (mid + 2, ICON_SIZE)], fill="brown")
    draw.line([(mid, ICON_SIZE - 2), (mid, 4)], fill="brown", width=1)


def draw_arc_length(draw):
    """Curved arc"""
    draw.arc([(2, 2), (ICON_SIZE - 2, ICON_SIZE - 2)], start=30, end=150, fill="magenta", width=3)


# Icon definitions
ICONS = [
    ("pan", draw_pan),
    ("calibrate", draw_calibrate),
    ("distance", draw_distance),
    ("radius", draw_radius),
    ("angle", draw_angle),
    ("two_line_angle", draw_two_line_angle),
    ("polygon_area", draw_polygon_area),
    ("coordinate", draw_coordinate),
    ("point_to_line", draw_point_to_line),
    ("arc_length", draw_arc_length),
]


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating toolbar icons in {OUTPUT_DIR}/\n")
    
    for name, draw_func in ICONS:
        create_icon(name, draw_func)
    
    print(f"\n✓ Generated {len(ICONS)} icons!")
    print("\nYou can now edit these PNG files with Paint or any image editor.")
    print("Recommended: Use transparent backgrounds and 20x20 or 24x24 pixel size.")


if __name__ == "__main__":
    main()
