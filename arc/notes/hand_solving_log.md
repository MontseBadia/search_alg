## Hand-solving log

~30 tasks, before any code. Viewer: arc/data_agi1/apps/testing_interface.html, load from arc/data/data/training/.
Write the first-noticed line before solving, not reconstructed after.

Also keep a running list of ops I needed, for the Week 5 DSL.

### Ops I used

- find_objects
- filter_by_color
- match_by_shapes
- translate
- split_grid
- stack_object
- crop
- group_by_color
- read_legend
- bounding_box
- fill
- paint_order
- erase
- has_open_hole
- move_to_edge
- recolor
- is_uniform
- downscale
- size
- shrink_from_center
- expand_from_center
- adjacent_side
- detect_background_color
- swap_objects
- layer_order
- to_column
- find_path
- fill_path
- locate_corners
- draw_line
- find_edge_bumps
- find_edge_notches
- mirror_edge_feature
- split_blocks
- draw_frame
- find_object_edge
- drop_through
- replicate_toward
- match_by_color
- symmetry_axis
- parity_check
- manhattan_distance
- color_cycle
- orient_by_long_side
- concat_with_gap
- output_size
- rotate_180
- majority_block
- different_cells
- diagonal_run

---

### Task id: 18447a8d

- time: 2 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: right shapes have color, those move; left shapes remain
- first hypothesis: right hand shapes are fit together with left hand shapes so they form a rectangle
- revised when / why: no
- final rule (one line): each coloured block moves left, to the level in which the shape gap fits exactly completing a rectangle, the piece keeps its color
- ops: find_objects, filter_by_color, match_by_shapes, translate
- difficulty 1-5: 1
- guess: will the model get it? yes, small grids, few objects

### Task id: 25c199f5

- time: 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: examples seems split onto three screens with an object each, then the results seems to combine those objects one on top of the other
- first hypothesis: give input grid is split into three grids, each containing one object, output grid puts object left at the bottom, keeping same center position, then middle grid object is added to top, then right object is added to top
- revised when / why: no
- final rule (one line): split input into 3 panels; stack the objects in each panel bottom-up (left, middle, right) each keeping its column, touching
- ops: split_grid, find_objects, stack_object, crop
- difficulty 1-5: 2
- guess: will the model get it? yes, few objects

### Task id: 305b1341

- time: 2 min
- solved? (attempts): yes, 2 attempts because i forgot to delete the color guidance at the top left
- noticed first: it seems as if the surrounding cells of the same-coloured dots are filled with a certain colour, defined by the top left guidance
- first hypothesis: same-coloured dots are surrounded by color defined on the top left, forming a rectangle, shapes overlap so the order is defined in the legend
- revised when / why: no
- final rule (one line): legend top-left maps dot color to frame color; around each same color dot group draw its bounding box + 1 in the frame color, dots kept; overlaps: higher legend row on top; erase legend
- ops: group_by_color, read_legend, bounding_box, fill, paint_order, erase
- difficulty 1-5: 3
- guess: will the model get it? no, shapes almost overlap, it's difficult

### Task id: 320afe60

- time: 2 min
- solved? (attempts): yes, 1 attempt
- noticed first: blue shapes get split into two, ones go to right and ones go to left
- first hypothesis: blue shapes get moved horizontally, if the blue bouding box is closed and it's all blue, they get moved to the left and turn red; if the boundaries contains yellow, they turn green and get moved to the right
- revised when / why: no
- final rule (one line): blue (1) shapes with all holes sealed turn red (2) and slide to left edge; shapes with a hole open to the outside turn green (3) and slide to right edge; same rows, same shape
- ops: find_objects, has_open_hole, move_to_edge, recolor
- difficulty 1-5: 3
- guess: will the model get it? no, guessing the rule to move to right or left is difficult

### Task id: 458e3a53

- time: < 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: the grid contains grid pattern inside, some cells are multi color but some are color consistent - those are extracted to a new output grid
- first hypothesis: the small grids inside that are color consistent are extracted into an output grid
- revised when / why: no
- final rule (one line): grid lines split input into cells; the uniform-color cells form a rectangle; output is that rectangle, one pixel per cell, maintaining the color
- ops: split_grid, is_uniform, crop, downscale
- difficulty 1-5: 2
- guess: will the model get it? yes, finding grid pattern is easy

