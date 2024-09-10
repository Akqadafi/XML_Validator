import lxml.etree as ET
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import logging
import zipfile
from tkinter import simpledialog

# Setup logging
logging.basicConfig(filename='xml_validator.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to compare XML structures, including attributes and values
def compare_xml_structure(xml1_root, xml2_root, check_attributes=False, check_values=False):
    """
    Compare the structure of two XML elements recursively and provide detailed feedback.
    
    Parameters:
    - xml1_root: Root element of the template XML.
    - xml2_root: Root element of the XML to be validated.
    - check_attributes: If True, will compare attributes of elements.
    - check_values: If True, will compare the text values inside elements.

    Returns:
    - match: True if the structures match, False otherwise.
    - details: Details about any structural mismatches.
    """

    # Compare tag names
    if xml1_root.tag != xml2_root.tag:
        return False, f"Mismatched tags: Template '{xml1_root.tag}' (line {xml1_root.sourceline}) vs XML '{xml2_root.tag}' (line {xml2_root.sourceline})"
    
    # Optionally compare attributes
    if check_attributes and xml1_root.attrib != xml2_root.attrib:
        return False, f"Mismatched attributes in tag '{xml1_root.tag}': {xml1_root.attrib} vs {xml2_root.attrib}"

    # Optionally compare text values
    if check_values and (xml1_root.text or '').strip() != (xml2_root.text or '').strip():
        return False, f"Mismatched values in tag '{xml1_root.tag}': '{xml1_root.text}' vs '{xml2_root.text}'"

    # Collect child elements (excluding comments)
    xml1_children = [child for child in xml1_root if not isinstance(child, ET._Comment)]
    xml2_children = [child for child in xml2_root if not isinstance(child, ET._Comment)]
    
    # Check for tag mismatches
    if len(xml1_children) != len(xml2_children):
        return False, f"Mismatched number of children in tag '{xml1_root.tag}': {len(xml1_children)} in template vs {len(xml2_children)} in XML"

    for child1, child2 in zip(xml1_children, xml2_children):
        match, details = compare_xml_structure(child1, child2, check_attributes, check_values)
        if not match:
            return False, details

    return True, "Structures match"

# Validate XML against template
def validate_xml_against_template(xml_file_path, template_file_path, check_attributes=False, check_values=False):
    """
    Validate the structure of an XML file against a template XML file.
    """
    try:
        xml1_tree = ET.parse(template_file_path)
        xml2_tree = ET.parse(xml_file_path)
    except Exception as e:
        return False, f"Error parsing files: {e}"

    return compare_xml_structure(xml1_tree.getroot(), xml2_tree.getroot(), check_attributes, check_values)

# File selection functions
def browse_xml():
    file_path = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML files", "*.xml")])
    xml_file_entry.delete(0, tk.END)
    xml_file_entry.insert(0, file_path)

def browse_template():
    file_path = filedialog.askopenfilename(title="Select Template XML File", filetypes=[("XML files", "*.xml")])
    template_file_entry.delete(0, tk.END)
    template_file_entry.insert(0, file_path)

# Function to validate a single XML file
def validate():
    xml_path_to_validate = xml_file_entry.get()
    template_path = template_file_entry.get()
    check_attributes = attr_check_var.get()
    check_values = val_check_var.get()

    if not xml_path_to_validate or not template_path:
        messagebox.showerror("Error", "Please select both XML and template files.")
        return

    match, details = validate_xml_against_template(xml_path_to_validate, template_path, check_attributes, check_values)
    messagebox.showinfo("Validation Result", details)
    logging.info(f"Validated: {xml_path_to_validate} | Result: {details}")

# Function to validate XML files in a folder
def validate_folder():
    folder_path = filedialog.askdirectory(title="Select Folder Containing XML Files")
    template_path = template_file_entry.get()
    check_attributes = attr_check_var.get()
    check_values = val_check_var.get()

    if not folder_path or not template_path:
        messagebox.showerror("Error", "Please select a folder and template file.")
        return

    results = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".xml"):
            xml_file_path = os.path.join(folder_path, file_name)
            match, details = validate_xml_against_template(xml_file_path, template_path, check_attributes, check_values)
            results[file_name] = details
            logging.info(f"Validated: {xml_file_path} | Result: {details}")

    result_text = "\n".join([f"{fname}: {res}" for fname, res in results.items()])
    messagebox.showinfo("Batch Validation Result", result_text)

# Drag-and-drop functionality (optional)
def drag_and_drop_handler(event):
    file_path = event.data
    xml_file_entry.delete(0, tk.END)
    xml_file_entry.insert(0, file_path)

# UI setup
app = tk.Tk()
app.title("XML Structure Validator")

# Frame for XML file
frame1 = tk.Frame(app)
frame1.pack(pady=10)
tk.Label(frame1, text="XML File Path:").pack(side=tk.LEFT)
xml_file_entry = tk.Entry(frame1, width=50)
xml_file_entry.pack(side=tk.LEFT)
tk.Button(frame1, text="Browse", command=browse_xml).pack(side=tk.LEFT)

# Frame for Template file
frame2 = tk.Frame(app)
frame2.pack(pady=10)
tk.Label(frame2, text="Template XML File Path:").pack(side=tk.LEFT)
template_file_entry = tk.Entry(frame2, width=50)
template_file_entry.pack(side=tk.LEFT)
tk.Button(frame2, text="Browse", command=browse_template).pack(side=tk.LEFT)

# Checkbox for attribute and value comparison
attr_check_var = tk.BooleanVar()
val_check_var = tk.BooleanVar()
attr_check = tk.Checkbutton(app, text="Check Attributes", variable=attr_check_var)
attr_check.pack(pady=5)
val_check = tk.Checkbutton(app, text="Check Values", variable=val_check_var)
val_check.pack(pady=5)

# Validation buttons
validate_button = tk.Button(app, text="Validate XML", command=validate)
validate_button.pack(pady=10)
batch_validate_button = tk.Button(app, text="Validate Folder of XMLs", command=validate_folder)
batch_validate_button.pack(pady=10)

# Progress bar (to be integrated for larger files)
progress = ttk.Progressbar(app, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=10)

# Drag-and-drop (optional, requires additional libraries)
# xml_file_entry.bind("<Drop>", drag_and_drop_handler)

app.mainloop()
