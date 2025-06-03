import tkinter as tk
from tkinter import messagebox, filedialog, ttk, Toplevel, Text, Scrollbar,Label,Button
import os
import csv
from datetime import datetime
from extractor import extract_document_data
from manage_db import insert_data, fetch_all_data
from fingerprint_matcher import find_best_match
from fraud_predictor import predict_fraud
from manage_db import delete_user_by_id

def show_ocr_result(data):
    popup = Toplevel()
    popup.title("OCR Extraction Result")
    popup.geometry("520x420")
    popup.configure(bg="white")

    header = tk.Label(popup, text="OCR Extraction Result", font=("Helvetica", 14, "bold"), bg="white", fg="#333")
    header.pack(pady=(10, 0))

    font_size = tk.IntVar(value=11)

    text_box = Text(popup, wrap="word", font=("Courier New", font_size.get()), bg="white", padx=10, pady=10)
    text_box.pack(expand=True, fill="both", padx=10, pady=(5, 0))

    scrollbar = Scrollbar(popup, command=text_box.yview)
    scrollbar.pack(side="right", fill="y")
    text_box.config(yscrollcommand=scrollbar.set)

    doc_type = data.get("Document Type", "").lower()
    formatted_lines = [f"{'Document Type'.ljust(18)}: {data.get('Document Type', '')}"]

    # Filter fields based on document type
    if doc_type == "pan":
        formatted_lines += [
            f"{'Name'.ljust(18)}: {data.get('Name', '')}",
            f"{'Father Name'.ljust(18)}: {data.get('Father Name', '')}",
            f"{'DOB'.ljust(18)}: {data.get('DOB', '')}",
            f"{'PAN Number'.ljust(18)}: {data.get('PAN Number', '')}"
        ]
    elif doc_type == "aadhaar":
        formatted_lines += [
            f"{'Name'.ljust(18)}: {data.get('Name', '')}",
            f"{'DOB'.ljust(18)}: {data.get('DOB', '')}",
            f"{'Gender'.ljust(18)}: {data.get('Gender', '')}",
            f"{'Aadhaar Number'.ljust(18)}: {data.get('Aadhaar Number', '')}"
        ]
    elif doc_type == "passport":
        formatted_lines += [
            f"{'Surname'.ljust(18)}: {data.get('Surname', '')}",
            f"{'Given Name'.ljust(18)}: {data.get('Given Name', '')}",
            f"{'DOB'.ljust(18)}: {data.get('DOB', '')}",
            f"{'Gender'.ljust(18)}: {data.get('Gender', '')}",
            f"{'Passport Number'.ljust(18)}: {data.get('Passport Number', '')}",
            f"{'Nationality'.ljust(18)}: {data.get('Nationality', '')}",
            f"{'Date of Expiry'.ljust(18)}: {data.get('Date of Expiry', '')}"
        ]
    
    # Suspicious flag logic
    def bad(val: str, bad_list: list[str]):
        """Return True if empty or in a list of fallback tokens."""
        return (not val) or (val.strip() in bad_list)

    suspicious = False

    if doc_type == "aadhaar":
        suspicious = any([
            bad(data.get("Name"),           ["Unknown Name"]),
            bad(data.get("DOB"),            ["01/01/1990"]),
            bad(data.get("Gender"),         ["Unknown"]),
            bad(data.get("Aadhaar Number"), ["000000000000"]),
        ])
    elif doc_type == "pan":
        suspicious = any([
            bad(data.get("Name"),        ["Unknown Name"]),
            bad(data.get("Father Name"), ["Unknown Father"]),
            bad(data.get("DOB"),         ["01/01/1990"]),
            bad(data.get("PAN Number"),  ["AAAAA0000A"]),
        ])
    elif doc_type == "passport":
        suspicious = any([
            bad(data.get("Surname"),          ["Unknown Name"]),
            bad(data.get("Given Name"),       ["Unknown Name"]),
            bad(data.get("DOB"),              ["01/01/1990"]),
            bad(data.get("Passport Number"),  ["A0000000"]),
        ])

    formatted_lines.append(f"{'Status'.ljust(18)}: {'Suspicious' if suspicious else 'Clear'}")
    
    formatted = "\n".join(formatted_lines)
    text_box.insert("1.0", formatted)
    text_box.config(state="disabled")

    controls = tk.Frame(popup, bg="white")
    controls.pack(pady=10)

    def copy_to_clipboard():
        popup.clipboard_clear()
        popup.clipboard_append(formatted)
        popup.update()
        tk.messagebox.showinfo("Copied", "OCR result copied to clipboard.")

    ttk.Button(controls, text="Copy to Clipboard", command=copy_to_clipboard).grid(row=0, column=0, padx=10)

    def increase_font():
        font_size.set(font_size.get() + 1)
        text_box.config(font=("Courier New", font_size.get()))

    def decrease_font():
        if font_size.get() > 8:
            font_size.set(font_size.get() - 1)
            text_box.config(font=("Courier New", font_size.get()))

    ttk.Button(controls, text="A+", width=4, command=increase_font).grid(row=0, column=1)
    ttk.Button(controls, text="A-", width=4, command=decrease_font).grid(row=0, column=2)

