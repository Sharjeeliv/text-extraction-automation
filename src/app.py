import tkinter as tk
from tkinter import filedialog, messagebox
from extract import extraction_entry, test
from analysis import analysis_entry
from params import PATH
from parse import parse_entry

import os


# *********************
# HELPER FUNCTIONS
# *********************
def run_extraction():
    texts_path = texts_entry.get()
    labels_path = labels_entry.get()
    output_path = output_entry.get()
    suffix = suffix_entry.get()
    exclude_files = exclude_entry.get().split()  # Assuming space-separated files
    extensions = ext_entry.get().split()
    
    # Validate inputs
    if not os.path.exists(texts_path):
        messagebox.showerror("Error", "Texts directory not found!")
        return
    if not os.path.exists(labels_path):
        messagebox.showerror("Error", "Labels directory not found!")
        return
    
    # Initialize paths and run the extraction
    PATH["LABELS"] = labels_path
    PATH["RESULTS"] = output_path
    PATH["TEXTS"] = texts_path

    try:
        parse_entry(texts_path, exclude=exclude_files, ext=extensions)
        extraction_entry(texts_path, exclude_files, extensions, suffix)
        messagebox.showinfo("Success", "Extraction completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        exit()

def run_analysis():
    texts_path = texts_entry.get()
    labels_path = labels_entry.get()
    output_path = output_entry.get()
    suffix = suffix_entry.get()
    exclude_files = exclude_entry.get().split()  # Assuming space-separated files
    extensions = ext_entry.get().split()
    
    # Validate inputs
    if not os.path.exists(texts_path):
        messagebox.showerror("Error", "Texts directory not found!")
        return
    if not os.path.exists(output_path):
        messagebox.showerror("Error", "Output directory not found!")
        return
    if not os.path.exists(labels_path):
        messagebox.showerror("Error", "Labels directory not found!")
        return
    
    # Initialize paths and run the extraction
    PATH["LABELS"] = labels_path
    PATH["RESULTS"] = output_path
    PATH["TEXTS"] = texts_path


    try:
        parse_entry(texts_path, exclude=exclude_files, ext=extensions)
        analysis_entry()
        extraction_entry(texts_path, exclude_files, extensions, suffix)
        
        messagebox.showinfo("Success", "Analysis completed!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        exit()

# *********************
# GUI SETUP
# *********************
root = tk.Tk()
root.title("Text Extraction Tool")

# Create a frame for better organization
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack()

# Texts Directory
tk.Label(main_frame, text="Input Directory:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
texts_entry = tk.Entry(main_frame, width=40)
texts_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(main_frame, text="Browse", command=lambda: texts_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2, padx=5, pady=5)

# Labels Directory
tk.Label(main_frame, text="Labels Directory:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
labels_entry = tk.Entry(main_frame, width=40)
labels_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(main_frame, text="Browse", command=lambda: labels_entry.insert(0, filedialog.askdirectory())).grid(row=1, column=2, padx=5, pady=5)

# Output Directory
tk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
output_entry = tk.Entry(main_frame, width=40)
output_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(main_frame, text="Browse", command=lambda: output_entry.insert(0, filedialog.askdirectory())).grid(row=2, column=2, padx=5, pady=5)

# Label Suffix
tk.Label(main_frame, text="Label Suffix:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
suffix_entry = tk.Entry(main_frame, width=40)
suffix_entry.grid(row=3, column=1, padx=10, pady=5)

# Exclude Files
tk.Label(main_frame, text="Exclude Files Words (space-separated):").grid(row=4, column=0, sticky='e', padx=5, pady=5)
exclude_entry = tk.Entry(main_frame, width=40)
exclude_entry.grid(row=4, column=1, padx=10, pady=5)

# File Extensions
tk.Label(main_frame, text="File Extensions (space-separated):").grid(row=5, column=0, sticky='e', padx=5, pady=5)
ext_entry = tk.Entry(main_frame, width=40)
ext_entry.grid(row=5, column=1, padx=10, pady=5)

# Buttons for Actions
btn_frame = tk.Frame(main_frame, pady=10)
btn_frame.grid(row=6, columnspan=3)

tk.Button(btn_frame, text="Run Extraction", command=run_extraction, width=20).grid(row=0, column=0, padx=10, pady=5)
tk.Button(btn_frame, text="Run with Analysis", command=run_analysis, width=20).grid(row=0, column=1, padx=10, pady=5)

# *********************
# GUI SETUP
# *********************
if __name__ == '__main__':
    root.mainloop()

