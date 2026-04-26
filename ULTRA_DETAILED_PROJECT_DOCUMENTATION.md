# No Way Out — Ultra Detailed Project Documentation

This document is a full technical reference for the project, including:
- architecture and runtime flow,
- module-by-module behavior,
- and **every class/function/method** with **what it does, how it works, and why it exists**.

---

## 1) Project Purpose and Design

**No Way Out** is a Pygame escape-room game with 3 playable levels. The codebase is organized around a **stack-based state machine**:
- `MenuState` (name input, new game/continue, character select, settings),
- `RoomState` (walking/interacting in room),
- `PuzzleState` (overlay puzzle UI),
- `VictoryState` (final celebration screen).

### Why this architecture
- Keeps screens isolated (menu logic doesn’t pollute gameplay logic).
- Supports overlays naturally (`PuzzleState` can be pushed on top of `RoomState`).
- Makes transitions explicit (`push`, `pop`, `change`).

---

## 2) Runtime Flow (Start to Finish)

1. `main.py:main()` initializes pygame, builds shared `game_context`, and pushes `MenuState`.
2. `MenuState` captures name, mode, and character; then changes to `RoomState`.
3. `RoomState.enter()` builds level map from TMX and creates `Player`.
4. On `E` near an interactable, `RoomState` pushes `PuzzleState`.
5. `PuzzleState` loads puzzle by id from `PUZZLE_REGISTRY`; success calls `RoomState.on_puzzle_solved()`.
6. When room exit unlocks and player interacts with it, room marks win and transitions:
   - level1 → level2,
   - level2 → level3,
   - level3 → `VictoryState`.
7. `VictoryState` returns to menu on key/mouse input.

---

## 3) Shared Data Contracts

### `game_context` keys (core runtime)
- `screen_w`, `screen_h`: window dimensions.
- `player_name`: entered in menu.
- `load_save`, `save_data`: continue-game flow.
- `sprite_id`: selected character (`finn`, `maeve`).
- `current_level`: `level1` / `level2` / `level3`.

### Save file schema (`data/savegame.json`)
- `player_name` (str)
- `current_room` (str, level id)
- `puzzles_solved` (list[str])
- `player_position` ([x, y])
- `sprite_id` (str)
- `timestamp` (ISO string)

### Settings schema (`data/settings.json`)
- `volume` (float 0..1)
- `muted` (bool)

---

## 4) Puzzle ID Registry and Mappings

`puzzles/easy_puzzles.py` exports `PUZZLE_REGISTRY` mapping IDs to classes.

- `caesar_cipher` → `CaesarCipherPuzzle`
- `binary_lock` → `BinaryLockPuzzle`
- `couch_slicing` / `bed_slicing` → `CouchSlicingPuzzle`
- `blinking_lights` → `BlinkingLightsPuzzle`
- `misplaced_tile` → `MisplacedTilePuzzle`
- `painting_code` → `PaintingPuzzle`
- `furnace_sequence` → `FurnacePuzzle`
- `box_math` → `BoxPuzzle`
- `chemistry_drops` → `ChemistryTable`
- `mirror_coords` → `MirrorPuzzle`
- `statue_riddle` → `StatueRiddlePuzzle`

Why this exists: decouples map objects from concrete class imports and lets `PuzzleState` load puzzles generically by string id.

---

## 5) Complete File + Function/Method Reference (What / How / Why)

### `main.py`

#### `get_gif_dimensions(path)`
- **What:** Reads source GIF dimensions.
- **How:** Uses Pillow `Image.open(...).size`.
- **Why:** Window scaling stays consistent with art source size.

#### `main()`
- **What:** Bootstraps game loop.
- **How:** Initializes pygame/audio, computes screen size, creates context, pushes menu state, then per frame handles events/update/draw.
- **Why:** Single controlled entry point for predictable startup and frame lifecycle.

---

### `engine/state_machine.py`

#### `StateMachine.__init__()`
- **What:** Creates internal state stack.
- **How:** Initializes `self._states = []`.
- **Why:** All transitions rely on stack state.

#### `StateMachine.current`
- **What:** Returns top state.
- **How:** Last element of stack or `None`.
- **Why:** Central dispatch target for input/update/draw.

#### `StateMachine.push(state)`
- **What:** Adds new active state.
- **How:** Pauses current, appends new, calls `enter()`.
- **Why:** Enables overlays like puzzle popup over room.

