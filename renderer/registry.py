from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from renderer.component import Component


class ComponentRegistry:
    """
    Central registry for component instances.

    This is intentionally small: swapping the storage layer later (per-session,
    per-tenant, DB-backed, etc.) should be easy.
    """

    _components: Dict[str, Component] = {}

    @classmethod
    def register(cls, name: str, component: Component) -> None:
        cls._components[name] = component

    @classmethod
    def get(cls, name: str) -> Component:
        try:
            return cls._components[name]
        except KeyError as e:
            raise KeyError(f"Component not registered: {name}") from e

    @classmethod
    def all(cls) -> dict[str, Component]:
        return dict(cls._components)


__all__ = ["ComponentRegistry"]

