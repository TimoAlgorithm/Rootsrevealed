import os.path
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from python_gedcom_2.parser import Parser
from python_gedcom_2.element.individual import IndividualElement
import python_gedcom_2.tags as tags
import tkinter.font as tkFont
from python_gedcom_2.element.element import Element

import csv

class MainWindow(tk.Tk):
    def __init__(self, parser: Parser, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = parser
        self.config(bg="#36312D")
        self.container = tk.Frame(self, bg="#36312D")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.show_frame(SelectorFrame)

    def show_frame(self, frame_class) -> None:
        for widget in self.container.winfo_children():
            widget.destroy()
        frame = frame_class(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


class SelectorFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: MainWindow):
        super().__init__(parent, bg="#36312D")
        self.controller = controller
        self.logo_image_original = Image.open("./images/logo.png")
        self.logo_label = tk.Label(self, bg="#36312D")
        self.logo_label.place(relx=0.5, rely=0.3, anchor="center")
        self.drop_area = tk.Frame(self, bg="#36312D")
        self.drop_area.place(relx=0.5, rely=0.7, anchor="center", relwidth=0.6, relheight=0.2)
        self.button_canvas = tk.Canvas(self.drop_area, highlightthickness=0, bg="#36312D")
        self.button_canvas.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.3, relheight=0.5)
        self.button_canvas.bind("<Configure>", self.resize_elements)
        self.button_canvas.bind("<Button-1>", self.on_button_click)
        self.after_idle(self.initial_draw)

    def initial_draw(self):
        self.update_idletasks()
        event = type('event', (object,), {'width': self.button_canvas.winfo_width(), 'height': self.button_canvas.winfo_height()})
        self.resize_elements(event)

    def choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Wähle eine GEDCOM-Datei aus",
            filetypes=[("GEDCOM-Dateien", "*.ged"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            try:
                self.controller.parser.parse_file(file_path)
                self.controller.show_frame(DisplayFrame)
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {e}")

    def on_button_click(self, event):
        self.choose_file()

    def draw_rounded_rect_button(self, canvas_width, canvas_height):
        self.button_canvas.delete("all")
        border_color = "#A48164"
        bg_color = "#BF9874"
        text_color = "#ffffff"
        border_thickness = 4
        corner_radius = min(canvas_width, canvas_height) * 0.2
        x1, y1 = 0, 0
        x2, y2 = canvas_width, canvas_height
        ix1, iy1 = border_thickness, border_thickness
        ix2, iy2 = canvas_width - border_thickness, canvas_height - border_thickness
        self._draw_rounded_rect(self.button_canvas, x1, y1, x2, y2, corner_radius, border_color)
        self._draw_rounded_rect(self.button_canvas, ix1, iy1, ix2, iy2, corner_radius - border_thickness, bg_color)
        font_size = max(8, int(canvas_height * 0.3))
        self.button_canvas.create_text(
            canvas_width / 2,
            canvas_height / 2,
            text="Datei auswählen",
            fill=text_color,
            font=("Arial", font_size, "bold")
        )

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, r, color):
        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, fill=color, outline=color)
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, fill=color, outline=color)
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, fill=color, outline=color)
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, fill=color, outline=color)
        canvas.create_rectangle(x1 + r, y1, x2 - r, y1 + r, fill=color, outline=color)
        canvas.create_rectangle(x1 + r, y2 - r, x2 - r, y2, fill=color, outline=color)
        canvas.create_rectangle(x1, y1 + r, x1 + r, y2 - r, fill=color, outline=color)
        canvas.create_rectangle(x2 - r, y1 + r, x2, y2 - r, fill=color, outline=color)
        canvas.create_rectangle(x1 + r, y1 + r, x2 - r, y2 - r, fill=color, outline=color)

    def resize_elements(self, event):
        width = self.winfo_width()
        if width > 0:
            logo_size = int(width * 0.2)
            if logo_size > 0:
                resized_logo = self.logo_image_original.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(resized_logo)
                self.logo_label.config(image=self.logo_photo)
        canvas_w = self.button_canvas.winfo_width()
        canvas_h = self.button_canvas.winfo_height()
        if canvas_w > 0 and canvas_h > 0:
            self.draw_rounded_rect_button(canvas_w, canvas_h)


class DisplayFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: MainWindow):
        super().__init__(parent, bg="#36312D")
        self.controller = controller

        # Menüleiste erstellen
        self.create_menu_bar()

        # Container für Baumstruktur
        self.container = tk.Frame(self, bg="#36312D")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Canvas für Baum
        self.canvas = tk.Canvas(self.container, bg="#36312D", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')

        # Scrollbars
        self.vbar = tk.Scrollbar(self.container, orient='vertical', command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky='ns')
        self.hbar = tk.Scrollbar(self.container, orient='horizontal', command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky='ew')
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        # Baum zeichnen
        self.horizontal_gap = 30
        self.vertical_gap = 80
        self.vertical_padding = 10
        self.horizontal_padding = 20
        self.font = tkFont.Font(family="Arial", size=12, weight="normal")
        elements = self.controller.parser.get_root_child_elements()
        eldest = [element for element in elements
                  if isinstance(element, IndividualElement) and not element.is_child_in_a_family()]

        self.last_clicked: str = ""
        self.objects: dict[int, str] = {}

        if eldest:
            start_x = 1000
            start_y = 50
            self.draw_tree(eldest[0], start_x, start_y)
            self.canvas.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_menu_bar(self):
        """Erstellt eine horizontale Menüleiste mit einem Logo und Buttons, die unterschiedlich groß sind."""
        # Menüleiste erstellen
        menu_bar = tk.Frame(self, bg="#2F2A25", height=70)
        menu_bar.pack(side="top", fill="x")

        # Spaltenkonfiguration für flexible Verteilung
        menu_bar.grid_columnconfigure(0, weight=0)  # Logo-Spalte
        for i in range(1, 6):  # Buttons-Spalten (4 Buttons + 1 Platzhalter)
            menu_bar.grid_columnconfigure(i, weight=1)

        # Logo hinzufügen
        try:
            logo_image = Image.open("images/logo.png").resize((60, 60), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = tk.Label(menu_bar, image=self.logo_photo, bg="#2F2A25")
            logo_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        except Exception as e:
            print(f"Fehler beim Laden des Logos: {e}")
            logo_label = tk.Label(menu_bar, text="Logo", bg="#2F2A25", fg="white", font=("Arial", 12, "bold"))
            logo_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Buttons hinzufügen mit unterschiedlichen Größen
        self.button_images = []
        button_paths_and_sizes = [
            ("images/Exportieren.png", (60, 60)),
            ("images/Speichern.png", (60, 60)),
            ("images/Zoom in.png", (50, 50)),
            ("images/Zoom out.png", (50,50)),
            ("images/Suche ohne Text.png", (250, 75))
        ]

        for path, size in button_paths_and_sizes:
            try:
                image = Image.open(path).resize(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.button_images.append((photo, size))
            except Exception as e:
                print(f"Fehler beim Laden des Bildes {path}: {e}")
                self.button_images.append((None, size))

        # Buttons erstellen und platzieren
        for i, (img, size) in enumerate(self.button_images):
            if img:
                btn = tk.Button(menu_bar, image=img, bg="#2F2A25", bd=0, highlightthickness=0,
                                command=lambda j=i: self.on_menu_button_click(j))
            else:
                btn = tk.Button(menu_bar, text=f"Button {i+1}", bg="#2F2A25", fg="white",
                                command=lambda j=i: self.on_menu_button_click(j))

            # Button in der entsprechenden Spalte platzieren
            btn.grid(row=0, column=i + 1, padx=10, pady=5, sticky="nsew")
            btn.config(width=size[0] // 10, height=size[1] // 10)  # Größe der Buttons anpassen

        # Platzhalter-Spalte am rechten Rand hinzufügen
        menu_bar.grid_columnconfigure(len(self.button_images) + 1, weight=2)



    def on_menu_button_click(self, index):
        """Wird aufgerufen, wenn ein Button in der Menüleiste geklickt wird."""
        if index == 0:
            self.export_data()
        elif index == 1:
            self.save_data()
        elif index == 2:
            self.zoom_in()
        elif index == 3:
            self.zoom_out()
        elif index == 4:
            self.search_person()

    def export_data(self):
        """Exportiert die aktuellen Daten als CSV-Datei."""
        file_path = filedialog.asksaveasfilename(
            title="Exportiere die Daten",
            defaultextension=".csv",
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            try:
                invid = []
                for element in self.controller.parser.get_root_child_elements():
                    if isinstance(element,IndividualElement):
                        invid.append(element)

                data = []
                for i in invid:
                    if i.get_birth_element():
                        if i.get_birth_element().has_date():
                            birt = i.get_birth_element().get_date_element().get_value()
                        else:
                            birt = None
                    else:
                        birt = None
                    if i.get_death_element():
                        if i.get_death_element().has_date():
                            deat = i.get_death_element().get_date_element().get_value()
                        else:
                            deat = None
                    else:
                        deat = None
                    children = self.controller.parser.get_children(i)
                    child_names = ""
                    for child in children:
                        child_names += child.get_name() +"; "
                    child_names = child_names[:-2]
                    parents = self.controller.parser.get_parents(i)
                    parent_str = ""
                    for parent in parents:
                        if parent:
                            parent_str += parent.get_name() + "; "
                    parent_str = parent_str[:-2]
                    data.append([i.get_name(), i.get_gender(), i.get_occupation(), birt, deat, child_names, parent_str])

                data_dicts = [dict(zip(["Name", "Gender", "Arbeit", "Geburt", "Tod", "Kinder", "Eltern (V,M)"], row)) for row in data]
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    csvwriter = csv.DictWriter(
                        csvfile,
                        fieldnames=["Name", "Gender", "Arbeit", "Geburt", "Tod", "Kinder", "Eltern (V,M)"],
                        delimiter=',',
                        quotechar='"',
                        quoting=csv.QUOTE_MINIMAL
                    )
                    # Write header row
                    csvwriter.writeheader()

                    # Write data rows
                    csvwriter.writerows(data_dicts)

                messagebox.showinfo("Exportieren", f"Datei erfolgreich exportiert nach {file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Exportieren: {e}")

    def save_data(self):
        """Speichert die aktuellen Änderungen."""
        file_path = filedialog.asksaveasfilename(
            title="Speichern",
            defaultextension=".ged",
            filetypes=[("GEDCOM-Dateien", "*.ged"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            with open(file_path, "w+", encoding="utf-8") as file:
                self.controller.parser.save_gedcom(file)
                messagebox.showinfo("Speichern", "Daten wurden erfolgreich gespeichert.")

    def zoom_in(self):
        """Zoomt in die Ansicht hinein und passt die Schriftgröße an."""
        scale_factor = 1.2
        self.canvas.scale("all", 0, 0, scale_factor, scale_factor)
        self.update_font_size(scale_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def zoom_out(self):
        """Zoomt aus der Ansicht heraus und passt die Schriftgröße an."""
        scale_factor = 0.8
        self.canvas.scale("all", 0, 0, scale_factor, scale_factor)
        self.update_font_size(scale_factor)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_font_size(self, scale_factor):
        """Passt die Schriftgröße basierend auf dem Zoom-Faktor an."""
        current_size = self.font['size']
        new_size = max(8, int(current_size * scale_factor))  # Mindestgröße der Schrift = 8
        self.font.configure(size=new_size)


    def search_person(self):
        """Öffnet ein Suchfenster, um nach Personen zu suchen."""
        search_window = tk.Toplevel(self)
        search_window.title("Person suchen")
        search_window.geometry("300x150")
        search_window.config(bg="#2F2A25")

        tk.Label(search_window, text="Name der Person:", bg="#2F2A25", fg="white").pack(pady=10)
        search_entry = tk.Entry(search_window)
        search_entry.pack(pady=5)

    def get_node_dimensions(self, person: IndividualElement):
        name = person.get_name()
        text_width = self.font.measure(name)
        node_width = text_width + self.horizontal_padding
        node_height = self.font.metrics("linespace") + self.vertical_padding
        return node_width, node_height

    def subtree_width(self, person: IndividualElement) -> int:
        children = self.controller.parser.get_children(person)
        node_width, _ = self.get_node_dimensions(person)
        if not children:
            return node_width
        children_widths = [self.subtree_width(child) for child in children]
        total_children_width = sum(children_widths) + self.horizontal_gap * (len(children) - 1)
        return max(node_width, total_children_width)

    def draw_tree(self, person: IndividualElement, x: int, y: int):
        node_width, node_height = self.get_node_dimensions(person)
        x1 = x - node_width / 2
        y1 = y
        x2 = x + node_width / 2
        y2 = y + node_height
        rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#7D625B", outline="#E9E4E1")
        text_id = self.canvas.create_text(x, y + node_height / 2, text=person.get_name(), fill="#ffffff", font=self.font)
        self.objects[rect_id] = person.get_pointer()
        self.objects[text_id] = person.get_pointer()

        self.canvas.tag_bind(rect_id, "<Button-1>", lambda e, item_id=rect_id: self.object_click_event(e, item_id))
        self.canvas.tag_bind(text_id, "<Button-1>", lambda e, item_id=text_id: self.object_click_event(e, item_id))

        children = self.controller.parser.get_children(person)

        if not children:
            return

        children_widths = [self.subtree_width(child) for child in children]
        total_children_width = sum(children_widths) + self.horizontal_gap * (len(children) - 1)
        child_top_y = y + node_height + self.vertical_gap
        start_x = x - total_children_width / 2
        for i, child in enumerate(children):
            cw = children_widths[i]
            child_x = start_x + cw / 2
            child_y = child_top_y
            mid_y = (y2 + child_y) / 2
            self.canvas.create_line(x, y2, x, mid_y, fill="#A48164")
            self.canvas.create_line(x, mid_y, child_x, mid_y, fill="#A48164")
            self.canvas.create_line(child_x, mid_y, child_x, child_y, fill="#A48164")
            self.draw_tree(child, child_x, child_y)
            start_x += cw + self.horizontal_gap

    def object_click_event(self, event, item_id):
        if item_id in self.objects:
            pointer = self.objects[item_id]
            person = self.controller.parser.get_element_by_pointer(pointer)
            EditPopup(person, self.controller).mainloop()


class EditPopup(tk.Tk):
    def __init__(self, person: IndividualElement, controller: MainWindow):
        super().__init__()
        self.controller = controller
        self.person = person

        self.title("Daten ändern")
        #self.geometry("400x280")
        self.resizable(False, False)
        self.configure(bg="#7A534D")  # Hintergrundfarbe

        is_name_tag_present = person.is_tag_present(tags.GEDCOM_TAG_NAME)

        self.given_name = person.get_name_as_tuple()[0] if is_name_tag_present else ""
        self.nachname = person.get_name_as_tuple()[1] if is_name_tag_present else ""
        self.geburtsdatum = person.get_birth_element().get_date_element().as_datetime() if person.get_birth_element() else ""
        self.sterbedatum = person.get_death_element().get_date_element().as_datetime() if person.get_death_element() else ""

        self.given_name_entry = self.create_label_entry("Name", 0, self.given_name)
        self.nachname_entry = self.create_label_entry("Nachname", 1, self.nachname)
        self.geburtsdatum_entry = self.create_label_entry("Geburtsdatum", 2, self.geburtsdatum)
        self.sterbedatum_entry = self.create_label_entry("Sterbedatum", 3, self.sterbedatum)

        fertig_button = tk.Button(
            self,
            text="Fertig",
            bg="#D5A77C",
            fg="white",
            font=("Helvetica", 12, "bold"),
            relief="flat",
            command=self.on_fertig_click
        )
        fertig_button.grid(row=4, column=0, columnspan=2, pady=20)

        text = tk.Label(self, text=self.person.to_gedcom_string(True), anchor="w", justify="left")
        text.grid(row=0, column=2, rowspan=5, padx=20, pady=10, sticky="nsew")

    def create_label_entry(self, text, row, labeltext):
        label = tk.Label(self, text=text, bg="#7A534D", fg="white", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")
        entry = tk.Entry(self, font=("Helvetica", 12), bg="#B38B82", fg="black", relief="flat")
        entry.insert(0, labeltext)
        entry.grid(row=row, column=1, padx=20, pady=10)
        return entry

    def on_fertig_click(self):
        new_name = self.given_name_entry.get()
        if new_name != self.given_name or self.nachname_entry.get() != self.nachname:
            name_element: Element = self.person.get_child_element_by_tag(tags.GEDCOM_TAG_NAME)
            name_element.get_child_element_by_tag(tags.GEDCOM_TAG_GIVEN_NAME).set_value(new_name)
            name_element.get_child_element_by_tag(tags.GEDCOM_TAG_SURNAME).set_value(self.nachname_entry.get())
            name_element.set_value(new_name + " /" + self.nachname_entry.get() + "/")

        # TODO: events und andere sachen editieren

        self.controller.show_frame(DisplayFrame)
        self.destroy()


if __name__ == "__main__":
    p: Parser = Parser()
    main = MainWindow(p)
    main.title("Roots Revealed - Ancestry Research")
    main.state("zoomed")
    main.mainloop()
