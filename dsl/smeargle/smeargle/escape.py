from __future__ import annotations


class Escape:
    @staticmethod
    def string(text: str) -> str:
        """Escape other sensitive characters that are not Typst control characters."""
        return text.replace("\\", "\\\\").replace('"', '\\"')
