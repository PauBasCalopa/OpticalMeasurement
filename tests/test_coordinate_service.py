"""Tests for CoordinateService - pure function tests, no tkinter needed."""

import pytest
from models.view_state import ViewState
from services.coordinate_service import CoordinateService as CS


def make_vs(zoom=1.0, pan_x=0.0, pan_y=0.0, cw=800, ch=600, iw=1000, ih=800):
    return ViewState(zoom=zoom, pan_x=pan_x, pan_y=pan_y,
                     canvas_width=cw, canvas_height=ch,
                     image_width=iw, image_height=ih)


class TestScreenToImage:
    def test_identity_at_zoom1_pan0(self):
        vs = make_vs(zoom=1.0, pan_x=0, pan_y=0)
        assert CS.screen_to_image(100, 200, vs) == (100.0, 200.0)

    def test_with_pan(self):
        vs = make_vs(zoom=1.0, pan_x=50, pan_y=30)
        assert CS.screen_to_image(150, 130, vs) == (100.0, 100.0)

    def test_with_zoom(self):
        vs = make_vs(zoom=2.0, pan_x=0, pan_y=0)
        assert CS.screen_to_image(200, 100, vs) == (100.0, 50.0)

    def test_with_zoom_and_pan(self):
        vs = make_vs(zoom=2.0, pan_x=100, pan_y=50)
        ix, iy = CS.screen_to_image(300, 150, vs)
        assert abs(ix - 100.0) < 1e-9
        assert abs(iy - 50.0) < 1e-9


class TestImageToScreen:
    def test_identity_at_zoom1_pan0(self):
        vs = make_vs(zoom=1.0, pan_x=0, pan_y=0)
        assert CS.image_to_screen(100, 200, vs) == (100.0, 200.0)

    def test_with_pan(self):
        vs = make_vs(zoom=1.0, pan_x=50, pan_y=30)
        assert CS.image_to_screen(100, 100, vs) == (150.0, 130.0)

    def test_with_zoom(self):
        vs = make_vs(zoom=2.0, pan_x=0, pan_y=0)
        assert CS.image_to_screen(100, 50, vs) == (200.0, 100.0)


class TestRoundTrip:
    """The critical property: screen→image→screen must be identity."""
    
    def test_roundtrip_various_states(self):
        states = [
            make_vs(zoom=1.0, pan_x=0, pan_y=0),
            make_vs(zoom=2.5, pan_x=100, pan_y=-50),
            make_vs(zoom=0.3, pan_x=-200, pan_y=300),
            make_vs(zoom=5.0, pan_x=50, pan_y=50),
        ]
        for vs in states:
            for sx, sy in [(0, 0), (400, 300), (799, 599), (100, 500)]:
                ix, iy = CS.screen_to_image(sx, sy, vs)
                sx2, sy2 = CS.image_to_screen(ix, iy, vs)
                assert abs(sx2 - sx) < 1e-6, f"X roundtrip failed: {sx}→{ix}→{sx2} with {vs}"
                assert abs(sy2 - sy) < 1e-6, f"Y roundtrip failed: {sy}→{iy}→{sy2} with {vs}"

    def test_roundtrip_after_pan(self):
        """Simulate: start, pan by delta, check roundtrip still holds."""
        vs = make_vs(zoom=2.0, pan_x=100, pan_y=50)
        # Pan right and down
        vs2 = CS.pan_by_screen_delta(vs, 30, -20)
        
        for sx, sy in [(400, 300), (0, 0), (799, 599)]:
            ix, iy = CS.screen_to_image(sx, sy, vs2)
            sx2, sy2 = CS.image_to_screen(ix, iy, vs2)
            assert abs(sx2 - sx) < 1e-6
            assert abs(sy2 - sy) < 1e-6

    def test_roundtrip_after_zoom_at_point(self):
        """Simulate: zoom at cursor, check roundtrip still holds."""
        vs = make_vs(zoom=1.0, pan_x=0, pan_y=0)
        vs2 = CS.zoom_at_point(vs, 400, 300, 2.5)
        
        for sx, sy in [(400, 300), (0, 0), (799, 599)]:
            ix, iy = CS.screen_to_image(sx, sy, vs2)
            sx2, sy2 = CS.image_to_screen(ix, iy, vs2)
            assert abs(sx2 - sx) < 1e-6
            assert abs(sy2 - sy) < 1e-6


class TestZoomAtPoint:
    def test_point_under_cursor_stays_fixed(self):
        vs = make_vs(zoom=1.0, pan_x=0, pan_y=0)
        cursor_x, cursor_y = 400, 300
        
        # Image coord under cursor before zoom
        ix_before, iy_before = CS.screen_to_image(cursor_x, cursor_y, vs)
        
        # Zoom in
        vs2 = CS.zoom_at_point(vs, cursor_x, cursor_y, 3.0)
        
        # Image coord under cursor after zoom
        ix_after, iy_after = CS.screen_to_image(cursor_x, cursor_y, vs2)
        
        assert abs(ix_after - ix_before) < 1e-6
        assert abs(iy_after - iy_before) < 1e-6

    def test_zoom_clamped(self):
        vs = make_vs(zoom=1.0)
        vs2 = CS.zoom_at_point(vs, 400, 300, 100.0, max_zoom=20.0)
        assert vs2.zoom == 20.0
        
        vs3 = CS.zoom_at_point(vs, 400, 300, 0.001, min_zoom=0.1)
        assert vs3.zoom == 0.1


class TestFitToWindow:
    def test_landscape_image_in_landscape_canvas(self):
        vs = make_vs(cw=800, ch=600, iw=1600, ih=1200)
        fitted = CS.fit_to_window(vs, margin=0)
        assert abs(fitted.zoom - 0.5) < 1e-6  # 800/1600 = 600/1200 = 0.5

    def test_image_is_centered(self):
        vs = make_vs(cw=800, ch=600, iw=400, ih=200)
        fitted = CS.fit_to_window(vs, margin=0)
        # zoom should be 2.0 (limited by height: 600/200=3, width: 800/400=2)
        # Wait - fit uses min, so zoom = min(2.0, 3.0) = 2.0
        assert abs(fitted.zoom - 2.0) < 1e-6
        # Image display size: 800x400, centered in 800x600
        assert abs(fitted.pan_x - 0) < 1e-6   # 800 - 800 = 0, centered = 0
        assert abs(fitted.pan_y - 100) < 1e-6  # 600 - 400 = 200, centered = 100


class TestClampPan:
    def test_small_image_is_centered(self):
        vs = make_vs(zoom=0.5, pan_x=999, pan_y=999, cw=800, ch=600, iw=400, ih=400)
        clamped = CS.clamp_pan(vs)
        # display: 200x200 in 800x600 → centered
        assert abs(clamped.pan_x - 300) < 1e-6  # (800-200)/2
        assert abs(clamped.pan_y - 200) < 1e-6  # (600-200)/2

    def test_large_image_cant_pan_too_far(self):
        vs = make_vs(zoom=2.0, pan_x=-5000, pan_y=-5000, cw=800, ch=600, iw=1000, ih=800)
        clamped = CS.clamp_pan(vs)
        # display: 2000x1600, margin = 50 (min(50, 200))
        # min_x = 800 - 2000 - 50 = -1250
        assert clamped.pan_x >= -1250
        assert clamped.pan_y >= -1550  # 600 - 1600 - 50
