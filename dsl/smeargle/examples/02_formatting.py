from smeargle import *

profile = Profile(
    name="Formatting Demo",
    website="example.com",
    github="example",
    phone="000-000-0000",
    email="demo@example.com",
)

page = PageConfig(
    profile=profile,
    margin=Margin(left=30, right=30, top=10, bottom=10),
    justify=True,
    pagesize="us-letter",
    font="DINOT",
)

SectionHeader("Education")

School(
    name="Example University",
    start="September 2020",
    until="June 2024",
    where="Nowhere, NA",
    gpa="*GPA*: 4.0/4.0",
    degrees=[
        Degree(title="*B.S.*", major="Computer Science", note="_Highest Honours_"),
    ],
)

SectionHeader("Industry Experience")

Job(
    company="Acme Corp",
    title="Software Engineer",
    start="June 2023",
    until="Present",
    where="Remote",
    bullets=[
        "Rewrote the deploy pipeline in *Rust*, cutting build times by _40%_.",
        "Introduced a `pre-commit` hook that runs `ruff` and `pyrefly` on every commit.",
        "Nesting works: *_bold and italic together_*. Raw spans stay literal: `*not bold*`.",
    ],
)

SectionHeader("Awards")

Award(title="*Employee of the Year*", organisation="Acme Corp (2024)")
