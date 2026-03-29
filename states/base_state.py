"""
Abstract base class for all game states.
Every screen (Menu, Room, Puzzle) inherits from this.
"""

from abc import ABC, abstractmethod


class State(ABC):
    """Base class for a game state/screen."""

    def __init__(self, machine, game_context):
        """
        Args:
            machine:      The StateMachine that owns this state.
            game_context: Shared dict carrying cross-state data
                          (screen, player_name, save_data, etc.)
        """
        self.machine = machine
        self.ctx = game_context          # shared context across states

    # --- Lifecycle ----------------------------------------------------------

    def enter(self):
        """Called when this state becomes the active state."""
        pass

    def exit(self):
        """Called when this state is removed from the stack."""
        pass

    def pause(self):
        """Called when a new state is pushed on top of this one."""
        pass

    def resume(self):
        """Called when the state above is popped and this becomes active."""
        pass

    # --- Per-frame hooks (must implement) -----------------------------------

    @abstractmethod
    def handle_events(self, events):
        """Process pygame events."""
        ...

    @abstractmethod
    def update(self, dt):
        """Update logic. dt = seconds since last frame."""
        ...

    @abstractmethod
    def draw(self, surface):
        """Render to the given surface."""
        ...
