def checksum(msg):
    sum = 0
    for i in range(0, len(msg), 2):
        sum += 0x100 * msg[i]
        if i + 1 < len(msg):
            sum += msg[i + 1]
        sum %= 0x10000
    return 0xFFFF - sum

def verify(msg, c):
    return checksum(msg) == c

# normal scenario
message = b"Hello World"
c = checksum(message)
assert verify(message, c)

# corruption in message
corrupted_message = bytes([message[0] ^ 32]) + message[1:]
assert not verify(corrupted_message, c)

# corruption in checksum
corrupted_c = c ^ 32
assert not verify(message, corrupted_c)