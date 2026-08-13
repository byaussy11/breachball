# Breach Ball — Project Brief (Working Draft)

*A unique, 2-player cooperative take on Breakout. Part of the Arcade Cabinet Game Project (Phase 1).*

---

## Working Title
**Breach Ball** (decided).

## Elevator Pitch
A 2-player cooperative brick-breaker where two players infiltrate an enemy spaceship section by section — the ball's color dictates who can (or must not) hit it, paddles gain unique skills over time, and each ship section's bricks, enemies, and boss demand coordinated paddle tech to beat, not just fast reflexes.

---

## Decided So Far

- **Player count:** 2 players, cooperative (not competitive).
- **Paddle colors (official):** Player 1 = silver (matching the shiny silver spinner). Player 2 = onyx black. (Earlier mockups used teal as a placeholder — not official.)
- **Ball color states:**
  - Neutral — either player can hit it.
  - Owned color (P1 or P2) — only that player can hit it.
  - Hazard/bomb color — neither player may hit it; must avoid.
- **Paddle skills:** Paddles can learn/gain skills that change how they behave (specifics TBD — see open questions).
- **Bricks:** Have special behaviors beyond simple destruction (specifics TBD — see open questions).
- **Bosses:** Have unique abilities requiring specific paddle-skill combos to counter. Confirmed example: boss fires a shot one player can absorb, then the other player returns/reflects it.
- **Lives/game over:** Losing the ball or getting hit by an enemy costs a life. Hitting 0 lives = game over (lose). Lives are a **shared pool** between both players, not individual — individual lives would create awkward questions for cooperative mechanics (and the arena itself) if one player's paddle ran out while the other kept playing.
- **No endless mode** for v1 — possible stretch goal if time allows.
- **Win condition:** Clear all breakable bricks and all enemies (indestructible bricks and permanent-hazard enemy variants don't count, since they're not meant to be cleared).
- **Level format:** Mix of hand-designed levels (especially bosses/scripted moments) and a data-driven format (e.g. JSON) for standard brick layouts.
- **Input hardware:** Two physical spinners. One is currently mapped to horizontal mouse movement, the other to vertical mouse movement.
- **Arena/paddle layout (default):** Each paddle moves in 1 dimension. Both paddles are horizontal, stacked at different heights (one nearer the bottom, one higher up) rather than side-by-side lanes. Players may switch positions (top/bottom) between levels.
- **Arena/paddle layout (variant, used sparingly):** Some levels swap in an L-shaped arrangement — one player's paddle stays horizontal on the bottom edge, the other player's paddle becomes vertical on a side edge — as an occasional change-up for variety, not the default.
- **Arena zone types (within the default stacked-paddle layout):**
  - **Shared zone (most common):** Bricks fill the whole field; both paddles defend the same ball; ball is lost only past the bottom paddle. Top paddle acts more like an obstacle/redirect point than a second "death line."
  - **Split zone (occasional variant):** Bricks split top/bottom; each paddle owns its own zone; ball can be lost past *either* paddle, not just the bottom one.
