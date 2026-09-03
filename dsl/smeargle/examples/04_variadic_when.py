from smeargle import *

flags = Flags()

profile = Profile(
    name="Kip Sorrell",
    website="kipsorrell.dev",
    github="kipsorrell",
    phone="555-0182",
    email="kip@kipsorrell.dev",
)

page = PageConfig(
    profile=profile,
    margin=Margin(left=30, right=30, top=10, bottom=10),
    justify=True,
    pagesize="us-letter",
    font="DINOT",
    template="./src/template-us-letter.typ",
)

SectionHeader("Industry Experience")

Job(
    company="Wyrmwood Software Co.",
    title="Staff Software Engineer",
    start="March 2022",
    until="Present",
    where="Remote (technically, the wilderness)",
    bullets=[
        "Rebuilt the checkout service so it fails gracefully instead of just failing.",
        When(
            flags.get("brag_about_uptime", default=True),
            "Kept the on-call pager silent for 400 consecutive nights.",
            "The two times it did go off, the culprit was DNS. It's always DNS.",
        ),
        When(
            flags.get("mention_intern_incident", default=False),
            "Talked an intern out of deploying on a Friday at 4:59pm.",
        ),
        "Mentored three new hires without losing a single one to the snack closet.",
    ],
)

When(
    flags.get("show_previous_chapter", default=True),
    Job(
        company="Blue Hole Expeditions",
        title="Cave Diving Instructor / Touring Bassist (weekends)",
        start="May 2019",
        until="February 2022",
        where="Various sinkholes and dive bars",
        bullets=["Never lost a student. Lost one bass amp, `permanently ~``, to a storm surge."],
    ),
)

SectionHeader("Side Projects")

Project(
    title="Emberwatch",
    organisation="Open Source",
    start="2023",
    until="Present",
    bullets=[
        "A wildfire-risk dashboard that actually loads in under a second.",
        *When(
            flags.get("include_stars_flex", default=True),
            "Quietly crossed 2k GitHub stars.",
            "Fielded exactly one death-threat-adjacent issue comment about tabs vs spaces.",
        ),
    ],
)

SectionHeader("Education")

School(
    name="Blackwater Institute of Technology",
    start="August 2015",
    until="May 2019",
    where="Blackwater, VT",
    gpa="3.9 / 4.0 (the 0.1 went to a robotics club incident)",
    degrees=[
        Degree(title="B.S.", major="Computer Science"),
        When(
            flags.get("include_minors", default=True),
            Degree(title="Minor", major="Mathematics"),
            Degree(title="Minor", major="Underwater Basket Weaving", note="yes, that's real"),
        ),
    ],
)

SectionHeader("Miscellany")

ListBlock(
    label="Skills",
    items=[
        "Python",
        "Rust",
        "Debugging other people's regex",
        When(
            flags.get("show_party_tricks", default=True),
            "Solves a Rubik's cube underwater",
            "Once fixed a production outage from a ski lift",
            "Knows exactly one card trick and performs it at every opportunity",
        ),
    ],
)
