"""
Minimap Widget

Shows a thumbnail of the full image with a rectangle indicating the
current viewport region. Clicking on the minimap pans the main canvas.
"""

import tkinter as tk
from typing import Optional
from PIL import Image, ImageTk

from models.view_state import ViewState


class MinimapWidget(tk.Canvas):
    """Small canvas that shows an overview thumbnail + viewport rectangle."""

    WIDTH = 200
    HEIGHT = 150

    def __init__(self, parent, app, **kwargs):
        kwargs.setdefault("width", self.WIDTH)
        kwargs.setdefault("height", self.HEIGHT)
        kwargs.setdefault("bg", "#2b2b2b")
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", "#555")
        super().__init__(parent, **kwargs)

        self.app = app
        self._thumb: Optional[ImageTk.PhotoImage] = None
        self._thumb_pil: Optional[Image.Image] = None
        self._scale = 1.0  # image-px → minimap-px
        self._offset_x = 0
        self._offset_y = 0

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_click)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def update_minimap(self, view_state: ViewState):
        """Redraw thumbnail and viewport rect for the given ViewState."""
        self.delete("all")

        img_mgr = self.app.image_manager
        if img_mgr.current_image_data is None or img_mgr.current_image_data.original_image is None:
            return

        src = img_mgr.current_image_data.original_image
        iw, ih = src.size
        cw = self.winfo_width() or self.WIDTH
        ch = self.winfo_height() or self.HEIGHT

        # Fit thumbnail inside minimap
        scale_x = cw / iw
        scale_y = ch / ih
        self._scale = min(scale_x, scale_y)
        tw = int(iw * self._scale)
        th = int(ih * self._scale)
        self._offset_x = (cw - tw) // 2
        self._offset_y = (ch - th) // 2

        # Create thumbnail
        self._thumb_pil = src.resize((max(1, tw), max(1, th)), Image.Resampling.LANCZOS)
        self._thumb = ImageTk.PhotoImage(self._thumb_pil)
        self.create_image(self._offset_x, self._offset_y, anchor=tk.NW, image=self._thumb)

        # Viewport rectangle
        vs = view_state
        if vs.zoom <= 0:
            return

        # Visible region in image coords
        vx0 = -vs.pan_x / vs.zoom
        vy0 = -vs.pan_y / vs.zoom
        vx1 = vx0 + vs.canvas_width / vs.zoom
        vy1 = vy0 + vs.canvas_height / vs.zoom

        # Clamp to image bounds
        vx0 = max(0, vx0)
        vy0 = max(0, vy0)
        vx1 = min(iw, vx1)
        vy1 = min(ih, vy1)

        # Convert to minimap coords
        rx0 = self._offset_x + vx0 * self._scale
        ry0 = self._offset_y + vy0 * self._scale
        rx1 = self._offset_x + vx1 * self._scale
        ry1 = self._offset_y + vy1 * self._scale

        self.create_rectangle(rx0, ry0, rx1, ry1, outline="yellow", width=2)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def _on_click(self, event):
        """Pan main canvas so that the clicked minimap point is centred."""
        if self._scale <= 0 or not hasattr(self.app, 'canvas'):
            return

        # Minimap click → image coords
        ix = (event.x - self._offset_x) / self._scale
        iy = (event.y - self._offset_y) / self._scale

        vs = self.app.canvas.view_state
        # New pan so that (ix, iy) is at centre of canvas
        new_pan_x = vs.canvas_width / 2 - ix * vs.zoom
        new_pan_y = vs.canvas_height / 2 - iy * vs.zoom
        new_vs = vs.with_pan(new_pan_x, new_pan_y)
        self.app.canvas._update_view_state(new_vs)
        self.app.canvas._refresh_display()
