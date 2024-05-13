import socket

# Server address and port
server_address = ('4.211.180.220', 53)  # Replace with the actual server address and port

# Message to send
message = "Hello, server!"

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect(server_address)

# Send the message
client_socket.sendall(message.encode())

# Receive response from the server


# Close the socket
client_socket.close()
