# External import
import struct
import sys

# Internal import
import protocol_pb2
import const


# Pack header
def pack_header(header_type, compression):
    header = protocol_pb2.Header()
    header.type = header_type
    header.compression = compression
    header_length = struct.pack('>H', len(header.SerializeToString()))
    return header_length + header.SerializeToString()


# Pack hello header and hello message
def pack_hello(info):
    hello = protocol_pb2.Hello()
    hello.device_name = info.device_name
    hello.client_name = info.client_name
    hello.client_version = info.client_version
    message_length = len(hello.SerializeToString())
    return struct.pack('>IH', const.MAGIC_HEX, message_length) + hello.SerializeToString()


# Pack header and cluster config message
def pack_cluster_config(info):
    header = pack_header(const.MSG_CLUSTER_CONFIG, info.compression)
    cluster_config = protocol_pb2.ClusterConfig()

    # Add folder to sync
    for f in info.shared_folders:
        folder = cluster_config.folders.add()
        folder.id = f
        device = folder.devices.add()
        device.id = info.device_id_bytes
    message_length = struct.pack('>I', (len(cluster_config.SerializeToString())))
    return header + message_length + cluster_config.SerializeToString()


# Pack header and ping message
def pack_ping(info):
    header = pack_header(const.MSG_PING, info.compression)
    ping = protocol_pb2.Ping()
    message_length = struct.pack('>I', len(ping.SerializeToString()))
    return header + message_length + ping.SerializeToString()


# Pack header and request message
def pack_request(info, request_id, folder, name, offset, size, block_hash, temporary):
    header = pack_header(const.MSG_REQUEST, info.compression)
    request = protocol_pb2.Request()
    request.id = request_id
    request.folder = folder
    request.name = name
    request.offset = offset
    request.size = size
    request.hash = block_hash
    #request.temporary = temporary
    message_length = struct.pack('>I',len(request.SerializeToString()))
    return header + message_length + request.SerializeToString()


# Unpack header and hello message
def unpack_hello(sock, utils):

    # Get magic number hello message
    magic = utils.receive_data(sock, const.INT32)
    hello = protocol_pb2.Hello()

    # Check if hello or other message
    if magic == const.MAGIC_BIN:

        # Get hello message length
        hello_length_byte = utils.receive_data(sock, const.INT16)

        hello_length = int("%d" % struct.unpack('>H', hello_length_byte))
        hello_data = utils.receive_data(sock, hello_length)

        # Import info to Protobuf "Hello" message
        hello.ParseFromString(hello_data)
        return hello
    else:
        sys.stderr.write("Receive hello error\n")
        return hello


# Unpack message
def unpack_message(sock, utils):

    # Receive header length, data
    header_length_bytes = utils.receive_data(sock, const.INT16)
    header_length = int("%d" % struct.unpack('>H', header_length_bytes))

    # Receive header data
    header = protocol_pb2.Header()
    header_data = utils.receive_data(sock, header_length)
    header.ParseFromString(header_data)

    # Receive message length, data
    message_length_bytes = utils.receive_data(sock, const.INT32)
    message_length = int("%d" % struct.unpack('>I', message_length_bytes))
    message_data = utils.receive_data(sock, message_length)
    return header.type, header.compression, parse(header.type, message_data)


def parse(header_type, message_data):
    if header_type == const.MSG_CLUSTER_CONFIG:
        return parse_cluster_config(message_data)
    elif header_type == const.MSG_INDEX:
        return parse_index(message_data)
    elif header_type == const.MSG_INDEX_UPDATE:
        return parse_index(message_data)
    elif header_type == const.MSG_RESPONSE:
        return parse_response(message_data)
    elif header_type == const.MSG_PING:
        return 0 # parse_ping(message_data)
    elif header_type == const.MSG_DOWNLOAD_PROGRESS:
        return parse_download_progress(message_data)
    elif header_type == const.MSG_CLOSE:
        return parse_close(message_data)


def parse_cluster_config(message_data):
    cluster_config = protocol_pb2.ClusterConfig()
    cluster_config.ParseFromString(message_data)
    return cluster_config


def parse_index(message_data):
    index = protocol_pb2.Index()
    index.ParseFromString(message_data)
    return index


def parse_response(message_data):
    response = protocol_pb2.Response()
    response.ParseFromString(message_data)
    return response


def parse_ping(message_data):
    ping = protocol_pb2.Ping()
    ping.ParseFromString(message_data)
    return ping


def parse_download_progress(message_data):
    download_progress = protocol_pb2.DownloadProgress()
    download_progress.ParseFromString(message_data)
    return download_progress


def parse_close(message_data):
    close = protocol_pb2.Close()
    close.ParseFromString(message_data)
    return close
