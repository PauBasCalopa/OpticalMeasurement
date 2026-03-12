# Pla d'Acció: Reestructuració Arquitectura OpticalMeasurement

## Objectiu
Reestructurar l'aplicació per tenir un flux de dades unidireccional, un sistema de coordenades robust (sense drift amb pan/zoom), i una separació clara entre lògica i presentació.

---

## Fase 0: Preparació

### 0.1 Netejar codi mort
- Eliminar `bind_events()` a `canvas_widget.py` (duplicat de `EventManager.bind_all_events()`)
- Eliminar mètodes legacy no usats
- Eliminar fitxers de docs/ obsolets (reports de cleanup anteriors)
- Eliminar tests/ que validen l'arquitectura antiga

### 0.2 Establir tests de referència
- Crear tests manuals documentats: obrir imatge, calibrar, mesurar, pan, zoom
- Verificar que l'app s'obre i les funcions bàsiques operen (encara que amb bugs)

---

## Fase 1: ViewState + CoordinateService (Resolució del problema de coordenades)

**Objectiu:** Eliminar el drift de coordenades canviant el model mental de "moure la imatge al canvas" a "canviar un viewport sobre la imatge".

### 1.1 Crear `ViewState` (dataclass)
```python
@dataclass
class ViewState:
    zoom: float = 1.0
    pan_offset_x: float = 0.0  # En coordenades d'imatge
    pan_offset_y: float = 0.0  # En coordenades d'imatge
    canvas_width: int = 0
    canvas_height: int = 0
    image_width: int = 0
    image_height: int = 0
```
- Fitxer: `models/view_state.py`
- Pan i zoom es representen com a estat pur, no com a posició d'un canvas item

### 1.2 Crear `CoordinateService` (funcions pures)
```python
class CoordinateService:
    @staticmethod
    def screen_to_image(screen_x, screen_y, view_state) -> (float, float)
    
    @staticmethod
    def image_to_screen(image_x, image_y, view_state) -> (int, int)
    
    @staticmethod
    def get_visible_image_rect(view_state) -> (x, y, w, h)
    
    @staticmethod
    def clamp_pan(view_state) -> ViewState  # Límits de pan
    
    @staticmethod
    def zoom_at_point(view_state, screen_x, screen_y, new_zoom) -> ViewState
    
    @staticmethod
    def fit_to_window(view_state) -> ViewState
```
- Fitxer: `services/coordinate_service.py`
- **Zero estat intern** — rep ViewState, retorna resultats o nou ViewState
- **Testable unitàriament** sense cap dependència de tkinter

### 1.3 Integrar amb `AppState`
- Afegir `view_state: ViewState` a `ApplicationState`
- Pan = `app_state.update_view_state(new_view_state)` → notifica observers
- Zoom = `app_state.update_view_state(new_view_state)` → notifica observers

### 1.4 Adaptar `ImageCanvas` al nou model
- Eliminar `_apply_smart_pan_boundaries()`, `_stabilize_coordinate_system()`, `_update_actual_zoom_level()`
- Eliminar `_force_coordinate_system_refresh()`
- El canvas NO mou items — repinta basant-se en ViewState
- `update_display()` és l'únic mètode que pinta:
  1. Calcula posició imatge a partir de ViewState
  2. Posiciona el canvas item amb `coords()`
  3. Repinta overlays

### 1.5 Adaptar `EventManager`
- Pan drag: calcula delta en coordenades d'imatge, actualitza ViewState
- Eliminar tota la lògica de validació post-pan (ja no cal)
- Eliminar `_stabilize_coordinate_system()` calls

### 1.6 Eliminar `CoordinateManager` (antiga)
- Tota la seva funcionalitat la cobreix `CoordinateService`
- `gui/canvas/coordinate_manager.py` → eliminat

---

## Fase 2: Simplificar ImageCanvas (desacoblar el God Object) ✅ COMPLETADA

### 2.1 Extreure lògica de zoom a `CoordinateService` ✅
- Fet a Fase 1 — zoom ja calcula ViewState via CoordinateService

### 2.2 Extreure `complete_measurement()` a `MeasurementEngine` ✅
- `MeasurementEngine.complete(tool_type, points)` creat
- `ImageCanvas.complete_measurement()` reduït a 3 línies significatives

### 2.3 Extreure export a `ExportService` ✅
- `services/export_service.py` creat amb tota la lògica de renderitzat
- `main_window.py` crida directament `ExportService.export()`
- ~350 línies eliminades de `canvas_widget.py`

### 2.4 Netejar `ImageCanvas` ✅
- De ~750 línies a ~367 línies
- Imports no usats eliminats (math, Image, ImageDraw, ImageFont)

---

## Fase 3: Flux unidireccional d'events ✅ COMPLETADA

### 3.1 Refactoritzar `EventManager` ✅
- `handle_left_click` delega a calibration_handler o tool_handler — sense switch de tool types
- `handle_left_drag/release` deleguen a tool_handler (PanTool gestiona pan)
- Right-click pan unificat; `pan_start` eliminat d'EventManager
- EventManager: de ~120 a 109 línies, molt més simple

