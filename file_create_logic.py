import datetime
import time
import os
import subprocess
import logging
import argparse

parser = argparse.ArgumentParser(prog='obzvon')
parser.add_argument('--number', dest='file_path', type=str, help='File with numbers')
parser.add_argument('--start_time', dest='start_time', type=int, help='End Time')
parser.add_argument('--end_time', dest='end_time', type=int, help='End Time')

args = parser.parse_args()
start_time = args.start_time
end_time = args.end_time

data_list_len = []


logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', filename="obzvon.log", level=logging.INFO)


def create_call_file(number):
    new_file = open('/var/spool/asterisk/outgoing/%s' % number, 'w+')
    new_file.write('''Channel: SIP/10.78.99.196/%s
MaxRetries: 0
Callerid: %s
RetryTime: 20
WaitTime: 20
Context: pa-system
Extension: 10
Priority: 1
''' % (number, number))
    os.chown('/var/spool/asterisk/outgoing/%s' % number, 995, 1000)
    logging.info( u'Call file for number %s was successfully created' % number)


def check_file_numbers():
    return len(os.listdir('/var/spool/asterisk/outgoing/'))


def check_call_numbers():
    call_numbers = subprocess.Popen(["asterisk -rx 'core show calls' | grep active | cut -d' ' -f1"], stdout=subprocess.PIPE, shell=True)
    (out, err) = call_numbers.communicate()
    return int(out)


def file_create_logic(phone_number, start_time, end_time):
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
                create_call_file(phone_number)
                break


def main_job(data_list):
    global bad_numbers
    global good_numbers
    global data_list_len
    data_list_len = len(data_list[0:])
    while data_list[0] != "":
        if int(len(data_list[0])) < 11:
            logging.warning(u'Bad number %s' % data_list[0])
            bad_numbers += 1
            data_list.remove(data_list[0])
        else:
            file_create_logic(data_list[0], start_time, end_time)
            good_numbers = good_numbers + 1
            data_list.remove(data_list[0])