class EKYCApp:
    def __init__(self, root, role="Employee"):
        self.root = root
        self.role = role
        self.root.title("eKYC Application")
        self.root.geometry("480x560")
        self.root.configure(bg="#f5f5f5")

        self.theme = "light"
        self.setup_styles()

        self.header_frame = tk.Frame(root, bg="#00a8a8", bd=2, relief="raised")
        self.header_frame.pack(fill="x", pady=(0, 10))

        title = tk.Label(self.header_frame, text="eKYC System", font=("Helvetica", 18, "bold"), bg="#00a8a8", fg="white")
        title.pack(pady=12)

        self.card_frame = tk.Frame(root, bg="white", bd=1, relief="groove")
        self.card_frame.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(self.card_frame, text="Select Document Type", bg="white", fg="black", font=("Helvetica", 10)).pack(pady=(10, 5))
        self.doc_type_var = tk.StringVar()
        self.doc_type_var.set("Aadhaar")
        ttk.OptionMenu(self.card_frame, self.doc_type_var, "Aadhaar", "Aadhaar", "PAN", "Passport").pack(pady=(0, 5))

        ttk.Button(self.card_frame, text=" Extract Document Data (OCR)", command=self.ocr).pack(pady=5)

        if self.role == "Admin":
            ttk.Button(self.card_frame, text=" Show Stored eKYC Data", command=self.show_data).pack(pady=5)
            ttk.Button(self.card_frame, text=" Export All eKYC to CSV", command=self.export_csv).pack(pady=5)

        ttk.Button(self.card_frame, text=" Match Fingerprint", command=self.match_fingerprint).pack(pady=5)
        
        # Toggle Theme
        self.toggle_frame = tk.Frame(root, bg=self.bg_color)
        self.toggle_frame.pack(pady=10)

        self.theme_label = tk.Label(self.toggle_frame, text="Light Mode", bg=self.bg_color, fg=self.fg_color, font=("Helvetica", 10))
        self.theme_label.pack(side="left")

        self.theme_switch = ttk.Checkbutton(
            self.toggle_frame, style="Switch.TCheckbutton",
            command=self.toggle_theme, variable=tk.IntVar(value=0)
        )
        self.theme_switch.pack(side="left", padx=10)

        # 🔓 Logout Button
        ttk.Button(self.root, text="Logout", command=self.logout).pack(pady=(0, 15))


    # ✅ Moved logout method OUTSIDE __init__ and inside class
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.root.destroy()
            show_login_screen()
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        self.bg_color = "#f5f5f5" if self.theme == "light" else "#2b2b2b"
        self.fg_color = "#000000" if self.theme == "light" else "#ffffff"
        button_color = "#ffffff" if self.theme == "light" else "#3c3f41"

        self.root.configure(bg=self.bg_color)
        style.configure("TButton", background=button_color, foreground=self.fg_color, font=("Helvetica", 10), padding=6, relief="flat")
        style.map("TButton", background=[("active", "#d9d9d9")], relief=[("pressed", "groove")])
        style.configure("Switch.TCheckbutton", background=self.bg_color, foreground=self.fg_color, font=("Helvetica", 10))

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.setup_styles()
        self.root.configure(bg=self.bg_color)
        self.theme_label.configure(text="Dark Mode" if self.theme == "dark" else "Light Mode", bg=self.bg_color, fg=self.fg_color)
        self.toggle_frame.configure(bg=self.bg_color)
        self.card_frame.configure(bg="white" if self.theme == "light" else "#3c3f41")
        self.header_frame.configure(bg="#00a8a8")  # Keep header color consistent
        for widget in self.card_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg="white" if self.theme == "light" else "#3c3f41", fg=self.fg_color)

    def ocr(self):
        file_path = filedialog.askopenfilename(title="Select Document Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            selected_type = self.doc_type_var.get()
            try:
                data = extract_document_data(file_path, selected_type)
                insert_data(data)
                show_ocr_result(data)
            except Exception as e:
                messagebox.showerror("OCR Error", str(e))
        else:
            messagebox.showwarning("Cancelled", "No file selected.")

    def show_data(self):
        rows = fetch_all_data()

        win = tk.Toplevel(self.root)
        win.title("Stored eKYC Data")
        win.geometry("1200x400")

    # Column names (first column will show S.No)
        columns = [
            "S.No", "Document Type", "Name", "Father Name", "DOB", "Gender",
            "Aadhaar", "PAN", "Passport", "Nationality"
        ]
        tree = ttk.Treeview(win, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

    # Insert data with sequential numbering and store actual ID in tag
        for index, row in enumerate(rows, start=1):
            real_id = row[0]  # Actual DB ID
            display_row = list(row)
            display_row[0] = index  # Show S.No instead of DB ID
            tree.insert("", tk.END, values=display_row, tags=(str(real_id),))

        tree.pack(fill=tk.BOTH, expand=True)

    # Add scrollbar
        scrollbar = Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both", padx=10, pady=10)

    # Delete button
        def delete_selected_row():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a row to delete.")
                return

            item = selected_item[0]
            real_id = tree.item(item, 'tags')[0]  # Get original ID for deletion

            confirm = messagebox.askyesno("Confirm", f"Delete user ID {real_id}?")
            if confirm:
                delete_user_by_id(real_id)
                tree.delete(item)
                messagebox.showinfo("Deleted", f"User ID {real_id} deleted.")

        delete_button = tk.Button(win, text="Delete Selected Row", command=delete_selected_row, bg="red", fg="white")
        delete_button.pack(pady=10)

    def show_suspicious_popup(self):
        popup = tk.Toplevel()
        popup.title("Suspicious Fingerprint Match")
        popup.geometry("400x300")
        popup.resizable(False, False)

    # ⚠️ Warning icon
        Label(popup, text="⚠️", font=("Segoe UI Emoji", 48)).pack(pady=10)

    # Warning message
        msg = (
            "This fingerprint is not linked to any enrolled identity.\n"
            "Either it is not stored or the match is invalid.\n"
            "Please verify and try again."
        )
        Label(popup, text=msg, font=("Arial", 12), justify="center", wraplength=360).pack(pady=10)

    # OK button
        Button(popup, text="OK", width=20, command=popup.destroy).pack(pady=20)
    

    def match_fingerprint(self): 
        file_path = filedialog.askopenfilename(title="Select Test Fingerprint Image", filetypes=[("BMP Files", "*.bmp")])
        if not file_path:
           messagebox.showwarning("Cancelled", "No file selected.")
           return

        dataset = os.path.join("dataset_FVC2000_DB4_B", "dataset", "train_data")
        best_match, score = find_best_match(file_path, dataset)

        if best_match and score >= 15:
            match_id = os.path.splitext(os.path.basename(best_match))[0]
            rows = fetch_all_data()
            matched_row = next((row for row in rows if any(match_id in str(field) for field in row)), None)

            if matched_row:
                doc_type = matched_row[1]
                name = matched_row[2]
                father_name = matched_row[3]
                dob = matched_row[4]
                gender = matched_row[5]
                aadhaar = matched_row[6]
                pan = matched_row[7]
                passport = matched_row[8]
                nationality = matched_row[9]
                timestamp = matched_row[15]
                status = matched_row[14]
                # ✅ Insert fingerprint match result into DB
                data = {
                    'Document Type': doc_type,
                    'Name': name,
                    'Father Name': father_name,
                    'DOB': dob,
                    'Gender': gender,
                    'Aadhaar Number': aadhaar,
                    'PAN Number': pan,
                    'Passport Number': passport,
                    'Nationality': nationality,
                    'status': status,
                }
                insert_data(data, fingerprint_score=score)
                
                popup = tk.Toplevel(self.root)
                popup.title("Fingerprint Match")
                popup.geometry("400x400")
                popup.resizable(False, False)

                label_tick = tk.Label(popup, text="✅", font=("Arial", 40), fg="green")
                label_tick.pack(pady=(20, 5))

                title_label = tk.Label(popup, text="Fingerprint Matched Successfully!", font=("Arial", 14, "bold"))
                title_label.pack(pady=(0, 15))

                info_frame = tk.Frame(popup)
                info_frame.pack(padx=20, anchor="w")

               

                def add_label(field, value):
                    label = tk.Label(info_frame, text=f"{field}: {value}", font=("Arial", 11))
                    label.pack(anchor="w", pady=2)

            # Add fields based on document type
                add_label("Document Type", doc_type)
                add_label("Name", name)

                if doc_type == "Aadhaar":
                    add_label("Date of Birth", dob)
                    add_label("Gender", gender)
                    add_label("Aadhaar Number", aadhaar)
                    add_label("Match Score", f"{score:.2f}/500")
                    add_label("Timestamp", timestamp)
                    add_label("Status", status)

                elif doc_type == "PAN":
                    add_label("Date of Birth", dob)
                    add_label("Father's Name", father_name)
                    add_label("PAN Number", pan)
                    add_label("Match Score", f"{score:.2f}/500")

                elif doc_type == "Passport":
                    add_label("Date of Birth", dob)
                    add_label("Gender", gender)
                    add_label("Passport Number", passport)
                    add_label("Nationality", nationality)
                    add_label("Match Score", f"{score:.2f}/500")
                    add_label("Timestamp", timestamp)
                    add_label("Status", status)
                entry = {    
                    'aadhaar_number': aadhaar or '',
                    'pan_number': pan or '',
                    'passport_number': passport or '',
                    'fingerprint_score': score
                }
                fraud_status = predict_fraud(entry)
                add_label("Predicted Status", fraud_status)
     
            
         # Copy to Clipboard
                def copy_to_clipboard():
                    text = "\n".join(f"{child.cget('text')}" for child in info_frame.winfo_children())
                    self.root.clipboard_clear()
                    self.root.clipboard_append(text)
                    self.root.update()
                    messagebox.showinfo("Copied", "Details copied to clipboard.")

                btn_copy = ttk.Button(popup, text="Copy to Clipboard", command=copy_to_clipboard)
                btn_copy.pack(pady=20)
            else:  
                 self.show_suspicious_popup()
            
        else:
            messagebox.showinfo("No Match", "No fingerprint match found or score too low.")  


    def export_csv(self):
        rows = fetch_all_data()
        if not rows:
            messagebox.showinfo("No Data", "No data available to export.")
            return

    # Generate a default filename with current timestamp
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"ekyc_export_{now}.csv"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv")],
            title="Save eKYC Data"
        )
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                 writer = csv.writer(f)
                 writer.writerow([
                     "ID", "Document Type", "Name", "Father Name", "DOB", "Gender",
                     "Aadhaar", "PAN", "Passport", "Nationality", "Place of Birth",
                     "Place of Issue", "Date of Issue", "Date of Expiry", "Status", "Timestamp","Fingerprint Score", "Predicted Status"
                 ])
                 writer.writerows(rows)

            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
def validate_login(role, username, password, login_window):
    if role == "Admin" and username == "admin" and password == "admin123":
        login_window.destroy()
        root = tk.Tk()
        app = EKYCApp(root, role="Admin")
        root.mainloop()
    elif role == "Employee" and username == "employee" and password == "emp123":
        login_window.destroy()
        root = tk.Tk()
        app = EKYCApp(root, role="Employee")
        root.mainloop()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")


def show_login_screen():
    login_window = tk.Tk()
    login_window.title("eKYC Login")
    login_window.geometry("420x440")
    login_window.configure(bg="white")
    login_window.resizable(False, False)

    # 🔷 Header
    header = tk.Frame(login_window, bg="#00a8a8", height=60)
    header.pack(fill="x")
    tk.Label(header, text="eKYC System Login", font=("Helvetica", 16, "bold"), bg="#00a8a8", fg="white").pack(pady=15)

    # 🔹 Form Frame
    form_frame = tk.Frame(login_window, bg="white")
    form_frame.pack(pady=20)

    # Role
    tk.Label(form_frame, text="Select Role", font=("Helvetica", 11), bg="white", fg="#333").grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
    role_var = tk.StringVar(value="Employee")
    ttk.Combobox(form_frame, textvariable=role_var, values=["Admin", "Employee"], state="readonly", width=32).grid(row=1, column=0, padx=10, pady=(0, 15))

    # Username
    tk.Label(form_frame, text="Username", font=("Helvetica", 11), bg="white", fg="#333").grid(row=2, column=0, sticky="w", padx=10)
    username_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=username_var, width=34).grid(row=3, column=0, padx=10, pady=(0, 15))

    # Password
    tk.Label(form_frame, text="Password", font=("Helvetica", 11), bg="white", fg="#333").grid(row=4, column=0, sticky="w", padx=10)
    password_var = tk.StringVar()
    password_entry = ttk.Entry(form_frame, textvariable=password_var, width=34, show="*")
    password_entry.grid(row=5, column=0, padx=10, pady=(0, 5))

    # 👁️ Show/Hide Password
    show_pass_var = tk.BooleanVar()
    def toggle_password():
        password_entry.config(show="" if show_pass_var.get() else "*")
    tk.Checkbutton(form_frame, text="Show Password", variable=show_pass_var, command=toggle_password, bg="white", font=("Helvetica", 9)).grid(row=6, column=0, sticky="w", padx=10)

    # 📝 Remember Me
    remember_var = tk.BooleanVar()
    tk.Checkbutton(form_frame, text="Remember Me", variable=remember_var, bg="white", font=("Helvetica", 9)).grid(row=7, column=0, sticky="w", padx=10, pady=(5, 10))

    # 🔓 Login Button
    ttk.Button(
        login_window,
        text="Login",
        command=lambda: validate_login(role_var.get(), username_var.get(), password_var.get(), login_window)
    ).pack(pady=10)

    # Footer
    tk.Label(login_window, text="© 2025 eKYC App", font=("Arial", 8), bg="white", fg="#888").pack(side="bottom", pady=10)

    login_window.mainloop()

if __name__ == "__main__":
    show_login_screen()
if __name__ == "__main__":    
    root = tk.Tk()
    app = EKYCApp(root)
    root.mainloop()
