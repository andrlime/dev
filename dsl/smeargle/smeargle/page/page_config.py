from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter
from .margin import Margin
from .profile import Profile


@dataclass
class PageConfig:
    profile: Profile
    margin: Margin
    justify: bool
    pagesize: str
    font: str
    template: str = "./src/template-us-letter.typ"

    def to_typst(self) -> str:
        return "\n".join(
            [
                f'#import "{self.template}": *',
                f"#set page(paper: {Formatter.to_typst(self.pagesize)}, margin: {self.margin.to_typst()})",
                f"#set text(font: {Formatter.to_typst(self.font)})",
                f"#set par(justify: {'true' if self.justify else 'false'})",
                "#set block(above: 0.1em, below: 0.75em)",
                self.profile.to_typst(),
            ]
        )