- **Volley/trade ball mechanic:** An intentional back-and-forth mechanic where the ball is meant to be volleyed between the two paddles as part of a puzzle/pattern — can appear as a special ball behavior *within* the shared-zone layout, not a separate arena type.
- **Split-zone dividers:** Built from the brick system itself — indestructible bricks form the wall dividing the two zones, rather than a separate arena element.
- **Paddle travel range:** Default is full-width travel for both paddles (left wall to right wall), same as the bottom paddle already had. A narrower travel lane for a paddle (leaving permanent unguardable gaps at the edges) is available as a level-design tool to use when it serves a specific level — same treatment as the L-shaped/split-zone variants, decided case-by-case rather than a fixed rule. Full-width range also matters for the laser skill: it lets the bottom paddle line up under any brick (including boss weak points) to fire straight up, so it isn't boxed out of reaching parts of the field.
- **Corner transfer tubes:** Tubes at the arena's corners let a paddle transition to a different lane (side wall or top). Bottom-left and top-left tubes are exclusive to Player 1, letting P1 traverse bottom/left/top lanes. Bottom-right and top-right tubes are exclusive to Player 2, letting P2 traverse bottom/right/top lanes. Usable freely at any time (not restricted to scripted moments). A paddle rotates to vertical orientation when in a side (left/right) lane, matching the L-shaped variant. If both players end up sharing the same lane, they arrange in the same "one above the other" stacked relationship as the default layout — no new overlap/collision logic needed between paddles.
- **Brick visual system:** Each brick type has its own associated color for at-a-glance readability. If the brick type list grows too large for color alone to distinguish, icons may be added later — especially if bricks move from rectangular to square.
- **Brick types (v1 candidate list):**
  - Standard — one hit, destroyed.
  - Armored/multi-hit — takes multiple hits, cracks visibly between them.
  - Regenerating — repairs itself over time if not fully destroyed.
  - Explosive — destroys neighboring bricks in a chain when hit.
  - Timed/Fuse — countdown; bad effect if it detonates before being destroyed.
  - Moving/Sliding — patrols a track, harder to line up a hit.
  - Indestructible — permanent, used to shape the arena and as split-zone dividers.
  - Color-locked (possible) — only breakable by the ball currently owned by the matching player; depends on final fit with the ball-ownership-color mechanic.
  - Pushable (new idea) — doesn't break on hit; instead moves in the direction the ball hit it from, until it hits a wall or another brick, at which point both are destroyed.
