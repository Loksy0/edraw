import os
import tkinter as tk
from tkinter import filedialog, simpledialog, colorchooser, messagebox
from PIL import Image, ImageDraw

def position_window(window, x, y):
    window.geometry(f"300x200+{x}+{y}")

current_shape = None

def start_draw(event):
    global start_x, start_y, width_text, height_text, current_shape
    start_x, start_y = event.x, event.y
    width_text = canvas.create_text(start_x, start_y - 10, text="", fill="blue", font=("Arial", 10), tags=("box_group",))
    height_text = canvas.create_text(start_x - 20, start_y, text="", fill="blue", font=("Arial", 10), tags=("box_group",))
    current_shape = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="black", fill="", width=2, tags=("box_group",))

def draw_shape(event):
    global start_x, start_y, current_shape, width_text, height_text
    if current_shape:
        canvas.coords(current_shape, start_x, start_y, event.x, event.y)
    width_px = abs(event.x - start_x)
    height_px = abs(event.y - start_y)
    dpi = 96
    width_cm = (width_px / dpi) * 2.54
    height_cm = (height_px / dpi) * 2.54
    canvas.coords(width_text, (start_x + event.x) / 2, min(start_y, event.y) - 10)
    canvas.itemconfig(width_text, text=f"{width_cm:.1f} cm")
    canvas.coords(height_text, min(start_x, event.x) - 20, (start_y + event.y) / 2)
    canvas.itemconfig(height_text, text=f"{height_cm:.1f} cm")

def finish_draw(event):
    global current_shape
    current_shape = None

def start_move(event):
    global selected_item, move_start_x, move_start_y
    selected_item = canvas.find_closest(event.x, event.y)
    move_start_x, move_start_y = event.x, event.y
    if selected_item:
        tags = canvas.gettags(selected_item)
        if "box_group" in tags:
            canvas.tag_raise("box_group")  # Podnosimy całą grupę

def move_shape(event):
    global selected_item, move_start_x, move_start_y
    if selected_item:
        tags = canvas.gettags(selected_item)
        if "box_group" in tags:
            dx = event.x - move_start_x
            dy = event.y - move_start_y
            canvas.move("box_group", dx, dy)  # Przesuwamy całą grupę
            move_start_x, move_start_y = event.x, event.y

def finish_draw(event):
    global current_shape
    current_shape = None

def draw_shape(event):
    global start_x, start_y, current_shape, width_text, height_text
    if current_shape:
        canvas.delete(current_shape)
    current_shape = canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="black", fill="", width=2)
    width_px = abs(event.x - start_x)
    height_px = abs(event.y - start_y)
    dpi = 96
    width_cm = (width_px / dpi) * 2.54
    height_cm = (height_px / dpi) * 2.54
    canvas.coords(width_text, (start_x + event.x) / 2, min(start_y, event.y) - 10)
    canvas.itemconfig(width_text, text=f"{width_cm:.1f} cm")
    canvas.coords(height_text, min(start_x, event.x) - 20, (start_y + event.y) / 2)
    canvas.itemconfig(height_text, text=f"{height_cm:.1f} cm")

def finish_draw(event):
    global start_x, start_y, current_shape
    current_shape = None  


def enable_tool(tool):
    canvas.unbind("<Button-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")
    if tool == "draw":
        canvas.bind("<Button-1>", start_draw)
        canvas.bind("<B1-Motion>", draw_shape)
        canvas.bind("<ButtonRelease-1>", finish_draw)
    elif tool == "text":
        canvas.bind("<Button-1>", add_text)
    elif tool == "remove":
        canvas.bind("<Button-1>", remove_shape)
    elif tool == "move":
        canvas.bind("<Button-1>", start_move)
        canvas.bind("<B1-Motion>", move_shape)

def add_text(event):
    global text_color
    x, y = event.x, event.y
    text_window = tk.Toplevel(drawhere)
    text_window.title("Wstaw tekst")
    position_window(text_window, 400, 200)
    text_window.geometry("300x200")
    tk.Label(text_window, text="Tekst:").pack()
    text_entry = tk.Entry(text_window, width=30)
    text_entry.pack()
    
    def choose_color():
        global text_color
        color = colorchooser.askcolor()[1]
        text_color = color
        color_button.config(bg=color)
    
    color_button = tk.Button(text_window, text="Wybierz kolor", command=choose_color)
    color_button.pack()
    text_size = tk.Scale(text_window, from_=8, to=36, orient=tk.HORIZONTAL, label="Wielkość tekstu")
    text_size.pack()
    
    def insert_text():
        text = text_entry.get()
        font_size = text_size.get()
        font_style = ("Arial", font_size)
        canvas.create_text(x, y, text=text, fill=text_color, font=font_style)
        text_window.destroy()
    
    tk.Button(text_window, text="Wstaw", command=insert_text).pack()

