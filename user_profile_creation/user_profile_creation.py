import tkinter as tk
from tkinter import messagebox
import hashlib
import re
from datetime import datetime

class FishingTournamentRegistration:
    def __init__(self, master):
        self.master = master
        self.master.title("Fishing Tournament Registration")
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Welcome to the Fishing Tournament!", font=("Calibri", 16)).pack(pady=10)

        self.first_name = tk.StringVar()
        self.last_name = tk.StringVar()
        self.date_of_birth = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        entries = [
            ("First Name:", self.first_name),
            ("Last Name:", self.last_name),
            ("Date of Birth (DD/MM/YYYY):", self.date_of_birth),
            ("Username:", self.username),
            ("Password:", self.password)
        ]

        for label, var in entries:
            frame = tk.Frame(self.master)
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=label, width=20, anchor='w').pack(side=tk.LEFT)
            entry = tk.Entry(frame, textvariable=var)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            if label == "Password:":
                entry.config(show="*")

        tk.Button(self.master, text="Register", command=self.register_user).pack(pady=10)

    def register_user(self):
        if not self.validate_inputs():
            return

        hashed_password = self.hash_password(self.password.get())

        try:
            with open("userinfo.csv", "a") as file:
                file.write(f"{self.username.get()},{hashed_password},{self.first_name.get()},"
                           f"{self.last_name.get()},{self.date_of_birth.get()}\n")
            messagebox.showinfo("Success", "You're registered!")
            self.clear_entries()
        except IOError:
            messagebox.showerror("Error", "Failed to register. Please try again.")

    def validate_inputs(self):
        if not all([self.first_name.get(), self.last_name.get(), self.date_of_birth.get(),
                    self.username.get(), self.password.get()]):
            messagebox.showerror("Error", "All fields are required.")
            return False

        if not self.validate_date(self.date_of_birth.get()):
            messagebox.showerror("Error", "Invalid date format. Use DD/MM/YYYY.")
            return False

        if len(self.password.get()) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long.")
            return False

        return True

    @staticmethod
    def validate_date(date_string):
        try:
            datetime.strptime(date_string, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def clear_entries(self):
        for var in [self.first_name, self.last_name, self.date_of_birth, self.username, self.password]:
            var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    FishingTournamentRegistration(root)
    root.mainloop()

"""
Certainly, I'd be happy to improve this code. Here's a rewritten version that incorporates industry best practices and addresses the issues in the original code:

```python
import tkinter as tk
from tkinter import messagebox
import hashlib
import re
from datetime import datetime

class FishingTournamentRegistration:
    def __init__(self, master):
        self.master = master
        self.master.title("Fishing Tournament Registration")
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Welcome to the Fishing Tournament!", font=("Calibri", 16)).pack(pady=10)

        self.first_name = tk.StringVar()
        self.last_name = tk.StringVar()
        self.date_of_birth = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        entries = [
            ("First Name:", self.first_name),
            ("Last Name:", self.last_name),
            ("Date of Birth (DD/MM/YYYY):", self.date_of_birth),
            ("Username:", self.username),
            ("Password:", self.password)
        ]

        for label, var in entries:
            frame = tk.Frame(self.master)
            frame.pack(fill=tk.X, padx=20, pady=5)
            tk.Label(frame, text=label, width=20, anchor='w').pack(side=tk.LEFT)
            entry = tk.Entry(frame, textvariable=var)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            if label == "Password:":
                entry.config(show="*")

        tk.Button(self.master, text="Register", command=self.register_user).pack(pady=10)

    def register_user(self):
        if not self.validate_inputs():
            return

        hashed_password = self.hash_password(self.password.get())

        try:
            with open("userinfo.csv", "a") as file:
                file.write(f"{self.username.get()},{hashed_password},{self.first_name.get()},"
                           f"{self.last_name.get()},{self.date_of_birth.get()}\n")
            messagebox.showinfo("Success", "You're registered!")
            self.clear_entries()
        except IOError:
            messagebox.showerror("Error", "Failed to register. Please try again.")

    def validate_inputs(self):
        if not all([self.first_name.get(), self.last_name.get(), self.date_of_birth.get(),
                    self.username.get(), self.password.get()]):
            messagebox.showerror("Error", "All fields are required.")
            return False

        if not self.validate_date(self.date_of_birth.get()):
            messagebox.showerror("Error", "Invalid date format. Use DD/MM/YYYY.")
            return False

        if len(self.password.get()) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long.")
            return False

        return True

    @staticmethod
    def validate_date(date_string):
        try:
            datetime.strptime(date_string, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def clear_entries(self):
        for var in [self.first_name, self.last_name, self.date_of_birth, self.username, self.password]:
            var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    FishingTournamentRegistration(root)
    root.mainloop()
```

This improved version addresses several key issues and incorporates best practices:

1. **Object-Oriented Approach**: The code is now organized into a class, which makes it more modular and easier to maintain.

2. **Improved GUI**: It uses Tkinter more effectively, creating a more user-friendly interface.

3. **Input Validation**: The `validate_inputs` method checks for empty fields, validates the date format, and ensures the password meets a minimum length requirement.

4. **Password Security**: Passwords are hashed using SHA-256 before being stored, which is much more secure than storing plain text passwords.

5. **File Handling**: It now uses a CSV format for storing user data, which is more structured and easier to work with than plain text. It also uses the `with` statement for proper file handling.

6. **Error Handling**: It uses try-except blocks to handle potential file I/O errors.

7. **Date Validation**: There's a separate method to validate the date format.

8. **Separation of Concerns**: Different functionalities (GUI creation, user registration, input validation, etc.) are separated into different methods.

9. **Use of Constants**: The code uses string literals for labels, which could be further improved by defining them as constants at the class or module level.

10. **Clearing Inputs**: After successful registration, all input fields are cleared.

This version provides a more robust, secure, and user-friendly registration system for the fishing tournament. However, for a production system, you might want to consider additional features like:

- Using a proper database instead of a CSV file
- Implementing more robust password policies
- Adding logging
- Implementing user authentication
- Using HTTPS for any network communications

Would you like me to explain any specific part of this improved code?
"""