import socket

# Define the target host and port
host = '40.66.43.9'  # '52.168.129.142'
        port = 53 # Port for receiving server status

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect((host, port))

    # Send a message
    message = "Hello, server!"
    client_socket.sendall(message.encode())

    # Receive a response (optional)
    response = client_socket.recv(1024)
    print("Received:", response.decode())

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the socket
    client_socket.close()
