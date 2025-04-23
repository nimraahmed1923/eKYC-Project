import tkinter as tk
from tkinter import messagebox, filedialog, ttk, Toplevel, Text, Scrollbar
import os
import csv
from datetime import datetime
from extractor import extract_document_data
from manage_db import insert_data, fetch_all_data
from fingerprint_matcher import find_best_match
from face_recognition_module import recognize_face


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
        f"{'Place of Birth'.ljust(18)}: {data.get('Place of Birth', '')}",
        f"{'Place of Issue'.ljust(18)}: {data.get('Place of Issue', '')}",
        f"{'Date of Issue'.ljust(18)}: {data.get('Date of Issue', '')}",
        f"{'Date of Expiry'.ljust(18)}: {data.get('Date of Expiry', '')}"
    ]
    fallback = {"Unknown Name", "Unknown", "",
                "01/01/1990",          # dummy DOB
                "A0000000"}            # dummy passport #
    suspicious = any(val in fallback
                     for key, val in data.items()
                     if key in {"Surname", "Given Name", "DOB",
                                "Gender", "Passport Number",
                                "Nationality", "Place of Birth",
                                "Place of Issue", "Date of Issue",
                                "Date of Expiry"})

    

    # Simple suspicious flag logic (if required field is missing)
    # ---------------- Suspicious flag logic ---------------- #
    def bad(val: str, bad_list: list[str]):
        """Return True if empty or in a list of fallback tokens."""
        return (not val) or (val.strip() in bad_list)

    suspicious = False               # default

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
    # ------------------------------------------------------- #

    # rebuild the formatted text, now including Status line
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
    def __init__(self, root):
        self.root = root
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
        ttk.OptionMenu(self.card_frame, self.doc_type_var, "Aadhaar", "Aadhaar", "PAN", "Passport").pack(pady=(0, 10))

        ttk.Button(self.card_frame, text="1. Extract Document Data (OCR)", command=self.ocr).pack(pady=5)
        ttk.Button(self.card_frame, text="2. Show Stored eKYC Data", command=self.show_data).pack(pady=5)
        ttk.Button(self.card_frame, text="3. Match Fingerprint", command=self.match_fingerprint).pack(pady=5)
        ttk.Button(self.card_frame, text="4. Match Face", command=self.match_face).pack(pady=5)
        ttk.Button(self.card_frame, text="5. Export All eKYC to CSV", command=self.export_to_csv).pack(pady=5)
        ttk.Button(self.card_frame, text="6. Exit", command=root.quit).pack(pady=10)

        self.toggle_frame = tk.Frame(root, bg=self.bg_color)
        self.toggle_frame.pack(pady=10)

        self.theme_label = tk.Label(self.toggle_frame, text="Light Mode", bg=self.bg_color, fg=self.fg_color, font=("Helvetica", 10))
        self.theme_label.pack(side="left")

        self.theme_switch = ttk.Checkbutton(
            self.toggle_frame, style="Switch.TCheckbutton",
            command=self.toggle_theme, variable=tk.IntVar(value=0)
        )
        self.theme_switch.pack(side="left", padx=10)

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

    def ocr(self):
        file_path = filedialog.askopenfilename(title="Select Document Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            selected_type = self.doc_type_var.get()  # FIXED LINE HERE
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
        display = "\n\n".join([str(row) for row in rows]) or "No data found."
        messagebox.showinfo("Stored eKYC Data", display)

    def match_fingerprint(self):
        file_path = filedialog.askopenfilename(title="Select Test Fingerprint Image", filetypes=[("BMP Files", "*.bmp")])
        if file_path:
            dataset = os.path.join("dataset_FVC2000_DB4_B", "dataset", "train_data")
            best_match, score = find_best_match(file_path, dataset)
            if best_match and score >= 15:
                match_id = os.path.splitext(os.path.basename(best_match))[0]
                rows = fetch_all_data()
                matched_row = next((row for row in rows if any(match_id in str(field) for field in row)), None)
                if matched_row:
                    name = matched_row[5] if len(matched_row) > 5 else "Unknown"
                    aadhaar = matched_row[2] if len(matched_row) > 2 else "Unknown"
                    pan = matched_row[3] if len(matched_row) > 3 else "Unknown"
                    address = matched_row[8] if len(matched_row) > 8 else "Unknown"
                    display = f"Fingerprint matched with record:\n\nName: {name}\nAadhaar: {aadhaar}\nPAN: {pan}\nAddress: {address}"
                    messagebox.showinfo("Fingerprint Match", display)
                else:
                    messagebox.showinfo("Fingerprint Match", f"Match found: {best_match}\nScore: {score}\nBut no linked eKYC record found.")
            else:
                messagebox.showwarning("Fingerprint Match", "No strong fingerprint match found.")
        else:
            messagebox.showwarning("Cancelled", "No file selected.")

    def match_face(self):
        file_path = filedialog.askopenfilename(title="Select Test Face Image", filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            known_faces = os.path.join("dataset", "faces")
            result = recognize_face(file_path, known_faces)
            if result:
                messagebox.showinfo("Face Match", f"Face matched with: {result}")
            else:
                messagebox.showwarning("Face Match", "No face matched.")
        else:
            messagebox.showwarning("Cancelled", "No file selected.")

    def export_to_csv(self):
        rows = fetch_all_data()
        if not rows:
            messagebox.showinfo("Export", "No data to export.")
            return
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"ekyc_export_{now}.csv"
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_filename,
                                                 filetypes=[("CSV files", "*.csv")], title="Save eKYC Data As")
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Document Type", "Aadhaar", "PAN", "Passport", "Name", "DOB", "Gender", "Address"])
                    writer.writerows(rows)
                messagebox.showinfo("Export Success", f"eKYC data exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
        else:
            messagebox.showwarning("Cancelled", "Export cancelled.")


if __name__ == "__main__":
    root = tk.Tk()
    app = EKYCApp(root)
    root.mainloop()