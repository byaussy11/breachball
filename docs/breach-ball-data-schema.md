# Breach Ball — Data Schema (Draft)

A first-pass data model translating the project brief into concrete structures. Intended as a
starting point for implementation in Claude Code — field names/types are suggestions, not final.

---

## Brick Types (catalog)

Reusable templates, defined once and referenced by ID wherever that brick appears in any level.
Naming convention embeds key stats for readability when hand-editing (e.g. `brick_arm_3hit` =
armored, 3 hits).

```json
{
  "brick_std": { "type": "standard", "hp": 1, "color": "#5DAA6E" },
  "brick_arm_3hit": { "type": "armored", "hp": 3, "color": "#8899AA" },
  "brick_regen_std": { "type": "regenerating", "hp": 1, "regen_seconds": 4, "color": "#5DAA6E" },
  "brick_explosive_std": { "type": "explosive", "hp": 1, "chain_radius": 1, "color": "#C1440E" },
  "brick_fuse_5s": { "type": "timed_fuse", "hp": 1, "fuse_seconds": 5, "color": "#C1440E" },
  "brick_moving_std": { "type": "moving", "hp": 1, "patrol_path": "horizontal_2", "color": "#5DAA6E" },
  "brick_wall": { "type": "indestructible", "color": "#444444" },
  "brick_locked_p1": { "type": "color_locked", "hp": 1, "color_lock_owner": "p1", "color": "silver" },
  "brick_push": { "type": "pushable", "color": "#5DAA6E" },
  "brick_std_cL": { "type": "standard", "hp": 1, "color": "#5DAA6E", "capsule_skill_id": "laser" },
  "brick_arm_cM": { "type": "armored", "hp": 3, "color": "#8899AA", "capsule_skill_id": "ball_magnet" },
  "brick_color_p1": { "type": "color_trigger", "hp": 1, "color": "silver", "sets_ball_color": "p1_owned" },
  "brick_color_p2": { "type": "color_trigger", "hp": 1, "color": "#141414", "sets_ball_color": "p2_owned" }
}
```

