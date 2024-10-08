from typing import Any


class Reflector:
    """Mixin to add reflection methods. Designed to be used with Ports"""

    @staticmethod
    def _get_methods(obj: Any, startswith: str | None = None) -> list[str]:
        methods = []

        for func in dir(obj):
            if callable(getattr(obj, func)):
                if startswith and not func.startswith(startswith):
                    continue

                methods.append(func)

        return methods
