## Rule components

Written before reading any transcript (precommit addendum, 26 October 2026).
Each component is one part of the final rule that can be checked on its own in the model's rule.
Score per transcript: components present / components total.

Judging:
- paraphrase counts, same meaning in other words is present
- binary, partly there is absent
- coverage only: extra wrong parts in the model's rule don't lower it, the outcome category and tags record those
- only what's in my final rule. Unresolved or underdetermined parts aren't components

---

### 18447a8d

final rule: each coloured block moves left, to the level in which the shape gap fits exactly completing a rectangle, the piece keeps its color

components:
- coloured blocks move, the other shapes stay
- move is horizontal, to the left
- vertical position: the level where the block fits the shape's gap
- fit is exact, block + shape complete a rectangle
- block keeps its colour

### 25c199f5

final rule: split input into 3 panels; stack the objects in each panel bottom-up (left, middle, right) each keeping its column, touching

components:
- input split into 3 panels
- output is the objects stacked in one panel
- stack order bottom-up: left, middle, right
- each object keeps its column
- objects touch, no gaps

### 305b1341

final rule: legend top-left maps dot color to frame color; around each same color dot group draw its bounding box + 1 in the frame color, dots kept; overlaps: higher legend row on top; erase legend

components:
- legend top-left maps dot colour -> frame colour
- one frame per same-colour dot group, not per dot
- frame = bounding box + 1
- dots kept inside the frame
- overlap: higher legend row on top
- legend erased

### 320afe60

final rule: blue (1) shapes with all holes sealed turn red (2) and slide to left edge; shapes with a hole open to the outside turn green (3) and slide to right edge; same rows, same shape

components:
- blue (1) shapes split by holes: all sealed vs one open to the outside
- sealed -> red (2), open -> green (3)
- sealed slide to left edge, open to right edge
- same rows, shape unchanged

### 458e3a53

final rule: grid lines split input into cells; the uniform-color cells form a rectangle; output is that rectangle, one pixel per cell, maintaining the color

components:
- grid lines split input into cells
- only uniform-colour cells kept, mixed ones dropped
- kept cells form a rectangle, output is that rectangle
- one pixel per cell, the cell's colour

### 5034a0b5

final rule: each border side has a color; interior objects of that color move 1 cell towards that side; other objects stay

components:
- each border side has a colour
- interior objects of a side's colour move towards that side
- move is exactly 1 cell
- objects matching no side stay

### 522fdd07

final rule: squares lose their outer 1-cell ring; single cells become a 9x9 square centered on them; colors kept

components:
- squares lose their outer 1-cell ring
- single cells become a 9x9 square
- 9x9 centred on the single cell
- colours kept

(underdetermined in the log: 1 cell -> 9x9 as a cycle. Not a component)

### 5623160b

final rule: dark red (9) objects remain at their place; every other object slides away from it until it touches the grid edge; direction from the touching dark red (9) cell to the piece

components:
- dark red (9) objects stay in place
- every other object moves away from the 9 it touches
- direction: from the touching 9 cell to the piece
- slides until it touches the grid edge

### 5a719d11

final rule: 0 band splits grid into left/right panel pairs; object swap panels, same position, each recolored to the background of the panel it came from

components:
- 0 band splits grid into left/right panel pairs
- objects swap to the other panel of the pair
- same position in the new panel
- recoloured to the background of the panel it came from

### 68bc2e87

final rule: rectangle outline overlap; output is a 1-wide column of their colors, bottom layer first, top layer last, excluding background

components:
- shapes are overlapping rectangle outlines
- output is a 1-wide column of their colours
- order by layer: bottom layer first, top layer last
- background excluded

### 753ea09b

final rule: long lines of one color bound a path from edge to edge; fill the path with that color, other color cells inside stay

components:
- long lines of one colour bound a path
- path runs edge to edge
- path filled with the lines' colour
- other-colour cells inside the path stay

### 7d7772cc

final rule: enclosed strip is a legend; each dot on the open side compares with the legend cell in its line: if same color, it moves next to band, otherwise it moves to final edge

components:
- enclosed strip is a legend
- each dot on the open side compared with the legend cell in its line
- same colour -> moves next to the band
- different colour -> moves to the far edge

### 7ec998c9

final rule: draw path in color 1: along top edge from a corner to the dot's column, down that column, dot kept, along bottom edge to opposite corner; start top left, or top right if dot is at exact center

components:
- path in colour 1, dot kept
- along top edge from a corner to the dot's column
- down the dot's column
- along bottom edge to the opposite corner
- starts top left, top right only if the dot is at the exact centre

### 8dab14c2

final rule: each bump/notch on a shape's edge adds the opposite at the same line on the opposite edge; originals stay

components:
- bumps and notches on a shape's edge
- each adds its opposite (bump -> notch, notch -> bump)
- on the opposite edge
- same line as the original
- originals stay

### 8fff9e47

final rule: input is 2x2 blocks, read from bottom-right block leftwards, then up; each block is one ring from outside in, its 4 cells color the ring's 4 corner L's in the same positions; output side is 2 x number of blocks

