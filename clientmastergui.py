import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import io
import socket
import numpy as np
import threading
import time

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
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(self.scrollable_frame, image=photo)
        label.image = photo
        label.pack(pady=5)


class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("500x400") 
        self.root.pack_propagate(True) 
        self.image_bytes = None
        self.image_label = tk.Label(root)
        self.option_var = tk.StringVar()
        self.option_var.set("grey filter")
        self.imgPath=None
        self.upload_button = tk.Button(root, text="Upload Photo", command=self.upload_image)
        self.option_menu = tk.OptionMenu(root, self.option_var, "grey filter", "edge detection", "color manipulation")
        self.convert_button = tk.Button(root, text="Convert", command=self.convert_image_thread)
        self.upload_button.pack()
        self.option_menu.pack()
        self.convert_button.pack()
        self.image_label.pack()
        self.scrollable_frame = ScrollableImageFrame(root)
        self.scrollable_frame.pack(side="top", fill="both", expand=True)
        self.server_status_label = tk.Label(root, text="Server Status: Unknown")
        self.server_status_label.pack()
    

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            image = Image.open(file_path)
            self.imgPath=file_path
            self.scrollable_frame.add_image(image)


    def resize_photo(self, photo, width, height):
        return photo.subsample(int(photo.width() / width), int(photo.height() / height))


    def convert_to_bytes(self, image):
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format=image.format)
        return img_byte_array.getvalue()
    

    def bytes_to_image(self,image_bytes):
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream)
        return image
    

    def send_image(self, conn, imagePath):
        # Open the image
        with open(imagePath, 'rb') as f:
            image_bytes = f.read()
        
        # Check if the image is a PNG
        if imagePath.lower().endswith('.png'):
            # Convert PNG to RGB mode
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            # Create a BytesIO object to hold the JPEG data
            output = io.BytesIO()
            # Save the image as JPEG to the BytesIO object
            image.save(output, format='JPEG')
            # Get the JPEG bytes
            image_bytes = output.getvalue()
        
        # Send the image size
        conn.sendall(len(image_bytes).to_bytes(4, byteorder='big'))
        # Send the image bytes
        conn.sendall(image_bytes)

    def receive_image(self,conn):
        length = int.from_bytes(conn.recv(4), byteorder='big')
        if length !=0:
            image_bytes = b''
            while len(image_bytes) < length:
                data = conn.recv(length - len(image_bytes))
                if not data:
                    break
                image_bytes += data
            return image_bytes,length


    def display_image_from_bytes(self,image_bytes):
        image_stream = io.BytesIO(image_bytes)
        image = Image.open(image_stream)
        image.show()

    def convert_image_thread(self):
        threading.Thread(target=self.convert_image).start()

    def receive_server_status(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_public_ip = '4.211.180.220'  # '52.168.129.142'
        port = 53  # Port for receiving server status
        try:
            client_socket.connect((server_public_ip, port))
            client_socket.send("st".encode('utf-8'))
            message = client_socket.recv(2).decode('utf-8')
            if message=="ok":
                return "active"
            elif message=="no":
                return "error"
            return message
        except ConnectionRefusedError:
            print("Connection to server failed.")
            return "Error in Master Node"
        
    def monitor_server_status_thread(self):
        threading.Thread(target=self.monitor_server_status).start()

    def monitor_server_status(self):
        while True:
            status = self.receive_server_status()
            self.server_status_label.config(text=f"Server Status: {status}")
            if status == "active":
                self.server_status_label.config(fg="green")
            else:
                self.server_status_label.config(fg="red")
            # Update label with server status
            
            time.sleep(1)  # Adjust the sleep time as needed


    def convert_image(self):
        processedImages=[]
        path=self.imgPath
        option = self.option_var.get()
        if option=="grey filter":
            option="gr"
        elif option=="edge detection":
            option="ed"
        elif option=="color manipulation":
            option="fl"
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_public_ip ='4.211.180.220'  #'52.168.129.142'
        port = 53 #53
        client_socket.connect((server_public_ip, port))
        client_socket.send(option.encode('utf-8'))
        self.send_image(client_socket,path)
        imageBytes,_=self.receive_image(client_socket)
        imageBytes=self.bytes_to_image(imageBytes)
        processedImages.append(imageBytes)
        for x in processedImages:
            self.scrollable_frame.add_image(x)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    app.monitor_server_status_thread()
    root.mainloop()
