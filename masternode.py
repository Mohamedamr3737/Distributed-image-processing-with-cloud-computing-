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
    print(f"Connection from: {addr}")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_public_ip, port))
    segments = split_image(5, image_bytes)
    processed_segments_bytes = []
    for segment in segments:
        client_socket.send(operation.encode('utf-8'))
        send_image_segments(client_socket, segment)
        processed_segment_bytes, _ = receive_image(client_socket)
        display_image_from_bytes(processed_segment_bytes)
        processed_segments_bytes.append(processed_segment_bytes)
    combined_image_path = combine_segments_to_bytes(processed_segments_bytes)  
    display_image_from_bytes(combined_image_path)
    send_image_segments(clientsockloggedonmaster,combined_image_path)   
    client_socket.close()


if __name__ == "__main__":
    recieveAndSendClient()