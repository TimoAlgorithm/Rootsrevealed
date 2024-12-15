import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from python_gedcom_2.parser import Parser
from python_gedcom_2.element.individual import IndividualElement
from tkinter import PhotoImage, StringVar

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
            self.controller.parser.parse_file(file_path)
            self.controller.show_frame(DisplayFrame)

    def on_button_click(self, event):
        self.choose_file()

    def drop_file(self):
        messagebox.showinfo("Drag-and-Drop", "Datei abgelegt!")

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
        canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=color, outline=color)
        canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=color, outline=color)
        canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=color, outline=color)
        canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=color, outline=color)

        canvas.create_rectangle(x1+r, y1, x2-r, y1+r, fill=color, outline=color)
        canvas.create_rectangle(x1+r, y2-r, x2-r, y2, fill=color, outline=color)
        canvas.create_rectangle(x1, y1+r, x1+r, y2-r, fill=color, outline=color)
        canvas.create_rectangle(x2-r, y1+r, x2, y2-r, fill=color, outline=color)
        canvas.create_rectangle(x1+r, y1+r, x2-r, y2-r, fill=color, outline=color)

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

class EditingMenuFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: MainWindow):
        super().__init__(parent, bg="#36312D")
        self.controller = controller

        title_label = tk.Label(self, text="Edit Family Tree", font=("Arial", 20, "bold"), bg="#36312D", fg="#FFFFFF")
        title_label.pack(pady=20)

        btn_add = tk.Button(self, text="Add Individual", command=self.add_individual, bg="#A48164", fg="#FFFFFF")
        btn_add.pack(pady=10)

        btn_delete = tk.Button(self, text="Delete Individual", command=self.delete_individual, bg="#A48164", fg="#FFFFFF")
        btn_delete.pack(pady=10)

        btn_modify = tk.Button(self, text="Modify Individual", command=self.modify_individual, bg="#A48164", fg="#FFFFFF")
        btn_modify.pack(pady=10)

        btn_back = tk.Button(self, text="Back", command=lambda: controller.show_frame(SelectorFrame), bg="#BF9874", fg="#FFFFFF")
        btn_back.pack(pady=20)

    def add_individual(self):
        messagebox.showinfo("Add", "Functionality to add an individual.")

    def delete_individual(self):
        messagebox.showinfo("Delete", "Functionality to delete an individual.")

    def modify_individual(self):
        messagebox.showinfo("Modify", "Functionality to modify an individual.")


class DisplayFrame(tk.Frame):
    def __init__(self, parent: tk.Frame, controller: MainWindow):
        super().__init__(parent, bg="#36312D")
        self.controller = controller
        self.root_elements = controller.parser.get_root_child_elements()
        self.search_results = []

        # Erstelle die Suchleiste
        self.create_search_bar()

        # Bereich für die Suchergebnisse
        self.result_area = tk.Text(self, wrap="word", height=20, width=80, bg="#36312D", fg="#FFFFFF", insertbackground="#FFFFFF")
        self.result_area.pack(pady=20)

    

    def create_search_bar(self):
        """Erstellt eine Suchleiste, bei der das Bild als Hintergrund dient."""
        search_frame = tk.Frame(self, bg="#36312D")
        search_frame.pack(pady=20)

        # Bild vorbereiten: Skalieren und ggf. Text hinzufügen
        try:
            # Bild laden und skalieren
            image = Image.open("images/Suche ohne Text.png")
            new_size = (500, 150)  # Breite x Höhe des Suchleisten-Bildes
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Text optional hinzufügen
            draw = ImageDraw.Draw(image)
            font_path = "arial.ttf"
            font_size = 20
            try:
                font = ImageFont.truetype(font_path, font_size)
            except:
                font = ImageFont.load_default()

            # Konvertiere zu PhotoImage
            self.search_bar_image = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Fehler beim Bearbeiten des Bildes: {e}")
            messagebox.showerror("Fehler", "Suchleisten-Bild konnte nicht geladen werden.")
            return

        # Canvas erstellen, um das Bild zu platzieren
        canvas = tk.Canvas(search_frame, width=new_size[0], height=new_size[1], bg="#36312D", highlightthickness=0)
        canvas.pack()

        # Hintergrundbild einfügen
        canvas.create_image(0, 0, anchor="nw", image=self.search_bar_image)

        # Eingabefeld (Entry) auf dem Bild platzieren
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 14),
            bg="#58504E",  # Transparenter Hintergrund
            fg="white",  # Textfarbe
            bd=0,  # Keine Umrandung
            highlightthickness=0,  # Keine Highlightumrandung
            insertbackground="#000000"  # Cursorfarbe
        )
        search_entry.place(x=80, y=40, width=300, height=50)  # Positioniere das Eingabefeld auf dem Bild

        # Such-Button auf der rechten Seite des Bildes, weiter nach rechts verschoben
        search_button = tk.Button(
            search_frame,
            text="Suchen",
            command=self.perform_search,
            bg="#2F4F4F",
            fg="white",
            font=("Arial", 12, "bold"),
            bd=0
        )
        search_button.place(x=400, y=47, width=60, height=30)  # Button weiter nach rechts verschoben

    def perform_search(self):
        """Führt die Suche nach einem Namen aus."""
        query = self.search_var.get().strip().lower()
        self.result_area.delete(1.0, tk.END)  # Lösche vorherige Ergebnisse

        if not query:
            self.result_area.insert(tk.END, "Bitte gib einen Namen ein.\n")
            return

        # Suche nach passenden Namen in den GEDCOM-Daten
        self.search_results = []
        for element in self.root_elements:
            if isinstance(element, IndividualElement):
                self.check_name(element, query, 0)

        # Ergebnisse anzeigen
        if self.search_results:
            for result in self.search_results:
                self.result_area.insert(tk.END, result + "\n")
        else:
            self.result_area.insert(tk.END, "Kein passender Name gefunden.\n")

    def check_name(self, individual, query, level):
        """Überprüft, ob der Name des Individuums zur Suchanfrage passt."""
        name = individual.get_name().lower()
        if query in name:
            self.search_results.append(f"{'   ' * level}{individual.get_name()}")

        # Suche rekursiv bei Kindern
        children = self.controller.parser.get_natural_children(individual)
        for child in children:
            self.check_name(child, query, level + 1)



if __name__ == "__main__":
    parser: Parser = Parser()
    main = MainWindow(parser)
    main.title("Roots Revealed - Ancestry Research")
    main.state("zoomed")
    main.mainloop()