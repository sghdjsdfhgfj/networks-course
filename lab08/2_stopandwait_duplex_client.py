import random
from socket import *

timeout = 1
packet_loss = 0.3
packet_size = 16
file_name = "transfer_test.txt"
save_to_file = "received_duplex_client.txt"

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(timeout)



def send(message):
    if random.random() >= packet_loss:
        print(f"Sending message: {message}")
        client_socket.sendto(message.encode(), ("localhost", 8080))
    else:
        print(f"Modeling client-side packet loss for message {message}")

sending = True
last_ack = 1
reading = True

print(f"Sending file {file_name}...")
print(f"Saving to {save_to_file}...")
with open(file_name, "r") as file:
    with open(save_to_file, "w") as save_file:
        contents = file.read(packet_size)
        message_no = 0

        send(f"message {message_no % 2} {contents}")
        while sending or reading:
            try:
                message, _ = client_socket.recvfrom(1024)
                message = message.decode()
                print("Received message:", message)
                if message == f"ack {message_no % 2}":
                    message_no += 1
                    if len(contents) == 0:
                        print("Successfully sent file!")
                        sending = False
                    else:
                        contents = file.read(packet_size)
                        send(f"message {message_no % 2} {contents}")
                elif message.startswith("message "):
                    packet_no = int(message.split(' ')[1])
                    if packet_no != last_ack:
                        last_ack = packet_no
                        packet_contents = message.split(' ', 2)[2]
                        if len(packet_contents) == 0:
                            print("Received empty packet; considering EOF")
                            reading = False
                        save_file.write(packet_contents)
                    else:
                        print("Duplicate message; not writing to file")
                    send(f"ack {packet_no}")
            except TimeoutError:
                print("Request timed out")
                if sending:
                    send(f"message {message_no % 2} {contents}")