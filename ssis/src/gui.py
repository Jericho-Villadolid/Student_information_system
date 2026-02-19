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
        btn_config = {"font": ("Arial", 12), "bg": "#ccd5ae", "fg": "black", "activebackground": "#d4a373", "relief": "flat", "pady": 10}
        
        tk.Button(self.sidebar, text="Students", command=lambda: self.switch_view("students"), **btn_config).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Programs", command=lambda: self.switch_view("programs"), **btn_config).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Colleges", command=lambda: self.switch_view("colleges"), **btn_config).pack(fill="x", padx=10, pady=5)
    
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

        #Sort Button
        self.sort_menu = ttk.Combobox(
            self.top_bar,
            values=["ID", "Name", "Course", "Year Level", "College"],
            state="readonly",
            width=15)
        self.sort_menu.set("Sort by:")
        self.sort_menu.pack(side="left", padx=10)

        #Add Button
        self.add_btn = tk.Button(self.top_bar, text="+ Add New", bg="#ccd5ae", fg="black", font=("Arial", 10), command=self.open_add_form)
        self.add_btn.pack(side="right", padx=5)

        #Table
        self.tree_frame = tk.Frame(self.main_window, bg="white")
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=10)
        tree_scroll = tk.Scrollbar(self.tree_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=tree_scroll.set, show="headings")
        self.tree.pack(expand=True, fill="both")
        tree_scroll.config(command=self.tree.yview)


    def switch_view(self, view_type):
        self.current_view = view_type
        self.load_table_data(view_type)


    def load_table_data(self, view_type):
        for item in self.tree.get_children(): self.tree.delete(item)
        
        DEFAULT_KEYS = {
        "students": ["student_id", "first_name", "last_name", "year_level", "gender", "program_code"],
        "programs": ["program_code", "program_name", "college_code"],
        "colleges": ["college_code", "college_name"]
    }
 
        columns = DEFAULT_KEYS[view_type]
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").upper())
            self.tree.column(col, anchor="center", width=120)

        files = {
            "students": "students.csv",
            "programs": "programs.csv",
            "colleges": "colleges.csv"}
        data = db.read_data(files[view_type])
        
        if data:
            columns = list(data[0].keys())
            self.tree["columns"] = columns

            for col in columns:
                self.tree.heading(col, text=col.replace("_"," ").upper())
                self.tree.column(col, width=120, anchor="center")
            for row in data:
                self.tree.insert("", "end", values=list(row.values()))
        else:
            print(f"No data found in {files[view_type]}")

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