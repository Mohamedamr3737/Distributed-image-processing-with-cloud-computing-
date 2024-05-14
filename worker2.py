import socket
import threading
from imageFunctionsMiddleware import *
from imageProcessingModule import *

def handle_client(client_socket, addr):
    print(f"Connection from: {addr}")
    while True:
        message=client_socket.recv(2).decode('utf-8')
        if message == "":
            continue

        elif message=="st":
            client_socket.send("ok".encode('utf-8'))
            
        elif message=="q":
            print("client disconnected")
            break
        else:
            try:
                image_bytes,length = receive_image(client_socket)
                
                if image_bytes is not None:
                    if message == "gr":
                        processed_image_bytes = greyFilter(image_bytes)
                        send_image_knownbytes(client_socket, (processed_image_bytes, len(processed_image_bytes)))
                    elif message == "ed":
                        edges_bytes = edgeDetection(image_bytes)
                        send_image_knownbytes(client_socket, (edges_bytes, len(edges_bytes)))
                    elif message == "fl":
                        filtered_image_bytes = imageFiltering(image_bytes)
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
    port = 12349
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    main()
