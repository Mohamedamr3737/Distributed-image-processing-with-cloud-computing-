import socket
import threading
from imageFunctionsMiddleware import *
from imageProcessingModule import *
from mpi4py import MPI


def main():
    comm=MPI.COMM_WORLD
    rank=comm.Get_rank()
    size = comm.Get_size()
    if rank==0:
        print(size)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '0.0.0.0'
        port = 53
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server listening on {host}:{port}")

        while True:
            client_socket, addr = server_socket.accept()
            operation=client_socket.recv(2).decode('utf-8')
            if operation =="st":
                for i in range(1,size-1):
                    comm.send((operation,None),dest=i)
                for i in range(1,size-1):
                    status=comm.recv(source=i)
                    client_socket.send(status.encode('utf-8'))
                
            else:
                try:
                    imageBytes, _ = receive_image(client_socket)
                
                    # client_thread = threading.Thread(target=sendImageToWorker, args=("localhost",12345,client_socket,imageBytes,operation,addr))
                    # client_thread.start()

                    segments = split_image(size-1, imageBytes) #to split the segment as the number of the worker nodes without the master
                    processed_segments_bytes = []
                    for i,segment in enumerate(segments):
                        comm.send((operation,segment),dest=i+1)
                        
                    for i,segment in enumerate(segments):
                        processed_segment_bytes=comm.recv(source=i+1)
                        display_image_from_bytes(processed_segment_bytes)
                        processed_segments_bytes.append(processed_segment_bytes)
                    combined_image_path = combine_segments_to_bytes(processed_segments_bytes)  
                    display_image_from_bytes(combined_image_path)
                    send_image_segments(client_socket,combined_image_path)
                except TypeError:
                        # Handle the case where receive_image returns None
                        print("Error: Received NoneType object instead of image bytes.")
                        continue
                except ValueError:
                        print("vale error")
                        continue
            # continue
    else:
       while True:
            message,image_bytes=comm.recv(source=0)
            if message == "":
                continue

            elif message=="st":
                comm.send("ok",dest=0)
            elif message=="q":
                print("client disconnected")
                break
            else:
                try:
        
                    if image_bytes is not None:
                        if message == "gr":
                            processed_image_bytes = greyFilter(image_bytes)
                            comm.send(processed_image_bytes,dest=0)
                            display_image_from_bytes(processed_image_bytes)
                        elif message == "ed":
                            edges_bytes = edgeDetection(image_bytes)
                            comm.send(edges_bytes,dest=0)
                            display_image_from_bytes(edges_bytes)
                        elif message == "fl":
                            filtered_image_bytes = imageFiltering(image_bytes)
                            comm.send(filtered_image_bytes,dest=0)
                            display_image_from_bytes(filtered_image_bytes)
                        else:
                            print(f"Unknown message: {message} enter right choice")
                            continue
                except Exception as e:
                    print(f"Error receiving image: {e}")
                    break

if __name__ == "__main__":
    main()