#### `StateMachine.pop()`
- **What:** Removes active state.
- **How:** Pops top, calls `exit()`, resumes new top.
- **Why:** Closes overlays and resumes underlying state.

#### `StateMachine.change(state)`
- **What:** Replaces active state.
- **How:** Pops old top with `exit()`, appends new, `enter()`.
- **Why:** Full transitions (menu→room, room→victory).

#### `StateMachine.handle_events(events)` / `update(dt)` / `draw(surface)`
- **What:** Delegates frame hooks.
- **How:** Calls same method on `current` if present.
- **Why:** Enforces “only active state drives game loop”.

---

### `states/base_state.py`

#### `State.__init__(machine, game_context)`
- **What:** Base constructor for all states.
- **How:** Stores machine and shared context.
- **Why:** Standardized state interface and shared data access.

#### `State.enter()` / `exit()` / `pause()` / `resume()`
- **What:** Lifecycle hooks.
- **How:** Default no-op methods.
- **Why:** Optional override points for transitions and stack behavior.

#### `State.handle_events(events)` / `update(dt)` / `draw(surface)`
- **What:** Abstract per-frame contract.
- **How:** Abstract methods (`ABC`) required in subclasses.
- **Why:** Guarantees each state can process input, logic, and rendering.

---

### `engine/settings.py`

#### `load_settings()`
- **What:** Loads persisted audio settings.
- **How:** Reads JSON; on any failure returns defaults `{muted:False, volume:0.20}`.
- **Why:** Robust startup even if settings file is missing/corrupt.

#### `save_settings(settings)`
- **What:** Persists settings JSON.
- **How:** Ensures directory exists, writes JSON in try/except.
- **Why:** Prevents settings write errors from crashing gameplay.

---

### `engine/save_system.py`

#### `save_game(player_name, current_room, puzzles_solved, player_pos, sprite_id='finn')`
- **What:** Saves current progression snapshot.
- **How:** Builds dict with position/puzzles/timestamp and dumps JSON.
- **Why:** Supports continue flow and level progression persistence.

#### `load_game()`
- **What:** Loads save data.
- **How:** Returns parsed JSON dict if file exists and valid, otherwise `None`.
- **Why:** Graceful continue support.

#### `has_save()`
- **What:** Save-file existence check.
- **How:** `os.path.exists(SAVE_FILE)`.
- **Why:** Menu conditionally shows “Continue”.

#### `delete_save()`
- **What:** Deletes save file.
- **How:** Removes file if present.
- **Why:** “New Game” should reset progression cleanly.

---

### `engine/player.py`

#### `load_sprite_images(sprite_id)`
- **What:** Loads animated directional frames.
- **How:** Reads sheet, slices rows/frames, smooth-scales to in-game sprite size; builds ping-pong sequence for 3-frame sheets.
- **Why:** Provides reusable directional animation data for `Player.draw()`.

#### `load_pfp(sprite_id, size=(100,100))`
- **What:** Loads character profile portrait.
- **How:** Loads configured `pfp` file and scales to UI size.
- **Why:** Character select screen needs stable portrait assets.

#### `load_idle_images(sprite_id)`
- **What:** Loads single-frame idle poses when available.
- **How:** Loads idle files, crops bounding box, scales to target physical height.
- **Why:** Better visual quality when standing still than using walk-frame freeze.

#### `Player.__init__(x, y, sprite_id=None)`
- **What:** Creates controllable player entity.
- **How:** Initializes collision rect, float positions, direction, animation state, and optional sprite assets.
- **Why:** Central object for movement/rendering and collision.

#### `Player.handle_input(keys)`
- **What:** Converts keyboard state to velocity.
- **How:** Checks WASD/arrow keys and assigns `vx,vy` plus facing direction.
- **Why:** Separates input translation from physics/collision pass.

#### `Player.move(dt, walls)`
- **What:** Performs movement + collisions.
- **How:** Axis-by-axis motion using float integration (`vx*dt`, `vy*dt`), collision correction against wall rects, animation frame progression only when physically moving.
- **Why:** Axis separation prevents corner-sticking and gives deterministic collision behavior.

#### `Player.draw(surface)`
- **What:** Draws sprite or placeholder.
- **How:** Chooses idle/walk frame by state/direction, applies runtime scale, anchors sprite bottom to collision rect.
- **Why:** Decouples physical footprint from visual sprite size for better gameplay feel.

#### `Player._draw_placeholder(surface)`
- **What:** Debug/fallback rendering.
- **How:** Draws colored rectangle with direction-dependent “face”.
- **Why:** Keeps game playable even if sprite loading fails.

