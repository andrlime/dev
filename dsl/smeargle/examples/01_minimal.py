from smeargle import *

profile = Profile(
    name="Jane Doe",
    website="www.janedoe.dev",
    github="janedoe",
    phone="+1 (555) 123-4567",
    email="jane*@*example.com",
)

page = PageConfig(
    profile=profile,
    margin=Margin(left=30, right=30, top=10, bottom=10),
    justify=True,
    pagesize="us-letter",
    font="DINOT",
)

SectionHeader("Industry Experience")

Job(
    company="Acme Corp",
    title="Software Engineer",
    start="June 2023",
    until="Present",
    where="Remote",
    bullets=[
        "Built internal tooling in Python and Rust to speed up the release pipeline.",
        "Mentored two new hires during their first quarter.",
    ],
)
