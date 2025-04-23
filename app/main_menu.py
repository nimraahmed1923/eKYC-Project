import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import csv
from datetime import datetime
from ocr_module import extract_document_data
from manage_db import insert_data, fetch_all_data
from fingerprint_matcher import find_best_match
from face_recognition_module import recognize_face

class EKYCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("eKYC Application")
        self.root.geometry("480x550")
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

        if self.theme == "light":
            self.bg_color = "#f5f5f5"
            self.fg_color = "#000000"
            button_color = "#ffffff"
        else:
            self.bg_color = "#2b2b2b"
            self.fg_color = "#ffffff"
            button_color = "#3c3f41"

        self.root.configure(bg=self.bg_color)
        style.configure("TButton", background=button_color, foreground=self.fg_color,
                        font=("Helvetica", 10), padding=6, relief="flat")
        style.map("TButton",
                  background=[("active", "#d9d9d9")],
                  relief=[("pressed", "groove")])

        style.configure("Switch.TCheckbutton",
                        background=self.bg_color,
                        foreground=self.fg_color,
                        font=("Helvetica", 10))

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.setup_styles()
        self.root.configure(bg=self.bg_color)
        self.theme_label.configure(text="Dark Mode" if self.theme == "dark" else "Light Mode",
                                   bg=self.bg_color, fg=self.fg_color)

    def ocr(self):
        file_path = filedialog.askopenfilename(title="Select Document Image", 
                                               filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            selected_type = self.doc_type_var.get()
            try:
                data = extract_document_data(file_path, selected_type)
                if data:
                    insert_data(data)
                    display = "\n".join([f"{key}: {val}" for key, val in data.items()])
                    messagebox.showinfo("OCR Success", f"Document data saved:\n\n{display}")
                else:
                    messagebox.showerror("OCR Error", "Failed to extract valid data.")
            except Exception as e:
                messagebox.showerror("OCR Error", str(e))
        else:
            messagebox.showwarning("Cancelled", "No file selected.")

    def show_data(self):
        rows = fetch_all_data()
        display = "\n\n".join([str(row) for row in rows]) or "No data found."
        messagebox.showinfo("Stored eKYC Data", display)

    def match_fingerprint(self):
        file_path = filedialog.askopenfilename(title="Select Test Fingerprint Image", 
                                               filetypes=[("BMP Files", "*.bmp")])
        if file_path:
            dataset = os.path.join("dataset_FVC2000_DB4_B", "dataset", "train_data")
            best_match, score = find_best_match(file_path, dataset)
            if best_match and score >= 15:
                match_id = os.path.splitext(os.path.basename(best_match))[0]

                rows = fetch_all_data()
                matched_row = None
                for row in rows:
                    for field in row:
                        if match_id in str(field):
                            matched_row = row
                            break
                    if matched_row:
                        break

                if matched_row:
                    name = matched_row[5] if len(matched_row) > 5 else "Unknown"
                    aadhaar = matched_row[2] if len(matched_row) > 2 else "Unknown"
                    pan = matched_row[3] if len(matched_row) > 3 else "Unknown"
                    address = matched_row[7] if len(matched_row) > 7 else "Unknown"

                    display = f"Fingerprint matched with record:\n\nName: {name}\nAadhaar: {aadhaar}\nPAN: {pan}\nAddress: {address}"
                    messagebox.showinfo("Fingerprint Match", display)
                else:
                    messagebox.showinfo("Fingerprint Match", f"Match found: {best_match}\nScore: {score}\nBut no linked eKYC record found.")
            else:  
                messagebox.showwarning("Fingerprint Match", "No strong fingerprint match found.")
        else:
            messagebox.showwarning("Cancelled", "No file selected.")

    def match_face(self):
        file_path = filedialog.askopenfilename(title="Select Test Face Image", 
                                               filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
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

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 initialfile=default_filename,
                                                 filetypes=[("CSV files", "*.csv")],
                                                 title="Save eKYC Data As")
        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Document Type", "Aadhaar", "PAN", "Passport", "Name", "DOB", "Address"])
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