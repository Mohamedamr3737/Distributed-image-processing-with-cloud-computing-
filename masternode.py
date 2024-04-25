import socket
import threading
from imageFunctionsMiddleware import *

def recieveAndSendClient():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12348
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        operation=client_socket.recv(2).decode('utf-8')
        imageBytes,_=receive_image(client_socket)
        client_thread = threading.Thread(target=sendImageToWorker, args=("localhost",12345,client_socket,imageBytes,operation,addr))
        client_thread.start()


def sendImageToWorker(server_public_ip,port,clientsockloggedonmaster,image_bytes,operation,addr):
# Create a socket object
    print(f"Connection from: {addr}")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Replace 'server_public_ip' with the public IP of the server

    # Connect to the server
    client_socket.connect((server_public_ip, port))

    # # Send the image
    # image_path = "depositphotos_49418809-stock-photo-frog-on-the-leaf.jpg"  # Replace with the actual image path
    # # Open the image file and read its bytes
    # with open(image_path, 'rb') as f:
    #         image_bytes = f.read()

    # operation=input("enter the operation gr for grey fl for filter ed for edge: ")
    segments = split_image(5, image_bytes)
    processed_segments_bytes = []
    for segment in segments:
        client_socket.send(operation.encode('utf-8'))
        send_image_segments(client_socket, segment)
        processed_segment_bytes, _ = receive_image(client_socket)
        display_image_from_bytes(processed_segment_bytes)
        processed_segments_bytes.append(processed_segment_bytes)
    # Concatenate all processed segments to form the processed image
    combined_image_path = combine_segments_to_bytes(processed_segments_bytes)
    
    display_image_from_bytes(combined_image_path)
    send_image_segments(clientsockloggedonmaster,combined_image_path)   
    # Close the connection with the server
    client_socket.close()



if __name__ == "__main__":
    recieveAndSendClient()