### Task id: 5034a0b5

- time: 3 minutes
- solved? (attempts): yes, 2 attempts because i had to change the rule
- noticed first: there are some colors in the frame sides, those stay the same, objects in the middle move
- first hypothesis: if objects in the middle have the same color of the colors on the top/bottom line frames, those objects move one cell upwards; if objects have the same color of the right/left line frames, they move one cell to the right; other objects remain
- revised when / why: yes, when submitted answer failed. why: because initial answer moved bottom-color objects once cell up, output showed each side pulls towards itself
- final rule (one line): each border side has a color; interior objects of that color move 1 cell towards that side; other objects stay
- ops: read_legend, find_objects, translate
- difficulty 1-5: 4
- guess: will the model get it? yes, it's easier for model to catch pattern, it's confusing for humans because of lots of objects/colors

### Task id: 522fdd07

- time: 2 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: it seems objects in output keep the same shape but are downscaled by one level, so they lose the outter border
- first hypothesis: objects keep the same color and shape, if they are bigger than just one cell, they downscale by losing the most outter 1-cell border on all sides; if they are just one cell, they grow to a rectangle 9x9 maintaining the centre 
- revised when / why: no
- final rule (one line): squares lose their outer 1-cell ring; single cells become a 9x9 square centered on them; colors kept
- underdetermined rule: when object becames smallest size (1 cell), they are back to biggest size (9x9)
- ops: find_objects, size, shrink_from_center, expand_from_center
- difficulty 1-5: 3
- guess: will the model get it? yes, clear size change

### Task id: 5623160b

- time: 3 minutes
- solved? (attempts): yes, 2 attempts as i changed the rule
- noticed first: shapes of different colors that are next to each other, are getting far apart so colors are not touching each other
- first hypothesis: objects of different color get far apart, moved to the grid edges except for the dark red objects that remain
- revised when / why: yes, i did not define the move direction rule, i moved each piece to the nearest edge
- final rule (one line): dark red (9) objects remain at their place; every other object slides away from it until it touches the grid edge; direction from the touching dark red (9) cell to the piece
- ops: find_objects, move_to_edge, adjacent_side, filter_by_color
- difficulty 1-5: 4
- guess: will the model get it? yes, direction should not be difficult to find

### Task id: 5a719d11

- time: 6 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: background colors remain, objects shift sides right/left
- first hypothesis: objects shift sides and acquire the color of the opposite side (left/right); if two sides don't have a different color, objects disappear
- revised when / why: no
- final rule (one line): 0 band splits grid into left/right panel pairs; object swap panels, same position, each recolored to the background of the panel it came from
- ops: split_grid, detect_background_color, find_objects, swap_objects, recolor
- difficulty 1-5: 4
- guess: will the model get it? no, it is hard to find out the rule when objects disappear
- comment after review: there aren't two rules, the objects disappear because the background color of the panel it comes from has the same color as the new panel background

### Task id: 68bc2e87

- time: < 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: output is the color palette of the different shapes ordered by the ones that are not cut first
- first hypothesis: grid contains objects that overlap each other; output is a grid containing the colors that overlap, with the top color at the bottom
- revised when / why: no
- final rule (one line): rectangle outline overlap; output is a 1-wide column of their colors, bottom layer first, top layer last, excluding background
- ops: find_objects, layer_order, to_column
- difficulty 1-5: 1
- guess: will the model get it? yes, few objects and overlaps

### Task id: 753ea09b

- time: 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: it seems like a certain path gets color-filled
- first hypothesis: there is a trace of a color which is not the background color, it marks a path and it needs to be filled with the same color
- revised when / why: no
- final rule (one line): long lines of one color bound a path from edge to edge; fill the path with that color, other color cells inside stay
- ops: find_path, fill_path
- difficulty 1-5: 1
- guess: will the model get it? yes, path is easy because it is long

### Task id: 7d7772cc

