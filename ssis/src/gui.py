import tkinter as tk
from tkinter import ttk, messagebox
import database as db

class SSIS_APP:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Student Information System")
        self.root.geometry("1000x600")
        self.current_view = "students"

        #sidebar
        self.sidebar = tk.Frame(self.root, bg="#e9edc9", width=200)
        self.sidebar.pack(side="left", fill="y")

        #main window
        self.main_window = tk.Frame(self.root, bg="#fefae0")
        self.main_window.pack(side="right",expand=True,fill="both")

        #header
        self.header = tk.Frame(self.main_window, height=50, bg="#DDA15E")
        self.header.pack(side="top", fill="x")

        self.setup_sidebar()
        self.setup_main_window()
        self.switch_view("students")

    def setup_sidebar(self):
        tk.Label(self.sidebar, text="Menu", fg="black", bg="#e9edc9", font=("Arial",14,"bold")).pack(pady=20)
        self.btn_config = {
            "font": ("Arial", 12),
            "bg": "#ccd5ae",
            "fg": "black",
            "activebackground": "#d4a373",
            "relief": "flat",
            "pady": 10,
            "cursor":  "hand2"}
        self.nav_buttons = {}
        views = [("Students", "students"), ("Programs", "programs"), ("Colleges", "colleges")]

        for text, v_type in views:
            btn = tk.Button(
                self.sidebar,
                text=text,
                command=lambda v=v_type: self.switch_view(v)    
                **self.btn_config
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[v_type] = btn
    
    def setup_main_window(self):
        self.top_bar = tk.Frame(self.main_window, bg="#fefae0", height=40)
        self.top_bar.pack(side="top", fill="x", padx=20, pady=0)

        #Search bar
        self.placeholder_text = "Search..."
        self.search_entry = tk.Entry(self.top_bar, font=('Arial', 12), width=40, bd=2, relief="groove", fg="gray")
        self.search_entry.insert(0, self.placeholder_text)
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.restore_placeholder)
        self.search_entry.pack(side="left", padx=15, pady=20)

        #Add Button
        self.add_btn = tk.Button(self.top_bar, text="+ Add New", bg="#ccd5ae", fg="black", font=("Arial", 10), command=self.open_add_form)
        self.add_btn.pack(side="right", padx=5)

        #Table
        self.tree_frame = tk.Frame(self.main_window, bg="white")
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=10)
        tree_scroll = tk.Scrollbar(self.tree_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=tree_scroll.set, show="headings")
        self.tree.tag_configure('evenrow', background='#f2f2f2')
        self.tree.pack(expand=True, fill="both")
        tree_scroll.config(command=self.tree.yview)

        #Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = tk.Label(self.main_window, textvariable=self.status_var, bd=1,
                                   relief="sunken", anchor="w", bg="#fefae0")
        self.status_bar.pack(side="bottom", fill="x")


    def switch_view(self, view_type):
        self.current_view = view_type
        self.update_sidebar_visuals(view_type)
        self.load_table_data(view_type)


    def load_table_data(self, view_type):
        for item in self.tree.get_children(): 
            self.tree.delete(item)
        
        files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
        data = db.read_data(files[view_type])
        
        if data:
            columns = list(data[0].keys())
            self.tree["columns"] = columns

            for col in columns:
                clean_name = col.replace("_", " ").upper()
                self.tree.heading(
                    col, 
                    text=clean_name, 
                    command=lambda c=col: self.sort_column(c, False)
                )
                self.tree.column(col, width=120, anchor="center")

            for i, row in enumerate(data):
                if i % 2 == 0:
                    self.tree.insert("", "end", values=list(row.values())) 
                else:
                    self.tree.insert("", "end", values=list(row.values()), tags=('evenrow',))
        self.status_var.set(f"Loaded {len(data)} records from {view_type}")

    def update_sidebar_visuals(self, active_view):
        for v_type, btn in self.nav_buttons.items():
            if v_type == active_view:
                btn.config(bg="#d4a373", fg="black", relief="sunken")
            else:
                btn.config(bg="#ccd5ae", fg="black", relief="flat")

    def sort_column(self, col, reverse):
        try:
            items = [(self.tree.set(k,col), k) for k in self.tree.get_children('')]
            try:
                items.sort(key=lambda t: float(t[0]), reverse=reverse)
            except ValueError:
                items.sort(key=lambda t: t[0].lower(), reverse=reverse)
            for index, (val, k) in enumerate(items):
                self.tree.move(k, '', index)
            for i, item in enumerate(self.tree.get_children()):
                if i % 2 == 0:
                 self.tree.item(item, tags=())
                else:
                    self.tree.item(item, tags=('evenrow',))
            for c in self.tree["columns"]:
                clean_name = c.replace("_"," ").upper()
                if c == col:
                    arrow = "▼" if reverse else "▲"
                    self.tree.heading(c, text=clean_name + arrow,
                                      command=lambda _c=c: self.sort_column(_c, not reverse))
                else:
                    self.tree.heading(c, text=clean_name,
                                      command=lambda _c=c: self.sort_column(_c, False))
        except Exception as e:
            messagebox.showerror("Sort error", f"An error occured while sorting {e}")
        self.status_var.set(f"Sorted by {col.replace('_', ' ')} {'Descending' if reverse else 'Ascending'}")

    def open_add_form(self):
        messagebox.showinfo("Add Info", f"Opening form for {self.current_view}")

    def clear_placeholder(self, event):
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def restore_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg="gray")