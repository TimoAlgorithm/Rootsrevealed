# Rootsrevealed
Das Coding-Projekt des Informatikkurses

Gedcom to .csv conversion: Kai

Klasse entwickeln: Birk, Martin, Justus W

Stammbaum visualisieren: Ivan, Timo, Jesper

UI Design: Justus B, Jan, Finn, Carsten

### Installation

#### MacOS

`python3 -m pip install -r requirements.txt`

#### Windows

`py -m pip install -r requirements.txt`


### Docs

[python-gedcom-2 docs](https://swanny0819.github.io/python-gedcom-2/python_gedcom_2/index.html)

[Gedcom Manual](https://gedcom.io/specifications/gedcom7-rc.pdf)

#### Unser Klassendiagramm umgesetzt

| Klassendiagramm   | python-gedcom-2                                                          |
|-------------------|--------------------------------------------------------------------------|
| Fam               | `FamilyElement`                                                          |
| Mother            | `.has_wife()`<br>`.get_wife_pointer() -> str`                            |
| Father            | `.has_husband()`<br>`.get_husband_pointer() -> str`                      |
| Children          | `.has_children()`<br>`.get_children_pointers() -> List[str]`             |
| Marriage, Divorce | `.get_events() -> List[EventDetail]`<br>`.get_child_element_by_tag(tag)` |

| Klassendiagramm | python-gedcom-2                                                                                                                                                                                                                            |
|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Indiv           | IndividualElement                                                                                                                                                                                                                          |
| Birth, Death    | `.get_events() -> List[EventDetail]`<br>`.get_child_element_by_tag(tag)`<br>`.get_death_element() -> DeathElement`                                                                                                                         |
| Name            | `.get_name() -> str`                                                                                                                                                                                                                       |
| Vorname         | `.get_name_as_tuple()[0] -> str`                                                                                                                                                                                                           |
| Nachname        | `.get_name_as_tuple()[1] -> str`                                                                                                                                                                                                           |
| Child in        | `.get_parent_family_pointer() -> str` für eine Liste an Pointern zu den Familien<br>`Parser.get_families(individual, python_gedcom_2.tags.GEDCOM_TAG_FAMILY_CHILD) -> List[FamilyElement]` für eine Liste aus tatsächlichen FamilyElements |
| Parent in       | `.get_spouse_families_pointer() -> List[str]`<br>`Parser.get_families(individual, python_gedcom_2.tags.GEDCOM_TAG_FAMILY_CHILD) -> List[FamilyElement]`                                                                                    |
| getChildren     | `Parser.get_natural_children(individual) -> List[IndividualElement]`                                                                                                                                                                       |
| getParents      | `Parser.get_parents(individual) -> (IndividualElement, IndividualElement)`                                                                                                                                                                 |

### TODO:

- [ ] move everything to src
- [ ] Parser.find_path_to_ancestor() testing maybe rewrite
- [ ] Parser.get_family_members() maybe rewrite to enum cause wtf is this
- [ ] Docs for DateElement
- [ ] Docs for Parser
- [ ] Types for Parser
