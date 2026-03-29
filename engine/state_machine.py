"""
State Machine — manages game state transitions.
States are pushed/popped on a stack so overlays (like puzzles) work naturally.
"""


class StateMachine:
    """Manages a stack of game states. The top state receives all updates."""

    def __init__(self):
        self._states = []

    @property
    def current(self):
        """Return the state on top of the stack, or None."""
        return self._states[-1] if self._states else None

    # --- Stack operations ---------------------------------------------------

    def push(self, state):
        """Push a new state on top (e.g. open a puzzle overlay)."""
        if self.current:
            self.current.pause()
        self._states.append(state)
        state.enter()

    def pop(self):
        """Remove the top state and resume the one below."""
        if self._states:
            old = self._states.pop()
            old.exit()
        if self.current:
            self.current.resume()

    def change(self, state):
        """Replace the top state entirely (e.g. menu → room)."""
        if self._states:
            old = self._states.pop()
            old.exit()
        self._states.append(state)
        state.enter()

    # --- Delegate to the current state --------------------------------------

    def handle_events(self, events):
        if self.current:
            self.current.handle_events(events)

    def update(self, dt):
        if self.current:
            self.current.update(dt)

    def draw(self, surface):
        if self.current:
            self.current.draw(surface)
