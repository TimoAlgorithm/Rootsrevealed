from klassen import *
from python_gedcom_2.parser import Parser

parser: Parser = Parser()

parser.parse_file(".\\gedcom_files\\The English and British Kings and Queens.ged")

elements: List[Element] = parser.get_root_child_elements()

for e in elements:
    
    if Individual.is_individual(e):
        print(e)