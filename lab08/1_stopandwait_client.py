import random
from socket import *

timeout = 1
packet_loss = 0.3
packet_size = 8
file_name = "transfer_test.txt"

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(timeout)

print(f"Sending file {file_name}...")
with open(file_name, "r") as file:
    contents = file.read(packet_size)
    message_no = 0
    while True:
        message = f"message {message_no % 2} {contents}"
        if random.random() >= packet_loss:
            print(f"Sending message: {message}")
            client_socket.sendto(message.encode(), ("localhost", 8080))
        else:
            print(f"Modeling client-side packet loss for message {message}")

        try:
            while True:
                response_message, _ = client_socket.recvfrom(1024)
                if response_message == b"ack " + str(message_no % 2).encode():
                    print("Received acknowledgement")
                    message_no += 1
                    if len(contents) == 0:
                        print("Successfully sent file!")
                        exit(0)
                    contents = file.read(packet_size)
                    break
                else:
                    print(f"Received unexpected message: {response_message.decode()}")
        except TimeoutError:
            print("Request timed out")