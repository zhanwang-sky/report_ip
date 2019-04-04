#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

import os

import time

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_email(smtp_server, from_addr, From, to_addr, To, subject, content, password):
    # Compose e-mail
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = format_addr('%s <%s>' % (From, from_addr))
    msg['To'] = format_addr('%s <%s>' % (To, to_addr))
    msg['Subject'] = Header(subject, 'utf-8').encode()
    # Send e-mail
    email_client = smtplib.SMTP(smtp_server)
    email_client.starttls()
    email_client.set_debuglevel(1)
    email_client.login(from_addr, password)
    email_client.sendmail(from_addr, [to_addr], msg.as_string())
    email_client.quit()

with open('config', 'r') as f:
    smtp_server = f.readline().strip()
    from_addr = f.readline().strip()
    From = f.readline().strip()
    to_addr = f.readline().strip()
    To = f.readline().strip()
    subject = f.readline().strip()
    curl_cmd = f.readline().strip()
    nr_entries = int(f.readline().strip())

print('smtp_server:', smtp_server)
print('from_addr:', from_addr)
print('From:', From)
print('to_addr:', to_addr)
print('To:', To)
print('Subject:', subject)
password = input('Password for smtp server: ')
print('Number of entries:', nr_entries)
print('curl command for getting public IP address: \'%s\'' % curl_cmd)
print()

seq_num = 0
content = ['' for i in range(nr_entries + 2)]
content[0] = 'Your IP change log:\n\n'
content[-1] = '\nSent by Python\n'
last_ip = ''
current_ip = 'n/a'
while True:
    last_ip = current_ip
    current_ip = os.popen(curl_cmd).readline().strip()
    if current_ip != last_ip:
        seq_num += 1
        timestamp = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        line = str('%s: %s -> %s\n' % (timestamp, last_ip, current_ip))
        if content[seq_num] != '':
            content.pop(1)
            content.insert(nr_entries, line)
        else:
            content[seq_num] = line
        if seq_num >= nr_entries:
            seq_num = 0
        ########## Test ##########
        print('----------')
        print(''.join(content))
        print('==========')
        ########## End of test ##########
        send_email(smtp_server, from_addr, From, to_addr, To, subject, ''.join(content), password)
    time.sleep(60)