---

### `engine/tmx_loader.py`

#### `TilesetInfo.__init__(...)`
- **What:** Stores metadata for one tileset.
- **How:** Captures gid range and image properties.
- **Why:** Needed for global tile id to image lookup.

#### `TilesetInfo.load_tiles()`
- **What:** Slices tileset image into per-tile surfaces.
- **How:** Loads PNG, iterates `tile_count`, computes row/col, stores local-id surfaces.
- **Why:** Runtime rendering needs fast tile surface access.

#### `TilesetInfo.get_tile(global_id)`
- **What:** Returns tile surface for global gid.
- **How:** Converts to local id via `global_id - firstgid`.
- **Why:** TMX layers store global gids, not local tileset indices.

#### `TileLayer.__init__(name, width, height, data)`
- **What:** Layer container.
- **How:** Stores metadata and flat tile-id array.
- **Why:** Preserves TMX layer order for rendering/collision extraction.

#### `TiledMap.__init__()`
- **What:** Initializes map model.
- **How:** Sets dimensions, tileset/layer collections.
- **Why:** One parsed object passed to room builders.

#### `TiledMap.pixel_width` / `pixel_height`
- **What:** Derived pixel dimensions.
- **How:** tile counts × tile size.
- **Why:** Used for surface allocation/scaling math.

#### `TiledMap.get_tileset_for_gid(gid)`
- **What:** Finds owning tileset for gid.
- **How:** Walks sorted tilesets by `firstgid`.
- **Why:** Correct surface lookup across multiple tilesets.

#### `TiledMap.render()`
- **What:** Pre-renders entire map.
- **How:** Creates transparent surface and renders each layer.
- **Why:** Faster frame rendering than redrawing each tile every frame.

#### `TiledMap._render_layer(surface, layer)`
- **What:** Draws one layer.
- **How:** Skips gid 0, extracts TMX flip flags, resolves tileset/tile, applies transforms, places using grid position with tall-tile y offset.
- **Why:** Converts TMX encoded tile stream into correctly transformed visuals.

#### `TiledMap._apply_flips(surf, h_flip, v_flip, d_flip)`
- **What:** Applies TMX transformation flags.
- **How:** Diagonal uses rotate+flip, then H/V flips.
- **Why:** TMX stores transformations in gid bits; renderer must decode them.

#### `TiledMap.get_layer_tile_positions(layer_name)`
- **What:** Lists occupied tile coordinates of a layer.
- **How:** Iterates layer data and returns non-zero gid cells.
- **Why:** Reused by collision and interactable generation.

#### `TiledMap.get_layer_bounding_rect(layer_name)`
- **What:** Pixel bounding box of non-empty tiles.
- **How:** Min/max row/col from occupied positions.
- **Why:** Easy interactable hitbox creation from authored layer shape.

#### `_parse_tsx(tsx_path, firstgid)`
- **What:** Parses external TSX file into `TilesetInfo`.
- **How:** Reads XML attributes and resolves image relative path.
- **Why:** TMX often references external tilesets.

#### `load_tmx(tmx_path)`
- **What:** Full TMX parser and loader.
- **How:** Parses map attrs, tilesets (external/embedded), deduplicates duplicate `firstgid`, loads tiles, parses CSV layers, records object groups.
- **Why:** Supplies a complete runtime map model for room construction.

---

### `engine/room.py`

#### `Interactable.__init__(rect, label, puzzle_id=None, color=(180,140,80))`
- **What:** Interaction object model.
- **How:** Stores geometry, display label, puzzle binding, solved state.
- **Why:** Uniform representation for puzzles, doors, gates, etc.

#### `Interactable.draw(surface, font, show_colored_block=True)`
- **What:** Draws legacy debug/object block + label.
- **How:** Solved color swap and text placement above rect.
- **Why:** Visual feedback and fallback where TMX art is not used.

#### `Room.__init__(width_tiles, height_tiles)`
- **What:** Runtime room container.
- **How:** Sets map dimensions, wall/interactable/light collections, optional pre-rendered TMX surface.
- **Why:** Central room data consumed by `RoomState`.

#### `Room.build_walls_border()`
- **What:** Adds perimeter collision walls.
- **How:** Appends 4 rects (top/bottom/left/right).
- **Why:** Fallback collision when map layer data absent.

#### `Room.draw(surface, font)`
- **What:** Draws room.
- **How:** TMX mode blits pre-rendered map; legacy mode draws floor/walls; always draws interactable labels.
- **Why:** Supports both authored TMX and non-TMX fallback.

