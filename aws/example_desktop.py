from tkinter import *
from tkinter import ttk


def main2():
    
    root = Tk()
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New")
    filemenu.add_command(label="Open")
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="File", menu=filemenu)

    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About")
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)

    frm = ttk.Frame(root, padding=10)
    frm.pack()
    # frm.grid()
    # ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
    # ttk.Button(frm, text="Run commment", command=lambda: print("Button Clicked!")).grid(column=1, row=1)
    # ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
    ttk.Label(frm, text="Hello World!").pack()
    ttk.Button(frm, text="Run commment", command=lambda: print("Button Clicked!")).pack()
    ttk.Button(frm, text="Quit", command=root.destroy).pack()

    # Center the window on the screen
    root.update_idletasks()
    width = 200
    height = 200
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Sample data for the table
    records = [
        ("Alice", 30, "Engineer"),
        ("Bob", 25, "Designer"),
        ("Charlie", 35, "Manager"),
    ]

    # Create a Treeview widget for the table
    tree = ttk.Treeview(frm, columns=("Name", "Age", "Occupation"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Age", text="Age")
    tree.heading("Occupation", text="Occupation")

    # Insert records into the table
    for record in records:
        tree.insert("", "end", values=record)

    tree.pack(pady=10)

    # Alternative: Use a simple grid of Labels to display the table
    table_frame = ttk.Frame(frm)
    table_frame.pack(pady=10)

    headers = ["Name", "Age", "Occupation"]
    for col, header in enumerate(headers):
        ttk.Label(table_frame, text=header, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", padding=5).grid(row=0, column=col, sticky="nsew")

    for row_idx, record in enumerate(records, start=1):
        for col_idx, value in enumerate(record):
            ttk.Label(table_frame, text=value, borderwidth=1, relief="solid", padding=5).grid(row=row_idx, column=col_idx, sticky="nsew")

    root.mainloop()

def main():
    root = Tk()
    root.title("Deploy")
    
    label = ttk.Label(root, text="Hello, World!")
    label.pack(pady=10)
    
    button = ttk.Button(root, text="Click Me", command=lambda: print("Button Clicked!"))
    button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main2()