components:
- input read as 2x2 blocks
- order: bottom-right block leftwards, then up
- each block is one ring, outside in
- block's 4 cells colour the ring's 4 corner L's, same positions
- output side = 2 x number of blocks

### 963c33f8

final rule: 9 block splits into columns that fall; columns ending in blue (1) stop when they find one gray (5); if no blue (1), they fall through gray (5) until bottom edge, overwriting it. UNRESOLVED: example two has some gray (5) cells that disappeared, example three has column shifted one to the right

components:
- 9 block splits into columns that fall straight down
- columns ending in blue (1) stop at the first gray (5)
- columns with no blue fall through gray to the bottom edge
- falling-through columns overwrite the gray

(noisy task: the unresolved parts aren't components. An explanation for them goes under tags, "noisy task, invented explanation")

### 9720b24f

final rule: small objects within a U-shape objects bounding box are erased; U-shape and objects outside them stay

components:
- U-shape objects
- small objects inside a U's bounding box erased
- U-shapes and objects outside stay

### 985ae207

final rule: each 3x3 ring repeats itself in steps of 3 toward the block whose color matches its center; stops with the first copy that overlaps, overwriting it

components:
- 3x3 ring targets the block matching its centre colour
- ring repeats toward it
- steps of 3
- stops at the first copy that overlaps the block
- that copy overwrites the block

### a09f6c25

final rule: shapes are recolored by symmetry axis: vertical axis turns green (3), horizontal axies turns blue (1), diagonal axis turns purple (6); single cells are erased

components:
- colour decided by the shape's symmetry axis
- vertical -> green (3)
- horizontal -> blue (1)
- diagonal -> purple (6)
- single cells erased

### a6953f00

final rule: output is 2x2 corner from the top of the input: right corner if grid size even, left if odd

components:
- output is 2x2
- taken from the top of the input
- side depends on parity of the grid size
- even -> right, odd -> left

(underdetermined in the log: rows or columns for parity, either counts)

### aaef0977

final rule: color each cell by its Manhattan distance from the dot, stepping through the cycle of colors stated at the examples (3, 4, 0, 5, 2, 8, 9, 6, 1), starting at dot's color

components:
- every cell coloured by its Manhattan distance from the dot
- colours repeat as a cycle over distance
- cycle order 3, 4, 0, 5, 2, 8, 9, 6, 1, the same in every example
- cycle starts at the dot's colour

### bd5af378

final rule: L-shape moves one inward; old L cells take the fill color; diagonal of fill color from inner corner to opposite; both L corners and rest, azure (8)

components:
- L-shape moves one cell inward
- old L cells take the fill colour
- diagonal of fill colour from the inner corner to the opposite one
- both L corners and the rest azure (8)

### d749d46f

final rule: objects from left to right are arranged twice, once at the top and once at the bottom of the grid; they have 1 column gaps in between; along the top, they ly on long side horizontally; along the bottom, they stand on long side vertically; width is the sum of long sides plus the gaps; height is 10

components:
- objects taken left to right
- placed twice, a row at the top and a row at the bottom
- 1 column gap between objects
- top: lying on the long side
- bottom: standing on the long side
- size: width = sum of long sides + gaps, height 10

### d753a70b

final rule: diamond shapes change by color, same center: 2 shrinks by one leve, 5 grows one level, others (8, 9) unchanged

components:
- diamond size change decided by colour, same centre
- red (2) shrinks one level
- gray (5) grows one level
- others (8, 9) unchanged

### db7260a4

final rule: blue (1) acts as water: falls straight down; if lands in cup with no gap, it fills the cup interior; if leaks, it keeps falling and may land in other cup, or until bottom edge where it spreads into a full horizontal line

components:
- blue (1) falls straight down
- cup with no gap: fills the cup interior
- cup with a gap: leaks, keeps falling, can land in another cup
- bottom edge: spreads into a full horizontal line

### df9fd884

final rule: two yellow (4) cups in opposite corners; the colored shape moves to the bottom edge, in the columns of the top cup's openings; shape unchanged

components:
- yellow (4) cups stay
- coloured shape moves to the bottom edge
- columns: the top cup's openings
- shape unchanged

### e729b7be

final rule: left shape is copied to the right side rotated 180º around the center point, mirroring across both axes

components:
- left shape copied to the right side, original stays
- copy rotated 180
- around the centre point

### e84fef15

final rule: grid is 5x5 copies of one block, one copy has cells erased to 8; output is the block, erased cells marked blue (1)

components:
- grid is 5x5 copies of one block
- one copy has cells erased to 8
- output is the block
- erased cells marked blue (1)

### ecb67b6d

final rule: objects of gray (5) that contain 3 cells in a diagonal line turn azure (8) whole object; others remain unchanged

components:
- only gray (5) objects change
- test: contains 3 cells in a diagonal line
- matching objects turn azure (8), whole object
- others unchanged

### fbf15a0b

final rule: two gray (5) markers: if stacked, cut grid into top/bottom halves; if side by side, cut into left/right halves; keep the half with the markers, erase markers to 8

components:
- two gray (5) markers decide the cut
- stacked -> top/bottom halves, side by side -> left/right
- keep the half with the markers
- markers erased to 8