#### `Room.get_nearby_interactable(player_rect, reach=10)`
- **What:** Finds interactable in reach.
- **How:** Inflates player rect and tests collisions.
- **Why:** Interaction prompt and `E` logic need proximity query.

#### `Room.all_puzzles_solved()`
- **What:** Checks room completion.
- **How:** `all()` over interactables that have `puzzle_id`.
- **Why:** Door/elevator unlock gate condition.

#### `build_easy_room()`
- **What:** Legacy hardcoded level 1 room builder.
- **How:** Creates fixed interactables/walls/door and start position.
- **Why:** Fallback when TMX asset missing.

#### `build_easy_room_from_tmx()`
- **What:** Level 1 room from TMX.
- **How:** Loads map, pre-renders surface, extracts border/furniture walls and interactables from named layers (`desk`, `lightboard`, `couch`, `escapedoor`).
- **Why:** Data-driven map authoring from Tiled.

#### `build_level2_room_from_tmx()`
- **What:** Level 2 room from hallway TMX.
- **How:** Builds walls/interactables (`door2`, `bump`, `painting`, `gate`, `elevator`) and light positions for blink effect.
- **Why:** Encodes level-specific mechanics with authored map semantics.

#### `_add_tile_walls(room, tiled_map, layer_name)`
- **What:** Utility to convert occupied tiles in layer to collision walls.
- **How:** For each non-empty tile, append `32x32` wall rect.
- **Why:** Precise per-tile collision for irregular objects.

#### `build_level3_room_from_tmx()`
- **What:** Level 3 dungeon room builder.
- **How:** Loads map, border+wall layer collisions, interactables (`furnace`, `supplytable`, `mirror`, `statues`, `drums3`, `door`), additional decoration collision layers.
- **Why:** Level 3 needs denser collision fidelity and more interactables.

---

### `states/menu_state.py`

#### `load_gif_frames(path, target_size)`
- **What:** Loads animated background frames.
- **How:** Iterates GIF frames via PIL, converts to pygame surfaces, scales each.
- **Why:** Menu visual style depends on animated background.

#### `MenuState.__init__(machine, ctx)`
- **What:** Initializes menu state and UI model.
- **How:** Loads persisted settings, initializes phase/menu/character selectors, fonts/colors.
- **Why:** Central setup for multi-step menu flow.

#### `MenuState.enter()`
- **What:** Runtime resource prep when menu becomes active.
- **How:** Loads GIF frames, starts looping music, preloads character PFP images.
- **Why:** Avoids loading media repeatedly every frame.

#### `MenuState._apply_volume()`
- **What:** Applies mute/volume to mixer.
- **How:** Sets music volume to 0 or configured scalar.
- **Why:** Single source of truth for audio output changes.

#### `MenuState.handle_events(events)`
- **What:** Routes all menu input.
- **How:** Processes quit, settings mouse controls, drag slider, keyboard dispatch by phase.
- **Why:** Input behavior differs by phase; centralized dispatcher keeps logic coherent.

#### Rect helper methods
- `_settings_icon_rect`, `_slider_track_rect`, `_slider_rect`, `_mute_rect`, `_back_btn_rect`
- **What:** Return clickable UI geometry.
- **How:** Computes rects from screen size and current volume.
- **Why:** Geometry encapsulation avoids duplicated layout math.

#### `MenuState._update_volume_from_mouse(mouse_x)`
- **What:** Converts mouse x to volume percent.
- **How:** Normalizes x relative to slider width and clamps to `[0,1]`.
- **Why:** Continuous drag-based volume control.

#### `MenuState._handle_name_input(event)`
- **What:** Handles typed player name.
- **How:** enter confirms, backspace edits, length-limited printable input, esc quits.
- **Why:** First step in menu flow; ensures non-empty name before proceeding.

#### `MenuState._build_menu()`
- **What:** Builds selectable menu items.
- **How:** Always adds “New Game”, conditionally appends “Continue” if save exists.
- **Why:** Prevents invalid continue option when no save exists.

#### `MenuState._handle_menu_select(event)`
- **What:** Handles New/Continue selection.
- **How:** Arrow navigation + enter action; New resets save and routes to character select; Continue loads save and starts game immediately.
- **Why:** Supports both fresh starts and resume path.

#### `MenuState._handle_char_select(event)`
- **What:** Handles character selection controls.
- **How:** Left/right cycle ids; enter confirms into context and starts room.
- **Why:** Character choice determines player sprite set.

