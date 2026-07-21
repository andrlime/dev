from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter


@dataclass
class Profile:
    name: str
    website: str
    github: str
    phone: str
    email: str

    def to_typst(self) -> str:
        return (
            "#profile(\n"
            f"  {Formatter.to_typst(self.name)},\n"
            f"  {Formatter.to_typst(self.website)},\n"
            f"  {Formatter.to_typst(self.phone)},\n"
            f"  {Formatter.to_typst(self.email)},\n"
            f"  {Formatter.to_typst(self.github)},\n"
            ")"
        )
