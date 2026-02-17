import tkinter as tk
from tkinter import ttk, messagebox
import database as db

class SSIS_APP:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Student Information System")
        self.root.geometry("1000x600")

        #sidebar
        self.sidebar = tk.Frame(self.root, bg="#2c3e50", width=200)
        self.sidebar.pack(side="left", fill="y")

        #main window
        self.main_window = tk.Frame(self.root, bg="white")
        self.main_window.pack(side="right",expand=True,fill="both")

        #header
        self.header = tk.Frame(self.main_window, height=50, bg="#ecf0f1")
        self.header.pack(side="top", fill="x")

        self.setup_sidebar()
        self.setup_main_window()

    def setup_sidebar(self):
        tk.Label(self.sidebar, text="Menu", fg="white", bg="#2c3e50", font=("Arial",14,"bold")).pack(pady=20)

        btn_config = {"font": ("Arial", 12), "bg": "#34495e", "fg": "white", "activebackground": "#1abc9c", "relief": "flat", "pady": 10}
        
        tk.Button(self.sidebar, text="Students", command=lambda: self.switch_view("students"), **btn_config).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Programs", command=lambda: self.switch_view("programs"), **btn_config).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Colleges", command=lambda: self.switch_view("colleges"), **btn_config).pack(fill="x", padx=10, pady=5)
    
    def setup_main_window(self):
        ctrl_frame = tk.Frame(self.main_window, bg="white", pady=10)
        ctrl_frame.pack(fill="x", padx=20)

        self.search_entry = tk.Entry(ctrl_frame, font=("Arial", 12), width=30)
        self.search_entry.pack(side="left", padx=5)

        self.sort_var = tk.StringVar(value="Sort by:")
        self.sort_menu = ttk.Combobox(ctrl_frame, textvariable=self.sort_var, values=["ID", "Name", "Code"])
        self.sort_menu.pack(side="left", padx=10)

        self.add_btn = tk.Button(ctrl_frame, text="+ Add New", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=self.open_add_form)
        self.add_btn.pack(side="right", padx=5)

        #Treeview
        self.tree_frame = tk.Frame(self.main_window)
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.tree = ttk.Treeview(self.tree_frame, columns=(), show="headings")
        self.tree.pack(expand=True, fill="both")


    def switch_view(self, view_type):
        self.current_view = view_type
        
        # Define columns based on your CSV formats
        if view_type == "students":
            cols = ("ID", "First Name", "Last Name", "Year Level", "Gender", "Course")
        elif view_type == "programs":
            cols = ("Program Code", "Course Name", "College")
        else: # colleges
            cols = ("College Code", "College Name")

        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.load_table_data()

    def load_table_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
        data = db.read_data(files[self.current_view])
        
        for item in data:
            self.tree.insert("", "end", values=list(item.values()))

    def open_add_form(self):
        messagebox.showinfo("Add Info", f"Opening form for {self.current_view}")