#### `MenuState._start_game()`
- **What:** Transition out of menu.
- **How:** `StateMachine.change(RoomState(...))`.
- **Why:** Enter core gameplay state.

#### `MenuState.update(dt)`
- **What:** Advances menu animation frame.
- **How:** Frame counter with configured delay.
- **Why:** Controls GIF playback speed independent of source frame timing.

#### `MenuState.draw(surface)`
- **What:** Master menu renderer.
- **How:** Draws background + overlays and delegates to phase-specific draw methods.
- **Why:** Keeps visual rendering structured by active phase.

#### `MenuState._draw_settings_icon(surface)`
- **What:** Draws settings button.
- **How:** Rounded rect with gear glyph.
- **Why:** Entry point to settings overlay.

#### `MenuState._draw_settings(surface, w, h)`
- **What:** Draws settings panel controls.
- **How:** Renders volume track/fill/knob, mute toggle, and back button.
- **Why:** In-game configurable audio UX.

#### `MenuState._draw_name_input(surface, w, h)`
- **What:** Draws name input screen.
- **How:** Prompt, input box, blinking cursor, footer hint.
- **Why:** Clear onboarding step before game starts.

#### `MenuState._draw_menu_select(surface, w, h)`
- **What:** Draws New/Continue selection list.
- **How:** Highlights current selection with color/prefix arrow.
- **Why:** Keyboard-first menu usability.

#### `MenuState._draw_char_select(surface, w, h)`
- **What:** Draws character cards and selection marker.
- **How:** Renders card frames, portrait fallback, labels, selection arrow.
- **Why:** Visual confirmation of selected avatar.

---

### `states/room_state.py`

#### `RoomState.__init__(machine, ctx)`
- **What:** Initializes gameplay state data.
- **How:** Sets room/player references, puzzle progress, blink timing constants, HUD assets, win and feedback timers.
- **Why:** Holds full per-level runtime state in one place.

#### `RoomState.enter()`
- **What:** Builds level and spawns player.
- **How:** Selects level builder, computes map-to-window scaling/offset, restores save if continuing, applies smaller hitbox/render scale for level2/3, auto-saves.
- **Why:** Normalizes setup path for fresh and resumed sessions.

#### `RoomState._check_door()`
- **What:** Updates unlock state and gate logic.
- **How:** If all puzzles solved, unlocks door/elevator labels and colors; in level2 removes gate after `blinking_lights` solved.
- **Why:** Encodes progression gating rules.

#### `RoomState._auto_save()`
- **What:** Persists current progression.
- **How:** Calls `save_game` with context and player position.
- **Why:** Preserves progress on transitions and exits.

#### `RoomState.handle_events(events)`
- **What:** Handles gameplay key events.
- **How:** quit saves+exits, ESC saves and returns menu, E triggers interact.
- **Why:** Core in-room controls and safe exit behavior.

#### `RoomState._interact(obj)`
- **What:** Executes interaction rules by object type/state.
- **How:** For unsolved puzzle object pushes `PuzzleState`; `misplaced_tile` has force-field gate requiring two failed bump attempts first; for unlocked exit sets win state.
- **Why:** Central interaction rule engine.

#### `RoomState.on_puzzle_solved(puzzle_id)`
- **What:** Receives puzzle success callback.
- **How:** Marks puzzle/object solved, triggers feedback flash, door/gate reevaluation, auto-save.
- **Why:** Synchronizes puzzle overlay success into room progression.

#### `RoomState._get_active_light()`
- **What:** Calculates current active hallway light (level2).
- **How:** Evaluates `blink_timer` against precomputed cycle durations and per-light blink windows.
- **Why:** Deterministic visual blink pattern used by puzzle clue.

#### `RoomState.update(dt)`
- **What:** Main gameplay update.
- **How:** Decrements timers, advances blink sequence, handles win transitions, moves player and clamps bounds, applies bump pushback logic, updates proximity prompt object.
- **Why:** Single per-frame logic loop for gameplay state.

#### `RoomState.draw(surface)`
- **What:** Main gameplay renderer.
- **How:** Draws native room+player to offscreen surface, scales/blits, adds level2 glow, HUD, prompts, feedback overlays, win overlay.
- **Why:** Keeps world rendering resolution-independent and UI layered.

#### `RoomState._draw_win(surface, w, h)`
- **What:** Draws level-complete overlay.
- **How:** Fade-to-black + fading text with level-specific transition message.
- **Why:** Communicates progression transitions cleanly.

