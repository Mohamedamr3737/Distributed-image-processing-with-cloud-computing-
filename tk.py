import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import io
import socket
from PIL import UnidentifiedImageError
import numpy as np
import threading


class ScrollableImageFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def add_image(self, image, max_width=300, max_height=300):
        # Resize the image
        width, height = image.size
        aspect_ratio = width / height
        if width > max_width or height > max_height:
            if aspect_ratio > 1:
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            image = image.resize((new_width, new_height))

        # Convert the image to PhotoImage
        photo = ImageTk.PhotoImage(image)

        # Create and pack the label with the image
        label = tk.Label(self.scrollable_frame, image=photo)
        label.image = photo
        label.pack(pady=5)


class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        # Set window size
        self.root.geometry("500x400") 
        self.root.pack_propagate(True) 
        # Variables
        self.image_bytes = None
        self.image_label = tk.Label(root)
        self.option_var = tk.StringVar()
        self.option_var.set("gr")

        # Widgets
        self.upload_button = tk.Button(root, text="Upload Photo", command=self.upload_image)
        self.option_menu = tk.OptionMenu(root, self.option_var, "grey", "edge", "filter")
        self.convert_button = tk.Button(root, text="Convert", command=self.convert_image_thread)

        # Layout
        self.upload_button.pack()
        self.option_menu.pack()
        self.convert_button.pack()
        self.image_label.pack()

        # Initialize scrollable frame
        self.scrollable_frame = ScrollableImageFrame(root)
        self.scrollable_frame.pack(side="top", fill="both", expand=True)

    def split_image(self,num_segments, image_bytes):
        img = np.array(Image.open(io.BytesIO(image_bytes)))
        height, width, _ = img.shape
        segment_height = height // num_segments
        segments = []
        for i in range(num_segments):
            start = i * segment_height
            end = start + segment_height
            if i == num_segments - 1:
                end = height
            segment = img[start:end, :, :]
            
            # Convert segment to bytes
            segment_bytes = io.BytesIO()
            Image.fromarray(segment).save(segment_bytes, format='JPEG')
            segment_bytes.seek(0)
            
            segments.append(segment_bytes.read())
        return segments
    
    def send_image_segments(self,conn, image_bytes):
        # print(image_bytes)
        # Send the length of the image first
        conn.sendall(len(image_bytes).to_bytes(4, byteorder='big'))
        # Send the image bytes
        conn.sendall(image_bytes)
    
    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            # self.display_image(image)
            self.scrollable_frame.add_image(image)
            self.image_bytes = self.convert_to_bytes(image)

    def resize_photo(self, photo, width, height):
        # Resize the photo and return the resized copy
        return photo.subsample(int(photo.width() / width), int(photo.height() / height))


    def convert_to_bytes(self, image):
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format=image.format)
        return img_byte_array.getvalue()
    
    def display_image_from_bytes(self,image_bytes):
        # Create a BytesIO object to read the image bytes
        image_stream = io.BytesIO(image_bytes)
        # Open the image using PIL (Python Imaging Library)
        image = Image.open(image_stream)
        # Display the image
        image.show()


    def bytes_to_image(self,image_bytes):
        # Create a BytesIO object to read the image bytes
        image_stream = io.BytesIO(image_bytes)
        # Open the image using PIL (Python Imaging Library)
        image = Image.open(image_stream)
        return image

    def combine_segments_to_bytes(self,segments):
    # Read the first segment to get the image dimensions
        first_segment = Image.open(io.BytesIO(segments[0]))
        width, height = first_segment.size
        
        # Create a new image with the same dimensions
        combined_image = Image.new("RGB", (width, height * len(segments)))
        
        # Paste each segment onto the combined image
        for i, segment_bytes in enumerate(segments):
            segment = Image.open(io.BytesIO(segment_bytes))
            combined_image.paste(segment, (0, i * height))
        
        # Save the combined image to a BytesIO object
        combined_image_bytes = io.BytesIO()
        combined_image.save(combined_image_bytes, format='JPEG')
        combined_image_bytes.seek(0)
        
        return combined_image_bytes.read()
    
    def receive_image(self,conn):
        # Receive the length of the image
        length = int.from_bytes(conn.recv(4), byteorder='big')
        if length !=0:
            # Receive the image bytes
            image_bytes = b''
            while len(image_bytes) < length:
                data = conn.recv(length - len(image_bytes))
                if not data:
                    break
                image_bytes += data
            return image_bytes,length

    def convert_image_thread(self):
        # Create a new thread for the conversion process
        threading.Thread(target=self.convert_image).start()

    def convert_image(self):
        processedImages=[]
        if self.image_bytes:
            image = Image.open(io.BytesIO(self.image_bytes))
            option = self.option_var.get()
            if option=="grey":
                option="gr"
            elif option=="edge":
                option="ed"
            elif option=="filter":
                option="fl"

            # self.display_image(image)
            # self.scrollable_frame.add_image(image)
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Replace 'server_public_ip' with the public IP of the server
            server_public_ip = 'localhost'
            port = 12345
            # Connect to the server
            client_socket.connect((server_public_ip, port))
            
            if self.image_bytes is not None:
                segments = self.split_image(3, self.image_bytes)
                processed_segments_bytes = []
                for segment in segments:
                    client_socket.send(option.encode('utf-8'))
                    self.send_image_segments(client_socket, segment)
                    try:
                        processed_segment_bytes, _ = self.receive_image(client_socket)
                    except TypeError as e:
                        print(e)
                    
                    try:
                        self.display_image_from_bytes(processed_segment_bytes)
                    except UnboundLocalError as e:
                        print(e)
                    processed_segments_bytes.append(processed_segment_bytes)
                # Concatenate all processed segments to form the processed image
                combined_image_path = self.combine_segments_to_bytes(processed_segments_bytes)
                self.display_image_from_bytes(combined_image_path)
                combined_image_path=self.bytes_to_image(combined_image_path)
                processedImages.append(combined_image_path)
                for x in processedImages:
                    # self.display_image(x)
                    self.scrollable_frame.add_image(x)

    # Methods for sending and receiving images...

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()
