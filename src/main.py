import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from python_gedcom_2.parser import Parser
from python_gedcom_2.element.individual import IndividualElement
import tkinter.font as tkFont
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
                                command=lambda i=i: self.on_menu_button_click(i))
            else:
                btn = tk.Button(menu_bar, text=f"Button {i+1}", bg="#2F2A25", fg="white",
                                command=lambda i=i: self.on_menu_button_click(i))

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
                # Daten aus dem Parser sammeln
                data = self.collect_tree_data()
                
                # CSV-Datei schreiben
                with open(file_path, mode="w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    
                    # Header schreiben
                    writer.writerow(["Name", "Elternteil", "Kind", "Weitere Informationen"])
                    
                    # Daten schreiben
                    for row in data:
                        writer.writerow(row)
                
                messagebox.showinfo("Exportieren", f"Datei erfolgreich exportiert nach {file_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Exportieren: {e}")

    def collect_tree_data(self):
        """Sammelt die Baumstruktur-Daten rekursiv und bereitet sie für den Export vor."""
        data = []

        def traverse_tree(person, parent_name=""):
            """Hilfsfunktion zum Durchlaufen des Baumes."""
            if isinstance(person, IndividualElement):
                name = person.get_name()
                children = self.controller.parser.get_children(person)
                data.append([name, parent_name, "Ja" if children else "Nein", ""])
                for child in children:
                    traverse_tree(child, parent_name=name)
        
        # Starte beim Wurzelelement
        elements = self.controller.parser.get_root_child_elements()
        eldest = [element for element in elements
                if isinstance(element, IndividualElement) and not element.is_child_in_a_family()]
        if eldest:
            traverse_tree(eldest[0])
        
        return data

    def save_data(self):
        """Speichert die aktuellen Änderungen."""
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

    def perform_search():
        search_name = search_entry.get().strip()
        if not search_name:
            messagebox.showwarning("Suche", "Bitte gib einen Namen ein.")
            return

        # Suche nach der Person in der GEDCOM-Datenstruktur
        found = False
        for person in self.controller.parser.get_root_child_elements():
            if isinstance(person, IndividualElement) and search_name.lower() in person.get_name().lower():
                messagebox.showinfo("Person gefunden", f"Person gefunden: {person.get_name()}")
                found = True
                break
        if not found:
            messagebox.showinfo("Nicht gefunden", "Keine Person mit diesem Namen gefunden.")

        tk.Button(search_window, text="Suchen", command=perform_search, bg="#BF9874", fg="white").pack(pady=10)

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
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#7D625B", outline="#E9E4E1")
        self.canvas.create_text(x, y + node_height / 2, text=person.get_name(), fill="#ffffff", font=self.font)
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


if __name__ == "__main__":
    p: Parser = Parser()
    main = MainWindow(p)
    main.title("Roots Revealed - Ancestry Research")
    main.state("zoomed")
    main.mainloop()
