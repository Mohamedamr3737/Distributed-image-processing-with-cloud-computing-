import socket
import threading
from imageFunctionsMiddleware import *
from imageProcessingModule import *
# from db import *
import urllib.request
import json
from datetime import datetime
def handle_client(client_socket, addr):
    print(f"Connection from: {addr}")
    while True:
        try:
            message=client_socket.recv(2).decode('utf-8')
            if message == "":
                continue

            elif message=="st":
                client_socket.send("ok".encode('utf-8'))
                client_socket.close()

            else:
                try:
                    image_bytes,length = receive_image(client_socket)
                    
                    if image_bytes is not None:
                        if message == "gr":
                            processed_image_bytes = greyFilter(image_bytes)
                            send_image_knownbytes(client_socket, (processed_image_bytes, len(processed_image_bytes)))
                            client_socket.close()
                        elif message == "ed":
                            edges_bytes = edgeDetection(image_bytes)
                            send_image_knownbytes(client_socket, (edges_bytes, len(edges_bytes)))
                            client_socket.close()
                        elif message == "fl":
                            filtered_image_bytes = imageFiltering(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "bl":
                            filtered_image_bytes = gaussian_blur(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "sk":
                            filtered_image_bytes = laplacian(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "iv":
                            filtered_image_bytes = invert_colors(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "bc":
                            filtered_image_bytes = adjust_brightness_contrast(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "rf":
                            filtered_image_bytes = apply_red_filter(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "bf":
                            filtered_image_bytes = apply_blue_filter(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "gf":
                            filtered_image_bytes = apply_green_filter(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "cc":
                            filtered_image_bytes = convert_color_space(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        elif message == "hm":
                            filtered_image_bytes = apply_heat_filter(image_bytes)
                            send_image_knownbytes(client_socket, (filtered_image_bytes, len(filtered_image_bytes)))
                            client_socket.close()
                        else:
                            print(f"Unknown message: {message} enter right choice")
                            continue
                except Exception as e:
                    print(f"Error receiving image: {e}")
                    # insert_log(f"worker {get_public_ip()} closed {e}  {datetime.now()}")
                    break
        except Exception as error:
            # insert_log(f"worker {get_public_ip()} closed {error}  {datetime.now()}")
            client_socket.close()
        


def get_public_ip():
    try:
        response = urllib.request.urlopen('http://httpbin.org/ip')
        data = json.loads(response.read().decode())
        ip_address = data['origin']
        return ip_address
    except Exception as e:
        print("Error getting public IP:", e)
        return None
    

def main():
    # insert_log(f"{get_public_ip()} worker started {datetime.now()}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host ='0.0.0.0'
    port =53
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    
    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        # client_thread.daemon=True
        client_thread.start()
    
if __name__ == "__main__":
    main()
