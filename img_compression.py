import heapq
from collections import Counter
from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

class Node:
    def __init__(self, freq, symbol, left=None, right=None):
        self.freq = freq
        self.symbol = symbol
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequencies):
    heap = [Node(freq, symbol) for symbol, freq in frequencies.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, merged)
    return heap[0]

def generate_codes(node, current_code="", codes={}):
    if node:
        if node.symbol is not None:
            codes[node.symbol] = current_code
        generate_codes(node.left, current_code + "0", codes)
        generate_codes(node.right, current_code + "1", codes)
    return codes

def encode_image(image_array, codes):
    flattened = image_array.flatten()
    return ''.join([codes[pixel] for pixel in flattened])

def decode_image(encoded_data, root, shape):
    decoded_array = []
    current_node = root
    for bit in encoded_data:
        current_node = current_node.left if bit == "0" else current_node.right
        if current_node.symbol is not None:
            decoded_array.append(current_node.symbol)
            current_node = root
    return np.array(decoded_array).reshape(shape)

def get_file_size(file_path):
    """Returns the file size in KB/MB."""
    size_bytes = os.path.getsize(file_path)
    if size_bytes < 1024 * 1024:  # Less than 1 MB
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Compressor")
        self.root.geometry("900x750")
        self.root.configure(bg="#282C34")

        # Title
        self.title_label = tk.Label(
            root, text="Image Compression Tool",
            font=("Helvetica", 24, "bold"),
            fg="#61AFEF", bg="#282C34"
        )
        self.title_label.pack(pady=20)

        # Upload Button
        self.upload_button = tk.Button(
            root, text="Upload Image", command=self.upload_image,
            font=("Helvetica", 16), bg="#61AFEF", fg="white",
            activebackground="#98C379", activeforeground="white",
            relief="flat", width=20
        )
        self.upload_button.pack(pady=10)

        # Compression Options Button
        self.options_button = tk.Button(
            root, text="Compression Options", command=self.show_options,
            font=("Helvetica", 16), bg="#61AFEF", fg="white",
            activebackground="#98C379", activeforeground="white",
            relief="flat", width=20, state=tk.DISABLED
        )
        self.options_button.pack(pady=10)

        # Image Display Area
        self.image_frame = tk.Frame(root, bg="#21252B", width=600, height=300)
        self.image_frame.pack(pady=20, padx=10)
        self.image_panel = tk.Label(self.image_frame, bg="#21252B")
        self.image_panel.pack()

        # Result Label
        self.result_label = tk.Label(
            root, text="", font=("Helvetica", 14), fg="#E06C75", bg="#282C34"
        )
        self.result_label.pack(pady=20)

        # Dimensions and File Size Label
        self.dimensions_label = tk.Label(
            root, text="", font=("Helvetica", 14), fg="#61AFEF", bg="#282C34"
        )
        self.dimensions_label.pack(pady=10)

        self.original_image = None
        self.image_array = None
        self.huffman_tree = None
        self.encoded_data = None
        self.compressed_image = None
        self.original_file_path = None  # To store the original file path

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.original_file_path = file_path  # Store the original file path
            self.original_image = Image.open(file_path)  # No grayscale conversion
            self.image_array = np.array(self.original_image)

            # Display the uploaded image
            image_thumbnail = self.original_image.copy()
            image_thumbnail.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(image_thumbnail)
            self.image_panel.configure(image=photo)
            self.image_panel.image = photo

            # Display original dimensions and file size
            original_width, original_height = self.original_image.size
            original_size = get_file_size(file_path)
            self.dimensions_label.configure(
                text=f"Original Dimensions: {original_width}x{original_height}\n"
                     f"Original File Size: {original_size}"
            )

            self.options_button.configure(state=tk.NORMAL)
            self.result_label.configure(text="Image uploaded successfully!")

    def show_options(self):
        options_window = tk.Toplevel(self.root)
        options_window.title("Compression Options")
        options_window.geometry("400x300")
        options_window.configure(bg="#282C34")

        tk.Label(
            options_window, text="Select Compression Option:",
            font=("Helvetica", 16), bg="#282C34", fg="#61AFEF"
        ).pack(pady=10)

        # Compression ratio option
        tk.Button(
            options_window, text="Set Compression Ratio", command=self.set_compression_ratio,
            font=("Helvetica", 14), bg="#61AFEF", fg="white",
            relief="flat", width=25
        ).pack(pady=10)

        # Resize option
        tk.Button(
            options_window, text="Set Height and Width", command=self.set_image_size,
            font=("Helvetica", 14), bg="#61AFEF", fg="white",
            relief="flat", width=25
        ).pack(pady=10)

        # Max file size option
        tk.Button(
            options_window, text="Set Max File Size", command=self.set_max_file_size,
            font=("Helvetica", 14), bg="#61AFEF", fg="white",
            relief="flat", width=25
        ).pack(pady=10)

    def set_compression_ratio(self):
        ratio = simpledialog.askstring("Compression Ratio", "Enter desired compression ratio (e.g., 0.5 for 50%):")
        if ratio:
            try:
                ratio = float(ratio)
                if 0 < ratio < 1:
                    self.compress_image(compression_ratio=ratio)
                else:
                    messagebox.showerror("Error", "Compression ratio must be between 0 and 1.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter a number.")

    def set_image_size(self):
        width = simpledialog.askstring("Image Width", "Enter desired width:")
        height = simpledialog.askstring("Image Height", "Enter desired height:")
        if width and height:
            try:
                width = int(width)
                height = int(height)
                if width > 0 and height > 0:
                    self.compress_image(new_size=(width, height))
                else:
                    messagebox.showerror("Error", "Width and height must be positive integers.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter integers.")

    def set_max_file_size(self):
        max_size = simpledialog.askstring("Max File Size", "Enter max file size in KB:")
        if max_size:
            try:
                max_size = int(max_size) * 1024  # Convert KB to bytes
                if max_size > 0:
                    self.compress_image(max_file_size=max_size)
                else:
                    messagebox.showerror("Error", "File size must be a positive integer.")
            except ValueError:
                messagebox.showerror("Error", "Invalid input. Please enter an integer.")

    def compress_image(self, compression_ratio=None, new_size=None, max_file_size=None):
        if compression_ratio:
            new_width = int(self.image_array.shape[1] * compression_ratio)
            new_height = int(self.image_array.shape[0] * compression_ratio)
            resized_image = self.original_image.resize((new_width, new_height))
        elif new_size:
            resized_image = self.original_image.resize(new_size)
        elif max_file_size:
            quality = 95
            resized_image = self.original_image
            while True:
                temp_path = "temp_image.jpg"
                resized_image.save(temp_path, "JPEG", quality=quality)
                if os.path.getsize(temp_path) <= max_file_size or quality <= 10:
                    break
                quality -= 5
            os.remove(temp_path)

        # Store the compressed image
        self.compressed_image = resized_image

        # Display result
        resized_thumbnail = resized_image.copy()
        resized_thumbnail.thumbnail((400, 300))
        photo = ImageTk.PhotoImage(resized_thumbnail)
        self.image_panel.configure(image=photo)
        self.image_panel.image = photo

        # Display original and compressed dimensions and file sizes
        original_width, original_height = self.original_image.size
        compressed_width, compressed_height = resized_image.size

        # Save compressed image temporarily to calculate its size
        temp_path = "temp_compressed_image.jpg"
        resized_image.save(temp_path, "JPEG")
        compressed_size = get_file_size(temp_path)
        os.remove(temp_path)

        original_size = get_file_size(self.original_file_path)

        self.dimensions_label.configure(
            text=f"Original Dimensions: {original_width}x{original_height}\n"
                 f"Original File Size: {original_size}\n"
                 f"Compressed Dimensions: {compressed_width}x{compressed_height}\n"
                 f"Compressed File Size: {compressed_size}"
        )

        # Ask the user if they want to download the compressed image
        self.ask_to_download()

    def ask_to_download(self):
        response = messagebox.askyesno("Download Image", "Do you want to download the compressed image?")
        if response:
            self.download_image()

    def download_image(self):
        if self.compressed_image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg",
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")]
            )
            if file_path:
                self.compressed_image.save(file_path)
                messagebox.showinfo("Success", f"Image saved successfully at {file_path}")
        else:
            messagebox.showerror("Error", "No compressed image available to save.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCompressorApp(root)
    root.mainloop()