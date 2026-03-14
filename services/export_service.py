"""
Export Service

Renders measurement overlays onto a PIL Image and saves to disk.
Extracted from ImageCanvas to decouple export logic from the GUI widget.
"""

from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

from models.measurement_data import MeasurementBase
from core.measurement_engine import MeasurementEngine


class ExportService:
    """Renders measurements onto an image and exports it."""

    def __init__(self, measurement_engine: MeasurementEngine):
        self.measurement_engine = measurement_engine

    def export(self, original_image: Image.Image, measurements: List[MeasurementBase],
               filename: str, overlays_visible: bool = True):
        """Export *original_image* with measurement annotations burned in.

        Parameters
        ----------
        original_image : PIL.Image
            The original (unscaled) image.
        measurements : list[MeasurementBase]
            All measurements to render.
        filename : str
            Destination path.  Extension determines format.
        overlays_visible : bool
            If False, measurements are skipped (image saved as-is).
        """
        export_image = original_image.copy()
        draw = ImageDraw.Draw(export_image)

        font = self._load_font(export_image.width)

        if overlays_visible:
            for measurement in measurements:
                self._draw_measurement(draw, measurement, export_image.size, font)

        # Save
        format_ext = filename.lower().rsplit('.', 1)[-1]
        if format_ext == 'jpg':
            format_ext = 'jpeg'

        if format_ext.upper() == 'JPEG':
            export_image.save(filename, format='JPEG', quality=95, optimize=True)
        else:
            export_image.save(filename, format=format_ext.upper())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_font(image_width: int) -> Optional[ImageFont.FreeTypeFont]:
        font_size = max(12, min(24, int(image_width / 80)))
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            try:
                return ImageFont.load_default()
            except Exception:
                return None

    def _draw_measurement(self, draw: ImageDraw.ImageDraw, measurement: MeasurementBase,
                          image_size: tuple, font):
        """Draw a single measurement overlay on the PIL image."""
        line_width = max(2, int(min(image_size) / 500))

        handler = {
            "distance": self._draw_distance,
            "radius": self._draw_radius,
            "angle": self._draw_angle,
            "two_line_angle": self._draw_two_line_angle,
            "polygon_area": self._draw_polygon_area,
            "coordinate": self._draw_coordinate,
            "point_to_line": self._draw_point_to_line,
            "arc_length": self._draw_arc_length,
        }.get(measurement.measurement_type)

        if handler:
            handler(draw, measurement, line_width, font)

    # --- Per-type renderers ------------------------------------------------

    def _draw_distance(self, draw, m, lw, font):
        x1, y1 = m.points[0]
        x2, y2 = m.points[1]
        draw.line([(x1, y1), (x2, y2)], fill="green", width=lw)

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 - 15
        self._draw_label(draw, mid_x, mid_y, m, font, "green")

    def _draw_radius(self, draw, m, lw, font):
        if not (hasattr(m, 'center_point') and m.center_point):
            return
        cx, cy = m.center_point
        cal = self.measurement_engine.calibration
        radius_px = (m.result / cal.scale_factor) if (cal and cal.is_calibrated) else m.result

        draw.ellipse([cx - radius_px, cy - radius_px, cx + radius_px, cy + radius_px],
                     outline="blue", width=lw)
        ps = lw * 2
        draw.ellipse([cx - ps, cy - ps, cx + ps, cy + ps], fill="blue")
        self._draw_label(draw, cx, cy - radius_px - 20, m, font, "blue")

    def _draw_angle(self, draw, m, lw, font):
        if len(m.points) < 3:
            return
        vx, vy = m.points[1]
        draw.line([(vx, vy), m.points[0]], fill="orange", width=lw)
        draw.line([(vx, vy), m.points[2]], fill="orange", width=lw)
        self._draw_label(draw, vx + 20, vy - 20, m, font, "orange")

    def _draw_two_line_angle(self, draw, m, lw, font):
        if len(m.points) < 4:
            return
        draw.line([m.points[0], m.points[1]], fill="purple", width=lw)
        draw.line([m.points[2], m.points[3]], fill="purple", width=lw)
        cx = sum(p[0] for p in m.points) / 4
        cy = sum(p[1] for p in m.points) / 4 - 15
        self._draw_label(draw, cx, cy, m, font, "purple")

    def _draw_polygon_area(self, draw, m, lw, font):
        if len(m.points) < 3:
            return
        coords = [(p[0], p[1]) for p in m.points]
        for i in range(len(coords)):
            draw.line([coords[i], coords[(i + 1) % len(coords)]], fill="cyan", width=lw)
        cx = sum(p[0] for p in coords) / len(coords)
        cy = sum(p[1] for p in coords) / len(coords)
        label = self.measurement_engine.format_measurement_result(m)
        parts = label.split(" | ")
        if len(parts) == 2:
            self._draw_text_with_bg(draw, cx, cy - 12, parts[0], font, "cyan", "cyan")
            self._draw_text_with_bg(draw, cx, cy + 12, parts[1], font, "cyan", "cyan")
        else:
            self._draw_label(draw, cx, cy, m, font, "cyan")

    def _draw_coordinate(self, draw, m, lw, font):
        for i, point in enumerate(m.points):
            x, y = point
            ps = lw * 3
            draw.ellipse([x - ps, y - ps, x + ps, y + ps], fill="yellow", outline="black", width=1)

            if m.coordinate_type == "single":
                coord_text = f"({x:.1f}, {y:.1f})"
            elif m.coordinate_type == "difference":
                coord_text = f"P{i+1} ({x:.1f}, {y:.1f})"
            else:
                coord_text = f"P{i+1}"

            self._draw_text_with_bg(draw, x + 15, y - 15, coord_text, font, "black", "yellow")
        
        # For difference mode, draw dashed line and delta info at midpoint
        if m.coordinate_type == "difference" and len(m.points) >= 2:
            draw.line([m.points[0], m.points[1]], fill="yellow", width=lw)
            mx = (m.points[0][0] + m.points[1][0]) / 2
            my = (m.points[0][1] + m.points[1][1]) / 2
            label = self.measurement_engine.format_measurement_result(m)
            parts = label.split(" | ")
            if len(parts) == 2:
                self._draw_text_with_bg(draw, mx, my - 12, parts[0], font, "black", "yellow")
                self._draw_text_with_bg(draw, mx, my + 12, parts[1], font, "black", "yellow")
            else:
                self._draw_text_with_bg(draw, mx, my, label, font, "black", "yellow")

    def _draw_point_to_line(self, draw, m, lw, font):
        if len(m.points) < 3:
            return
        point, line_start, line_end = m.points[0], m.points[1], m.points[2]

        from utils.math_utils import find_closest_point_on_line
        closest = find_closest_point_on_line(point, line_start, line_end)

        draw.line([line_start, line_end], fill="red", width=lw)
        ps = lw * 2
        draw.ellipse([point[0] - ps, point[1] - ps, point[0] + ps, point[1] + ps],
                     fill="red", outline="white", width=1)
        draw.line([point, closest], fill="red", width=lw)
        ms = lw
        draw.ellipse([closest[0] - ms, closest[1] - ms, closest[0] + ms, closest[1] + ms],
                     fill="yellow", outline="red", width=1)
        self._draw_label(draw, point[0] + 20, point[1] - 20, m, font, "red")

    def _draw_arc_length(self, draw, m, lw, font):
        if len(m.points) < 3:
            return
        # Draw point markers
        for pt in m.points:
            ps = lw * 2
            draw.ellipse([pt[0] - ps, pt[1] - ps, pt[0] + ps, pt[1] + ps],
                         fill="magenta", outline="white", width=1)
        
        # Draw arc curve if center is known
        if hasattr(m, 'center_point') and m.center_point:
            import math
            from utils.math_utils import calculate_circle_center_radius
            center = m.center_point
            # Get pixel radius
            cal = self.measurement_engine.calibration
            rpx = (m.radius / cal.scale_factor) if (cal and cal.is_calibrated and m.radius) else (m.radius or 0)
            
            # Calculate angles
            angle1 = math.atan2(m.points[0][1] - center[1], m.points[0][0] - center[0])
            angle2 = math.atan2(m.points[1][1] - center[1], m.points[1][0] - center[0])
            angle3 = math.atan2(m.points[2][1] - center[1], m.points[2][0] - center[0])
            
            def norm(a):
                return a % (2 * math.pi)
            a1, a2, a3 = norm(angle1), norm(angle2), norm(angle3)
            
            def ccw_between(start, mid, end):
                if start <= end:
                    return start <= mid <= end
                else:
                    return mid >= start or mid <= end
            
            if ccw_between(a1, a2, a3):
                if a3 >= a1:
                    sweep = a3 - a1
                else:
                    sweep = (2 * math.pi - a1) + a3
                start_angle = a1
            else:
                if a1 >= a3:
                    sweep = a1 - a3
                else:
                    sweep = (2 * math.pi - a3) + a1
                start_angle = a3
            
            # Generate arc polyline
            num_segments = max(24, int(sweep / math.pi * 48))
            arc_pts = []
            for i in range(num_segments + 1):
                frac = i / num_segments
                a = start_angle + frac * sweep
                ix = center[0] + rpx * math.cos(a)
                iy = center[1] + rpx * math.sin(a)
                arc_pts.append((ix, iy))
            
            if len(arc_pts) >= 2:
                draw.line(arc_pts, fill="magenta", width=lw, joint="curve")
            
            # Center dot
            cs = lw
            draw.ellipse([center[0] - cs, center[1] - cs, center[0] + cs, center[1] + cs],
                         fill="magenta", outline="white", width=1)
        else:
            # Fallback: straight lines
            for i in range(len(m.points) - 1):
                draw.line([m.points[i], m.points[i + 1]], fill="magenta", width=lw)
        
        # Multi-line label
        cx = sum(p[0] for p in m.points) / len(m.points)
        cy = sum(p[1] for p in m.points) / len(m.points)
        label = self.measurement_engine.format_measurement_result(m)
        parts = label.split(" | ")
        y_offset = -(len(parts) * 14) // 2
        for i, part in enumerate(parts):
            self._draw_text_with_bg(draw, cx, cy + y_offset + i * 14, part, font, "magenta", "magenta")

    # --- Text helpers -------------------------------------------------------

    def _draw_label(self, draw, x, y, measurement, font, color):
        """Draw formatted measurement result at (x, y)."""
        text = self.measurement_engine.format_measurement_result(measurement)
        self._draw_text_with_bg(draw, x, y, text, font, color, color)

    @staticmethod
    def _draw_text_with_bg(draw, x, y, text, font, text_color, outline_color):
        """Draw text with a white background rectangle for readability."""
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.rectangle([x - tw // 2 - 2, y - th // 2 - 2,
                            x + tw // 2 + 2, y + th // 2 + 2],
                           fill="white", outline=outline_color)
            draw.text((x - tw // 2, y - th // 2), text, fill=text_color, font=font)
        else:
            draw.text((x, y), text, fill=text_color)