- **Design principle — 1-player support:** The game must also work solo, reusing the same arena layouts and boss mechanics as 2-player wherever possible (not separately redesigned per mode). Solo control scheme: **switch/toggle** — one spinner, but the player can toggle which of the two paddles is "active" at any moment. The non-active paddle holds its last position rather than freezing uselessly or mirroring the active one, so it can be pre-positioned (e.g. lined up to reflect an absorbed boss shot) before switching focus back to it. Mirrored-movement was considered and rejected: it breaks down for bricks that spawn multiple balls (paddles can't cover divergent ball positions) and for boss mechanics like absorb-then-reflect that require the two paddles in genuinely different horizontal positions at the same time.
- **Difficulty scaling by player count:** Solo is expected to be somewhat harder than 2-player for high-intensity moments (e.g. multi-ball chaos), which is acceptable. Level data may scale things like ball count or enemy count based on player count rather than trying to make solo strictly equivalent to 2p.
- **Fallback:** If solo-via-single-spinner proves too difficult to make work well across all mechanics, the game may end up 2-player only.
- **Simultaneous-reactive-tracking limitation (known gap):** Switch/toggle can't support moments requiring true simultaneous reactive control of two independent moving targets (e.g. two live, color-locked balls in play at once) — the parked paddle can't adjust to a ball that moves away from where it was left. Default handling: scope these specific moments out of solo (2-player-exclusive, or redesigned as sequential for solo). Revisit only if a specific mechanic down the road causes genuine problems — not solving pre-emptively. Hope is that solo mode mostly needs targeted tweaks (reduced counts, sequential vs. simultaneous variants) rather than wholesale redesigns.

---

## Paddle Abilities

### Innate (always available, no acquisition needed)
- **Slam attack:** A paddle moving at higher speed can damage/destroy small enemies on contact — e.g. an enemy that grabs the ball and tries to carry it out the bottom of the screen can be knocked away by a paddle slamming into it from the side.

### Learned/Acquired Skills (via skill bricks and/or power-up devices — delivery mechanism still open, see Open Questions)
- **Grow** — tiered, 3 levels: paddle becomes progressively larger.
- **Laser shooter** — tiered: Lvl 1 = slow, single shot from paddle's center. Lvl 2 = faster single shot. Lvl 3 = adds additional shots to the left and right. (Good model for other tiered skills too.)
- **Ball magnet** — tiered, 3 levels: pulls the ball toward the paddle, presumably stronger pull/range at higher tiers (specifics TBD).
- **Sticky** — tiered, 3 levels: Lvl 1 = ball sticks to the paddle on contact instead of bouncing immediately, allowing an aimed release. Lvl 2 = adds a dotted trajectory-preview line showing the ball's initial direction on release. Lvl 3 = extends that preview line through the first bounce off a wall/brick, continuing on to show where it goes next.
- (List will keep growing as design continues.)

### Ball-Affecting Skills (new category — affect the ball itself, not the paddle)
- **Slow ball** — reduces ball speed.
- **Piercing ball** — ball blasts straight through bricks instead of bouncing off, destroying them as it passes. Open for later: duration-based (lasts N seconds) vs. count-based (pierces N bricks then reverts); does it pierce every brick type (armored, indestructible) or just standard ones; does it still trigger special brick effects (explosive chain, enemy-spawn) as it passes through.
- (List will keep growing as design continues.)

### Cooperative/Special (innate ability)
- **Ball duplication (working name):** If the bottom paddle stays at least 60% horizontally aligned under the top paddle for a set duration, a new ball is created on the board. Chosen over a simpler "both paddles just stand still anywhere" version specifically because the alignment requirement forces players into a position the *level* controls the safety of, rather than letting them retreat somewhere safe to charge — preserving the intended risk (can't catch capsules, can't react to enemies/color-changes/other threats while channeling). Designed to give players an active choice of pacing — e.g. spend a few seconds on this while an existing ball is productively bouncing around the bricks on its own. Taking damage (enemy hit, lightning stun, etc.) mid-charge resets progress to zero.
  - **Innate, not learned:** Unlike grow/laser/magnet/sticky (which represent something attached to one paddle and fit the per-paddle capsule-catch delivery system), this ability only exists in the interaction *between* both paddles, so gating it behind a single-paddle capsule pickup would be an awkward fit. Available from the start; likely introduced via an early tutorial-style level rather than earned as a mid-game reward.
  - **No hard gameplay cap on balls in play:** Consistent with existing uncapped brick-triggered multi-ball moments — capping this specific source would be an inconsistent rule for players to learn. The mechanic is self-throttling anyway, since channeling costs real time/exposure, so players won't spam it into unmanageable chaos without real risk. A generous technical-only safety ceiling (e.g. ~30 balls) should still exist under the hood purely as an engineering safeguard against bugs, not as a felt gameplay limit.
  - **Timing:** 5 seconds to complete the alignment channel (make this an easily tweakable constant, not hardcoded — will likely need tuning once playtested).
  - **New ball color:** White/neutral — either paddle can hit it, same as any other neutral ball. Its color can change afterward same as any ball, based on level mechanics/broken bricks.


- **Extra life** — rare drop, not a paddle ability, just a resource.

## Bosses

### Boss Concept #1 (unnamed, not tied to a specific Section yet)
A multi-phase fight that cycles through most of the game's core systems in one encounter:
1. **Breakdown phase** — standard ball-and-brick play against the boss's defenses (likely armor-style bricks on the boss itself).
2. **Weak-point phase** — once defenses are worn down, red flashing weak points appear that must be hit with the players' *acquired paddle attacks* (e.g. laser), not just the ball — ties acquired skills directly into boss relevance, not just level-clearing.
3. **Malfunction trigger** — players work the ball into a specific crevice/pocket on the boss, jamming it; this causes the boss to stutter its movement and spark.
4. **Payoff** — the malfunctioning boss fires a laser; one paddle absorbs it, then it's passed almost immediately to the other paddle, which fires it back at the boss. Exact timing window is tunable for difficulty.
5. **Unique enemies**, specific to this boss fight, spawn throughout to add pressure during the above phases.
- Open: how many times does the full breakdown→weak-point→malfunction→payoff cycle need to repeat to defeat the boss? Does the reflected laser count as the boss's actual "damage," or is it more of a stagger/reset mechanic that starts the cycle over?
- **Optional idea (not yet decided necessary):** paddles could temporarily move to the left/right walls during a boss fight — extra bricks/red weak-point lights on the sides to destroy. Wouldn't require new tech, since it's the same underlying mechanic as the existing L-shaped arena variant, just applied within a boss fight (possibly as a later-phase escalation). Revisit once specific bosses are being designed and it's clearer whether a given fight benefits from it.


- Levels are organized into **Sections**: 9 regular levels followed by a boss on the 10th level, repeating per Section.
- **Theme (locked in):** A spaceship infiltration story — the players are boarding/infiltrating an enemy ship. Each Section represents a different part of the ship (examples: Docking, Engines, Filtration, Command), and carries its own themed set of enemies, brick types/rules, and visual identity. Section-ending bosses are likely tied to that area's theme (e.g. an Engines-section boss built around heat/energy mechanics, a Command-section boss built around control/manipulation mechanics).


## Skill Delivery
- **Mechanism:** Capsule-catch, Arkanoid/brick-breaker style. Destroying a skill brick drops a falling capsule that must be physically caught by a paddle — not granted automatically on destruction.
- **Who gets it:** Whichever paddle physically catches the capsule receives the skill (or tier-up), regardless of which paddle's ball broke the brick. Since the default arena has two stacked horizontal paddles, this makes positioning a real in-the-moment decision — the paddle nearer the brick (often the top one) gets first chance, but a capsule falling through the gap gives the other paddle a shot too.
- **If uncaught:** A capsule that falls past both paddles is lost for good — no second chance, no respawn.
- Implies skills are earned **per-paddle**, not shared team-wide (each player can end up with a different skill loadout depending on what they catch).
- **On death:** When a paddle dies (loses a life), it loses all its skills — no persistence across a life loss.


*Naming for enemies, paddles, and enemy-specific visual theme is deferred until further along — now that "Breach Ball" and the spaceship-infiltration theme are locked, enemy names can be tackled anytime.*
*Naming convention idea (not yet decided): enemies as numbered drones/bots, with model-number-style names that spell a word in leetspeak — e.g. the ball-grabber as `TH13F` or `7H13F`, the shielded deflector as `D-FLCTR` (dropped-vowel style, a nice variant alongside the number-substitution style). Fits the "drone" framing well; still open whether this surfaces in actual gameplay UI (may be too cryptic at a glance) or stays as flavor text in a codex/credits-style screen.*
- **Ball-grabber:** Grabs hold of the ball and tries to carry it out the bottom of the screen; can be knocked away by a paddle's slam attack (see Innate Abilities above). Counts as an enemy that must be cleared to win the level, per the win condition.
- **Lightning jellyfish** *(working name candidates: `W1R3`, `5T1NG`, or `J3LLYF15H`/`J3L1YF15H` — a knowing nickname, since the crew calls it "jellyfish" for how it looks despite it being a wired drone)* — Visually a drone with a bundle of live, wriggling hot wires trailing from its underside (reads as jellyfish tentacles, but makes diegetic sense as exposed wiring/current rather than an actual creature). Floats around, periodically shoots paddle-colored lightning bolts. If the same-colored paddle is hit, that paddle is stunned for a few seconds. Deliberately color-coded (not neutral) so it creates teamwork moments — e.g. one player takes the stun on purpose so the other is free to handle the ball.
- **Shielded deflector:** Descends from the top with a small shield beneath it, deflecting the ball as it moves downward — making it harder to keep the ball up and harder to hit bricks while it's in play. The shield only protects against direct/frontal (downward) hits; it can be damaged by a ball connecting from above (e.g. on a return path, hitting its unshielded top) or by a paddle's slam attack side-swiping it as it tries to pass by. If it passes the player and exits off the bottom, it reappears at the top or a side to descend again, looping rather than being a one-time threat. Some versions may be fully indestructible (a harder, permanent-hazard variant) rather than the standard destructible one. Per the win condition, the standard destructible version must be cleared like any other enemy; the indestructible variant is presumably excluded (not meant to be cleared), consistent with permanent-hazard bricks.
- **Diving drone (working name pending theme naming pass):** A paddle-attacking enemy with four phases:
  1. **Track/hover** — flies to a position above a paddle and hovers there, adjusting horizontally to follow the paddle's movement. Bobs slightly up and down while hovering to read as a floating disc. No damage/collision with the paddle during this phase.
  2. **Telegraph** — commits to attack by completing one full circle; stops tracking the paddle the instant this begins, so the attack targets where the circle happened, not the paddle's current position. Does **not** touch or damage either paddle during the telegraph — it's a pure visual warning, not a hazard.
  3. **Dive** — drops straight down along the circle's position. Has a visible spike/pointed hazard on its underside so contact clearly reads as lethal.
  4. **Recovery** — glides slowly back upward to attempt again. This is the vulnerability window for the paddle's innate slam attack. A paddle positioned in its ascent path physically blocks it (can't pass through), stalling it in place — this can be used to either slam it immediately, or hold it there while the other paddle repositions to help.
  - **Loops indefinitely** if not destroyed — a persistent, escalating threat rather than a limited-attempt one, so it needs to be dealt with promptly.
  - Open: does it take one slam hit to destroy, or multiple?
  - Open: how this enemy's dive/telegraph geometry adapts when targeting a paddle on the top or side (left/right) lanes rather than the default bottom — "dive straight down" doesn't translate directly to those orientations.

