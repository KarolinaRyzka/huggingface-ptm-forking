def formatCard(card):

    #empty dict
    sections = {}
    #split model card based on sections with the delimeter "##""
    subsection = card.split("## ")

    #traverse each subsection, return sections of each card in dict
    for section in subsection:
        section = sections[section.split("\n")[0]]
    return sections