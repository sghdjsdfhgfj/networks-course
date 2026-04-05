from email.message import EmailMessage
from smtplib import SMTP_SSL
from sys import argv

host_name = "smtp.gmail.com"
sender = "reas.qf0@gmail.com"
with open("password.txt") as f:
    password = f.read().strip()

recipient = argv[1]
contents_file = argv[2]

message = EmailMessage()
if contents_file.endswith(".txt"):
    with open(contents_file, "r") as f:
        message.set_content(f.read())
elif contents_file.endswith(".html"):
    with open(contents_file, "r") as f:
        message.set_content(f.read(), subtype="html")
else:
    print('input file should be a txt or html file')
    exit(1)

with SMTP_SSL(host_name) as smtp:
    smtp.set_debuglevel(1)
    smtp.login(sender, password)
    smtp.send_message(message, sender, recipient)