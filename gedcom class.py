class GedcomRecord:
    def __init__(self, record_id, record_type):
        self.record_id = record_id  # The record's ID (e.g., @I0@)
        self.record_type = record_type  # The type of the record (e.g., INDI or FAM)

        # Individual attributes
        self.name = None
        self.sex = None
        self.birth_date = None
        self.birth_place = None
        self.death_date = None
        self.death_place = None
        self.burial_date = None
        self.burial_place = None
        self.father_family_id = None
        self.mother_family_id = None
        self.spouse_family_ids = []  # Multiple spouse families (FAMS)
        self.children = []  # Children (FAMC)
        self.notes = []
        self.changed_date = None
        self.changed_time = None

        # Family attributes
        self.marriage_date = None
        self.divorce_date = None
        self.marital_status = None

    def __repr__(self):
        # Format the representation of the record for printing
        details_str = "\n    ".join(f"{key}: {value}" for key, value in self.__dict__.items() if value)
        return f"Record ID: {self.record_id}\nType: {self.record_type}\nDetails:\n    {details_str}\n"




def parse_gedcom(file_path):
    records = []
    current_record = None
    current_family = None

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(" ", 2)
            if len(parts) < 2:
                continue  # Skip malformed lines

            level = parts[0]
            tag = parts[1]
            value = parts[2] if len(parts) == 3 else None

            if level == "0":  # Start of a new record
                if current_record:
                    records.append(current_record)
                if current_family:
                    records.append(current_family)

                # Initialize a new record
                if tag.startswith('@I'):  # Individual record
                    current_record = GedcomRecord(record_id=tag, record_type="INDI")
                elif tag.startswith('@F'):  # Family record
                    current_family = GedcomRecord(record_id=tag, record_type="FAM")
                else:
                    current_record = None
                    current_family = None

            elif current_record:
                # Handle individual-related tags
                if tag == "NAME":
                    current_record.name = value
                elif tag == "SEX":
                    current_record.sex = value
                elif tag == "BIRT":
                    current_record.birth_date = None
                    current_record.birth_place = None
                elif tag == "DATE" and current_record.birth_date is None:
                    current_record.birth_date = value
                elif tag == "PLAC" and current_record.birth_place is None:
                    current_record.birth_place = value
                elif tag == "DEAT":
                    current_record.death_date = None
                    current_record.death_place = None
                elif tag == "DATE" and current_record.death_date is None:
                    current_record.death_date = value
                elif tag == "PLAC" and current_record.death_place is None:
                    current_record.death_place = value
                elif tag == "BURI":
                    current_record.burial_date = None
                    current_record.burial_place = None
                elif tag == "DATE" and current_record.burial_date is None:
                    current_record.burial_date = value
                elif tag == "PLAC" and current_record.burial_place is None:
                    current_record.burial_place = value
                elif tag == "FAMC":
                    current_record.father_family_id = value
                elif tag == "FAMS":
                    current_record.spouse_family_ids.append(value)
                elif tag == "CHAN":
                    current_record.changed_date = None
                    current_record.changed_time = None
                elif tag == "DATE" and current_record.changed_date is None:
                    current_record.changed_date = value
                elif tag == "TIME" and current_record.changed_time is None:
                    current_record.changed_time = value
                elif tag == "NOTE":
                    current_record.notes.append(value)

            elif current_family:
                # Handle family-related tags
                if tag == "HUSB":
                    current_family.husband_id = value
                elif tag == "WIFE":
                    current_family.wife_id = value
                elif tag == "CHIL":
                    current_family.children.append(value)
                elif tag == "MARR":
                    current_family.marriage_date = None
                elif tag == "DATE" and current_family.marriage_date is None:
                    current_family.marriage_date = value
                elif tag == "DIV":
                    current_family.divorce_date = None
                elif tag == "DATE" and current_family.divorce_date is None:
                    current_family.divorce_date = value
                elif tag == "_MSTAT":
                    current_family.marital_status = value
                elif tag == "CHAN":
                    current_family.changed_date = None
                    current_family.changed_time = None
                elif tag == "DATE" and current_family.changed_date is None:
                    current_family.changed_date = value
                elif tag == "TIME" and current_family.changed_time is None:
                    current_family.changed_time = value

        # Append the last record
        if current_record:
            records.append(current_record)
        if current_family:
            records.append(current_family)

    return records




# Path to the GEDCOM file
gedcom_file_path = "The Kennedy Family.ged"  # Replace with the actual file path

# Parse the GEDCOM file
parsed_records = parse_gedcom(gedcom_file_path)

# Print only the first 5 records
for record in parsed_records[:1000]:
    print(record)