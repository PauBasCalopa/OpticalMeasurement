"""Tests for undo/redo functionality in ApplicationState."""

import pytest
from core.app_state import ApplicationState
from models.measurement_data import DistanceMeasurement


def _make_measurement(label="test"):
    m = DistanceMeasurement()
    m.label = label
    m.points = [(0, 0), (10, 10)]
    m.result = 14.14
    return m


class TestUndoRedo:
    def setup_method(self):
        self.state = ApplicationState()

    def test_initial_state(self):
        assert not self.state.can_undo
        assert not self.state.can_redo

    def test_undo_add(self):
        m = _make_measurement()
        self.state.add_measurement(m)
        assert len(self.state.measurements) == 1
        assert self.state.can_undo

        self.state.undo()
        assert len(self.state.measurements) == 0
        assert not self.state.can_undo
        assert self.state.can_redo

    def test_redo_add(self):
        m = _make_measurement()
        self.state.add_measurement(m)
        self.state.undo()
        self.state.redo()
        assert len(self.state.measurements) == 1
        assert self.state.measurements[0].id == m.id

    def test_undo_remove(self):
        m = _make_measurement()
        self.state.add_measurement(m)
        self.state.remove_measurement(m.id)
        assert len(self.state.measurements) == 0

        self.state.undo()  # undo remove → re-add
        assert len(self.state.measurements) == 1
        assert self.state.measurements[0].id == m.id

    def test_undo_clear(self):
        m1 = _make_measurement("m1")
        m2 = _make_measurement("m2")
        self.state.add_measurement(m1)
        self.state.add_measurement(m2)
        self.state.clear_measurements()
        assert len(self.state.measurements) == 0

        self.state.undo()  # undo clear → restore both
        assert len(self.state.measurements) == 2

    def test_redo_clear(self):
        m = _make_measurement()
        self.state.add_measurement(m)
        self.state.clear_measurements()
        self.state.undo()
        assert len(self.state.measurements) == 1
        self.state.redo()  # redo clear
        assert len(self.state.measurements) == 0

    def test_new_action_clears_redo(self):
        m1 = _make_measurement("m1")
        m2 = _make_measurement("m2")
        self.state.add_measurement(m1)
        self.state.undo()
        assert self.state.can_redo
        self.state.add_measurement(m2)  # new action clears redo
        assert not self.state.can_redo

    def test_multiple_undo(self):
        m1 = _make_measurement("m1")
        m2 = _make_measurement("m2")
        m3 = _make_measurement("m3")
        self.state.add_measurement(m1)
        self.state.add_measurement(m2)
        self.state.add_measurement(m3)
        assert len(self.state.measurements) == 3

        self.state.undo()
        assert len(self.state.measurements) == 2
        self.state.undo()
        assert len(self.state.measurements) == 1
        self.state.undo()
        assert len(self.state.measurements) == 0
        assert not self.state.can_undo
