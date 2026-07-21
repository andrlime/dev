from smeargle import *

flags = Flags()

profile = Profile(
    name="Conditional Demo",
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

SectionHeader("Industry Experience")

Job(
    company="Acme Corp",
    title="Software Engineer",
    start="June 2023",
    until="Present",
    where="Remote",
    bullets=["Always shown, regardless of flags."],
)

When(
    flags.exchange,
    Job(
        company="Studying Abroad Inc.",
        title="Exchange Researcher",
        start="September 2026",
        until="February 2027",
        where="Zurich, Switzerland",
        bullets=["Only shown when EXCHANGE=true -- otherwise still registered, just suppressed."],
    ),
)

When(flags.get("show_awards", default=True), SectionHeader("Awards"))
When(
    flags.get("show_awards", default=True),
    Award(title="Employee of the Year", organisation="Acme Corp"),
)