`sets_ball_color` is an optional field (mirrors `capsule_skill_id`'s per-entry-flag pattern) naming a
ball `color_state` (`neutral`, `p1_owned`, `p2_owned`, `hazard`) applied to whichever ball hits that
brick — a `color_trigger` brick is how ball-ownership colors actually get set during play, enforced
against paddles per the ball-ownership-color mechanic above.

`capsule_skill_id` is an optional field on any catalog entry (omit or `null` for a brick that
drops nothing). Rather than tracking capsule drops as a separate list of coordinates, a
capsule-dropping brick is just its own catalog entry that you place directly in the grid like any
other brick — one less thing to keep in sync by hand.

**Capsule brick naming convention:** a lowercase `c` in the ID always marks a capsule-dropping
brick, followed immediately by an uppercase letter identifying which skill it drops:

| Letter | Skill |
|---|---|
| `G` | Grow |
| `L` | Laser |
| `M` | Ball Magnet |
| `S` | Sticky |

E.g. `brick_std_cL` = a standard brick dropping a Laser capsule; `brick_arm_cM` = an armored
brick dropping a Ball Magnet capsule. This table should grow alongside any new capsule-delivered
skills (ball-affecting skills like Slow Ball / Piercing Ball would need letters assigned too, once
their delivery method is finalized).

**Types (v1 candidate list):** `standard`, `armored`, `regenerating`, `explosive`, `timed_fuse`,
`moving`, `indestructible`, `color_locked`, `pushable`, `color_trigger`. Capsule-dropping is a per-instance flag,
added when the type is placed in a level (see below), not baked into the catalog entry, since the
same brick type might drop a capsule in one level and not another.

Open items: exact HP values per type (shown above are placeholders), regen timing, chain-explosion
radius, fuse duration, patrol path format for moving bricks, and whether color-locked bricks need
a distinct visual treatment from ball-ownership colors (see brief's open questions).

---

## Enemy Types (catalog) + Spawn List

Same reusable-template pattern as bricks: define each distinct enemy configuration once, then
reference it by ID wherever it spawns.

```json
{
  "enemy_types": {
    "th13f": { "type": "ball_grabber", "hp": 1, "destructible": true },
    "w1r3": { "type": "lightning_jellyfish", "hp": 1, "lightning_color": "p1", "stun_seconds": 2 },
    "d-flctr": { "type": "shielded_deflector", "hp": 2, "shield_facing": "down", "loop_on_exit": true },
    "d-flctr_hard": { "type": "shielded_deflector", "destructible": false, "shield_facing": "down", "loop_on_exit": true }
  },
  "enemy_spawns": [
    { "enemy_type": "th13f", "spawn_x": 300, "spawn_y": 0, "trigger": "time:5s" },
    { "enemy_type": "w1r3", "spawn_x": 100, "spawn_y": 50, "trigger": "time:12s" }
  ]
}
```

Unlike bricks (which sit in a static grid), enemies typically need per-spawn timing/position data,
so they stay as a flat spawn list rather than a 2D grid — but still reference reusable type IDs
rather than repeating full definitions.

**Types so far:** `ball_grabber`, `lightning_jellyfish`, `shielded_deflector` (destructible and
indestructible variants).

---

## Paddle Skill

```json
{
  "skill_id": "laser",
  "display_name": "Laser Shooter",
  "delivery": "capsule_catch",
  "max_tier": 3,
  "tiers": [
    { "tier": 1, "params": { "shot_count": 1, "shot_speed": "slow", "positions": ["center"] } },
    { "tier": 2, "params": { "shot_count": 1, "shot_speed": "fast", "positions": ["center"] } },
    { "tier": 3, "params": { "shot_count": 3, "shot_speed": "fast", "positions": ["left", "center", "right"] } }
  ],
  "lost_on_death": true
}
```

**Skills so far:** `grow` (3 tiers), `laser` (3 tiers, shown above), `ball_magnet` (3 tiers — field
shape: single continuous arch anchored at paddle's bottom corners, growing wider/taller per tier),
`sticky` (2 tiers — tier 2 adds trajectory preview line).

**Innate abilities** (not capsule-delivered, always on): `slam_attack` (paddle moving above a
speed threshold damages/destroys small enemies on contact), `ball_duplication` (bottom paddle
60%+ horizontally aligned under top paddle for 5 seconds creates a new neutral-color ball; damage
resets progress to zero; no hard cap on balls in play; timing should be an easily tweakable
constant).

**Ball-affecting skills** (affect the ball, not the paddle): `slow_ball`, `piercing_ball` (open:
duration vs. count-based, which brick types it pierces, whether it still triggers brick effects
like explosions while passing through).

---

## Ball

```json
{
  "id": "ball_01",
  "color_state": "neutral",
  "owner": null,
  "x": 340,
  "y": 200,
  "vx": 4.2,
  "vy": -3.1,
  "piercing": false,
  "speed_multiplier": 1.0
}
```

`color_state` is one of `neutral`, `p1_owned`, `p2_owned`, `hazard` (additional "requires both
players" state deferred per brief's open questions).

---

## Paddle

```json
{
  "player": 1,
  "color": "silver",
  "x": 340,
  "lane": "bottom",
  "orientation": "horizontal",
  "size_tier": 1,
  "active_skills": { "laser": 2, "sticky": 1 },
  "travel_range": "full_width"
}
```

`lane` is one of `bottom`, `top`, `left`, `right`. `orientation` flips to `vertical` automatically
when `lane` is `left` or `right`. `travel_range` is `full_width` by default; a level can override
to a narrower range as a level-design choice.

**Lane assignment is level-scoped, not a standing feature.** Each level explicitly assigns which
lane(s) each player has access to — a level can hard-fix P1 to `bottom` and P2 to `top` with no
tubes at all, or give one player several lanes while the other keeps just one. Transfer tubes are
only needed (and only present) when a level wants to give a specific player mobility between
multiple lanes — they're opt-in per-level infrastructure, not something every level has. See the
Level/Section format below for how this is configured.

**Spinner-to-paddle direction mapping:** Clockwise spinner rotation always drives the paddle the
same consistent way around the arena's perimeter loop, regardless of which lane it's currently in
— this keeps controls from feeling like they "flip" when moving between lanes via a tube.
- `bottom` lane: clockwise → paddle moves right
- `right` lane: clockwise → paddle moves up
- `top` lane: clockwise → paddle moves left
- `left` lane: clockwise → paddle moves down
(Counter-clockwise reverses each of the above.) This should live in the shared `controls.py`
abstraction (see Engine Scope in the brief) as a lookup keyed by current lane.

---

## Level / Section

```json
{
  "section": "Engines",
  "level_number": 4,
  "is_boss_level": false,
  "arena_type": "shared_zone",
  "paddle_lanes": {
    "p1": { "lanes": ["bottom"], "tubes": false },
    "p2": { "lanes": ["top"], "tubes": false }
  },
  "player_count_scaling": { "1": { "max_balls": 1 }, "2": { "max_balls": 2 } },
  "brick_grid": [
    [null,          "brick_std",     "brick_std_cL",  null,            null],
    ["brick_arm_3hit", "brick_std",  null,            "brick_arm_3hit", null],
    [null,          "brick_push",    "brick_explosive_std", "brick_push", null]
  ],
  "enemy_types": { "th13f": { "type": "ball_grabber", "hp": 1, "destructible": true } },
  "enemy_spawns": [
    { "enemy_type": "th13f", "spawn_x": 300, "spawn_y": 0, "trigger": "time:5s" }
  ],
  "boss_id": null
}
```

`brick_grid` is a 2D array (rows = `grid_y`, columns = `grid_x`) of brick-type-ID strings or
`null` for an empty cell — mirrors the visual layout directly, easy to hand-edit, and is the
natural format for a level editor's "paint with this brush" tool to read/write. `paddle_lanes`
defines, per level, which lane(s) each player can occupy and whether tubes exist to move between
them — this example shows a fixed top/bottom split with no tubes; a level giving a player
multiple lanes would set `"tubes": true` and list more than one lane.

**Optional compact authoring format:** Before the level editor exists, hand-typing nested JSON
arrays of quoted brick IDs is tedious to eyeball for larger grids. An alternative — convertible to
the same `brick_grid` shape by a small loader function — is a row-string + legend format, similar
to old-school ASCII level maps:

```json
{
  "legend": { ".": null, "S": "brick_std", "A": "brick_arm_3hit", "L": "brick_std_cL" },
  "rows": [
    "..L..",
    "AS..A",
    ".P.E."
  ]
}
```

Each character maps to a brick-type ID (or `null`) via the legend; a small conversion function
expands this into the full `brick_grid` array at load time. Much faster to hand-write and visually
scan than the nested-array form, at the cost of being limited to single-character codes — fine for
a manageable legend size, less practical if a level uses a very large number of distinct brick
types at once.

**Validation rules for `paddle_lanes` (level designer / editor should enforce these):**
- `"tubes": true` is only valid when `lanes` has more than one entry — a single-lane assignment
  never needs tubes, since there's nowhere to transfer to.
- Tubes physically connect *adjacent* lanes only, via the corners: for P1 that's
  bottom↔left↔top; for P2 that's bottom↔right↔top. A lane list of `["bottom", "top"]` alone is
  **invalid** for either player — there's no tube that skips directly from bottom to top without
  passing through the connecting side lane. If a player's lanes include both `bottom` and `top`,
  the list must also include their connecting side lane (`left` for P1, `right` for P2).
  Valid P1 examples: `["bottom"]` (no tubes), `["bottom","left"]`, `["left","top"]`,
  `["bottom","left","top"]`. Invalid: `["bottom","top"]`.

Sections are groups of 10 levels (9 regular + boss on the 10th). `arena_type` is one of
`shared_zone`, `split_zone`, `l_shaped`. Mix of hand-authored levels (bosses/scripted moments)
and data-driven JSON for standard layouts, per the brief.

---

## Tooling — Level Editor
Plan to build a simple level editor as a dev-mode toggle inside the game itself, rather than a
separate standalone tool — it can reuse the same code that reads `brick_grid`/`enemy_spawns` and
renders them, just adding: a brush palette (pick a brick-type ID or enemy-type ID), mouse-click to
paint/erase a grid cell, and an export-to-JSON action. Worth building early, as soon as the basic
brick-grid rendering pipeline exists, since every level authored afterward gets much faster.

---

## Open Items Carried Over From the Brief
See the brief's Open Questions section for design-level items not yet reflected here (color-locked
brick visuals, 1-player edge cases, boss roster, additional ball states). This schema will need
another pass once those are resolved.