def start_move(event):
    global selected_item, move_start_x, move_start_y
    selected_item = canvas.find_closest(event.x, event.y)
    move_start_x, move_start_y = event.x, event.y
    if selected_item:
        tags = canvas.gettags(selected_item)
        if "module" in tags:
            canvas.tag_raise("module")
        else:
            canvas.tag_raise(selected_item)

def remove_shape(event):
    global selected_item
    selected_item = canvas.find_closest(event.x, event.y)
    if selected_item:
        tags = canvas.gettags(selected_item)
        if "module" in tags:
            canvas.delete("module")
        else:
            canvas.delete(selected_item)


COLORS = ["red", "blue", "black", "green", "purple"]
def load_plugins():
    plugins_folder = "plugins"
    if not os.path.exists(plugins_folder):
        os.makedirs(plugins_folder)
    plugins = []
    for file in os.listdir(plugins_folder):
        if file.endswith(".ed"):
            try:
                with open(os.path.join(plugins_folder, file), "r") as f:
                    plugin_data = f.readlines()
                    plugin_info = parse_plugin(plugin_data)
                    plugins.append(plugin_info)
            except Exception as e:
                messagebox.showerror("Błąd wtyczki", f"Nie udało się wczytać pluginu {file}: {e}")
    return plugins

def parse_plugin(data):
    plugin_info = {
        "creator": None,
        "name": None,
        "version": None,
        "type": None,
        "modules": []
    }
    current_module = None
    for line in data:
        line = line.strip()
        if line.startswith("#def creator"):
            plugin_info["creator"] = line.split("=", 1)[1].strip()
        elif line.startswith("#def name"):
            plugin_info["name"] = line.split("=", 1)[1].strip()
        elif line.startswith("#def version"):
            plugin_info["version"] = line.split("=", 1)[1].strip()
        elif line.startswith("#def type"):
            plugin_info["type"] = line.split("=", 1)[1].strip()
        elif line.startswith("-"):
            current_module = {"name": line[1:].strip()}
        elif line.startswith("#start"):
            current_module["start"] = line.split()[1]
        elif line.startswith("#end"):
            current_module["end"] = line.split()[1]
            plugin_info["modules"].append(current_module)
            current_module = None
        elif "=" in line and current_module is not None:
            key, value = line.split("=", 1)
            current_module[key.strip()] = value.strip()
    return plugin_info

def show_modules():
    plugins = load_plugins()
    module_window = tk.Toplevel(toolpanel)
    module_window.title("Modules")
    module_window.geometry("400x300")
    for plugin in plugins:
        tk.Label(module_window, text=f"Plugin: {plugin['name']} by {plugin['creator']}").pack()
        for module in plugin["modules"]:
            module_frame = tk.Frame(module_window, relief=tk.RAISED, borderwidth=1)
            module_frame.pack(fill=tk.X, padx=5, pady=5)
            tk.Label(module_frame, text=module["name"], font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
            tk.Button(module_frame, text="Dodaj", command=lambda m=module: add_module(m)).pack(side=tk.RIGHT)

def add_module(module):
    try:
        raw_width = module.get("width", "5.0 cm").replace("cm", "").strip().strip('"')
        raw_height = module.get("height", "5.0 cm").replace("cm", "").strip().strip('"')
        width = float(raw_width) * 37.795275591  
        height = float(raw_height) * 37.795275591  

        color = module.get("color", "black") if module.get("color") in COLORS else "black"
        size_show = module.get("size_show", "False").lower() == "true"
        text_place = module.get("text_place", "center")
        text_size = int(module.get("text_size", "12"))
        text_color = module.get("text_color", "black")

        center_x = canvas.winfo_width() // 2
        center_y = canvas.winfo_height() // 2

        x1 = center_x - (width / 2)
        y1 = center_y - (height / 2)
        x2 = center_x + (width / 2)
        y2 = center_y + (height / 2)

        group = []
        rect = canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2, tags=("module",))
        group.append(rect)

        dpi = 96
        width_cm = (width / dpi) * 2.54
        height_cm = (height / dpi) * 2.54
        
        if size_show:
            width_text = canvas.create_text((x1 + x2) / 2, y1 - 10, text=f"{width_cm:.1f} cm", font=("Arial", 10), fill="blue", tags=("module",))
            height_text = canvas.create_text(x1 - 20, (y1 + y2) / 2, text=f"{height_cm:.1f} cm", font=("Arial", 10), fill="blue", tags=("module",))
            group.extend([width_text, height_text])

        if text_place == "center":
            text_x, text_y = center_x, center_y
        elif text_place == "up":
            text_x, text_y = center_x, y1 + 10
        elif text_place == "down":
            text_x, text_y = center_x, y2 - 10
        elif text_place == "left":
            text_x, text_y = x1 + 10, center_y
        elif text_place == "right":
            text_x, text_y = x2 - 10, center_y

        text_item = canvas.create_text(text_x, text_y, text=module["name"], fill=text_color, font=("Arial", text_size), tags=("module",))
        group.append(text_item)

        messagebox.showinfo("Dodano moduł", f"Moduł {module['name']} został dodany na płótno!")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się dodać modułu: {e}")

