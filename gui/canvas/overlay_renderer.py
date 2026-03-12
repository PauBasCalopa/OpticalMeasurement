"""
Overlay Renderer

Renders measurement overlays on a tkinter Canvas.
Stateless: each call to render_all() clears existing overlays and redraws
from the authoritative list of measurements.  No item-id tracking needed.
"""

from typing import List, Tuple
from models.measurement_data import MeasurementBase
from models.view_state import ViewState
from services.coordinate_service import CoordinateService

# Measurement-type → colour mapping
_COLORS = {
    "distance": "green",
    "radius": "blue",
    "angle": "orange",
    "two_line_angle": "purple",
    "polygon_area": "cyan",
    "coordinate": "red",
    "point_to_line": "brown",
    "arc_length": "magenta",
}

_TAG = "overlay"          # All overlay items share this tag
_HIGHLIGHT_TAG = "overlay_highlight"
_GRID_TAG = "grid_overlay"
_FONT = ("Arial", 8)


class OverlayRenderer:
    """Renders measurement overlays on the canvas."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.visible = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render_all(self, measurements: List[MeasurementBase], view_state: ViewState):
        """Clear and redraw every measurement overlay."""
        self.canvas.delete(_TAG)
        if not self.visible:
            return
        for m in measurements:
            self._render_one(m, view_state)

    def draw_measurement_overlay(self, measurement: MeasurementBase):
        """Draw a single newly-added measurement (incremental)."""
        if not self.visible:
            return
        self._render_one(measurement, self.canvas.view_state)

    def remove_measurement_overlay(self, measurement_id: str):
        """Remove overlays for one measurement."""
        self.canvas.delete(f"m_{measurement_id}")

    def clear_all_overlays(self):
        """Remove every overlay from the canvas."""
        self.canvas.delete(_TAG)

    def redraw_all_overlays(self):
        """Convenience: re-render from app_state."""
        from core.app_state import app_state
        self.render_all(app_state.measurements, self.canvas.view_state)

    def toggle_visibility(self) -> bool:
        self.visible = not self.visible
        if self.visible:
            self.redraw_all_overlays()
        else:
            self.canvas.delete(_TAG)
        return self.visible

    def set_visibility(self, v: bool):
        if self.visible != v:
            self.toggle_visibility()

    def get_visibility(self) -> bool:
        return self.visible

    def render_grid(self, view_state: ViewState, spacing: int = 50, color: str = "#cccccc"):
        """Render a grid overlay in image coordinates."""
        self.canvas.delete(_GRID_TAG)
        if view_state.image_width <= 0 or view_state.image_height <= 0:
            return
        # Draw vertical lines
        x = 0
        while x <= view_state.image_width:
            sx1, sy1 = self._s(x, 0, view_state)
            sx2, sy2 = self._s(x, view_state.image_height, view_state)
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=1,
                                    dash=(2, 4), tags=(_GRID_TAG,))
            x += spacing
        # Draw horizontal lines
        y = 0
        while y <= view_state.image_height:
            sx1, sy1 = self._s(0, y, view_state)
            sx2, sy2 = self._s(view_state.image_width, y, view_state)
            self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color, width=1,
                                    dash=(2, 4), tags=(_GRID_TAG,))
            y += spacing
        # Grid sits below measurement overlays (only if overlay items exist)
        if self.canvas.find_withtag(_TAG):
            self.canvas.tag_lower(_GRID_TAG, _TAG)

    def clear_grid(self):
        """Remove grid overlay."""
        self.canvas.delete(_GRID_TAG)

    def highlight_measurement(self, measurement_id: str):
        """Draw a yellow highlight behind a specific measurement's items."""
        self.clear_highlight()
        tag = f"m_{measurement_id}"
        items = self.canvas.find_withtag(tag)
        for item in items:
            itype = self.canvas.type(item)
            coords = self.canvas.coords(item)
            if not coords:
                continue
            if itype == "line":
                self.canvas.create_line(
                    *coords, fill="yellow", width=5,
                    tags=(_HIGHLIGHT_TAG,))
            elif itype == "oval":
                self.canvas.create_oval(
                    *coords, outline="yellow", width=3,
                    tags=(_HIGHLIGHT_TAG,))
            elif itype == "text":
                cx, cy = coords[0], coords[1]
                self.canvas.create_rectangle(
                    cx - 30, cy - 8, cx + 30, cy + 8,
                    outline="yellow", width=2,
                    tags=(_HIGHLIGHT_TAG,))
        # Ensure highlights sit behind the actual overlays (only if overlay items exist)
        if self.canvas.find_withtag(_TAG):
            self.canvas.tag_lower(_HIGHLIGHT_TAG, _TAG)

    def clear_highlight(self):
        """Remove any highlight."""
        self.canvas.delete(_HIGHLIGHT_TAG)

    def find_measurement_at(self, screen_x: int, screen_y: int) -> str | None:
        """Return the measurement_id of the overlay nearest to (screen_x, screen_y), or None."""
        items = self.canvas.find_overlapping(
            screen_x - 5, screen_y - 5, screen_x + 5, screen_y + 5)
        for item in items:
            tags = self.canvas.gettags(item)
            for t in tags:
                if t.startswith("m_"):
                    return t[2:]  # strip "m_" prefix → measurement id
        return None

    # ------------------------------------------------------------------
    # Internal: dispatch to per-type renderers
    # ------------------------------------------------------------------

    def _render_one(self, m: MeasurementBase, vs: ViewState):
        handler = {
            "distance": self._r_distance,
            "radius": self._r_radius,
            "angle": self._r_angle,
            "two_line_angle": self._r_two_line_angle,
            "polygon_area": self._r_polygon,
            "coordinate": self._r_coordinate,
            "point_to_line": self._r_point_to_line,
            "arc_length": self._r_arc_length,
        }.get(m.measurement_type)
        if handler:
            handler(m, vs)

    # helpers ---------------------------------------------------------------

    def _s(self, ix: float, iy: float, vs: ViewState) -> Tuple[int, int]:
        """Image → screen coordinate shorthand."""
        sx, sy = CoordinateService.image_to_screen(ix, iy, vs)
        return int(sx), int(sy)

    def _tags(self, m: MeasurementBase) -> tuple:
        return (_TAG, f"m_{m.id}")

    def _label(self, m: MeasurementBase) -> str:
        return self.canvas.measurement_engine.format_measurement_result(m)

    def _text(self, sx, sy, text, color, m):
        self.canvas.create_text(sx, sy, text=text, fill=color,
                                font=_FONT, tags=self._tags(m))

    def _line(self, sx1, sy1, sx2, sy2, color, m, **kw):
        self.canvas.create_line(sx1, sy1, sx2, sy2, fill=color,
                                width=kw.get("width", 2),
                                tags=self._tags(m), **{k: v for k, v in kw.items() if k != "width"})

    def _oval(self, cx, cy, r, color, m, **kw):
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                tags=self._tags(m), **kw)

    # --- Per-type renderers ------------------------------------------------

    def _r_distance(self, m, vs):
        if len(m.points) < 2:
            return
        s1 = self._s(*m.points[0], vs)
        s2 = self._s(*m.points[1], vs)
        c = _COLORS["distance"]
        self._line(*s1, *s2, c, m)
        mx, my = (s1[0] + s2[0]) // 2, (s1[1] + s2[1]) // 2
        self._text(mx, my - 10, self._label(m), c, m)

    def _r_radius(self, m, vs):
        if not (hasattr(m, 'center_point') and m.center_point):
            return
        c = _COLORS["radius"]
        cs = self._s(*m.center_point, vs)
        cal = self.canvas.measurement_engine.calibration
        rpx = (m.result / cal.scale_factor) if (cal and cal.is_calibrated) else m.result
        rs = rpx * vs.zoom
        self._oval(*cs, rs, c, m, outline=c, width=2)
        self._oval(*cs, 2, c, m, fill=c, outline=c)
        self._text(cs[0], cs[1] - rs - 15, self._label(m), c, m)

    def _r_angle(self, m, vs):
        if len(m.points) < 3:
            return
        c = _COLORS["angle"]
        sv = self._s(*m.points[1], vs)
        s1 = self._s(*m.points[0], vs)
        s3 = self._s(*m.points[2], vs)
        self._line(*sv, *s1, c, m)
        self._line(*sv, *s3, c, m)
        self._text(sv[0] + 20, sv[1] - 20, self._label(m), c, m)

    def _r_two_line_angle(self, m, vs):
        if len(m.points) < 4:
            return
        c = _COLORS["two_line_angle"]
        sp = [self._s(*p, vs) for p in m.points]
        self._line(*sp[0], *sp[1], c, m)
        self._line(*sp[2], *sp[3], c, m)
        mx = sum(p[0] for p in sp) // 4
        my = sum(p[1] for p in sp) // 4
        self._text(mx, my - 15, self._label(m), c, m)

    def _r_polygon(self, m, vs):
        if len(m.points) < 3:
            return
        c = _COLORS["polygon_area"]
        sp = [self._s(*p, vs) for p in m.points]
        for i in range(len(sp)):
            ni = (i + 1) % len(sp)
            self._line(*sp[i], *sp[ni], c, m)
        cx = sum(p[0] for p in sp) // len(sp)
        cy = sum(p[1] for p in sp) // len(sp)
        label = self._label(m)
        parts = label.split(" | ")
        if len(parts) == 2:
            self._text(cx, cy - 8, parts[0], c, m)
            self._text(cx, cy + 8, parts[1], c, m)
        else:
            self._text(cx, cy, label, c, m)

    def _r_coordinate(self, m, vs):
        if len(m.points) < 1:
            return
        c = _COLORS["coordinate"]
        cs = 5  # crosshair size
        s1 = self._s(*m.points[0], vs)
        self._line(s1[0] - cs, s1[1], s1[0] + cs, s1[1], c, m)
        self._line(s1[0], s1[1] - cs, s1[0], s1[1] + cs, c, m)
        self._text(s1[0] + 15, s1[1] - 15, self._label(m), c, m)

        if (hasattr(m, 'coordinate_type') and m.coordinate_type == "difference"
                and len(m.points) >= 2):
            s2 = self._s(*m.points[1], vs)
            self._line(s2[0] - cs, s2[1], s2[0] + cs, s2[1], c, m)
            self._line(s2[0], s2[1] - cs, s2[0], s2[1] + cs, c, m)
            self._line(*s1, *s2, c, m, width=1, dash=(5, 5))

    def _r_point_to_line(self, m, vs):
        if len(m.points) < 3:
            return
        c = _COLORS["point_to_line"]
        sp = self._s(*m.points[0], vs)
        sl = self._s(*m.points[1], vs)
        se = self._s(*m.points[2], vs)
        self._line(*sl, *se, c, m)
        self._oval(*sp, 3, c, m, fill=c, outline="white", width=1)

        # Perpendicular to closest point on line (image coords → screen)
        from utils.math_utils import find_closest_point_on_line
        closest = find_closest_point_on_line(m.points[0], m.points[1], m.points[2])
        sc = self._s(*closest, vs)
        self._line(*sp, *sc, c, m, width=1, dash=(3, 3))

        tx = (sp[0] + sc[0]) // 2
        ty = (sp[1] + sc[1]) // 2
        self._text(tx, ty - 10, self._label(m), c, m)

    def _r_arc_length(self, m, vs):
        if len(m.points) < 3:
            return
        c = _COLORS["arc_length"]
        sp = [self._s(*p, vs) for p in m.points]
        for i in range(len(sp) - 1):
            self._line(*sp[i], *sp[i + 1], c, m, width=3)
        for p in sp:
            self._oval(*p, 2, c, m, fill=c, outline=c)
        if hasattr(m, 'center_point') and m.center_point:
            sc = self._s(*m.center_point, vs)
            self._oval(*sc, 2, c, m, fill=c, outline="white", width=1)
        tx = sum(p[0] for p in sp) // len(sp)
        ty = sum(p[1] for p in sp) // len(sp)
        self._text(tx, ty - 20, self._label(m), c, m)
