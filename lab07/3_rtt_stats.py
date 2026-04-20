from datetime import datetime
from socket import *
import time

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(1)

rtts = []
losses = 0

for message_no in range(1, 11):
    message = f"Ping {message_no} {datetime.now().strftime('%H:%M:%S')}"
    print(f"Sending message: {message}")
    start = time.time()
    client_socket.sendto(message.encode(), ("localhost", 8080))
    try:
        response_message, _ = client_socket.recvfrom(1024)
        end = time.time()
        rtts.append(end - start)

        print("Received message:", response_message.decode())
    except TimeoutError:
        print("Request timed out")
        losses += 1

    if len(rtts) > 0:
        min_rtt = round(min(rtts) * 1000)
        max_rtt = round(max(rtts) * 1000)
        avg_rtt = round(max(rtts) * 1000)
        loss_pct = round(losses / message_no * 100)
        print(f"""Ping statistics:
        Packets: Sent = {message_no}, Received = {message_no - losses}, Lost = {losses} ({loss_pct}% loss),
    Approximate round trip times in milli-seconds:
        Minimum = {min_rtt}ms, Maximum = {max_rtt}ms, Average = {avg_rtt}ms""")
    print()
    time.sleep(1)
    message_no += 1