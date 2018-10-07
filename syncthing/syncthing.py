# External import
import threading
import os
import queue
import sys

# Internal import
import serialize
import const
import utils

message_queue = queue.Queue()
block_queue = queue.Queue(const.MAX_QUEUE_SIZE)
block_dict = dict()


class Syncthing(threading.Thread):

    def __init__(self, info):
        threading.Thread.__init__(self)
        self.info = info
        self.socket = None
        self.request_id = 0
        self.utils = None

    def run(self):

        self.utils = utils.Utils()

        # Init socket
        self.socket = self.utils.init_socket(self.info)
        if self.info.normal_mode: print("Connected on Syncthing node: %s:%s" % (self.info.host, self.info.port))

        # Send hello to master
        self.send_message(serialize.pack_hello(self.info))
        self.receive_hello()

        # Thread receive message
        threading.Thread(target=self.thread_message, args=[]).start()

        # Process received message
        while True:
            self.wait_message()

    def wait_message(self):

            # Get one message from queue
            message = message_queue.get()

            if message.type == const.MSG_CLUSTER_CONFIG:
                if self.info.normal_mode: print("[%s] Received: MSG_CLUSTER_CONFIG" % self.utils.get_time())

                # Receive and send cluster config
                self.receive_cluster_config(message.data)
                self.send_message(serialize.pack_cluster_config(self.info))
            elif message.type == const.MSG_INDEX:
                if self.info.normal_mode: print("[%s] Received: MSG_INDEX" % self.utils.get_time())

                # Start thread process index
                threading.Thread(target=self.receive_index, args=[message.data]).start()
            elif message.type == const.MSG_INDEX_UPDATE:
                if self.info.normal_mode: print("[%s] Received: MSG_INDEX_UPDATE" % self.utils.get_time())

                # Start thread process index update
                threading.Thread(target=self.receive_index, args=[message.data]).start()
            elif message.type == const.MSG_REQUEST:
                if self.info.normal_mode: print("[%s] Received: MSG_REQUEST" % self.utils.get_time())
            elif message.type == const.MSG_RESPONSE:
                if self.info.verbose_mode: print("[%s] Received: MSG_RESPONSE" % self.utils.get_time())
                self.receive_response(message.data)
            elif message.type == const.MSG_PING:
                if self.info.normal_mode: print("[%s] Received: MSG_PING" % self.utils.get_time())
                self.send_message(serialize.pack_ping(self.info))
                if self.info.normal_mode: print("[%s] Sent: MSG_PING" % self.utils.get_time())
            else:
                if self.info.normal_mode: print("[%s] Received: MSG_CLOSE" % self.utils.get_time())
                exit("Server close the connection, reason: %s" % message.data.reason)

    def send_message(self, packed_message):
        self.utils.send_data(self.socket, packed_message)

    def receive_message(self):
        return serialize.unpack_message(self.socket, self.utils)

    def receive_index(self, index):

        if self.info.verbose_mode: print("Folder name:        %s\n" % index.folder)
        for file in index.files:
            if self.info.verbose_mode: print("File name:          %s" % file.name)

        # Create base directory where the file will be added/deleted
        base_dir = os.path.join(self.info.sync_directory, index.folder)

        # Process all the directory
        self.process_folders(index.files, base_dir)

        # Process all files
        self.process_files(index.files, base_dir, index.folder)

    def process_folders(self, folders, base_dir):
        self.utils.create_dir(base_dir)
        for folder in folders:

            # Check if folder and not deleted
            if folder.type == const.FOLDER and not folder.deleted:

                # Forge current folder path
                folder_path = os.path.join(base_dir, folder.name)

                # Check if folder not exists
                if not os.path.isdir(folder_path):
                    self.utils.create_dir(folder_path)
                    if self.info.verbose_mode: print("[%s] Folder created: %s" % (self.utils.get_time(), folder_path))

    def process_files(self, files, base_dir, folder):
        for file in files:

            # Forge current file path
            file_path = os.path.join(base_dir, file.name)

            # Check if file and not deleted
            if file.type == const.FILE and not file.deleted:
                if self.info.verbose_mode: print("[%s] Begin request block for file: %s" % (self.utils.get_time(), file_path))

                # Process all index file blocks
                for i, block in enumerate(file.Blocks):

                    # Gen request id
                    self.request_id += 1
                    request_id = self.request_id

                    # Add block to match response
                    block_dict[request_id] = self.utils.struct_block(folder, file_path,\
                                                                     block.offset, file.modified_s, file.size)
                    block_queue.put(request_id)

                    # Send request block
                    self.request_block(folder, file.name, block.offset, block.size, block.hash, request_id)
                if self.info.verbose_mode: print("[%s] End request block for file: %s" % (self.utils.get_time(), file_path))
            elif file.type == const.SYMLINK and not file.deleted:

                # Check if symlink already exist
                if not os.path.islink(file_path):

                    # Forge symlink path and create symlink
                    if self.info.verbose_mode: print("[%s] Symlink created: %s" % (self.utils.get_time(), file_path))
                    sym_target_path = os.path.join(base_dir, file.symlink_target)
                    os.symlink(sym_target_path, file_path)

    def request_block(self, folder, file_name, block_offset, block_size, block_hash, request_id):

        # Send request for block
        self.send_message(serialize.pack_request(self.info, request_id, folder, \
                                                 file_name, block_offset, block_size, block_hash, False))

    def receive_response(self, response):

        # Get request block info
        block = block_dict.pop(response.id, None)
        block_queue.get()

        # Check if the key exist
        if block is not None:

            # Create tmp path
            tmp_file_path = block.path + ".tmp"

            # Set start offset to tmp file
            self.utils.write_bytes_file_offset(tmp_file_path, response.data, block.offset)

            # Check if last block
            if self.utils.check_file_end(block.size, tmp_file_path):

                # Remove and rename tmp file
                if os.path.exists(block.path):
                    os.remove(block.path)
                if not os.path.exists(block.path):
                    os.rename(tmp_file_path, block.path)

                # Add modification date
                os.utime(block.path, (block.date, block.date))
                if self.info.normal_mode: print("[%s] Receive all block for file: %s" % (self.utils.get_time(), block.path))

        # Notify queue done
        block_queue.task_done()

    def receive_hello(self):
        hello = serialize.unpack_hello(self.socket, self.utils)
        if self.info.normal_mode: print("Device remote name:    %s" % hello.device_name)
        if self.info.normal_mode: print("Client remote name:    %s" % hello.client_name)
        if self.info.normal_mode: print("Client remote version: %s\n" % hello.client_version)

    def receive_cluster_config(self, cluster_config):
        for folder in cluster_config.folders:

            # Add available folder from cluster config
            self.info.shared_folders.append(folder.id)

            if self.info.normal_mode: print("Folder to sync:  %s" % folder.id)
            for device in folder.devices:
                if self.info.verbose_mode: print("Id:           %s" % hex(int(device.id.hex(), base=16)))
                if self.info.verbose_mode: print("Name:         %s" % device.name)
                if self.info.verbose_mode: print("Addresses:    %s" % device.addresses)
                if self.info.verbose_mode: print("Max sequence: %s" % device.max_sequence)
                if self.info.verbose_mode: print("Compression:  %s" % device.compression)
                if self.info.verbose_mode: print("Index_id:     %s\n" % device.index_id)

    def thread_message(self):
        global message_queue
        while True:
            try:

                # Get message from server
                t, c, d = self.receive_message()
                message = self.utils.struct_message(t, c, d)
                message_queue.put(message)
            except self.socket.timeout:
                pass
            except ConnectionResetError as msg:
                sys.stderr.write("Socket connection reset: %s\n" % msg)
                exit()
            except self.error as msg:
                sys.stderr.write("Socket error: %s\n" % msg)
                exit()