- time: < 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: grid is split, dots on one side seems to move, not the other ones
- first hypothesis: grid is split, the enclosed side defines the colored cells that must get closer to the band, otherwise colored cells must shift to edge always moving perpendicular to the band
- revised when / why: no
- final rule (one line): enclosed strip is a legend; each dot on the open side compares with the legend cell in its line: if same color, it moves next to band, otherwise it moves to final edge
- ops: read_legend, find_objects, move_to_edge, stack_object
- difficulty 1-5: 1
- guess: will the model get it? yes, examples are clear

### Task id: 7ec998c9

- time: < 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: it seems i need to trace a color path from one edge to another crossing the coloured cell in the middle
- first hypothesis: if the colored cell is in the centre, draw a path from bottom left to top right; otherwise draw path from top left to bottom right
- revised when / why: no
- final rule (one line): draw path in color 1: along top edge from a corner to the dot's column, down that column, dot kept, along bottom edge to opposite corner; start top left, or top right if dot is at exact center
- ops: find_objects, locate_corners, draw_line
- difficulty 1-5: 2
- guess: will the model get it? yes, simple rule

### Task id: 8dab14c2

- time: < 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: it seems shapes with cells that stand out or make a whole create the opposite effect on the other side
- first hypothesis: shape can have holes or standing out cells; if hole, it should create a stand out cell on the opposite side; and the same for stand out cells
- revised when / why: no
- final rule (one line): each bump/notch on a shape's edge adds the opposite at the same line on the opposite edge; originals stay
- ops: find_objects, find_edge_bumps, find_edge_notches, mirror_edge_feature
- difficulty 1-5: 2
- guess: will the model get it? yes, shapes are simple

### Task id: 8fff9e47

- time: 5 minutes
- solved? (attempts): yes, 1 attempt but took long because I miscalculated grid size
- noticed first: we start with a legend and then draw rectangles inside rectangles following legend colors
- first hypothesis: input is legend, it starts reading from bottom right to bottom left, then each row up. first color defines half bottom right edge stripe, second half bottom left edge stripe, third half bottom right but second row, etc. Each row up indicates whether to start from top or bottom, alternatively
- revised when / why: no
- final rule (one line): input is 2x2 blocks, read from bottom-right block leftwards, then up; each block is one ring from outside in, its 4 cells color the ring's 4 corner L's in the same positions; output side is 2 x number of blocks
- ops: read_legend, split_blocks, draw_frame
- difficulty 1-5: 4
- guess: will the model get it? no, legend is hard to read

### Task id: 963c33f8

- time: 10 minutes
- solved? (attempts): yes, 2 attemps, failed first one because I slided object vertically and horizontally, then only vertically
- noticed first: there is a dark red shape that gets split, rest of shapes remain
- first hypothesis: dark red object on top slides down each column; if it has blue ending, it stops whenever it touches gray object, otherwise it slides until bottom edge
- revised when / why: yes, because on second example, it slides until edge but then some gray cells disappear, and on third example it slides and shifts right - i still haven't figured out why
- final rule (one line): 9 block splits into columns that fall; columns ending in blue (1) stop when they find one gray (5); if no blue (1), they fall through gray (5) until bottom edge, overwriting it. UNRESOLVED: example two has some gray (5) cells that disappeared, example three has column shifted one to the right
- ops: find_objects, find_object_edge, stack_object, drop_through
- difficulty 1-5: 5
- guess: will the model get it? no, rule is hard, still not clear to me
- NOISY TASK: I solved it without finding the exact rule, or it could be that example two and three have some errors in it

### Task id: 9720b24f

- time: < 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: some objects have other smaller objects inside, it seems they disappear in the output
- first hypothesis: objects have U shape: if they have smaller objects inside, they get deleted; rest remain
- revised when / why: no
- final rule (one line): small objects within a U-shape objects bounding box are erased; U-shape and objects outside them stay
- ops: bounding_box, erase
- difficulty 1-5: 1
- guess: will the model get it? yes, U shape is easy to find

### Task id: 985ae207

