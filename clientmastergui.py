import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import io
import socket
import numpy as np
import threading
import time
import json
import sys
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
        label_frame = tk.Frame(self.scrollable_frame)
        label = tk.Label(label_frame, image=photo)
        label.image = photo
        label.pack(pady=5, side="top")
        download_button = tk.Button(label_frame, text="Download", command=lambda: self.save_image(image))
        download_button.pack(side="bottom")
        label_frame.pack(pady=5, padx=5)

    def save_image(self, image):
        default_filename="image.png"
        file_path = filedialog.asksaveasfilename(defaultextension=".png",initialfile=default_filename, filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if file_path:
            image.save(file_path)

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("550x550") 
        self.root.pack_propagate(True) 
        self.image_bytes = None
        self.image_label = tk.Label(root)
        self.option_var = tk.StringVar()
        self.option_var.set("grey filter")
        self.imgPath=None
        self.uploaded_images = []
        self.upload_button = tk.Button(root, text="Upload Photo", command=self.upload_image)
        self.option_menu = tk.OptionMenu(root, self.option_var, "grey filter", "edge detection", "color sharpening","blur","sketch","invert colors","brightness contrast","red filter","blue filter","green filter","convert color","heat map")
        self.convert_button = tk.Button(root, text="Convert", command=self.convert_image_thread)
        self.upload_button.pack()
        self.option_menu.pack()
        self.convert_button.pack()
        self.image_label.pack()
        self.scrollable_frame = ScrollableImageFrame(root)
        self.scrollable_frame.pack(side="top", fill="both", expand=True)
        self.success_fail_label = tk.Label(root, text="", fg="green") 
        self.success_fail_label.pack()  
        self.masters_label = tk.Label(root, text="Masters Status: Unknown")
        self.masters_label.pack() 
        self.server_status_label = tk.Label(root, text="workers Status: Unknown")
        self.server_status_label.pack()
        self.masters=[("51.120.112.111",53),("4.232.128.42",53)]
        self.workingmasterslists=[]
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.root.destroy()
        sys.exit(0)

    def upload_image(self):
        self.uploaded_images = []
        file_types = [("Image Files", "*.jpg; *.jpeg; *.png; *.gif; *.bmp")]
        file_paths = filedialog.askopenfilenames(filetypes=file_types)
        
        if file_paths:
            for file_path in file_paths:
                image = Image.open(file_path)
                self.uploaded_images.append(file_path)
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
        with open(imagePath, 'rb') as f:
            image_bytes = f.read()
        
        if imagePath.lower().endswith('.png'):
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            output = io.BytesIO()
            image.save(output, format='JPEG')
            image_bytes = output.getvalue()
        conn.sendall(len(image_bytes).to_bytes(4, byteorder='big'))
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
        thread=threading.Thread(target=self.convert_image)
        thread.daemon = True  
        thread.start()


    def receive_list_from_socket(self,client_socket):
        buffer_size_str = client_socket.recv(1024).decode('utf-8')
        buffer_size = int(buffer_size_str)
        client_socket.send(b'OK')  # Send acknowledgment
        received_data = b''
        while len(received_data) < buffer_size:
            received_data += client_socket.recv(min(buffer_size - len(received_data), 1024))
        return json.loads(received_data.decode('utf-8'))


    def receive_server_status(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip,por=self.workingmasterslists[0]
        try:
            client_socket.connect((ip, por))
            client_socket.send("st".encode('utf-8'))
            message = self.receive_list_from_socket(client_socket)
            print(message)
            if message=="ok":
                return "active"
            elif message=="no":
                return "error"
            return message
        except Exception as E:
            print("Connection to server failed.")
            return "Error in Master Node"
        
    def monitor_server_status_thread(self):
        thread=threading.Thread(target=self.monitor_server_status)
        thread.daemon = True
        thread.start()

    def monitor_server_status(self):
        while True:
            try:
                status = self.receive_server_status()
                self.server_status_label.config(text=f"Available workers ({len(status)}): {status}")
                
                time.sleep(1)  
            except Exception as E:
                print(E)
                continue

    def monitormaster(self,server_public_ip, port):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_public_ip, port))
            client_socket.send("mc".encode('utf-8'))
            message = client_socket.recv(2).decode('utf-8')
            if message == "ok":
                print("master is still alive")
                return message
            else:
                print("master is dead")
        except ConnectionRefusedError:
            return "no"
        

    def chechWorkingmasters(self):
        
        while True:
            try:
                for i,master in enumerate(self.masters):
                    ip,ports=master
                    message=self.monitormaster(ip,ports)
                    if message == "ok":
                        if master not in self.workingmasterslists:
                                self.workingmasterslists.append(master)
                    else:
                        if master in self.workingmasterslists:
                            self.workingmasterslists.remove(master)
                self.masters_label.config(text=f"Available Masters ({len(self.workingmasterslists)}): {self.workingmasterslists}")
                
                time.sleep(1)
            except Exception as e:
                print(e)
                continue
    
    def monitor_masters_thread(self):
        thread=threading.Thread(target=self.chechWorkingmasters)
        thread.daemon = True  # Make the thread a daemon thread
        thread.start()

    def convert_image(self):
        processedImages=[]
        path=self.imgPath
        option = self.option_var.get()
        if option=="grey filter":
            option="gr"
        elif option=="edge detection":
            option="ed"
        elif option=="color sharpening":
            option="fl"
        elif option=="blur":
            option="bl"
        elif option=="sketch":
            option="sk"
        elif option=="invert colors":
            option="iv"
        elif option=="brightness contrast":
            option="bc"
        elif option=="red filter":
            option="rf"
        elif option=="blue filter":
            option="bf"
        elif option=="green filter":
            option="gf"
        elif option=="convert color":
            option="cc"
        elif option=="heat map":
            option="hm"
        
        
        sockets=[]
        
        print(self.uploaded_images)
        for path in self.uploaded_images:
         
            ip,por=self.workingmasterslists[0]
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, por)) 
            client_socket.send(option.encode('utf-8'))
            self.send_image(client_socket,path)
            sockets.append(client_socket)
        try:
            for client_socket in sockets:   
                imageBytes,_=self.receive_image(client_socket)
                imageBytes=self.bytes_to_image(imageBytes)
                processedImages.append(imageBytes)
                self.success_fail_label.config(text="Conversion successful", fg="green")
        except Exception as E:
            self.success_fail_label.config(text="Conversion failed, Try again", fg="red")
        for x in processedImages:
            self.scrollable_frame.add_image(x)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    app.monitor_masters_thread()
    time.sleep(4) #this delay is to wait for the system to get the working masters
    app.monitor_server_status_thread()
    root.mainloop()
