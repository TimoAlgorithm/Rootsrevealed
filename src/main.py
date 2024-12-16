import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from python_gedcom_2.parser import Parser
from python_gedcom_2.element.individual import IndividualElement
import tkinter.font as tkFont


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
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = tk.Frame(self, bg="#36312D")
        self.container.grid(row=0, column=0, sticky='nsew')
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self.container, bg="#36312D", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.vbar = tk.Scrollbar(self.container, orient='vertical', command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky='ns')
        self.hbar = tk.Scrollbar(self.container, orient='horizontal', command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky='ew')
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
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
