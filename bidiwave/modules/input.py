"""Módulo input del protocolo BiDi."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from bidiwave.protocol.constants import (
    INPUT_PERFORM_ACTIONS,
    INPUT_RELEASE_ACTIONS,
    INPUT_SET_FILES,
)
from bidiwave.protocol.results import InputSource
from bidiwave.transport.connection import Connection

if TYPE_CHECKING:
    from bidiwave.modules.browsing import BrowsingContext

PointerType = Literal["mouse", "pen", "touch"]


class InputModule:
    """Módulo para simular input del usuario (teclado, mouse, scroll).

    Comandos:
        - perform_actions — ejecuta una secuencia de acciones de input
        - release_actions — cancela todas las acciones en curso
        - set_files — selecciona archivos en un <input type="file">

    Ejemplo:
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {"type": "pointerMove", "x": 100, "y": 200},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0},
                ],
            ),
        ]
        await client.input.perform_actions(context, actions)
    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    async def perform_actions(
        self,
        context: BrowsingContext | str,
        actions: list[InputSource],
    ) -> None:
        """Ejecuta una secuencia de acciones de input en un context.

        Args:
            context: BrowsingContext o context ID donde ejecutar las acciones.
            actions: Lista de InputSource, cada una representando un
                dispositivo virtual (teclado, mouse, wheel) con sus acciones.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {
            "context": ctx_id,
            "actions": [a.model_dump(by_alias=True, exclude_none=True) for a in actions],
        }
        await self._connection.send_command(INPUT_PERFORM_ACTIONS, params)

    async def release_actions(
        self,
        context: BrowsingContext | str,
    ) -> None:
        """Cancela todas las acciones de input en curso para un context.

        Args:
            context: BrowsingContext o context ID.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        await self._connection.send_command(
            INPUT_RELEASE_ACTIONS, {"context": ctx_id}
        )

    async def set_files(
        self,
        context: BrowsingContext | str,
        element: str,
        files: list[str],
    ) -> None:
        """Selecciona archivos en un elemento <input type="file">.

        Args:
            context: BrowsingContext o context ID.
            element: Shared ID del elemento input file.
            files: Lista de rutas absolutas de archivos a seleccionar.
        """
        ctx_id = context.id if hasattr(context, "id") else context
        params: dict[str, Any] = {
            "context": ctx_id,
            "element": {"sharedId": element},
            "files": files,
        }
        await self._connection.send_command(INPUT_SET_FILES, params)

    async def click(
        self,
        context: BrowsingContext | str,
        x: int | float,
        y: int | float,
        button: int = 0,
        duration: int = 0,
    ) -> None:
        """Conveniencia: click en coordenadas (x, y).

        Args:
            context: BrowsingContext o context ID.
            x: Coordenada X relativa al viewport.
            y: Coordenada Y relativa al viewport.
            button: 0 = izquierdo, 1 = medio, 2 = derecho.
            duration: Duración del press en ms.
        """
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {
                        "type": "pointerMove",
                        "x": x,
                        "y": y,
                        "duration": duration,
                    },
                    {"type": "pointerDown", "button": button},
                    {"type": "pointerUp", "button": button},
                ],
            ),
        ]
        await self.perform_actions(context, actions)

    async def double_click(
        self,
        context: BrowsingContext | str,
        x: int | float,
        y: int | float,
    ) -> None:
        """Conveniencia: doble click en coordenadas (x, y).

        Args:
            context: BrowsingContext o context ID.
            x: Coordenada X relativa al viewport.
            y: Coordenada Y relativa al viewport.
        """
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {"type": "pointerMove", "x": x, "y": y},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0},
                    {"type": "pointerDown", "button": 0},
                    {"type": "pointerUp", "button": 0},
                ],
            ),
        ]
        await self.perform_actions(context, actions)

    async def type_text(
        self,
        context: BrowsingContext | str,
        text: str,
    ) -> None:
        """Conveniencia: escribe texto tecla por tecla.

        Args:
            context: BrowsingContext o context ID.
            text: Texto a escribir.
        """
        key_actions: list[dict[str, Any]] = []
        for char in text:
            key_actions.append({"type": "key", "value": char})
        actions = [
            InputSource(type="key", id="keyboard", actions=key_actions),
        ]
        await self.perform_actions(context, actions)

    async def press_key(
        self,
        context: BrowsingContext | str,
        key: str,
    ) -> None:
        """Conveniencia: presiona y suelta una tecla.

        Usa el formato de key del protocolo (ej: "Enter", "Tab", "Escape",
        o un caracter literal como "a").

        Args:
            context: BrowsingContext o context ID.
            key: Tecla a presionar (ej: "Enter", "a", "Escape").
        """
        actions = [
            InputSource(
                type="key",
                id="keyboard",
                actions=[
                    {"type": "key", "value": key},
                    {"type": "key", "value": key},
                ],
            ),
        ]
        await self.perform_actions(context, actions)

    async def scroll(
        self,
        context: BrowsingContext | str,
        delta_x: int = 0,
        delta_y: int = 0,
        x: int = 0,
        y: int = 0,
        duration: int | None = None,
    ) -> None:
        """Conveniencia: scroll del mouse wheel.

        Args:
            context: BrowsingContext o context ID.
            delta_x: Cantidad de scroll horizontal (positivo = derecha).
            delta_y: Cantidad de scroll vertical (positivo = abajo).
            x: Coordenada X del puntero durante el scroll.
            y: Coordenada Y del puntero durante el scroll.
            duration: Duración del scroll en ms.
        """
        wheel_action: dict[str, Any] = {
            "type": "scroll",
            "x": x,
            "y": y,
            "deltaX": delta_x,
            "deltaY": delta_y,
        }
        if duration is not None:
            wheel_action["duration"] = duration
        actions = [
            InputSource(type="wheel", id="wheel", actions=[wheel_action]),
        ]
        await self.perform_actions(context, actions)

    async def drag_and_drop(
        self,
        context: BrowsingContext | str,
        start_x: int | float,
        start_y: int | float,
        end_x: int | float,
        end_y: int | float,
        duration: int = 100,
    ) -> None:
        """Conveniencia: drag and drop desde (start_x, start_y) hasta (end_x, end_y).

        Args:
            context: BrowsingContext o context ID.
            start_x: Coordenada X inicial.
            start_y: Coordenada Y inicial.
            end_x: Coordenada X final.
            end_y: Coordenada Y final.
            duration: Duración del movimiento en ms.
        """
        actions = [
            InputSource(
                type="pointer",
                id="mouse",
                actions=[
                    {
                        "type": "pointerMove",
                        "x": start_x,
                        "y": start_y,
                        "duration": 0,
                    },
                    {"type": "pointerDown", "button": 0},
                    {
                        "type": "pointerMove",
                        "x": end_x,
                        "y": end_y,
                        "duration": duration,
                    },
                    {"type": "pointerUp", "button": 0},
                ],
            ),
        ]
        await self.perform_actions(context, actions)
