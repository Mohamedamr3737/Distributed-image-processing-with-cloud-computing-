import socket
import threading
import json
from imageFunctionsMiddleware import *
# from db import *
from datetime import datetime
import urllib.request
workerslist=[('40.82.152.147',53),('20.215.232.32',53),('20.28.42.106',53)]
print(len(workerslist))

def send_list_over_socket(client_socket, data):
    try:
        serialized_data = json.dumps(data)
        buffer_size = len(serialized_data)
        client_socket.send(str(buffer_size).encode('utf-8'))
        client_socket.recv(2)  
        client_socket.sendall(serialized_data.encode('utf-8'))
    except Exception as e:
        print(e)


def monitorWorker(server_public_ip, port, clientsockloggedonmaster,i):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_public_ip, port))
        client_socket.send("st".encode('utf-8'))
        message = client_socket.recv(2).decode('utf-8')
        if message == "ok":
            print("Worker is still alive")
        else:
            print("Worker is dead")
    except ConnectionRefusedError:
        print("Connection to worker failed. Worker might be down.")
    

def monitorWorker2(server_public_ip, port):
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

def chechWorkinworkers(workerslist):
    workingWorkerlists=[]
    for i,worker in enumerate(workerslist):
        ip,ports=worker
        try:
            message=monitorWorker2(ip,ports)
            if message == "ok":
                # insert_log(f"{worker} is still alive {datetime.now()}")  # Log message to database
                if worker not in workingWorkerlists:
                        workingWorkerlists.append(worker)
            else:
                # insert_log(f"{worker} is dead {datetime.now()} ") 
                if worker in workingWorkerlists:  
                    workingWorkerlists.remove(worker)
        except Exception as e:
            print(e)
    return workingWorkerlists

def recieveAndSendClient():
    # insert_log(f"{get_public_ip()} worker started {datetime.now()}")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host ='0.0.0.0'
    port = 53
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    workingWorkerlistscheckst=chechWorkinworkers(workerslist)
    while True:
        client_socket, addr = server_socket.accept()
        try:
            operation=client_socket.recv(2).decode('utf-8')
        except Exception as e:
            print(e)
        if operation =="st":
            workingWorkerlistscheckst=chechWorkinworkers(workerslist)
            try:
                send_list_over_socket(client_socket,workingWorkerlistscheckst)
            except  Exception as E:
                print(E)
        elif operation=="mc":#master check
            client_socket.send("ok".encode('utf-8')) 
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
        # display_image_from_bytes(processed_segment_bytes)
        processed_segments_bytes.append(processed_segment_bytes)
    if len(processed_segments_bytes)==len(segments):
        combined_image_path = combine_segments_to_bytes(processed_segments_bytes)  
        # display_image_from_bytes(combined_image_path)
        send_image_segments(clientsockloggedonmaster,combined_image_path)   
    else:
        sendImageToWorker(clientsockloggedonmaster,image_bytes,operation,addr)#recursion to check if segment is failed its processes the image again
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
    
if __name__ == "__main__":
    recieveAndSendClient()