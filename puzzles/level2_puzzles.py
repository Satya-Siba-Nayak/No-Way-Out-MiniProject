import os

class BlinkingLightsPuzzle:
    """Puzzle 1 (Level 2) — Observe the blinking lights and determine the count."""

    PUZZLE_ID = "blinking_lights"
    TITLE = "THE BLINKING LIGHTS"

    def __init__(self):
        self.solution = "324"  # For example: 3 red, 2 green, 4 blue

        self.description = [
            "A panel on the door flashes a pattern of colored lights in a loop.",
            "",
            "It flashes Red 3 times...",
            "Then Green 2 times...",
            "Then Blue 4 times...",
            "",
            "A keypad asks for a 3-digit code."
        ]

    def check_answer(self, answer):
        return answer.strip() == self.solution


class MisplacedTilePuzzle:
    """Puzzle 2 (Level 2) — A riddle found under a bumped tile."""

    PUZZLE_ID = "misplaced_tile"
    TITLE = "THE HIDDEN NOTE"

    def __init__(self):
        self.solution = "ECHO"

        self.description = [
            "After being pushed back by the strange force, you notice a loose tile.",
            "You pry it open and find a dusty note with a riddle:",
            "",
            "\"I speak without a mouth and hear without ears.",
            " I have no eyes, yet I see the world. What am I?\"",
            "",
            "Enter your answer below."
        ]

    def check_answer(self, answer):
        return answer.strip().upper() == self.solution


class PaintingPuzzle:
    """Puzzle 3 (Level 2) — Inspect the painting and extract the hidden code."""

    PUZZLE_ID = "painting_code"
    TITLE = "THE EERIE PAINTING"

    def __init__(self):
        self.solution = "1379"
        
        # We will parse this in PuzzleState to actually draw the image.
        _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.image_path = os.path.join(_BASE_DIR, "Maps", "Level 2", "Painting.png")

        self.description = [
            "You inspect the eerie painting hanging on the wall.",
            "There seems to be something hidden within the artwork...",
            "",
            "A small safe next to it requires a 4-digit code."
        ]

    def check_answer(self, answer):
        return answer.strip() == self.solution