---

## Open Questions (running list)

1. **Color-locked bricks:** Depends on how well the "brick color = matching player" idea reads against the existing ball-ownership-color mechanic — need to make sure brick colors and ball-ownership colors don't visually collide/confuse.
2. **1-player edge cases:** Track any specific mechanics (as skills/bosses are designed) that turn out to need scoping out of solo or a sequential-instead-of-simultaneous variant, per the simultaneous-reactive-tracking limitation above.
3. Boss roster and the specific "unique solution" mechanic per boss. (Deferred — will come as the game gets developed, not needed to resolve now.)
4. Additional ball states beyond neutral/owned/hazard (e.g. a "combo" state requiring both players)? (Revisit later.)

---

## Subsystems Inherited from Roadmap
(from ARCADE_PROJECT_README.md — this game is expected to establish these for reuse later)
- Spinner/analog input mapping
- Ball physics & collision (AABB/circle)
- Brick/level data format
- 2-player local input handling

---

## Version Roadmap

**Current state (v0.1.0–v0.1.2):** Initial scaffolding is complete. Two paddles exist and can be
positioned top, bottom, or side; ball movement and collision detection (paddles, walls, bricks)
are working; bricks break on hit; several special brick types are already implemented. Not yet
implemented: real win/lose detection (all four screen edges currently act as generic walls,
rather than the actual shared-zone/split-zone rules). v0.1.2 added a local, non-committed config
file.

