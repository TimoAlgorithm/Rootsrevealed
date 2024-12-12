"""GEDCOM element consisting of tag `gedcom.tags.GEDCOM_TAG_FAMILY`"""

from typing import List
from python_gedcom_2.element.element import Element
import python_gedcom_2.tags
from python_gedcom_2.element.event_detail import EventDetail


class NotAnActualFamilyError(Exception):
    pass


class FamilyElement(Element):

    def get_tag(self):
        return python_gedcom_2.tags.GEDCOM_TAG_FAMILY

    def has_children(self) -> bool:
        """Returns whether there is at least one child in this family.
        """
        return self.is_tag_present(python_gedcom_2.tags.GEDCOM_TAG_CHILD)

    def has_husband(self) -> bool:
        """Returns whether the family has a husband
        """
        return self.is_tag_present(python_gedcom_2.tags.GEDCOM_TAG_HUSBAND)

    def has_wife(self) -> bool:
        """Returns whether the family has a husband
        """
        return self.is_tag_present(python_gedcom_2.tags.GEDCOM_TAG_WIFE)

    def get_husband_pointer(self) -> str:
        """Returns the pointer to the husband individual or an empty string if the family has none
        """
        return self.get_child_element_by_tag(python_gedcom_2.tags.GEDCOM_TAG_HUSBAND).get_value() if self.has_husband() else ""

    def get_wife_pointer(self) -> str:
        """Returns the pointer to the wife individual or an empty string if the family has none
        """
        return self.get_child_element_by_tag(python_gedcom_2.tags.GEDCOM_TAG_WIFE).get_value() if self.has_wife() else ""

    def get_children_pointers(self) -> List[str]:
        """Returns a list of direct children of this family. This function is not recursive.
        """
        return [child.get_value() for child in self.get_child_elements() if child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_CHILD]

    def get_events(self) -> List[EventDetail]:
        return [child for child in self.get_child_elements() if isinstance(child, EventDetail)]
