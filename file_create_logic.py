import datetime
import time
import os
import subprocess
import logging
import argparse

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', filename="obzvon.log", level=logging.INFO)


def create_call_file(number, router_ip):
    new_file = open('/var/spool/asterisk/outgoing/%s' % number, 'w+')
    new_file.write('''Channel: SIP/%s/%s
MaxRetries: 0
Callerid: %s
RetryTime: 20
WaitTime: 20
Context: pa-system
Extension: 10
Priority: 1
''' % (router_ip, number, number))
    os.chown('/var/spool/asterisk/outgoing/%s' % number, 995, 1000)
    logging.info( u'Call file for number %s was successfully created' % number)


def check_file_numbers():
    return len(os.listdir('/var/spool/asterisk/outgoing/'))


def check_call_numbers():
    call_numbers = subprocess.Popen(["asterisk -rx 'core show calls' | grep active | cut -d' ' -f1"], stdout=subprocess.PIPE, shell=True)
    (out, err) = call_numbers.communicate()
    return int(out)


def get_router_ip(routers):
    if routers['a'][1] == 2:
        routers['a'][1] = 1
        return (routers['a'][0], routers)
    elif routers['a'][1] == 1:
        routers['a'][1] = 0
        return (routers['a'][0], routers)
    elif routers['a'][1] == 0:
        routers['a'][1] = 2
        return (routers['b'][0], routers)


def file_create_logic(phone_number, start_time, end_time, router_ip):
    if datetime.date.weekday(datetime.date.today()) > 4:
        start_time = 14
    while True:
        now = datetime.datetime.now()
        if now.hour < start_time or now.hour > 19:
            logging.warning( u'Bad time for customer call')
            time.sleep(600)
            continue
        else:
            if check_file_numbers() > 11:
                time.sleep(2)
                continue
            else:
                create_call_file(phone_number, router_ip)
                break
