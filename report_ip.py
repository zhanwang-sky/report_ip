#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_email(SMTP_host, account, password, From, To, to_addr, subject, content):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = format_addr('%s <%s>' % (From, account))
    msg['To'] = format_addr('%s <%s>' % (To, to_addr))
    msg['Subject'] = Header(subject, 'utf-8').encode()
    email_client = smtplib.SMTP(SMTP_host)
    email_client.starttls()
    email_client.set_debuglevel(1)
    email_client.login(account, password)
    email_client.sendmail(account, [to_addr], msg.as_string())
    email_client.quit()

#send_email(smtp_server, from_addr, password, sender, receiver, to_addr, subject, 'This e-mail is sent by Python...')