**Audio manager (foundational, build alongside 0.2.0):** A minimal wrapper for playing SFX/music
(`play_sound("brick_break")`, `play_music("section_theme")`) — belongs with the other shared
plumbing (`controls.py`, resolution scaling) rather than being bolted on later. Building this once,
early, means every milestone after just adds a sound file and a call into it.

**0.2.0 — Playable Core Loop:** Replace the placeholder "all four sides are walls" behavior with
real win/lose rules — shared-zone default (lose only past the bottom paddle) and split-zone
variant (lose past either paddle) — plus a shared lives pool and game over, the win condition
(all breakable bricks cleared), and ball ownership colors (neutral/P1/P2/hazard) with actual
enforcement of who can hit which ball. This is the milestone where the game becomes genuinely
loseable/winnable for the first time, rather than just running. Audio opportunity: the
most-heard SFX in the game — ball bounce (paddle/wall/brick), brick break, life lost, game
over/win stings.

**0.3.0 — First Pixel-Art Pass (Paddles):** Swap the placeholder paddle rectangles for the sprites
already prototyped earlier in design (base paddle plus the laser turret attachment), palette-swapped
to the official colors — silver for Player 1, onyx black for Player 2. Low-risk, high-payoff step
since the groundwork already exists; no reason to wait for the rest of the art to do this one.
Also a good point to add a paddle "life lost" death animation/sequence, now that the base paddle
sprite exists to animate.

**0.4.0 — Paddle Skills & Capsule System:** Capsule drop/catch mechanics, the tiered skills (Grow
3 tiers, Laser 3 tiers, Ball Magnet 3 tiers, Sticky 3 tiers including the trajectory-preview and
bounce-preview levels), skill loss on paddle death, the innate slam attack, and the ball
duplication cooperative mechanic (60% alignment channel, 5 seconds, resets on damage). Art
opportunity: capsule sprites and laser projectile art, building on the turret sprite groundwork
from 0.3.0. Audio opportunity: capsule catch, skill activation per type (laser fire, magnet hum,
sticky catch/release), ball duplication charge/complete.

**0.5.0 — Enemies:** Ball-grabber, lightning jellyfish (wired-drone visual concept), and shielded
deflector (both destructible and indestructible variants), plus the spawn system. Extends the win
condition to also require clearing enemies, not just bricks. Art opportunity: sprite each enemy as
it's implemented rather than batching all enemy art at the end, including a death animation per
enemy type as each one gets its sprite. Audio opportunity: SFX per enemy
(grab, zap/stun, deflector clank), enemy defeat sound.