#### `RoomState.pause()` / `resume()`
- **What:** Lifecycle hooks when overlay states are pushed/popped.
- **How:** currently no-op.
- **Why:** Placeholder for future pause/resume mechanics.

---

### `states/puzzle_state.py`

#### `PuzzleState.__init__(machine, ctx, puzzle_id, room_state)`
- **What:** Initializes puzzle overlay context.
- **How:** Stores puzzle id and callback target (`room_state`), UI state, text state, fonts/colors.
- **Why:** Encapsulates all transient puzzle interaction state.

#### `PuzzleState.enter()`
- **What:** Resolves puzzle implementation and media assets.
- **How:** Looks up class in registry, instantiates, optionally loads image and precomputes thumbnail/full sizes.
- **Why:** Puzzle content is data-driven by id and should load once per open.

#### `PuzzleState.handle_events(events)`
- **What:** Handles puzzle overlay input.
- **How:** Supports close on ESC, submit on Enter, input editing, zoom toggle with TAB/click, close-after-solve on any key.
- **Why:** Keeps puzzle UX modal and keyboard-driven.

#### `PuzzleState._submit()`
- **What:** Validates answer.
- **How:** Calls puzzle `check_answer`; on success sets solved feedback and calls `room_state.on_puzzle_solved`; on failure clears input and shows error.
- **Why:** Bridges puzzle logic result back to room progression.

#### `PuzzleState.update(dt)`
- **What:** Update hook.
- **How:** no-op.
- **Why:** Overlay has event-driven behavior; no continuous simulation needed.

#### `PuzzleState.draw(surface)`
- **What:** Draws puzzle panel.
- **How:** Dark overlay, optional zoomed image mode, title, wrapped description, image thumbnail, answer box, feedback and control hint.
- **Why:** Consistent readable UI for all puzzle classes.

#### `PuzzleState._draw_zoomed_image(surface, w, h)`
- **What:** Fullscreen image inspection mode.
- **How:** Draws darkened backdrop, centered full image with border and close hint.
- **Why:** Supports image-based clues (e.g., painting code).

---

### `states/victory_state.py`

#### `Particle.__init__(x, y, color)`
- **What:** Confetti particle init.
- **How:** Randomizes velocity/decay and sets life.
- **Why:** Lightweight celebratory visual elements.

#### `Particle.update()`
- **What:** Advances particle physics.
- **How:** Applies velocity, gravity, and life decay.
- **Why:** Animated, finite-life confetti behavior.

#### `Particle.draw(surface)`
- **What:** Draws particle with alpha.
- **How:** Renders small circle on per-particle transparent surface.
- **Why:** Fade-out effect with simple blending.

#### `VictoryState.__init__(machine, ctx)`
- **What:** Initializes victory screen resources.
- **How:** Creates fonts, particle list, color palette, timers.
- **Why:** Prepares celebratory rendering state.

#### `VictoryState.enter()`
- **What:** Entry behavior after game completion.
- **How:** Resets level context and spawns initial confetti burst.
- **Why:** Ensures returning to menu starts at level1 and gives immediate celebration feedback.

#### `VictoryState.handle_events(events)`
- **What:** Handles exit from victory screen.
- **How:** quit exits process; any key/click returns to menu.
- **Why:** Simple user-controlled completion flow.

#### `VictoryState.update(dt)`
- **What:** Advances celebration animation.
- **How:** Spawns additional particles probabilistically, updates/removes dead particles, scrolls stripe background offset.
- **Why:** Keeps victory screen visually dynamic.

#### `VictoryState.draw(surface)`
- **What:** Draws complete victory scene.
- **How:** Draws striped background, particles, floating title with shadow, messages, blinking prompt.
- **Why:** Final payoff and clear return instruction.

---

### `puzzles/easy_puzzles.py`

#### `CaesarCipherPuzzle.__init__()`
- **What:** Initializes Caesar puzzle data.
- **How:** Defines encrypted word `KHOOR`, shift 3, computes solution, description lines.
- **Why:** Intro puzzle teaching simple substitution reasoning.

#### `CaesarCipherPuzzle.check_answer(answer)`
- **What:** Validates player answer.
- **How:** strip + uppercase compare against solution.
- **Why:** Case-insensitive input tolerance.

#### `BinaryLockPuzzle.__init__()`
- **What:** Initializes random 4-bit puzzle.
- **How:** Generates bits, computes decimal value from binary sequence.
- **Why:** Replay variation and binary-to-decimal challenge.