### 3.2 Simplificar ToolHandler + Tools ✅
- Nou `ToolResult` (NONE, ADD_POINT, COMPLETE) definit a `base_tool.py`
- `BaseTool.handle_click(image_x, image_y, point_count) → ToolResult` — rep coords d'imatge
- Tools ja no dibuixen al canvas ni gestionen temp_points
- ToolHandler processa ToolResult: afegeix punt, dibuixa marker temp, completa mesura
- Eliminat codi fallback `_check_measurement_completion`

### 3.3 Unificar gestió de punts temporals ✅
- `temp_points` ara viu a `ToolHandler`, no a `ImageCanvas`
- `temp_overlays` list eliminat — ús de tags "temp" directament
- `ImageCanvas.complete_measurement()` eliminat — ToolHandler._complete_measurement() és l'únic path
- `ImageCanvas`: de 367 a 308 línies

---

## Fase 4: OverlayRenderer ✅ COMPLETADA

### 4.1 Refactoritzar `OverlayManager` → `OverlayRenderer` ✅
- `OverlayRenderer` sense dict d'item IDs — usa tags tkinter (`overlay`, `m_{id}`)
- `render_all()` esborra i repinta; `draw_measurement_overlay()` incremental
- `remove_measurement_overlay(id)` → `canvas.delete(f"m_{id}")`
- Visibilitat via `toggle_visibility()` que esborra/repinta tot
- Arreglat bug `point_to_line`: ara usa `find_closest_point_on_line` per la perpendicular real

### 4.2 Separar lògica de dibuix de lògica de geometria del overlay ✅
- Cada `_r_{type}` rep `(measurement, view_state)` i converteix image→screen amb `CoordinateService`
- Helper `_s(ix, iy, vs)` centralitza la conversió
- Helpers `_line`, `_text`, `_oval` apliquen tags automàticament

---

## Fase 5: Polish i Features pendents ✅ COMPLETADA

### 5.1 Undo/Redo ✅
- Command stack a `AppState` (`_UndoEntry` amb kind add/remove/clear)
- `undo()` / `redo()` reverteixen/reapliquen accions de mesura
- Ctrl+Z / Ctrl+Y connectats via menú Edit (enable/disable dinàmic)
- 8 tests unitaris a `tests/test_undo_redo.py`

### 5.2 Millorar UX del Sidebar ✅
- Selecció al sidebar → highlight groc (halo) de l'overlay al canvas
- Click sobre overlay (en mode pan) → selecció automàtica al sidebar
- `OverlayRenderer.highlight_measurement()` / `clear_highlight()`
- `OverlayRenderer.find_measurement_at()` per hit-test per tags

### 5.3 Millorar feedback visual de les tools ✅
- Línia de preview (dash) del darrer punt posat fins al cursor
- `ToolHandler.handle_motion()` dibuixa preview amb tag `"preview"`
- Es neteja automàticament en cancel·lar o completar la mesura

---

## Estructura de fitxers resultant

```
core/
    app_state.py          # Estat centralitzat (refactored)
    image_manager.py      # Càrrega i cache d'imatges (simplificat)

models/
    calibration_data.py   # (sense canvis)
    image_data.py         # (sense canvis)
    measurement_data.py   # (sense canvis)
    view_state.py         # NOU: ViewState dataclass

services/
    coordinate_service.py # NOU: Conversions screen↔image (funcions pures)
    measurement_service.py# RENOMBRAT de measurement_engine.py
    export_service.py     # NOU: Exportació d'imatge amb overlays

gui/
    main_window.py        # Finestra principal (simplificat)
    dialogs.py            # (sense canvis)
    menus.py              # (sense canvis)
    canvas/
        image_viewport.py # RENOMBRAT de canvas_widget.py (reduït a ~150 línies)
        event_handler.py  # RENOMBRAT de event_manager.py (simplificat)
        tool_handler.py   # (simplificat)
        overlay_renderer.py # RENOMBRAT de overlay_manager.py
        calibration_handler.py # (simplificat)
        tools/
            base_tool.py       # (simplificat)
            measurement_tool.py
            pan_tool.py
            polygon_tool.py

utils/
    math_utils.py         # (sense canvis)

# ELIMINATS:
#   gui/canvas/coordinate_manager.py  → reemplaçat per services/coordinate_service.py
```

---

## Ordre d'Implementació i Dependències

```
Fase 0 ──→ Fase 1 ──→ Fase 2 ──→ Fase 3 ──→ Fase 4 ──→ Fase 5
(neteja)   (coords)   (canvas)   (events)   (overlays)  (features)
                │
                └── Aquesta fase sola ja resol el problema de pan/zoom
```

**Cada fase deixa l'app funcional.** No es trenca res entre fases.

---

## Riscos i Decisions

| Decisió | Opció A | Opció B | Recomanació |
|---------|---------|---------|-------------|
| Framework GUI | Mantenir tkinter | Migrar a Qt/PySide | **Mantenir tkinter** — el problema no és el framework, és l'arquitectura |
| Rendering | Moure canvas item | Repintar cada frame | **Moure canvas item** però posició calculada des de ViewState (tkinter no és un game engine, repintar tot és innecessari) |
| Undo/Redo | Command pattern | State snapshots | A decidir a Fase 5 |
| Tests | Unit tests amb pytest | + Integration tests amb tkinter | Unit tests per services, manual per GUI |
