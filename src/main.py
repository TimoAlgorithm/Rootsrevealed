from python_gedcom_2.parser import Parser
from python_gedcom_2.element.element import Element

parser: Parser = Parser()

parser.parse_file("./gedcom_files/The English and British Kings and Queens.ged")

elements: list[Element] = parser.get_root_child_elements()
