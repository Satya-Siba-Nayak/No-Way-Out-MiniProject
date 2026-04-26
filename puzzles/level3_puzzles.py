class FurnacePuzzle:
    TITLE = "The Furnace"
    description = [
        "You see a blazing furnace with three slots for ore.",
        "You have Red, White, and Black ores.",
        "Insert three ores in the correct order.",
        "Type the three colors separated by spaces (e.g., 'Red White Black')."
    ]

    def __init__(self):
        self.sequence = []
        self.solved = False

    def check_answer(self, player_input):
        cleaned = [s.strip().lower() for s in player_input.split()]
        if len(cleaned) == 3 and cleaned == ["red", "white", "black"]:
            self.solved = True
            return True
        return False

class BoxPuzzle:
    TITLE = "Wooden Boxes"
    description = [
        "A stack of crates is sealed tight.",
        "A label says: 'To find the key, multiply the number",
        "of crates by the number of their faces.'",
        "There are 5 crates stacked here."
    ]

    def __init__(self):
        self.solved = False
        self.num_crates = 5
        self.faces_per_crate = 6

    def check_answer(self, player_input):
        correct_answer = str(self.num_crates * self.faces_per_crate)
        if player_input.strip() == correct_answer:
            self.solved = True
            return True
        return False

class ChemistryTable:
    TITLE = "Chemistry Table"
    description = [
        "The table has an empty flask and several vials:",
        "Vial A: 2 drops",
        "Vial B: 1 drop",
        "Vial C: 5 drops",
        "Mix the vials to reach exactly 4 drops.",
        "Type the vials you want to add, separated by spaces (e.g., 'A A' or 'A B B')."
    ]

    def __init__(self):
        self.flask_amount = 0
        self.solved = False
        self.vials = {'a': 2, 'b': 1, 'c': 5}

    def check_answer(self, player_input):
        cleaned = player_input.lower().replace(" ", "")
        
        # Shortcut: if they just type '4'
        if cleaned == "4":
            self.solved = True
            return True
            
        drops = 0
        for char in cleaned:
            if char in self.vials:
                drops += self.vials[char]
        
        if drops == 4:
            self.solved = True
            return True
        return False

class MirrorPuzzle:
    TITLE = "The Mirror"
    description = [
        "You look at the mirror and see a hidden bloody handprint",
        "reflecting a specific tile grid on the floor.",
        "Type the X,Y coordinates of that tile (e.g., '7,3')."
    ]

    def __init__(self):
        self.solved = False
        self.target_x = "7" 
        self.target_y = "3"

    def check_answer(self, player_input):
        cleaned = player_input.replace(" ", "")
        if cleaned == f"{self.target_x},{self.target_y}":
            self.solved = True
            return True
        return False

class StatueRiddlePuzzle:
    TITLE = "The Mage Statue"
    description = [
        "The Mage Statue's eyes glow as it speaks:",
        "'I have keys but open no doors.",
        " I have space but no room.",
        " You can enter, but you can never go outside.",
        " What am I?'"
    ]

    def __init__(self):
        self.solved = False
        self.tries_left = 3
        self.correct_answer = "keyboard"

    def check_answer(self, player_input):
        if self.tries_left <= 0:
            return False
            
        cleaned_input = player_input.lower().strip()
        
        if cleaned_input == self.correct_answer:
            self.solved = True
            return True
        else:
            self.tries_left -= 1
            if self.tries_left > 0:
                self.description.append(f"False. You have {self.tries_left} tries left.")
            else:
                self.description.append("You are unworthy. The puzzle is locked!")
            return False

LEVEL3_PUZZLES = {
    "furnace_sequence": FurnacePuzzle,
    "box_math": BoxPuzzle,
    "chemistry_drops": ChemistryTable,
    "mirror_coords": MirrorPuzzle,
    "statue_riddle": StatueRiddlePuzzle
}
