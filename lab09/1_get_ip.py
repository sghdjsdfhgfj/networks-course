import subprocess

ipconfig_output = subprocess.check_output(["ipconfig"]).decode()

lines = [x.strip() for x in ipconfig_output.split("\n")]
ip, mask = None, None
for line in lines:
    if line.startswith("IPv4 Address"):
        ip = line.split(":")[1].strip()
    if line.startswith("Subnet Mask"):
        mask = line.split(":")[1].strip()
print("IPv4 Address:", ip)
print("Subnet Mask:", mask)