#### `BinaryLockPuzzle.check_answer(answer)`
- **What:** Validates decimal input.
- **How:** `int()` parse with ValueError guard then numeric compare.
- **Why:** Rejects non-numeric answers safely.

#### `CouchSlicingPuzzle.__init__()`
- **What:** Initializes string slicing puzzle.
- **How:** Uses clue `ZZZGOLDZZZ` and slice `[3:7]` => `GOLD`, plus narrative description.
- **Why:** Puzzle built around indexing/slicing concept.

#### `CouchSlicingPuzzle.check_answer(answer)`
- **What:** Validates extracted word.
- **How:** strip + uppercase compare to solution.
- **Why:** Prevents whitespace/case mismatches.

**Registry behavior in module:**
- Imports level2 and level3 puzzle classes, defines `PUZZLE_REGISTRY`, and `update()` merges level3 mapping.
- Why: Single import point for `PuzzleState` regardless of level.

---

### `puzzles/level2_puzzles.py`

#### `BlinkingLightsPuzzle.__init__()`
- **What:** Defines level2 light puzzle with code `324`.
- **How:** Stores solution and hint description.
- **Why:** Directly tied to hallway blink animation in `RoomState`.

#### `BlinkingLightsPuzzle.check_answer(answer)`
- **What:** Validates code.
- **How:** stripped string equality.
- **Why:** Exact sequence required.

#### `MisplacedTilePuzzle.__init__()`
- **What:** Defines riddle puzzle with solution `ECHO`.
- **How:** Stores prompt text from riddle.
- **Why:** Narrative payoff after bump-force mechanic.

#### `MisplacedTilePuzzle.check_answer(answer)`
- **What:** Validates riddle answer.
- **How:** strip + uppercase compare.
- **Why:** Case-insensitive acceptance.

#### `PaintingPuzzle.__init__()`
- **What:** Defines image-driven code puzzle.
- **How:** sets solution `1379`, computes absolute `image_path`, stores description.
- **Why:** Enables `PuzzleState` image thumbnail/zoom clue flow.

#### `PaintingPuzzle.check_answer(answer)`
- **What:** Validates 4-digit code.
- **How:** stripped string compare.
- **Why:** Numeric code should be exact.

---

### `puzzles/level3_puzzles.py`

#### `FurnacePuzzle.__init__()`
- **What:** Initializes order puzzle state.
- **How:** sets sequence holder and solved flag.
- **Why:** Progress-tracked object puzzle.

#### `FurnacePuzzle.check_answer(player_input)`
- **What:** Validates ore order.
- **How:** lowercases/splits and compares to `[red, white, black]`.
- **Why:** Enforces exact sequence challenge.

#### `BoxPuzzle.__init__()`
- **What:** Initializes crate math puzzle data.
- **How:** sets `num_crates=5`, `faces_per_crate=6`.
- **Why:** Encodes puzzle parameters explicitly.

#### `BoxPuzzle.check_answer(player_input)`
- **What:** Validates multiplication result.
- **How:** compares stripped input to `30`.
- **Why:** Simple arithmetic gate puzzle.

#### `ChemistryTable.__init__()`
- **What:** Initializes vial-drop puzzle.
- **How:** stores vial values `{a:2,b:1,c:5}` and solved flag.
- **Why:** Supports combinational input evaluation.

#### `ChemistryTable.check_answer(player_input)`
- **What:** Validates reaching 4 drops.
- **How:** allows shortcut input `'4'`; otherwise sums per-character vial tokens and checks `drops == 4`.
- **Why:** Flexible answer entry while preserving target constraint.

#### `MirrorPuzzle.__init__()`
- **What:** Initializes coordinate puzzle target.
- **How:** target `7,3`.
- **Why:** Uses spatial clue style puzzle.

#### `MirrorPuzzle.check_answer(player_input)`
- **What:** Validates coordinate answer.
- **How:** strips spaces and compares to `7,3`.
- **Why:** Accepts formatting variation with spaces.

#### `StatueRiddlePuzzle.__init__()`
- **What:** Initializes riddle with attempt limit.
- **How:** sets `tries_left=3`, `correct_answer='keyboard'`.
- **Why:** Adds tension via bounded attempts.

#### `StatueRiddlePuzzle.check_answer(player_input)`
- **What:** Validates answer with lockout feedback.
- **How:** if tries exhausted returns false; else compares normalized input, decrements tries on fail, appends dynamic feedback lines.
- **Why:** Stateful multi-attempt riddle behavior.

