# External import
import shutil
import os
import errno
import pathlib
import socket
import sys
import ssl
import collections
import threading
import datetime

# Internal import
import const


class Utils:

    def __init__(self):
        self.lock_recv_socket = threading.Lock()
        self.lock_send_socket = threading.Lock()
        self.lock_file = threading.Lock()

    def clean_sync_directory(self, path):
        if not os.path.isdir(path):
            return
        shutil.rmtree(path)

    def create_dir(self, path):
        try:
            if not os.path.exists(path):
                pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        except OSError as msg:
            if msg.errno != errno.EEXIST:
                sys.stderr.write("Create directory: : %s\n" % msg)
                raise

    def init_socket(self, info):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(const.SOCKET_WORKING_TIMOUT)
        except socket.error as msg:
            sys.stderr.write("Creation socket error: %s\n" % msg)
            s = None
        try:
            s = ssl.wrap_socket(s, keyfile=info.key, certfile=info.cert, ssl_version=ssl.PROTOCOL_SSLv23)
        except ssl.socket_error as msg:
            sys.stderr.write("Ssl wrap_socket function error: %s\n" % msg)
            s = None
        try:
            s.connect((info.host, info.port))
        except socket.error as msg:
            sys.stderr.write("Could not open socket: %s\n" % msg)
            s.close()
            s = None
        if s is None:
            sys.exit("Init socket error")
        return s

    def receive_data(self, sock, size):
        if size != 0:
            self.lock_recv_socket.acquire()
            data = sock.recv(1)
            size -= 1
            while size > 0:
                data += sock.recv(1)
                size -= 1
            self.lock_recv_socket.release()
            return data
        else:

            # Fix problem with no compression with CC
            return const.CC_VALUE

    def send_data(self, sock, data):

        self.lock_send_socket.acquire()
        sock.sendall(data)
        self.lock_send_socket.release()

    def write_bytes_file_offset(self, path, data, offset):
        self.lock_file.acquire()
        try:
            f = open(path, 'r+b')
        except IOError:
            f = open(path, 'wb')
        f.seek(offset)
        f.write(data)
        f.close()
        self.lock_file.release()

    def struct_message(self, message_type, message_compression, message_data):
        Message = collections.namedtuple('Message', 'type compression data')
        return Message(type=message_type, compression=message_compression, data=message_data)

    def struct_block(self, block_folder, block_file, block_offset, block_date, file_size):
        Message = collections.namedtuple('Message', 'folder path offset date size')
        return Message(folder=block_folder, path=block_file, offset=block_offset, date=block_date, size=file_size)

    def check_file_end(self, size, file_path):
        if size == os.path.getsize(file_path):
            return True
        return False

    def get_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")
