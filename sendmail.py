#!/usr/bin/env python3
import sys
import smtplib
import dns.resolver
from email.mime.text import MIMEText
from email.header import Header


class Email:
    def __init__(self, sender, receiver, subject, body):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body

    def sendmail(self):
        domain = self.receiver.split("@")[1]
        answers = dns.resolver.query(domain, "MX")
        if len(answers) <= 0:
            sys.stderr.write("No mail servers found for destination\n")
            sys.exit(1)
        server = str(answers[0].exchange)
        msg = MIMEText(self.body, "plain", "utf-8")
        msg["Subject"] = Header(self.subject, "utf-8")
        server = smtplib.SMTP(server)
        #        server.set_debuglevel(1)
        server.sendmail(self.sender, self.receiver, msg.as_string())
        server.quit()