#### `LEVEL3_PUZZLES` (module constant)
- **What:** Mapping of level3 ids to classes.
- **How:** dictionary literal.
- **Why:** merged into central registry in `easy_puzzles.py`.

---

### Tooling / Maintenance Scripts (root)

> These scripts are utility scripts for map-asset maintenance and include hardcoded local Windows paths at file bottom; they are not used by game runtime.

### `check_assets.py`
#### `check_assets(map_dir)`
- **What:** Reports missing and unused TMX/TSX/image files.
- **How:** Parses TMX→TSX→image references, compares with directory contents, prints reports.
- **Why:** Helps validate map asset consistency.

### `verify_assets.py`
#### `find_missing_in_assets(map_dir)`
- **What:** Verifies level3 referenced TSX/image files exist.
- **How:** Parses `DungeonLevel3.tmx`, then each tileset and image path, prints missing list.
- **Why:** Final consistency check after reorganization.

### `remap_assets.py`
#### `remap_and_find_missing(map_dir)`
- **What:** Repairs broken TSX image source paths where basename exists locally.
- **How:** Rewrites `<image source>` to basename if file found; prints strictly missing assets.
- **Why:** Fixes path portability problems from moved assets.

### `organize_level3.py`
#### `organize_level3()`
- **What:** Reorganizes level3 map files into an `assets/` folder and rewrites TMX/TSX references.
- **How:** Renames directory, edits TMX tileset sources, edits TSX image sources, moves used TSX/PNG files, deletes unused top-level assets.
- **Why:** Standardizes level3 structure and reference integrity.

---

## 6) Notable Engineering Decisions and Implications

- **Pre-rendered TMX map surfaces:** better runtime performance; tradeoff is memory footprint per room.
- **Rect-based collision:** simple and robust for top-down rooms; tradeoff is no pixel-perfect collisions.
- **State-machine stack:** clean overlays and transitions; tradeoff is careful lifecycle management.
- **Context dict over globals:** easy cross-state data flow; tradeoff is weak typing/implicit keys.
- **Puzzle registry by id:** decouples puzzle UI from puzzle implementations; simplifies extensibility.

---

## 7) How to Extend Safely

- Add new puzzle class with `TITLE`, `description`, `check_answer`, then register id in `PUZZLE_REGISTRY`.
- Add interactable layer in TMX and map that layer name to puzzle id in corresponding `build_level*_room_from_tmx` function.
- Keep save compatibility when renaming puzzle IDs (consider alias IDs like `bed_slicing`).
- Keep `RoomState._check_door()` rules in sync with any new gate/door mechanics.

---

## 8) Current Gaps / Technical Debt Observed

- `pytest` not installed and no repository test/lint config discovered.
- Some utility scripts execute directly at import due to bottom-of-file calls and use machine-specific Windows paths.
- `RoomState.draw()` references `self.ACCENT` via `hasattr` fallback, implying inconsistent color constant definition.

---

## 9) Quick Index: All Classes and Callables (Complete)

#### Classes
- `StateMachine`, `State`, `MenuState`, `RoomState`, `PuzzleState`, `VictoryState`, `Particle`
- `Player`, `Room`, `Interactable`, `TilesetInfo`, `TileLayer`, `TiledMap`
- `CaesarCipherPuzzle`, `BinaryLockPuzzle`, `CouchSlicingPuzzle`
- `BlinkingLightsPuzzle`, `MisplacedTilePuzzle`, `PaintingPuzzle`
- `FurnacePuzzle`, `BoxPuzzle`, `ChemistryTable`, `MirrorPuzzle`, `StatueRiddlePuzzle`

#### Top-level functions
- `main.get_gif_dimensions`, `main.main`
- `engine.save_system.save_game/load_game/has_save/delete_save`
- `engine.settings.load_settings/save_settings`
- `engine.player.load_sprite_images/load_pfp/load_idle_images`
- `engine.room.build_easy_room/build_easy_room_from_tmx/build_level2_room_from_tmx/_add_tile_walls/build_level3_room_from_tmx`
- `engine.tmx_loader._parse_tsx/load_tmx`
- `states.menu_state.load_gif_frames`
- `check_assets.check_assets`
- `verify_assets.find_missing_in_assets`
- `remap_assets.remap_and_find_missing`
- `organize_level3.organize_level3`

This list is exhaustive for all project `.py` files currently present.
