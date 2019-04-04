#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

import smtplib

import os
import socket
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
    email_client = smtplib.SMTP(smtp_server, 25, 'Winterfell', 30)
    # Try to send e-mail, if not successful, do not forget to close session
    try:
        email_client.starttls()
        email_client.set_debuglevel(1)
        email_client.login(from_addr, password)
        email_client.sendmail(from_addr, [to_addr], msg.as_string())
    finally:
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
    retry_interval = int(f.readline().strip())
    max_retry = int(f.readline().strip())

print('smtp_server:', smtp_server)
print('from_addr:', from_addr)
print('From:', From)
print('to_addr:', to_addr)
print('To:', To)
print('Subject:', subject)
password = input('Password for smtp server: ')
print('Number of entries:', nr_entries)
print('curl command for getting public IP address: \'%s\'' % curl_cmd)
print('retry interval:', retry_interval)
print('Max retry:', max_retry)
print('########################################')
print('## Script started:\n')

seq_num = 0
content = ['' for i in range(nr_entries + 2)]
content[0] = 'Your IP change log:\n\n'
content[-1] = '\nSent by Python\n'
last_ip = 'n/a'
current_ip = ''
while True:
    retry_count = 0
    # Try to get current IP address
    print('\n========================================')
    print('Try to get IP address:\n')
    while retry_count < max_retry:
        try:
            current_ip = os.popen(curl_cmd).readline().strip()
            socket.inet_aton(current_ip)
        except:
            print('xxxxxxxxxxxxxxxxxxxx')
            print('failed to get IP address')
            retry_count += 1
            time.sleep(retry_interval)
        else:
            break
    if retry_count < max_retry and current_ip != last_ip:
        seq_num += 1
        timestamp = time.strftime('%Y-%m-%d %H:%M', time.localtime())
        line = str('%s %s -> %s\n' % (timestamp, last_ip, current_ip))
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
        print('----------')
        ########## End of test ##########
        # Try to send e-mail
        print('\n========================================')
        print('Try to send e-mail:\n')
        while retry_count < max_retry:
            try:
                send_email(smtp_server, from_addr, From, to_addr, To, subject, ''.join(content), password)
            except:
                print('an error occured during sending e-mail')
                print('XXXXXXXXXXXXXXXXXXXX')
                retry_count += 1
                time.sleep(retry_interval)
            else:
                print('e-mail was sent successfully')
                print('____________________')
                last_ip = current_ip
                break
    time.sleep(retry_interval * (max_retry - retry_count))
