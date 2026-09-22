from dataclasses import dataclass
from random import Random


# Specifies orientation, possible length, attachnment...
@dataclass(frozen=True)
class StrokeSpec:
    orientation: str
    lengths: tuple[int, ...]
    attach_to: int | None = None
    attachment: str = 'independent'


# Holds the immutable structural specification
@dataclass(frozen=True)
class CharacterType:
    strokes: tuple[StrokeSpec, ...]


# Represents one concrete trajectory
@dataclass(frozen=True)
class Stroke:
    start: tuple[int, int]
    end: tuple[int, int]


# Holds the executed stroke
@dataclass(frozen=True)
class Token:
    strokes: tuple[Stroke, ...]


# Samples lengths and resolves attachments
def generate_token(character_type: CharacterType, rng: Random) -> Token:
    result = []
    for index, spec in enumerate(character_type.strokes):
        length = rng.choice(spec.lengths)
        if spec.attachment == 'independent':
            if spec.attach_to is not None:
                raise ValueError('Independent stroke cannot have a parent')
            start = (12, 5)
        elif spec.attachment == 'midpoint':
            if spec.attach_to is None or not 0 <= spec.attach_to < index:
                raise ValueError('Attachment must refer to an earlier stroke')
            parent = result[spec.attach_to]
            start = ((parent.start[0] + parent.end[0]) // 2,
                     (parent.start[1] + parent.end[1]) // 2)
        else:
            raise ValueError(f'Unknown attachment: {spec.attachment}')

        x, y = start
        if spec.orientation == 'horizontal':
            end = (x + length, y) if spec.attachment != 'independent' else (x + length // 2, y)
            if spec.attachment == 'independent':
                start = (x - length // 2, y)
        elif spec.orientation == 'vertical':
            end = (x, y + length)
        else:
            raise ValueError(f'Unknown orientation: {spec.orientation}')
        result.append(Stroke(start, end))
    return Token(tuple(result))


# Converts trajectories into a character grid
def render(token: Token, width: int = 25, height: int = 20) -> str:
    grid = [['.' for _ in range(width)] for _ in range(height)]
    for stroke in token.strokes:
        x1, y1 = stroke.start
        x2, y2 = stroke.end
        if x1 != x2 and y1 != y2:
            raise ValueError('Only axis-aligned strokes are supported')
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if not (0 <= x < width and 0 <= y < height):
                    raise ValueError('Stroke outside canvas')
                grid[y][x] = '#'
    return '\n'.join(''.join(row) for row in grid)


T_TYPE = CharacterType((
    StrokeSpec('horizontal', (6, 10, 14)),
    StrokeSpec('vertical', (5, 8, 11), attach_to=0, attachment='midpoint'),
))


def test_generator() -> None:
    rng = Random(7)
    tokens = [generate_token(T_TYPE, rng) for _ in range(30)]
    assert len(set(tokens)) > 1, 'Stochastic generation should produce variation'
    for token in tokens:
        horizontal, vertical = token.strokes
        midpoint = ((horizontal.start[0] + horizontal.end[0]) // 2,
                    (horizontal.start[1] + horizontal.end[1]) // 2)
        assert vertical.start == midpoint, 'Attachment relation must be preserved'
        assert horizontal.start[1] == horizontal.end[1]
        assert vertical.start[0] == vertical.end[0]
        assert len(render(token).splitlines()) == 20
    assert T_TYPE.strokes[1].attachment == 'midpoint'
    print('PASS: 30 valid tokens; varied geometry; midpoint relation preserved; rendering valid; type unchanged.')
    print('Distinct tokens:', len(set(tokens)))
    for number, token in enumerate(tokens[:2], 1):
        print(f'\nToken {number}: {token.strokes}')
        print(render(token))


# RESULTS:
# 30 tokens generated and validated.
# 9 distinct token geometries observed.
# Every vertical stroke started at the horizontal stroke's midpoint.
# Every token rendered inside the canvas.
# The character type remained unchanged.


if __name__ == '__main__':
    test_generator()
