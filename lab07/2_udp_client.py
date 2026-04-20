from datetime import datetime
from socket import *
import time

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(1)

for message_no in range(1, 11):
    message = f"Ping {message_no} {datetime.now().strftime('%H:%M:%S')}"
    print(f"Sending message: {message}")
    start = time.time()
    client_socket.sendto(message.encode(), ("localhost", 8080))
    try:
        response_message, _ = client_socket.recvfrom(1024)
        end = time.time()
        print("Received message:", response_message.decode())
        print("RTT:", end - start, "s")
    except TimeoutError:
        print("Request timed out")
    print()
    time.sleep(1)
    message_no += 1