- time: 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: it seems square shape copies itself towards the colored object that matches the color they have inside
- first hypothesis: square object with color inside copies itself towards the colored object that matches the inside, until it touches it
- revised when / why: no
- final rule (one line): each 3x3 ring repeats itself in steps of 3 toward the block whose color matches its center; stops with the first copy that overlaps, overwriting it
- ops: find_objects, replicate_toward, match_by_color
- difficulty 1-5: 2
- guess: will the model get it? yes, shapes are easy

### Task id: a09f6c25

- time: 2 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: it seems objects change color but remain at place
- first hypothesis: objects that are horizontally aligned, turn blue; vertically-aligned turn green; diagonally aligned turn purple
- revised when / why: no
- final rule (one line): shapes are recolored by symmetry axis: vertical axis turns green (3), horizontal axies turns blue (1), diagonal axis turns purple (6); single cells are erased
- ops: find_objects, symmetry_axis, recolor, erase
- difficulty 1-5: 2
- guess: will the model get it? no, some objects can get confusing

### Task id: a6953f00

- time: 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: it seems that grid colors get compacted into a smaller grid
- first hypothesis: output is always 2x2; generated by always choosing 2x2 from top right or left of input, depending on number of input rows: right if even, left if odd
- revised when / why: no
- final rule (one line): output is 2x2 corner from the top of the input: right corner if grid size even, left if odd
- ops: parity_check, crop
- difficulty 1-5: 3
- guess: will the model get it? no, rule can be difficult to find
- underdetermined rule: not sure whether rows or columns define parity check

### Task id: aaef0977

- time: 2 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: starts with grid and one cell color, then there is a pattern created centered at the colored cell
- first hypothesis: starting out at colored cell, a mosaic pattern is created around the center, following colors from example
- revised when / why: no
- final rule (one line): color each cell by its Manhattan distance from the dot, stepping through the cycle of colors stated at the examples (3, 4, 0, 5, 2, 8, 9, 6, 1), starting at dot's color
- ops: find_objects, manhattan_distance, color_cycle
- difficulty 1-5: 2
- guess: will the model get it? yes, patterns are easy to catch

### Task id: bd5af378

- time: 2 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: from two initial colors, a pattern is created and the orientation and colors depend on input
- first hypothesis: starting with two colors, the L-shape shifts position but keeps almost same shape, the containing color forms pattern, rest is background; orientation is defined by vertex of L-shape
- revised when / why: no
- final rule (one line): L-shape moves one inward; old L cells take the fill color; diagonal of fill color from inner corner to opposite; both L corners and rest, azure (8)
- ops: find_objects, translate, recolor, draw_line, fill
- difficulty 1-5: 2
- guess: will the model get it? yes, it's about copying pattern with proper colors

### Task id: d749d46f

- time: 4 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: it seems like shapes are copied against their symmetries, or similar
- first hypothesis: objects at top are shifted horizontally against top edge, then those same objects are shifted vertically and positioned in the same order at the bottom edge, output has height 10 always
- revised when / why: no
- final rule (one line): objects from left to right are arranged twice, once at the top and once at the bottom of the grid; they have 1 column gaps in between; along the top, they ly on long side horizontally; along the bottom, they stand on long side vertically; width is the sum of long sides plus the gaps; height is 10
- ops: find_objects, orient_by_long_side, concat_with_gap, move_to_edge, output_size
- difficulty 1-5: 4
- guess: will the model get it? no, rule is difficult to extract

### Task id: d753a70b

- time: 2 minutes
- solved? (attempts): yes, 2 attempts because i had to review the rule
- noticed first: diamond shapes shrink by one level, one cell shape grows to diamon by one level
- first hypothesis: diamond shapes shrink by one level, one cell grows by one level
- revised when / why: yes, because at first i thought all shapes shrink, but that is not true, some of them grow, some of them remain, depending on color
- final rule (one line): diamond shapes change by color, same center: 2 shrinks by one leve, 5 grows one level, others (8, 9) unchanged
- ops: find_objects, filter_by_color, shrink_from_center, expand_from_center
- difficulty 1-5: 3
- guess: will the model get it? yes, few shapes

### Task id: db7260a4

