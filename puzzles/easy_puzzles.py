"""
Easy Puzzles — Keya's 3 puzzles adapted for Pygame UI.

Original logic from nowayouttt.py is preserved. Each puzzle is now a class
with description text and an answer-checking method, so PuzzleState can
render them as a graphical overlay instead of using console input().
"""

import random


class CaesarCipherPuzzle:
    """Puzzle 1 — decrypt a Caesar cipher word."""

    PUZZLE_ID = "caesar_cipher"
    TITLE = "THE DUSTY NOTE"

    def __init__(self):
        self.secret = "KHOOR"
        self.shift = 3
        self.solution = "".join([chr(ord(c) - self.shift) for c in self.secret])
        # solution == "HELLO"

        self.description = [
            "You find a crumpled note on the desk.",
            f'The note reads: "{self.secret}"',
            f"A small dial nearby is set to {self.shift}.",
            "",
            "Decrypt the word to open the drawer.",
        ]

    def check_answer(self, answer):
        return answer.strip().upper() == self.solution


class BinaryLockPuzzle:
    """Puzzle 2 — convert a binary sequence to decimal."""

    PUZZLE_ID = "binary_lock"
    TITLE = "THE FLICKERING PANEL"

    def __init__(self):
        self.bits = [random.randint(0, 1) for _ in range(4)]
        self.solution = sum(bit * (2 ** i)
                           for i, bit in enumerate(reversed(self.bits)))

        self.description = [
            "Four lights flash in sequence on a metal panel.",
            f"Pattern: {self.bits}",
            "A keypad awaits a decimal code.",
            "",
            "Enter the decimal value of the binary pattern.",
        ]

    def check_answer(self, answer):
        try:
            return int(answer.strip()) == self.solution
        except ValueError:
            return False


class CouchSlicingPuzzle:
    """Puzzle 3 — extract a substring from a coded string."""

    PUZZLE_ID = "couch_slicing"
    TITLE = "THE OLD COUCH"

    def __init__(self):
        self.clue = "ZZZGOLDZZZ"
        self.solution = self.clue[3:7]   # "GOLD"

        self.description = [
            "Tucked between the couch cushions, you find a coded card:",
            f'  [{self.clue}]',
            "",
            "A scrap of paper wedged in the armrest says:",
            "'Discard the 3 sleepers at the start,",
            " and the 3 sleepers at the end.'",
            "",
            "What is the secret word?",
        ]

    def check_answer(self, answer):
        return answer.strip().upper() == self.solution


# Registry — maps puzzle_id to its class
from puzzles.level2_puzzles import BlinkingLightsPuzzle, MisplacedTilePuzzle, PaintingPuzzle
from puzzles.level3_puzzles import LEVEL3_PUZZLES

PUZZLE_REGISTRY = {
    "caesar_cipher": CaesarCipherPuzzle,
    "binary_lock": BinaryLockPuzzle,
    "couch_slicing": CouchSlicingPuzzle,
    # Keep backward compatibility with old save files
    "bed_slicing": CouchSlicingPuzzle,
    # Level 2 Puzzles
    "blinking_lights": BlinkingLightsPuzzle,
    "misplaced_tile": MisplacedTilePuzzle,
    "painting_code": PaintingPuzzle,
}
PUZZLE_REGISTRY.update(LEVEL3_PUZZLES)

"""
Medium Puzzles:
1.Player has to guess the last number in the given fibonacci series
def puzzle_fibonacci_safe():
    # Sequence: 1(1), 1(2), 2(3), 3(4), 5(5), 8(6), 13(7), 21(8), 34(9), 55(10)
    sequence = [1, 1]
    for i in range(8):
        sequence.append(sequence[-1] + sequence[-2])
    solution = sequence[9]
    
    print("--- THE BRASS SAFE ---")
    print("The numbers 1, 1, 2, 3, 5, 8 are etched into the dial.")
    print("Clue: 'The tenth step completes the circle.'")
    
    guess = input("Enter the 10th number: ")
    if guess == str(solution):
        print("Click! The safe door swings open.")
        return True
    return False

2.On the coffee table there are 4 objects: open book, plant, pen, and stone.
A shadow chart in the open book shows the correct positions (not just order).
Player must arrange the 4 items in the exact positions shown in the shadow diagram.
Animation: When correct, a soft light shines from the lamp onto the table + a compartment opens.
Python Logic:
Pythoncorrect_positions = {
    "book": (1, 2),
    "plant": (3, 1),
    "pen": (2, 3),
    "stone": (4, 2)
}

if table_objects == correct_positions:
    show_message("The shadows match perfectly!")
    coffee_table_compartment_open = True
    add_item("cipher_note")

3.Three coins (small, medium, large) are scattered. A wooden box on the coffee table has three slots.
Note says: “Smallest to largest.”
Tiled Setup Tips

Coffee table object named coin_box
Add property required_order = "small,medium,large"

Python Logic
Pythoncorrect_order = ["small", "medium", "large"]

if coins_in_box == correct_order:
    coin_box_sprite.set_frame(1)           # open frame
    show_message("The box clicks open!")
    add_item("silver_key")

4.

"""
