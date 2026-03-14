"""
Toolbar Widget

Visual toolbar with icon buttons for quick access to measurement tools.
Icons are loaded from PNG files in assets/icons/ with fallback to drawn shapes.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk


# Tool definitions: (tool_name, label, shortcut, icon_drawer)
_TOOLS = [
    ("pan", "Pan", "Space"),
    ("calibrate", "Calibrate", "F4"),
    ("sep1", None, None),
    ("distance", "Distance", "F5"),
    ("radius", "Radius", "F6"),
    ("angle", "Angle", "F7"),
    ("two_line_angle", "2-Line Angle", "F8"),
    ("sep2", None, None),
    ("polygon_area", "Polygon", "F9"),
    ("coordinate", "Coords", "F10"),
    ("point_to_line", "Pt-to-Line", "F11"),
    ("arc_length", "Arc Length", "F12"),
]

_BTN_SIZE = 28
_ICON_PAD = 4


class ToolBar(ttk.Frame):
    """Horizontal toolbar with icon buttons for each tool."""

    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.buttons: dict[str, tk.Canvas] = {}
        self.active_tool: str = "pan"
        self.icon_images: dict[str, ImageTk.PhotoImage] = {}  # Keep references
        self._load_icons()
        self._build()
    
    def _load_icons(self):
        """Load PNG icons from assets/icons/ folder."""
        icon_dir = Path(__file__).parent.parent / "assets" / "icons"
        icon_size = (_BTN_SIZE - 2 * _ICON_PAD, _BTN_SIZE - 2 * _ICON_PAD)
        
        for tool_name, _, _ in _TOOLS:
            if tool_name.startswith("sep"):
                continue
            
            icon_path = icon_dir / f"{tool_name}.png"
            if icon_path.exists():
                try:
                    img = Image.open(icon_path)
                    img = img.resize(icon_size, Image.Resampling.LANCZOS)
                    self.icon_images[tool_name] = ImageTk.PhotoImage(img)
                except Exception as e:
                    print(f"Warning: Could not load icon {icon_path}: {e}")
                    # Will use fallback drawing

    def _build(self):
        for tool_name, label, shortcut in _TOOLS:
            if tool_name.startswith("sep"):
                sep = ttk.Separator(self, orient=tk.VERTICAL)
                sep.pack(side=tk.LEFT, fill=tk.Y, padx=4, pady=2)
                continue

            btn = tk.Canvas(self, width=_BTN_SIZE, height=_BTN_SIZE,
                            highlightthickness=1, highlightbackground="#999",
                            bg="#f0f0f0", cursor="hand2")
            btn.pack(side=tk.LEFT, padx=1, pady=2)

            self._draw_icon(btn, tool_name)

            tip_text = f"{label} ({shortcut})" if shortcut else label
            btn.bind("<Enter>", lambda e, b=btn, t=tip_text: self._on_enter(b, t))
            btn.bind("<Leave>", lambda e, b=btn: self._on_leave(b))

            if tool_name == "calibrate":
                btn.bind("<Button-1>", lambda e: self.app.start_calibration())
            else:
                btn.bind("<Button-1>", lambda e, tn=tool_name: self._on_click(tn))

            self.buttons[tool_name] = btn

        self._highlight("pan")

    # ------------------------------------------------------------------
    # Icon drawing (uses PNG images when available, fallback to shapes)
    # ------------------------------------------------------------------

    def _draw_icon(self, c: tk.Canvas, tool: str):
        # Try to use loaded PNG image first
        if tool in self.icon_images:
            mid = _BTN_SIZE // 2
            c.create_image(mid, mid, image=self.icon_images[tool])
            return
        
        # Fallback to geometric shapes if image not found
        s = _BTN_SIZE
        p = _ICON_PAD
        mid = s // 2

        if tool == "pan":
            # Four arrows
            c.create_line(mid, p, mid, s - p, fill="black", width=1.5)
            c.create_line(p, mid, s - p, mid, fill="black", width=1.5)
            c.create_polygon(mid, p, mid - 3, p + 5, mid + 3, p + 5, fill="black")
            c.create_polygon(mid, s - p, mid - 3, s - p - 5, mid + 3, s - p - 5, fill="black")
            c.create_polygon(p, mid, p + 5, mid - 3, p + 5, mid + 3, fill="black")
            c.create_polygon(s - p, mid, s - p - 5, mid - 3, s - p - 5, mid + 3, fill="black")

        elif tool == "calibrate":
            # Ruler
            c.create_line(p, s - p - 2, s - p, p + 2, fill="blue", width=2)
            for frac in (0.25, 0.5, 0.75):
                x = p + (s - 2 * p) * frac
                y = (s - p - 2) - (s - 2 * p - 4) * frac
                c.create_line(x - 3, y + 3, x + 3, y - 3, fill="blue", width=1)

        elif tool == "distance":
            c.create_line(p + 2, s - p - 2, s - p - 2, p + 2, fill="green", width=2)
            c.create_oval(p, s - p - 4, p + 4, s - p, fill="green")
            c.create_oval(s - p - 4, p, s - p, p + 4, fill="green")

        elif tool == "radius":
            cx, cy, r = mid, mid, mid - p - 1
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="blue", width=1.5)
            c.create_line(cx, cy, cx + r, cy, fill="blue", width=1.5)
            c.create_oval(cx - 2, cy - 2, cx + 2, cy + 2, fill="blue")

        elif tool == "angle":
            c.create_line(mid, s - p, p + 2, p + 2, fill="orange", width=2)
            c.create_line(mid, s - p, s - p - 2, p + 2, fill="orange", width=2)

        elif tool == "two_line_angle":
            c.create_line(p, mid - 3, s - p, mid - 3, fill="purple", width=1.5)
            c.create_line(p + 3, s - p, s - p - 3, p, fill="purple", width=1.5)

        elif tool == "polygon_area":
            pts = [mid, p + 2, s - p - 2, mid - 2, s - p - 4, s - p - 2,
                   p + 4, s - p - 2, p + 2, mid - 2]
            c.create_polygon(pts, outline="cyan", fill="", width=1.5)

        elif tool == "coordinate":
            cs = 5
            c.create_line(mid - cs, mid, mid + cs, mid, fill="red", width=1.5)
            c.create_line(mid, mid - cs, mid, mid + cs, fill="red", width=1.5)
            c.create_text(s - p - 2, p + 4, text="xy", fill="red",
                          font=("Arial", 6))

        elif tool == "point_to_line":
            c.create_line(p + 2, p + 4, s - p - 2, p + 4, fill="brown", width=1.5)
            c.create_oval(mid - 2, s - p - 4, mid + 2, s - p, fill="brown")
            c.create_line(mid, s - p - 2, mid, p + 4, fill="brown", width=1, dash=(2, 2))

        elif tool == "arc_length":
            import math
            pts = []
            for i in range(12):
                a = math.radians(200 + i * (300 - 200) / 11)
                x = mid + (mid - p - 1) * math.cos(a)
                y = mid - (mid - p - 1) * math.sin(a)
                pts.extend([x, y])
            if len(pts) >= 4:
                c.create_line(pts, fill="magenta", width=2, smooth=True)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def _on_click(self, tool_name: str):
        self.app.select_tool(tool_name)

    def set_active(self, tool_name: str):
        """Update the visual highlight to reflect the active tool."""
        self._highlight(tool_name)

    def _highlight(self, tool_name: str):
        self.active_tool = tool_name
        for name, btn in self.buttons.items():
            if name == tool_name:
                btn.configure(bg="#cce0ff", highlightbackground="#3388dd")
            else:
                btn.configure(bg="#f0f0f0", highlightbackground="#999")

    # Tooltip ---------------------------------------------------------------

    def _on_enter(self, btn: tk.Canvas, text: str):
        x = btn.winfo_rootx() + btn.winfo_width() // 2
        y = btn.winfo_rooty() + btn.winfo_height() + 4
        self._tip = tk.Toplevel(btn)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(self._tip, text=text, bg="#ffffe0", relief="solid",
                        borderwidth=1, font=("TkDefaultFont", 8))
        lbl.pack()

    def _on_leave(self, btn: tk.Canvas):
        if hasattr(self, "_tip") and self._tip:
            self._tip.destroy()
            self._tip = None
