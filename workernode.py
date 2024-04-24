import socket
import threading
import os
import io
from PIL import Image
import cv2
import numpy as np
def send_image_knownbytes(conn, image):
    image_bytes = image[1] 
    # print(image_bytes)
    # Send the length of the image first
    conn.sendall(image_bytes.to_bytes(4, byteorder='big'))
    # Send the image bytes
    conn.sendall(image[0])


def display_image_from_bytes(image_bytes):
    # Create a BytesIO object to read the image bytes
    image_stream = io.BytesIO(image_bytes)
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_stream)
    # Display the image
    image.show()


def receive_image(conn):
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



def handle_client(client_socket, addr):
    print(f"Connection from: {addr}")
    while True:
        message=client_socket.recv(2).decode('utf-8')
        if message == "":
            continue
        elif message=="q":
            print("client disconnected")
            break
        else:
            try:
                image_bytes,length = receive_image(client_socket)
                
                if image_bytes is not None:
                    if message == "gr":
                        # display_image_from_bytes(image_bytes)
                        # send_image_knownbytes(client_socket,(image_bytes,length))
                        # Perform image processing
                        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
                        # Example: Convert image to grayscale
                        processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        # Optionally, send the processed image back to the client
                        # convert processed image back to bytes
                        processed_image_bytes = cv2.imencode('.jpg', processed_image)[1].tobytes()
                        # send processed image
                        send_image_knownbytes(client_socket, (processed_image_bytes, len(processed_image_bytes)))
                    elif message == "ed":
                        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
                        # Convert image to grayscale
                        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        # Perform Canny edge detection
                        edges = cv2.Canny(gray_image, 100, 200)  # Adjust the threshold values as needed
                        # Display the detected edges
                        # Optionally, send the detected edges back to the client
                        # Convert edges to bytes
                        edges_bytes = cv2.imencode('.jpg', edges)[1].tobytes()
                        # Send detected edges
                        send_image_knownbytes(client_socket, (edges_bytes, len(edges_bytes)))
                    elif message == "fl":
                        # Perform image filtering
                        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
                        
                        # Apply Gaussian blur
                        blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
                        
                        # Apply sharpening filter
                        kernel_sharpening = np.array([[-1, -1, -1],
                                                    [-1, 9, -1],
                                                    [-1, -1, -1]])
                        sharpened_image = cv2.filter2D(blurred_image, -1, kernel_sharpening)
                        # Optionally, send the filtered image back to the client
                        # Convert filtered image to bytes
                        filtered_image_bytes = cv2.imencode('.jpg', sharpened_image)[1].tobytes()
                        # Send filtered image
                        send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                    else:
                        print(f"Unknown message: {message} enter right choice")
                        continue
            except Exception as e:
                print(f"Error receiving image: {e}")
                break
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12345
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
