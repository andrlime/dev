#let big_header(body, primary_color) = {
    show heading.where(
        level: 1
    ): it => text(
        fill: primary_color,
        size: 20pt,
        [
            #upper({it.body})
            #v(-15pt)
        ]
    )
    heading(level: 1, body)
}

#let section_header(body, primary_color) = {
    show heading.where(
        level: 2
    ): it => text(
        fill: primary_color,
        size: 10.5pt,
        [
            #v(3pt)
            #{it.body}
            #v(-9pt)
            #line(length: 100%, stroke: 0.3pt + primary_color)
        ]
    )
    parbreak()
    block[
        #upper(strong(delta: 100, heading(level: 2, body)))
    ]
}

#let company_name(name) = {
    show heading.where(
        level: 2
    ): it => text(
        size: 10pt,
        [
            #{it.body}
            #h(0.5em)
        ]
    )
    heading(level: 2, name)
}

#let section(header) = {
    section_header(header, rgb("#009bd7"))
}

#let icon(name, label, shift: 1.5pt) = {
  /*box(
    baseline: shift,
    height: 10pt,
    image("./icons/" + name + ".svg")
  )
  h(3pt)*/
  label
}

#let tabulate(list, separator) = {
    for elem in list {
        if elem == list.last() {
            elem
        } else {
            elem + separator + " "
        }
    }
}

#let profile(
    name,
    website,
    phone,
    email,
    github,
) = {
    set align(center)
    big_header(name, rgb("#009bd7"))
    text(10pt)[
        #tabulate((
            icon("phone", phone),
            icon("email", email),
            link("https://github.com/" + github)[
                #icon("github", "www.github.com/" + github)
            ],
            link("https://" + website)[
                #icon("github", website)
            ],
        ), h(1.5em))
    ]
}

#let school(
    name,
    year,
    degree,
    location,
    gpa
) = {
    block[
        #text(10pt)[
            #company_name(name)
            #h(1fr)
            #text(year)
        ]
        #if degree != "" [
            #linebreak()
            #text(10pt)[
                #degree #h(1fr) #gpa
            ]
        ]
    ]
}

#let tags(
    label,
    list
) = {
    parbreak()
    block[
        #text(10pt, hyphenate: false)[
            #emph(label): 
            #tabulate(list, ",")
        ]
    ]
}

#let position(
    company, position, time_period, location, bullets
) = {
    block[
        #text(10pt)[
            #company_name(company)
            #emph(position)
            #h(1fr)
            #text(time_period)
        ]
        #if bullets.len() > 0 [
            #linebreak()
            #text(10pt)[
                #list(
                    tight: true,
                    indent: 0pt,
                    ..bullets
                )
            ]
        ]
    ]
}

#let futureposition(
    company, position, time_period, location
) = {
    block[
        #text(10pt)[
            #company_name(company)
            #emph(position)
            #h(1fr)
            #text(time_period)
        ]
    ]
}

#let job(
    company, positions
) = {
    for p in positions {
        position(company, p.at(0), p.at(1), p.at(2), p.at(3))
    }
}

#let futurejob(
    company, positions
) = {
    for p in positions {
        futureposition(company, p.at(0), p.at(1), p.at(2))
    }
}

#let project(
    title, client, date, bullets
) = {
    block[
        #text(10pt)[
            #company_name(title)
            #emph(client)
            #h(1fr)
            #text(date)
        ]
        #linebreak()
        #text(10pt)[
            #list(
                tight: true,
                indent: 0pt,
                ..bullets
            )
        ]
    ]
}

#let award(
    title, who
) = {
    block[
        #text(10pt)[
            #strong(title) #h(1fr) #text(who)
        ]
    ]
}

#let pub(citation) = {
    block[
        #text(10pt)[#citation]
    ]
}
