"""GEDCOM element consisting of tag `gedcom.tags.GEDCOM_TAG_INDIVIDUAL`"""

import re as regex
from typing import Tuple, List

from python_gedcom_2.element.birth import BirthElement
from python_gedcom_2.element.death import DeathElement
from python_gedcom_2.element.element import Element
import python_gedcom_2.tags
from python_gedcom_2.element.event_detail import EventDetail


class NotAnActualIndividualError(Exception):
    pass


class IndividualElement(Element):

    def get_tag(self):
        return python_gedcom_2.tags.GEDCOM_TAG_INDIVIDUAL

    def is_deceased(self):
        """Checks if this individual is deceased
        :rtype: bool
        """
        return self.is_tag_present(python_gedcom_2.tags.GEDCOM_TAG_DEATH)

    def is_child(self):
        """Checks if this element is a child of a family
        :rtype: bool
        """
        return self.is_tag_present(python_gedcom_2.tags.GEDCOM_TAG_FAMILY_CHILD)

    def is_spouse(self):
        """Checks if this element is a spouse in a family
        :rtype: bool
        """
        return self.is_tag_present(python_gedcom_2.tags.GEDCOM_TAG_FAMILY_SPOUSE)

    def is_private(self):
        """Checks if this individual is marked private
        :rtype: bool
        """
        for child in self.get_child_elements():
            if child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_PRIVATE:
                private = child.get_value()
                if private == 'Y':
                    return True

        return False

    def get_name_as_tuple(self) -> Tuple[str, str]:
        """Returns an individual's names as a tuple: (`str` given_name, `str` surname)
        If this person has a suffix (e.g., 'Jr') it gets removed entirely.
        :rtype: tuple
        """
        given_name = ""
        surname = ""

        # Return the first gedcom.tags.GEDCOM_TAG_NAME that is found.
        # Alternatively as soon as we have both the gedcom.tags.GEDCOM_TAG_GIVEN_NAME and _SURNAME return those.
        found_given_name = False
        found_surname_name = False

        for child in self.get_child_elements():
            if child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_NAME:
                # Some GEDCOM files don't use child tags but instead
                # place the name in the value of the NAME tag.
                if child.get_value() != "":
                    name = child.get_value().split('/')

                    if len(name) > 0:
                        given_name = name[0].strip()
                        if len(name) > 1:
                            surname = name[1].strip()

                    return given_name, surname

                for child_of_child in child.get_child_elements():

                    if child_of_child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_GIVEN_NAME:
                        given_name = child_of_child.get_value()
                        found_given_name = True

                    if child_of_child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_SURNAME:
                        surname = child_of_child.get_value()
                        found_surname_name = True

                if found_given_name and found_surname_name:
                    return given_name, surname

        # If we reach here we are probably returning empty strings
        return given_name, surname

    def get_name(self) -> str:
        return " ".join(self.get_name_as_tuple())

    def get_all_names(self):
        return [a.get_value() for a in self.get_child_elements() if a.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_NAME]

    def surname_match(self, surname_to_match):
        """Matches a string with the surname of an individual
        :type surname_to_match: str
        :rtype: bool
        """
        (_, surname) = self.get_name_as_tuple()
        return regex.search(surname_to_match, surname, regex.IGNORECASE)

    def given_name_match(self, given_name_to_match):
        """Matches a string with the given name of an individual
        :type given_name_to_match: str
        :rtype: bool
        """
        (given_name, _) = self.get_name_as_tuple()
        return regex.search(given_name_to_match, given_name, regex.IGNORECASE)

    def get_gender(self) -> str:
        """Returns the gender of a person in string format
        :rtype: str
        """
        gender = ""

        for child in self.get_child_elements():
            if child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_SEX:
                gender = child.get_value()

        return gender

    def get_census_data(self):
        """Returns a list of censuses of an individual formatted as tuples: (`str` date, `str` place, `list` sources)
        :rtype: list of tuple
        """
        census = []

        for child in self.get_child_elements():
            if child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_CENSUS:

                date = ''
                place = ''
                sources = []

                for child_of_child in child.get_child_elements():

                    if child_of_child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_DATE:
                        date = child_of_child.get_value()

                    if child_of_child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_PLACE:
                        place = child_of_child.get_value()

                    if child_of_child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_SOURCE:
                        sources.append(child_of_child.get_value())

                census.append((date, place, sources))

        return census

    def get_occupation(self) -> str:
        """Returns the occupation of a person
        """
        occupation = ""

        for child in self.get_child_elements():
            if child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_OCCUPATION:
                occupation = child.get_value()

        return occupation

    def get_birth_element(self) -> BirthElement | None:
        return self.get_child_element_by_tag(python_gedcom_2.tags.GEDCOM_TAG_BIRTH)

    def get_death_element(self) -> DeathElement | None:
        return self.get_child_element_by_tag(python_gedcom_2.tags.GEDCOM_TAG_DEATH)

    def get_events(self) -> List[EventDetail]:
        return [child for child in self.get_child_elements() if isinstance(child, EventDetail)]

    def is_child_in_a_family(self) -> bool:
        return self.is_tag_present(python_gedcom_2.tags.GEDCOM_TAG_FAMILY_CHILD)

    def get_parent_family_pointer(self) -> str | None:
        """Returns the pointer to the family that this individual is a child of
        """
        if self.is_child_in_a_family():
            return self.get_child_element_by_tag(python_gedcom_2.tags.GEDCOM_TAG_FAMILY_CHILD).get_value()
        return None

    def get_spouse_families_pointer(self) -> List[str]:
        """Returns the pointer to the family that this individual is a child of
        """
        return [child.get_value() for child in self.get_child_elements() if child.get_tag() == python_gedcom_2.tags.GEDCOM_TAG_FAMILY_SPOUSE]
