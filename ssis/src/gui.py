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
                command=lambda v=v_type: self.switch_view(v),    
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
        self.search_entry.bind("<KeyRelease>", self.filter_search)

        #Add Button
        self.add_btn = tk.Button(self.top_bar, text="+ Add New", bg="#ccd5ae", fg="black", font=("Arial", 10), command=self.open_add_form)
        self.add_btn.pack(side="right", padx=5)

        #Batch Delete Mode Button
        self.del_mode_btn = tk.Button(
            self.top_bar, text="🗑 Delete Mode",
            bg="#faedcd",
            command=lambda: self.toggle_delete_mode(True),
            font=("Arial", 10, "bold")
        )
        self.del_mode_btn.pack(side="right", padx=5)

        #Table
        self.tree_frame = tk.Frame(self.main_window, bg="white")
        self.tree_frame.pack(expand=True, fill="both", padx=20, pady=10)
        tree_scroll = tk.Scrollbar(self.tree_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=tree_scroll.set, show="headings")
        self.tree.tag_configure('evenrow', background='#f2f2f2')
        self.tree.pack(expand=True, fill="both")
        tree_scroll.config(command=self.tree.yview)


    def switch_view(self, view_type):
        self.current_view = view_type
        self.update_sidebar_visuals(view_type)
        self.load_table_data(view_type)


    def load_table_data(self, view_type, delete_mode=False):
        for item in self.tree.get_children(): 
            self.tree.delete(item)
        
        files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
        data = db.read_data(files[view_type])
        
        if data:
            cols = list(data[0].keys())
            display_cols = ["select"] + cols if delete_mode else cols
            self.tree["columns"] = display_cols

            if delete_mode:
                self.tree.heading("select", text="SELECT")
                self.tree.column("selcet", width=70, anchor="center")

            for col in cols:
                self.tree.heading(col, text=col.replace("_", " ").upper(), 
                              command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=120, anchor="center")

            for i, row in enumerate(data):
                tag = ('evenrow',) if i % 2 != 0 else ()
                values = ["☐"] + list(row.values()) if delete_mode else list(row.values())
                self.tree.insert("", "end", values=values, tags=tag)


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


    def filter_search(self, event=None):
        query = self.search_entry.get().lower()

        if query == "" or query == self.placeholder_text.lower():
            self.load_table_data(self.current_view)
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
        all_data = db.read_data(files[self.current_view])
        filtered_results = []
        for row in all_data:
            row_values_string = " ".join(str(value) for value in row.values()).lower()
            if query in row_values_string:
                filtered_results.append(row)

        for i, row in enumerate(filtered_results):
            tag = 'evenrow' if i % 2 != 0 else ''
            self.tree.insert("", "end", values=list(row.values()), tags=(tag,))


    def open_add_form(self):
        self.form_window = tk.Toplevel(self.root)
        self.form_window.title(f"Add New {self.current_view[:-1].capitalize()}")
        self.form_window.geometry("400x500")
        self.form_window.configure(bg="#fefae0")
        self.form_window.grab_set()

        field_configs = {
            "students": ["Student ID", "First Name", "Last Name", "Year Level", "Gender", "Program Code"],
            "programs": ["Program Code", "Program Name", "College Code"],
            "colleges": ["College Code", "College Name"]
        }

        self.inputs = {}
        fields = field_configs[self.current_view]

        for field in fields:
            frame = tk.Frame(self.form_window, bg="#fafae0")
            frame.pack(fill="x", padx=30, pady=10)

            tk.Label(frame, text=field, bg="#fafae0", font=("Arial", 12, "bold")).pack(side="top", anchor="w")

            if field == "Gender":
                entry = ttk.Combobox(frame, values=["M", "F", "O"], state="readonly")
            elif field == "Year Level":
                entry = ttk.Combobox(frame, values=["1", "2", "3", "4"], state="readonly")
            else:
                entry = tk.Entry(frame, font=("Arial, 11"), bd=2, relief="groove")
            entry.pack(fill="x", pady=5)
            self.inputs[field] = entry
        tk.Button(
            self.form_window,
            text="SAVE RECORD",
            bg="#ccd5ae",
            font=("Arial", 11, "bold"),
            command=self.submit_data
        ).pack(pady=30)


    def submit_data(self):
        raw_data = {field: widget.get() for field, widget in self.inputs.items()}

        if any(val == "" for val in raw_data.values()):
            messagebox.showwarning("Input Error", "All Fields Required")
            return
        
        mapping = {
            "students": {
            "Student ID": "student_id", "First Name": "first_name", "Last Name": "last_name",
            "Year Level": "year_level", "Gender": "gender", "Program Code": "program_code"
            },
            "programs": {"Program Code": "program_code", "Program Name": "program_name", "College Code": "college_code"},
            "colleges": {"College Code": "college_code", "College Name": "college_name"}
            }
        
        final_dict = {mapping[self.current_view][k]: v for k, v in raw_data.items()}

        if self.current_view =="colleges":
            success, msg = db.validate_college(final_dict["college_code"])
        elif self.current_view == "programs":
            success, msg = db.validate_program(final_dict["program_code"], final_dict["college_code"])
        else:
            success, msg = db.validate_student(final_dict["student_id"], final_dict["gender"], final_dict["program_code"])

        if success:
            db.append_row(f"{self.current_view}.csv", list(final_dict.keys()), final_dict)
            messagebox.showinfo("Success", f"{self.current_view.capitalize()} added successfully")
            self.form_window.destroy()
            self.load_table_data(self.current_view)
        else:
            messagebox.showerror("Validation Error", msg)


    def toggle_delete_mode(self, active):
        self.delete_mode = active
        if active:
            self.add_btn.pack_forget()
            self.del_mode_btn.pack_forget()

            self.confirm_frame = tk.Frame(self.tree_frame, bg="#fefae0")
            self.confirm_frame.pack(side="right")

            tk.Button(self.confirm_frame, text="CONFRIM DELETION", bg="#ff4d4d", fg="black",
                      command=self.execute_batch_delete).pack(side="right", padx=5)
            tk.Button(self.confirm_frame, text="CANCEL", bg="#ccd5ae",
                      command=lambda: self.toggle_delete_mode(False)).pack(side="right")
            self.tree.bind("<ButtonRelease-1>", self.toggle_checkbox)
        else:
            if hasattr(self, 'confirm_frame'): self.confirm_frame.destroy()
            self.add_btn.pack(side="right", padx=5)
            self.del_mode_btn.pack(side="right")
            self.tree.unbind("<ButtonRelease-1>")
        self.load_table_data(self.current_view, delete_mode=active)

    
    def toggle_checkbox(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if item and column == "#1":
            current_values = list(self.tree.item(item, "values"))
            current_values[0] = "☑" if current_values[0] == "☐" else "☐"
            self.tree.item(item, values=current_values)
    

    def execute_batch_delete(self):
        selected_items = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            if values[0] == "☑":
                selected_items.append(str(values[1]))
        
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select records to delete.")
            return

        if messagebox.askyesno("Confirm", f"Delete {len(selected_items)} selected records?"):
            files = {"students": "students.csv", "programs": "programs.csv", "colleges": "colleges.csv"}
            filename = files[self.current_view]
            id_col = {"students": "student_id", "programs": "program_code", "colleges": "college_code"}[self.current_view]

        data = db.read_data(filename)
        new_data = [row for row in data if str(row[id_col]) not in selected_items]

        fieldnames = list(data[0].keys())
        db.save_data(filename, fieldnames, new_data)

        messagebox.showinfo("Success", f"Deleted {len(selected_items)} records.")
        self.delete_mode(False)


    def clear_placeholder(self, event):
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")


    def restore_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.config(fg="gray")