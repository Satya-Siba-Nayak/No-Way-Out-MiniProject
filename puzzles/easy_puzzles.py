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
PUZZLE_REGISTRY = {
    "caesar_cipher": CaesarCipherPuzzle,
    "binary_lock": BinaryLockPuzzle,
    "couch_slicing": CouchSlicingPuzzle,
    # Keep backward compatibility with old save files
    "bed_slicing": CouchSlicingPuzzle,
}
