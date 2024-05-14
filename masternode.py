import socket
import threading
import json
from imageFunctionsMiddleware import *

workerslist=[('localhost',12345),('localhost',12349),('localhost',12333)]
print(len(workerslist))

def send_list_over_socket(client_socket, data):
    serialized_data = json.dumps(data)
    buffer_size = len(serialized_data)
    client_socket.send(str(buffer_size).encode('utf-8'))  # Send buffer size first
    client_socket.recv(2)  # Wait for acknowledgment
    client_socket.sendall(serialized_data.encode('utf-8'))


def monitorWorker(server_public_ip, port, clientsockloggedonmaster,i):
# while True:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_public_ip, port))
        client_socket.send("st".encode('utf-8'))
        message = client_socket.recv(2).decode('utf-8')
        if message == "ok":
            # clientsockloggedonmaster.send(("ok").encode('utf-8'))
            print("Worker is still alive")
        else:
            print("Worker is dead")
    except ConnectionRefusedError:
        # clientsockloggedonmaster.send(("no").encode('utf-8'))
        print("Connection to worker failed. Worker might be down.")
    

def monitorWorker2(server_public_ip, port):
# while True:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_public_ip, port))
        client_socket.send("st".encode('utf-8'))
        message = client_socket.recv(2).decode('utf-8')
        if message == "ok":

            print("Worker is still alive")
            return message
        else:
            print("Worker is dead")
    except ConnectionRefusedError:
        return "no"
        print("Connection to worker failed. Worker might be down.")
    # time.sleep(5)  # Adjust sleep time as needed

def chechWorkinworkers(workerslist):
    workingWorkerlists=[]
    for i,worker in enumerate(workerslist):
        ip,ports=worker
        message=monitorWorker2(ip,ports)
        if message == "ok":
            if worker not in workingWorkerlists:
                    workingWorkerlists.append(worker)
            else:
                if worker in workingWorkerlists:
                    workingWorkerlists.remove(worker)
    return workingWorkerlists

def recieveAndSendClient():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'localhost'
    port = 12348
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    workingWorkerlistscheckst=chechWorkinworkers(workerslist)
    while True:
        client_socket, addr = server_socket.accept()
        # for i,worker in enumerate(workerslist):
        #     ip,ports=worker
        #     message=monitorWorker2(ip,ports)
        #     if message=="ok":
        #         if worker not in workingWorkerlistscheckst:
        #             workingWorkerlistscheckst.append(worker)
        #     else:
        #         if worker in workingWorkerlistscheckst:
        #             workingWorkerlistscheckst.remove(worker)#check only
        operation=client_socket.recv(2).decode('utf-8')
        if operation =="st":
            # for i,worker in enumerate(workingWorkerlistscheckst):
            #     ip,port=worker
            #     monitorWorker(ip,port,client_socket,i)
            workingWorkerlistscheckst=chechWorkinworkers(workerslist)
            send_list_over_socket(client_socket,workingWorkerlistscheckst)
        else:
            imageBytes,_=receive_image(client_socket)
            client_thread = threading.Thread(target=sendImageToWorker, args=(client_socket,imageBytes,operation,addr))
            client_thread.start()


def sendImageToWorker(clientsockloggedonmaster,image_bytes,operation,addr):
    print(f"Connection from: {addr}")
    workingworkers=chechWorkinworkers(workerslist)
    segments = split_image(len(workingworkers), image_bytes)
    clientsockets=[]
    processed_segments_bytes = []
    for i,worker in enumerate(workingworkers):
        ip,ports=worker
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((ip, ports))
            client_socket.send(operation.encode('utf-8'))
            send_image_segments(client_socket, segments[i])
            clientsockets.append(client_socket)
        except:
            sendImageToWorker(clientsockloggedonmaster,image_bytes,operation,addr)#recursion to check if segment is failed its processes the image again

    for socketi in clientsockets:
        processed_segment_bytes, _ = receive_image(socketi)
        display_image_from_bytes(processed_segment_bytes)
        processed_segments_bytes.append(processed_segment_bytes)
    if len(processed_segments_bytes)==len(segments):
        combined_image_path = combine_segments_to_bytes(processed_segments_bytes)  
        display_image_from_bytes(combined_image_path)
        send_image_segments(clientsockloggedonmaster,combined_image_path)   
    else:
        sendImageToWorker(clientsockloggedonmaster,image_bytes,operation,addr)#recursion to check if segment is failed its processes the image again
    client_socket.close()


if __name__ == "__main__":
    recieveAndSendClient()