from typing import List
from python_gedcom_2.element.element import Element
from python_gedcom_2.element.individual import IndividualElement
from python_gedcom_2.element.family import FamilyElement
from python_gedcom_2.element.event_detail import EventDetail


class Event:
    """Klasse die ein Event in Gedcom darstellt, also ein Tag mit einem Datum und oder Ort
    """
    def __init__(self, event: EventDetail):
        self.__event = event
        
    def get_event(self):
        return self.__event


class Family:
    def __init__(self, element: FamilyElement):
        self.__element = element
        
    def get_element(self):
        return self.__element


class Individual:
    """Klasse aller einzelner Menschen
    """
    def __init__(self, element: IndividualElement):
        self.__element = element 
    
    def get_element(self):
        return self.__element

    @staticmethod
    def is_individual(element: Element) -> bool:
        return isinstance(element, IndividualElement)
