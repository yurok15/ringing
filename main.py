#!/usr/bin/python2.7
###########################################################
#
# This python script is used to generate asterisk call files
# into the directory /var/spool/asterisk/outgoing/
#
# Written by : Yuriy Zhigulskiy
# email: yurok15@gmail.com
# github: yurok15@gmail.com
# Created date: Dec 26, 2017
# Last modified: Jan 28, 2018
# Tested with : Python 2.7
# Script Revision: 0.8
# Revision 0.6 threading and statistics was added
# Revision 0.7 differrent router with cost was added
# Revision 0.8 blacklist added
##########################################################



from thread import start_new_thread
import argparse
import socket
from file_create_logic import *

parser = argparse.ArgumentParser(prog='obzvon')
parser.add_argument('--number', dest='file_path', type=str, help='File with numbers')
parser.add_argument('--start_time', dest='start_time', type=int, help='End Time')
parser.add_argument('--end_time', dest='end_time', type=int, help='End Time')
args = parser.parse_args()


start_time = args.start_time
end_time = args.end_time
routers = {'a': ['10.78.99.196', 2], 'b': ['10.78.99.195', 1]}


bad_numbers = 0
good_numbers = 0
data_list_len = []


sock = socket.socket()
sock.bind(('127.0.0.1', 9090))
sock.listen(1)


def net_thread():
    global data_list_len
    while True:
        conn, addr = sock.accept()
        conn.sendall("Good numbers: " + str(good_numbers) + "\n"
                     + "Bad numbers: " + str(bad_numbers) + "\n"
                     + "Total numbers: " + str(data_list_len) + "\n"
                     + "Done in %: " + str((good_numbers + bad_numbers)*100/data_list_len) + "%\n"
                     )
        conn.close()


def main_job(data_list, blacklist):
    global bad_numbers
    global good_numbers
    global data_list_len
    global routers
    data_list_len = len(data_list[0:])
    while data_list[0] != "":
        if int(len(data_list[0])) < 11:
            logging.warning(u'Bad number %s' % data_list[0])
            bad_numbers += 1
            data_list.remove(data_list[0])
        else:
            if data_list[0] in blacklist:
                logging.warning(u'Number %s in blacklist' % data_list[0])
                data_list.remove(data_list[0])
                continue
            router_ip, routers = get_router_ip(routers)
            file_create_logic(data_list[0], start_time, end_time, router_ip)
            good_numbers = good_numbers + 1
            data_list.remove(data_list[0])


def get_blacklist():
    with open('blacklist') as blk:
        read_data = blk.read()
    blacklist = read_data.split()
    return(blacklist)


def main():
    with open(args.file_path) as file:
        read_data = file.read()
    data_list = read_data.split()
    blacklist = get_blacklist()
    start_new_thread(net_thread, ())
    start_new_thread(main_job(data_list, blacklist), ())


if __name__ == "__main__":
    main()
