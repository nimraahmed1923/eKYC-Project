import tkinter as tk
from tkinter import ttk, messagebox
from gui_main import run_main_gui  # Assuming your main GUI function is in gui_main.py

# Hardcoded credentials (you can connect to DB later)
CREDENTIALS = {
    'admin': 'admin123',
    'employee': 'emp123'
}

class LoginWindow:
    def _init_(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("350x220")

        ttk.Label(root, text="Username:", font=("Segoe UI", 10)).pack(pady=10)
        self.username_entry = ttk.Entry(root, width=30)
        self.username_entry.pack()

        ttk.Label(root, text="Password:", font=("Segoe UI", 10)).pack(pady=10)
        self.password_entry = ttk.Entry(root, show="*", width=30)
        self.password_entry.pack()

        self.login_button = ttk.Button(root, text="Login", command=self.check_login)
        self.login_button.pack(pady=20)

    def check_login(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()

        if user in CREDENTIALS and CREDENTIALS[user] == pwd:
            messagebox.showinfo("Login Successful", f"Welcome, {user}!")
            self.root.destroy()
            run_main_gui(user)  # Launch your main app with user role
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")

# Run the login window first
if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()