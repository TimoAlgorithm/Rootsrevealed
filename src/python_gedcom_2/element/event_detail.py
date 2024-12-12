from python_gedcom_2 import tags
from python_gedcom_2.element.date import DateElement
from python_gedcom_2.element.element import Element


class EventDetail(Element):
    """
    An EventDetail can be one of many kinds of actual Element. This is an abstract class to contain a lot of shared methods.
    (See page 29 of the GEDCOM 5.5 spec for details)
    NOTE: This is different from an event element, which is a legitimate GEDCOM tag and has its own rules.
    """

    __family_event_tags = ["ANUL", "CENS", "DIV", "DIVF", "ENGA", "MARB", "MARC", "MARL", "MARS", "MARR"]
    __individual_event_tags = ["BIRT", "CHR", "DEAT", "ADOP", 'BURI', 'CREM', 'BAPM', 'BARM', 'BASM', 'BLES', 'CHRA', 'CONF', 'FCOM', 'ORDN', 'NATU', 'EMIG', 'IMMI', 'CENS', 'PROB', 'WILL', 'GRAD', 'RETI']

    def has_date(self) -> bool:
        """Returns True if this EventDetail has a DateElement as a child.
        """
        return self.is_tag_present(tags.GEDCOM_TAG_DATE)

    def has_place(self) -> bool:
        """Returns True if this EventDetail has a place specified as a child.
        """
        return self.is_tag_present(tags.GEDCOM_TAG_PLACE)

    def get_date_element(self) -> DateElement | None:
        """Returns the DateElement of this EventDetail if it exists.
        """
        for child in self.get_child_elements():
            if isinstance(child, DateElement):
                return child

        return None

    def is_family_event(self) -> bool:
        return any(self.get_tag() == tag for tag in EventDetail.__family_event_tags)

    def is_individual_event(self) -> bool:
        return any(self.get_tag() == tag for tag in EventDetail.__individual_event_tags)