**0.6.0 — Level Data Pipeline & Level Editor:** Full brick-type catalog and `brick_grid` JSON
loading (finishing out the remaining v1 brick types — regenerating, timed-fuse, moving, pushable,
color-locked — alongside what's already implemented), plus a first-pass paint-mode level editor
built as a dev-mode toggle inside the game itself, reusing the same grid-rendering pipeline. Art
opportunity: brick sprites per type, a natural moment to tackle since building/using the editor
means spending a lot of time looking at the grid.

**0.7.0 — Arena Variants & Transfer Tubes:** Split-zone and L-shaped arena variants, corner
transfer tubes, the per-level `paddle_lanes` configuration and validation rules, the lane-based
clockwise spinner-direction mapping, and paddle travel-range variants (full-width default vs.
narrower level-design option). Art opportunity: tube visuals, arena wall/frame dressing. Audio
opportunity: tube whoosh/transition sound.

**0.8.0 — Solo Mode & Input Polish:** The switch/toggle single-spinner control scheme for 1-player
mode, and difficulty scaling by player count (e.g. reduced ball/enemy counts for solo).

**0.9.0 — First Boss, Attract Mode & First Full Section:** Boss Concept #1 (breakdown phase,
weak-point phase, malfunction trigger, absorb-and-reflect payoff), boss-specific enemies, the
attract-mode/coin-op shell (insert coin, press start, demo loop, credits), and a complete first
Section (9 regular levels + boss on the 10th) playable end-to-end. Art opportunity: the boss
sprite and attract-mode screens — saved for last since the boss design was the most recently
finalized of the major systems — plus a boss death sequence, likely the most elaborate animation
in the game given the fight's multi-phase structure, and a natural capstone moment. Audio opportunity: this is where music really lands — attract-mode
theme, boss music, and optionally a Section theme, since it's the first point with a complete,
playable loop worth scoring. Also boss-specific SFX (malfunction stutter/spark, absorb/reflect).

**1.0.0 — First playable release:** One full Section playable end-to-end in both 1-player and
2-player modes, stable, with attract mode and coin-op conventions fully in place.


Skill delivery is now settled (capsule-catch). Good next targets: the boss roster (question #6), win-condition specifics (#4), or filling out more of the paddle skill list.

## Engine Scope (for implementation phase)
Build shared/generic from the start: controls abstraction (`controls.py` mapping physical input, including spinner, to logical per-player actions), resolution/aspect ratio, and the attract-mode/coin-op shell — these are cabinet-level concerns the master README already flags as "decide early." Everything else (ball physics, bricks, paddle skills, enemies, boss state machines) should be written directly and specifically for Breach Ball rather than pre-abstracted into a generic engine. Revisit what's actually reusable once game #2 is underway and there are two real examples to generalize from, rather than guessing now.

**Resolution/aspect ratio:** Final cabinet monitor not yet chosen, but confirmed landscape mounting, general classic-arcade feel (referenced: TMNT arcade). Build against a **640×480 virtual/logical resolution (4:3 landscape)** as the working target — render everything to this fixed-size surface, then scale that surface to whatever the real monitor turns out to be at deploy time (same nearest-neighbor scaling approach already used for pixel-art sprites). This decouples development from the final hardware decision — layouts, brick grids, and gameplay math are all built against the fixed virtual coordinate space, so picking real hardware later only means changing one scale factor.

**Controls dev/testing fallback:** Since development happens in WSL without the physical cabinet/spinner attached most of the time, `controls.py` should include a keyboard fallback (e.g. arrow keys or A/D) mapped to the same logical per-player actions as the spinner — lets gameplay be tested on a regular machine, with the real spinner only needed once testing on the actual cabinet.

## Art/Visual Pipeline
For initial implementation, use simple placeholder shapes (rects, circles, flat colors) for paddles, balls, bricks, and enemies — this makes core functionality (collision, skill states, color-ownership logic, arena layout) easy to build, debug, and see working correctly without waiting on final art. Real retro pixel-art sprites are a later pass, swapped in once gameplay systems are solid; some early sprite experiments (a base paddle, a laser turret attachment) were prototyped and liked, but aren't being wired in yet.
