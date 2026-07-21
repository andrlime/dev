from __future__ import annotations

from dataclasses import dataclass


class Formatter:
    STYLE_OF_CHAR = {"*": "strong", "_": "emph", "`": "raw"}

    @dataclass
    class StyledRun:
        styles: list[str]  # outermost first
        text: str

        def to_typst(self) -> str:
            expr = f'"{Formatter.escape_string_literal(self.text)}"'
            for wrapper in reversed(self.styles):
                expr = f"{wrapper}({expr})"
            return expr

    @staticmethod
    def escape_string_literal(text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"')

    @staticmethod
    def parse(text: str) -> list[Formatter.StyledRun]:
        stack: list[str] = []
        runs: list[Formatter.StyledRun] = []
        current = ""

        def in_raw() -> bool:
            return bool(stack) and stack[-1] == "`"

        for ch in text:
            if stack and ch == stack[-1]:
                runs.append(Formatter.StyledRun([Formatter.STYLE_OF_CHAR[c] for c in stack], current))
                stack.pop()
                current = ""
            elif not in_raw() and ch in Formatter.STYLE_OF_CHAR:
                runs.append(Formatter.StyledRun([Formatter.STYLE_OF_CHAR[c] for c in stack], current))
                stack.append(ch)
                current = ""
            else:
                current += ch

        runs.append(Formatter.StyledRun([Formatter.STYLE_OF_CHAR[c] for c in stack], current))
        return runs

    @staticmethod
    def to_typst(text: str) -> str:
        runs = [run for run in Formatter.parse(text) if run.text != ""]
        if not runs:
            return '""'
        return " + ".join(run.to_typst() for run in runs)
