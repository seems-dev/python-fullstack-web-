from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from renderer.elements import Element
from renderer.render import render as render_html
from renderer.state import State, useRef, useState


@dataclass
class Component:
    """
    Production-oriented base component.

    - `id`: stable DOM container id (no random ids scattered)
    - `state`: persisted server-side (per component instance; can be replaced with session storage later)
    """

    id: str
    state: State = field(default_factory=State)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Component.id must be non-empty")
        # Initialize state only once.
        if not self.state._data:  # type: ignore[attr-defined]
            self.state = State(**self.initial_state())

    def initial_state(self) -> dict[str, Any]:
        return {}

    def render(self, state: State) -> Element | str:
        raise NotImplementedError

    def handle(self, action: str, payload: dict[str, Any]) -> None:
        handler = getattr(self, f"on_{action}", None)
        if handler:
            handler(self.state, payload)

    def to_html(self) -> str:
        self.state.reset_hooks()
        return render_html(self.render(self.state))


__all__ = ["Component", "useState", "useRef"]