def save_project():
    file = filedialog.asksaveasfilename(defaultextension=".eds", filetypes=[("Easy Draw Save", "*.eds"), ("All files", "*.*")])
    if file:
        with open(file, 'w') as f:
            # Zapisujemy wszystkie elementy z płótna
            for item in canvas.find_all():
                item_type = canvas.type(item)
                coords = canvas.coords(item)
                if item_type == "rectangle":
                    outline = canvas.itemcget(item, "outline")
                    width = canvas.itemcget(item, "width")
                    f.write(f"rect:{coords[0]},{coords[1]},{coords[2]},{coords[3]},{outline},{width}\n")
                elif item_type == "text":
                    text = canvas.itemcget(item, "text")
                    fill = canvas.itemcget(item, "fill")
                    font = canvas.itemcget(item, "font")
                    f.write(f"text:{coords[0]},{coords[1]},{text},{fill},{font}\n")
                elif item_type == "line" or item_type == "oval":  # Można dodać obsługę innych typów
                    f.write(f"{item_type}:{','.join(map(str, coords))}\n")
            messagebox.showinfo("Zapisano", "Projekt został zapisany!")

def load_project():
    file = filedialog.askopenfilename(defaultextension=".eds", filetypes=[("Easy Draw Save", "*.eds"), ("All files", "*.*")])
    if file:
        canvas.delete("all")
        with open(file, 'r') as f:
            for line in f:
                parts = line.strip().split(":")
                item_type = parts[0]
                if item_type == "rect":
                    x1, y1, x2, y2, outline, width = parts[1].split(",")
                    canvas.create_rectangle(float(x1), float(y1), float(x2), float(y2), outline=outline, width=float(width))  # Zmiana na float
                elif item_type == "text":
                    x, y, text, fill, font = parts[1].split(",", 4)
                    canvas.create_text(float(x), float(y), text=text, fill=fill, font=font)
                elif item_type == "line" or item_type == "oval":
                    coords = list(map(float, parts[1].split(",")))
                    if item_type == "line":
                        canvas.create_line(*coords)
                    elif item_type == "oval":
                        canvas.create_oval(*coords)
        messagebox.showinfo("Wczytano", "Projekt został wczytany!")

# DRAW HERE
drawhere = tk.Tk()
drawhere.title("DRAW WINDOW")
position_window(drawhere, 150, 25)
drawhere.geometry("1090x700")
drawhere.resizable(height=False, width=False)
canvas = tk.Canvas(drawhere, bg="white", width=1090, height=700)
canvas.pack()

save_button = tk.Button(drawhere, text="Zapisz", command=lambda: save_project())
save_button.place(x=10, y=10)

load_button = tk.Button(drawhere, text="Wczytaj", command=lambda: load_project())
load_button.place(x=80, y=10)

def zapisz_notes():
    file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file:
        with open(file, 'w') as f:
            f.write(text_widget.get("1.0", tk.END))

def wczytaj_notes():
    file = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file:
        with open(file, 'r') as f:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", f.read())

# NOTES
notes = tk.Tk()
notes.title("NOTES")
position_window(notes, 1250, 25)
notes.geometry("250x680")
notes.resizable(height=False, width=False)
text_widget = tk.Text(notes)
text_widget.pack(fill=tk.BOTH, expand=True)

# MENU DLA NOTES
plik_menu_notes = tk.Menu(notes, tearoff=0)  # Oddzielne menu dla notes
notes.config(menu=plik_menu_notes)
plik_menu_notes.add_command(label="Zapisz", command=zapisz_notes)
plik_menu_notes.add_command(label="Wczytaj z", command=wczytaj_notes)

# TOOL PANEL
toolpanel = tk.Tk()
toolpanel.title("TOOL PANEL")
position_window(toolpanel, 25, 25)
toolpanel.geometry("120x199")
toolpanel.resizable(height=False, width=False)

box_tool = tk.Button(toolpanel, text="BOX", height=1, width=10, font=("Arial", 14), command=lambda: enable_tool("draw"))
box_tool.place(x=0, y=0)
text_tool = tk.Button(toolpanel, text="TEXT", height=1, width=10, font=("Arial", 14), command=lambda: enable_tool("text"))
text_tool.place(x=0, y=40)
box_tool = tk.Button(toolpanel, text="MOVE", height=1, width=10, font=("Arial", 14), command=lambda: enable_tool("move"))
box_tool.place(x=0, y=80)
remove_tool = tk.Button(toolpanel, text="REMOVE", height=1, width=10, font=("Arial", 14), command=lambda: enable_tool("remove"))
remove_tool.place(x=0, y=120)
modules_button = tk.Button(toolpanel, text="MODULES", height=1, width=10, font=("Arial", 14), command=show_modules)
modules_button.place(x=0, y=160)

# LOAD
toolpanel.mainloop()
drawhere.mainloop()
notes.mainloop()