- time: < 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: seems like blue cell slides down: if reaches the bottom, it spreads into blue line, if stuck inside the shape, it fills the shape
- first hypothesis: blue cell slides down: if it gets stuck inside U-shape, it fills cells inside shape, otherwise it reaches the bottom edge and spreads into a horizontal line
- revised when / why: no
- final rule (one line): blue (1) acts as water: falls straight down; if lands in cup with no gap, it fills the cup interior; if leaks, it keeps falling and may land in other cup, or until bottom edge where it spreads into a full horizontal line
- ops: find_objects, has_open_hole, fill, move_to_edge, draw_line
- difficulty 1-5: 1
- guess: will the model get it? yes, three options: fills shape, leaks or converts to line

### Task id: df9fd884

- time: 1 minute
- solved? (attempts): yes, 1 attempt
- noticed first: yellow shapes remain, colored shapes move to bottom right side of the grid
- first hypothesis: the grid is split vertically by two; on one side there is always a yellow shape with a colored shape (it can be on the edge or close to yellow shape), then output must move the colored shape to the other side of the grid and opposite side: if shape was touching edge, it should be close to yellow object this time, or other way around
- revised when / why: no
- final rule (one line): two yellow (4) cups in opposite corners; the colored shape moves to the bottom edge, in the columns of the top cup's openings; shape unchanged
- ops: find_objects, find_edge_notches, filter_by_color, translate, move_to_edge
- difficulty 1-5: 3
- guess: will the model get it? yes, few shapes

### Task id: e729b7be

- time: 3 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: grid is split into two, shape on the left, it seems output produces a symmetry of the shape on the right side, but somehow distortioned
- first hypothesis: grid is split into two, left side shape is projected symmetrically along the vertical axis, then horizontal axis
- revised when / why: no
- final rule (one line): left shape is copied to the right side rotated 180º around the center point, mirroring across both axes
- ops: find_objects, split_grid, rotate_180
- difficulty 1-5: 3
- guess: will the model get it? yes, symmetry is easy once found

### Task id: e84fef15

- time: 15 minutes
- solved? (attempts): yes, 3 attemps because it took me quite some time to get the rule
- noticed first: grid is fully packed with smaller grids and patterns, it seems output is some kind of color pattern extracted from those
- first hypothesis: smaller grids inside grid contain same info, black pieces remain black, if they touch other cells, those turn blue, pieces in the same row as black turn blue but only the one that is closest, pieces in the same column remain as they are unless they touch the black
- revised when / why: yes because my rule did not work out, i tried modifying when and where the black defined the pattern but in my second guess it did not work for all three examples either, until I realised I can't get a rule that way so I must look at the smaller grids, then I found there is one smaller grid which is different and it defines which cells remain in color, and missing cells turn blue
- final rule (one line): grid is 5x5 copies of one block, one copy has cells erased to 8; output is the block, erased cells marked blue (1)
- ops: split_grid, majority_block, different_cells, recolor
- difficulty 1-5: 5
- guess: will the model get it? yes, rule is difficult to find visually but not hard to infer
- comment: FAILED by ARC rules, only 2 attempts allowed

### Task id: ecb67b6d

- time: 2 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: seems like output is copied and only some shapes change color
- first hypothesis: shapes that change color to azure (8) are those that contain three contiguous diagonal cells, no matter the direction
- revised when / why: no
- final rule (one line): objects of gray (5) that contain 3 cells in a diagonal line turn azure (8) whole object; others remain unchanged
- ops: find_objects, diagonal_run, recolor
- difficulty 1-5: 4
- guess: will the model get it? no, too many confusing shapes

### Task id: fbf15a0b

- time: 2 minutes
- solved? (attempts): yes, 1 attempt
- noticed first: it looks like the grid gets cut using some rule, it somehow shrinks
- first hypothesis: gray legend marks direction in which the grid needs to be split onto half, then output draws only the split that the legend is on
- revised when / why: no
- final rule (one line): two gray (5) markers: if stacked, cut grid into top/bottom halves; if side by side, cut into left/right halves; keep the half with the markers, erase markers to 8
- ops: read_legend, split_grid, crop, erase
- difficulty 1-5: 2
- guess: will the model get it? no, legend is not intuitive
