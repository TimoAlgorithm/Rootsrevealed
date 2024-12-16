import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from python_gedcom_2.parser import Parser
from python_gedcom_2.element.individual import IndividualElement


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
        self.root_elements = controller.parser.get_root_child_elements()

        # Suchleiste erstellen
        self.create_search_bar()

        # Canvas für den Baum erstellen
        self.tree_canvas = tk.Canvas(self, bg="#2F2A25", scrollregion=(0, 0, 2000, 2000))
        self.tree_canvas.pack(fill="both", expand=True)

        # Scrollbars hinzufügen
        self.v_scroll = tk.Scrollbar(self, orient="vertical", command=self.tree_canvas.yview)
        self.v_scroll.pack(side="right", fill="y")
        self.tree_canvas.config(yscrollcommand=self.v_scroll.set)

        self.h_scroll = tk.Scrollbar(self, orient="horizontal", command=self.tree_canvas.xview)
        self.h_scroll.pack(side="bottom", fill="x")
        self.tree_canvas.config(xscrollcommand=self.h_scroll.set)

        # Baum zeichnen
        self.display_tree()

    def display_tree(self):
        """Zeichnet den Baum grafisch auf das Canvas."""
        self.tree_canvas.delete("all")  # Löscht vorherige Inhalte
        start_x = 1000  # Startposition x
        start_y = 50    # Startposition y
        level_spacing = 100  # Abstand zwischen Ebenen
        sibling_spacing = 200  # Abstand zwischen Geschwistern

        # Wurzelelemente zeichnen
        for root in self.root_elements:
            if isinstance(root, IndividualElement):
                self.draw_tree_node(root, start_x, start_y, level_spacing, sibling_spacing)
                break

    def draw_tree_node(self, individual, x, y, level_spacing, sibling_spacing, parent_coords=None):
        """Zeichnet ein Rechteck für das Individuum und verbindet es mit dem Elternknoten."""
        # Rechteck erstellen
        rect_width = 120
        rect_height = 40
        name = individual.get_name() or "Unbekannt"

        # Rechteck und Name zeichnen
        self.tree_canvas.create_rectangle(x, y, x + rect_width, y + rect_height, fill="#A48164", outline="#4E3B31")
        self.tree_canvas.create_text(x + rect_width / 2, y + rect_height / 2, text=name, fill="white", font=("Arial", 10))

        # Linie zum Elternknoten ziehen
        if parent_coords:
            parent_x, parent_y = parent_coords
            self.tree_canvas.create_line(parent_x, parent_y, x + rect_width / 2, y, fill="white", width=2)

        # Kinder zeichnen
        children = self.controller.parser.get_natural_children(individual)
        if children:
            num_children = len(children)
            child_x_start = x - (num_children - 1) * sibling_spacing // 2  # Zentrierung der Kinder
            child_y = y + level_spacing

            for i, child in enumerate(children):
                child_x = child_x_start + i * sibling_spacing
                self.draw_tree_node(child, child_x, child_y, level_spacing, sibling_spacing, (x + rect_width / 2, y + rect_height))

    def create_search_bar(self):
        """Erstellt eine Suchleiste."""
        search_frame = tk.Frame(self, bg="#36312D")
        search_frame.pack(pady=10)

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 14), bg="#58504E", fg="white", bd=0)
        search_entry.pack(side="left", padx=10)

        search_button = tk.Button(search_frame, text="Suchen", command=self.perform_search, bg="#2F4F4F", fg="white", font=("Arial", 12, "bold"), bd=0)
        search_button.pack(side="left")

    def perform_search(self):
        """Sucht nach einem Namen und zeigt den Baum entsprechend an."""
        query = self.search_var.get().strip().lower()
        if not query:
            messagebox.showinfo("Hinweis", "Bitte gib einen Namen ein.")
            return

        # Suche nach passenden Individuen
        found_individuals = []
        for element in self.root_elements:
            if isinstance(element, IndividualElement) and query in element.get_name().lower():
                found_individuals.append(element)

        # Baum neu zeichnen, nur für die gefundenen Individuen
        self.tree_canvas.delete("all")
        start_x = 1000
        start_y = 50
        for i, individual in enumerate(found_individuals):
            self.draw_tree_node(individual, start_x + i * 300, start_y, 100, 200)




if __name__ == "__main__":
    parser: Parser = Parser()
    main = MainWindow(parser)
    main.title("Roots Revealed - Ancestry Research")
    main.state("zoomed")
    main.mainloop()