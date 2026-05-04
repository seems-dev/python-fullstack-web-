"""
Component decorator system for Xania.

Provides a proper component model with:
- Type-safe props
- Composition support
- Consistent rendering
- Metadata and introspection

Example:
    @component(props={"name": str, "count": int})
    def Card(ctx):
        return Div(
            H1(f"Hello {ctx.props['name']}"),
            P(f"Count: {ctx.props['count']}"),
            class_name="p-4 border rounded"
        )
    
    # Usage:
    card = Card(name="Alice", count=42)
    print(card.render())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, TypeVar, Generic
from xania.renderer.elements import Element
from xania.engine.serializer import serialize

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class ComponentContext:
    """Context passed to a component render function."""
    
    props: dict[str, Any]
    children: list[Any] = field(default_factory=list)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a prop with optional default."""
        return self.props.get(key, default)


@dataclass
class ComponentMetadata:
    """Metadata about a component."""
    
    name: str
    props_schema: dict[str, type] = field(default_factory=dict)
    """Mapping of prop name to expected type."""
    
    doc: Optional[str] = None
    is_builtin: bool = False


class ComponentInstance:
    """
    An instance of a component with props and children.
    """
    
    def __init__(
        self,
        render_fn: Callable[[ComponentContext], Element | str],
        metadata: ComponentMetadata,
        props: dict[str, Any],
        children: list[Any],
    ):
        self._render_fn = render_fn
        self._metadata = metadata
        self._props = props
        self._children = children
    
    @property
    def metadata(self) -> ComponentMetadata:
        return self._metadata
    
    def render(self) -> Element | str:
        """Render the component to an Element or HTML string."""
        ctx = ComponentContext(props=self._props, children=self._children)
        return self._render_fn(ctx)
    
    def to_html(self) -> str:
        """Render to HTML string."""
        result = self.render()
        return serialize(result)


def component(
    *,
    props: Optional[dict[str, type]] = None,
    name: Optional[str] = None,
) -> Callable[[F], Callable[..., ComponentInstance]]:
    """
    Decorator to create a typed, composable component.
    
    Args:
        props: Schema mapping prop names to types (for validation/docs)
        name: Optional component name (defaults to function name)
    
    Example:
        @component(props={"title": str, "count": int})
        def Counter(ctx):
            return Div(
                H1(ctx.props['title']),
                P(f"Count: {ctx.props['count']}")
            )
        
        counter = Counter(title="My Counter", count=5)
        print(counter.to_html())
    """
    
    props_schema = props or {}
    
    def decorator(fn: F) -> Callable[..., ComponentInstance]:
        component_name = name or fn.__name__
        metadata = ComponentMetadata(
            name=component_name,
            props_schema=props_schema,
            doc=fn.__doc__,
            is_builtin=False,
        )
        
        def wrapper(*children: Any, **props_dict: Any) -> ComponentInstance:
            # Validate props against schema
            for prop_name, prop_type in props_schema.items():
                if prop_name in props_dict:
                    value = props_dict[prop_name]
                    if not isinstance(value, prop_type):
                        raise TypeError(
                            f"{component_name}: prop '{prop_name}' "
                            f"expected {prop_type.__name__}, got {type(value).__name__}"
                        )
            
            return ComponentInstance(
                render_fn=fn,
                metadata=metadata,
                props=props_dict,
                children=list(children),
            )
        
        # Preserve metadata on wrapper
        wrapper.__name__ = component_name
        wrapper.__doc__ = fn.__doc__
        wrapper._component_metadata = metadata  # type: ignore
        
        return wrapper
    
    return decorator


def builtin_component(
    name: str,
    props_schema: Optional[dict[str, type]] = None,
) -> Callable[[F], Callable[..., ComponentInstance]]:
    """
    Mark a component as builtin (part of the framework).
    Used for internal components that don't need full validation.
    """
    return component(name=name, props=props_schema)


__all__ = [
    "component",
    "builtin_component",
    "ComponentContext",
    "ComponentInstance",
    "ComponentMetadata",
]
