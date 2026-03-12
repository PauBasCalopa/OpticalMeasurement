# Pla d'Acció V2.2: Noves Funcionalitats

## Context
L'arquitectura de l'aplicació ha estat completament reestructurada (fases 0-5 originals completades).
L'objectiu ara és afegir noves funcionalitats i millorar la UX.

---

## Fase 1: Perímetre del Polígon

**Objectiu:** Afegir el càlcul i visualització del perímetre als polígons (actualment només es calcula l'àrea).

### 1.1 Funció de càlcul del perímetre
- **Fitxer:** `utils/math_utils.py`
- Crear `calculate_polygon_perimeter(points)` — suma de distàncies euclidanes entre vèrtexs consecutius (incloent el segment de tancament del primer a l'últim punt)
- Reutilitzar `calculate_distance()` existent per cada segment

### 1.2 Actualitzar model de dades
- **Fitxer:** `models/measurement_data.py`
- Afegir camp `perimeter: float = 0.0` a `PolygonAreaMeasurement`
- El model emmagatzema àrea i perímetre conjuntament

### 1.3 Calcular perímetre al motor de mesures
- **Fitxer:** `core/measurement_engine.py`
- Dins `calculate_polygon_area_measurement()`:
  - Cridar `calculate_polygon_perimeter(points)`
  - Aplicar calibratge: `perimeter_real = perimeter_px × scale_factor` (lineal, no quadràtic com l'àrea)
  - Assignar al camp `perimeter` del resultat
- Actualitzar `format_measurement_result()` per incloure "Perimeter: X.XX units"

### 1.4 Mostrar perímetre a l'overlay del canvas
- **Fitxer:** `gui/canvas/overlay_renderer.py`
- Dins `_r_polygon()`: mostrar dues línies de text al centroide:
  - Línia 1: `"Area: X.XX units²"`
  - Línia 2: `"Perim: Y.YY units"`

### 1.5 Incloure perímetre a l'exportació
- **Fitxer:** `services/export_service.py`
- Dins `_draw_polygon_area()`: afegir text del perímetre sota el de l'àrea

### 1.6 Verificació
- Crear polígon amb 3+ punts → ha de mostrar àrea + perímetre
- Exportar imatge → el text ha d'incloure ambdós valors
- Amb i sense calibratge

---

## Fase 2: Toolbar Visual

**Objectiu:** Barra de botons amb icones per accedir ràpidament a les eines, substituint la navegació exclusiva per menú/teclat.

### 2.1 Crear mòdul de toolbar
- **Fitxer nou:** `gui/toolbar.py`
- Classe `ToolBar(ttk.Frame)` amb botons per cada eina:
  - Pan, Distance, Radius, Angle, Two-Line Angle, Polygon Area, Point Coordinates, Point-to-Line, Arc Length
  - Botó de Calibratge separat
- Icones generades amb tkinter Canvas (formes geomètriques simples — línia, cercle, angle, polígon)
- Sense dependències externes d'imatges

### 2.2 Integrar toolbar al layout
- **Fitxer:** `gui/main_window.py`
- Inserir `ToolBar` entre la barra de menú i el canvas
- Connectar cada botó a `set_tool()` del canvas

### 2.3 Feedback visual de l'eina activa
- **Fitxer:** `gui/toolbar.py`
- Ressaltar el botó actiu amb fons diferent (relief=SUNKEN o color)
- Actualitzar quan canvia l'eina (des de menú, teclat o toolbar)

### 2.4 Sincronització toolbar ↔ menú ↔ teclat
- **Fitxer:** `gui/menus.py`
- Totes les fonts de selecció d'eina passen pel mateix callback
- L'estat visual del toolbar es manté consistent

### 2.5 Verificació
- Canviar eina per toolbar → el botó es ressalta, l'eina canvia
- Canviar eina per teclat/menú → el botó del toolbar s'actualitza
- Tooltip (hover) mostra nom de l'eina + drecera

---

## Fase 3: Grid/Graella Superposada

**Objectiu:** Quadrícula configurable sobre la imatge per ajudar a alinear mesures i tenir referència visual.

### 3.1 Opcions de menú
- **Fitxer:** `gui/menus.py`
- Afegir al menú View:
  - "Show Grid" (toggle, drecera: G)
  - "Grid Settings..." (obre diàleg de configuració)

### 3.2 Renderitzar graella
- **Fitxer:** `gui/canvas/overlay_renderer.py`
- Nou mètode `render_grid(view_state, spacing, color, opacity)`
- Dibuixar línies verticals i horitzontals en coordenades d'imatge
- Respectar zoom/pan (convertir image→screen)
- Usar tag `"grid"` per gestionar visibilitat
- Renderitzar SOTA els overlays de mesures

### 3.3 Diàleg de configuració
- **Fitxer:** `gui/dialogs.py`
- `GridSettingsDialog`:
  - Espaiat (en píxels o unitats calibrades)
  - Color de la graella (selecció de presets)
  - Opacitat (slider)
  - Subdivisions (opcional)

### 3.4 Estat de la graella
- **Fitxer:** `core/app_state.py`
- Afegir `grid_visible: bool`, `grid_spacing: int`, `grid_color: str`

### 3.5 Verificació
- G per mostrar/amagar graella
- Zoom/pan → la graella segueix la imatge correctament
- Canviar espaiat → s'actualitza immediatament

---

## Fase 4: Ajust de Contrast i Brillantor

**Objectiu:** Permetre modificar la visualització de la imatge per veure millor detalls, sense alterar la imatge original.

### 4.1 Sliders al sidebar
- **Fitxer:** `gui/main_window.py`
- Afegir secció "Image Adjustments" al sidebar:
  - Slider Brightness (0.0 - 2.0, default 1.0)
  - Slider Contrast (0.0 - 2.0, default 1.0)
  - Botó "Reset" per tornar a 1.0/1.0

### 4.2 Processament d'imatge
- **Fitxer:** `core/image_manager.py`
- Usar `PIL.ImageEnhance.Brightness` i `PIL.ImageEnhance.Contrast`
- Mantenir la imatge original intacta
- Cache de la imatge ajustada per evitar recalcular a cada repintat
- Invalidar cache quan canvien els sliders

### 4.3 Integrar amb el canvas
- **Fitxer:** `gui/canvas_widget.py`
- `update_display()` usa la imatge ajustada (no l'original) per renderitzar
- L'exportació utilitza la imatge ORIGINAL (sense ajustos)

### 4.4 Verificació
- Moure sliders → la imatge canvia en temps real
- Exportar → la imatge exportada NO té els ajustos
- Reset → torna a la visualització original
- Carregar nova imatge → sliders tornen a 1.0

---

## Fase 5: Minimap (Navegador)

**Objectiu:** Mini preview de la imatge sencera amb rectangle de viewport per orientar-se quan es fa zoom.

### 5.1 Widget minimap
- **Fitxer nou:** `gui/minimap_widget.py`
- Classe `MinimapWidget(tk.Canvas)` (~200×150px)
- Mostra thumbnail de la imatge sencera
- Dibuixa rectangle vermell indicant la zona visible actual

### 5.2 Integrar al sidebar
- **Fitxer:** `gui/main_window.py`
- Col·locar el minimap a dalt del sidebar (sobre la secció de calibratge)
- Actualitzar-se automàticament quan canvia el ViewState (zoom/pan)

### 5.3 Navegació interactiva
- **Fitxer:** `gui/minimap_widget.py`
- Clic al minimap → el viewport es centra a aquella posició
- Drag al minimap → pan en temps real
- Calcular la correspondència minimap_coords → image_coords → ViewState

### 5.4 Rendiment
- Generar thumbnail un cop (quan es carrega imatge)
- Només redibuixar el rectangle de viewport a cada moviment
- Amagar minimap si la imatge sencera és visible (zoom ≤ fit)

### 5.5 Verificació
- Zoom in → apareix rectangle al minimap
- Pan → el rectangle es mou
- Clic al minimap → el canvas navega allà
- Canviar imatge → minimap s'actualitza

---

## Ordre d'Implementació

```
Fase 1 ──→ Fase 2 ──→ Fase 3 ──→ Fase 4 ──→ Fase 5
(perim.)   (toolbar)   (grid)    (contrast)  (minimap)
  ↑
  └── Més ràpida i útil, sense canvis de UI majors
```

**Cada fase deixa l'app funcional.** Es pot desplegar després de cada fase.

---

## Fitxers afectats per fase

| Fitxer | F1 | F2 | F3 | F4 | F5 |
|--------|:--:|:--:|:--:|:--:|:--:|
| `utils/math_utils.py` | ✏️ | | | | |
| `models/measurement_data.py` | ✏️ | | | | |
| `core/measurement_engine.py` | ✏️ | | | | |
| `core/app_state.py` | | | ✏️ | | |
| `core/image_manager.py` | | | | ✏️ | |
| `gui/canvas/overlay_renderer.py` | ✏️ | | ✏️ | | |
| `gui/canvas_widget.py` | | | | ✏️ | |
| `gui/main_window.py` | | ✏️ | | ✏️ | ✏️ |
| `gui/menus.py` | | ✏️ | ✏️ | | |
| `gui/dialogs.py` | | | ✏️ | | |
| `gui/toolbar.py` | | 🆕 | | | |
| `gui/minimap_widget.py` | | | | | 🆕 |
| `services/export_service.py` | ✏️ | | | | |

✏️ = Modificat | 🆕 = Nou
