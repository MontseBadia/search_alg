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
- final rule (one line): blue shapes with all holes sealed turn red and slide to left edge; shapes with a hole open to the outside turn green and slide to right edge; same rows, same shape
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
- final rule (one line): dark red objects remain at their place; every other object slides away from it until it touches the grid edge; direction from the touching dark red cell to the piece
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

### Task id:

- time:
- solved? (attempts):
- noticed first:
- first hypothesis:
- revised when / why:
- final rule (one line):
- ops:
- difficulty 1-5:
- guess: will the model get it?

### Task id:

- time:
- solved? (attempts):
- noticed first:
- first hypothesis:
- revised when / why:
- final rule (one line):
- ops:
- difficulty 1-5:
- guess: will the model get it?
