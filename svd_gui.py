import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import random
import os
import pickle
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

NEW_LINE_PER_WORD = False

def create_svg(data):
    # Set up SVG container with a minimal width and height, which will be dynamically adjusted
    svg = Element('svg', xmlns="http://www.w3.org/2000/svg", version="1.1")
    
    x_offset = 10  
    y_offset = 10
    radius = 5
    line_height = 20
    circle_spacing = 15
    
    max_width = 0
    max_height = 0

    # Iterate through the data
    for line in data:
        if line == ' ': # newline for newword
            y_offset += line_height
            x_offset = 10
            continue
        
        # Draw circles for each '0' and '1'
        for char in line:
            color = 'red' if char == '0' else 'black'
            circle = SubElement(svg, 'circle', cx=str(x_offset), cy=str(y_offset), r=str(radius), fill=color)
            x_offset += circle_spacing  # Move to the next position horizontally

        # Track the width and height to adjust SVG dimensions
        max_width = max(max_width, x_offset)
        max_height = y_offset + line_height

        if NEW_LINE_PER_WORD:
            y_offset += line_height
            x_offset = 10  # Reset horizontal position for the next line

    svg.set('width', str(max_width))
    svg.set('height', str(max_height))

    svg_str = tostring(svg, 'utf-8')
    parsed_svg = minidom.parseString(svg_str)
    return parsed_svg.toprettyxml(indent="  ")

current_encryption = None
current_encryption_name = ""

ALPHABET = "abcdefghijklmnopqrstuvwxyzäöüß.!-"

class BinaryTreeNode:
    def __init__(self, char=None, left=None, right=None):
        self.char = char
        self.left = left
        self.right = right

def lame_log(number):
    for exp in range(10):
        if 2**exp >= number:
            return exp

def generate_balanced_binary_tree(alphabet):
    nodes = [BinaryTreeNode(char) for char in alphabet]
    random.shuffle(nodes)
    
    while len(nodes) & (len(nodes) - 1) != 0:
        nodes.append(None)
    
    while len(nodes) > 1:
        new_nodes = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1] if i + 1 < len(nodes) else None
            parent = BinaryTreeNode()
            parent.left = left
            parent.right = right
            new_nodes.append(parent)
        nodes = new_nodes
    
    return nodes[0]

def create_encryption():
    global current_encryption, current_encryption_name
    tree = generate_balanced_binary_tree(ALPHABET)
    current_encryption = tree
    current_encryption_name = f"encryption_{random.randint(1000, 9999)}"  # Unique name for the encryption
    
    # Save the encryption to a file
    save_encryption(current_encryption, current_encryption_name)
    
    # Print the binary tree to the terminal
    print("Generated Full Encryption Tree:")
    print_tree(current_encryption)
    
    # Update the current encryption label
    current_encryption_label.config(text=f"Current Encryption: {current_encryption_name}")
    messagebox.showinfo("Encryption", f"New encryption created and saved as {current_encryption_name}.svd")

def save_encryption(tree, name):
    with open(f"{name}.svd", 'wb') as f:
        pickle.dump(tree, f)

def load_encryption():
    global current_encryption, current_encryption_name
    filepath = filedialog.askopenfilename(filetypes=[("Encryption Files", "*.svd")])
    if filepath:
        # Load the encryption tree from the file
        with open(filepath, 'rb') as f:
            current_encryption = pickle.load(f)
        current_encryption_name = os.path.basename(filepath).replace(".svd", "")
        
        # Print the loaded tree to the terminal
        print(f"Loaded Encryption Tree from {current_encryption_name}:")
        print_tree(current_encryption)
        
        current_encryption_label.config(text=f"Current Encryption: {current_encryption_name}")

def get_encryption_path(tree, char, path=""):
    if tree is None:
        return None
    if tree.char == char:
        return path
    left_path = get_encryption_path(tree.left, char, path + "0")
    if left_path is not None:
        return left_path
    return get_encryption_path(tree.right, char, path + "1")

def encrypt_file():
    if current_encryption is None:
        messagebox.showerror("Error", "No encryption loaded or created!")
        return
    
    filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filepath:
        return
    
    # Read the file content
    with open(filepath, 'r', encoding='utf-8') as file:
        text = file.read().lower()
    
    # Generate encryption paths for each character
    encrypted_text = []
    for char in text:
        if char in ALPHABET:
            path = get_encryption_path(current_encryption, char)
            encrypted_text.append(path)
        else:
            encrypted_text.append(' ')

    save_encrypted_image(encrypted_text, os.path.basename(filepath))

def save_encrypted_image(encrypted_text, original_filename):
    # Create SVG
    svg_content = create_svg(encrypted_text)

    # Save SVG to a file
    with open(f"{original_filename}_encrypted.svg", "w") as f:
        f.write(svg_content)
    messagebox.showinfo("Encryption", f"Successfully encrypted text to {original_filename}_encrypted.svg")

def print_tree(tree, level=0):
    if tree is not None:
        if tree.char is not None:
            print(f"{' ' * (level * 2)}{tree.char}")
        else:
            print(f"{' ' * (level * 2)}Internal Node")
        print_tree(tree.left, level + 1)
        print_tree(tree.right, level + 1)

root = tk.Tk()
root.title("Schwarzmariskanischer Diskus Verschlüsserer")

tk.Button(root, text="Create Encryption", command=create_encryption).pack(pady=10)
tk.Button(root, text="Load Encryption", command=load_encryption).pack(pady=10)

current_encryption_label = tk.Label(root, text="Current Encryption: None")
current_encryption_label.pack(pady=10)

tk.Button(root, text="Select Text File to Encrypt", command=encrypt_file).pack(pady=10)

root.mainloop()
