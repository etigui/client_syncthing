# Internal import
from id import Id


class Info:

    def __init__(self, sync_directory, cert, key, host, port, verbose, normal_mode=True, compression=0):
        self.sync_directory = sync_directory
        self.shared_folders = []
        self.device_name = "guizell"
        self.client_name = "syncthing"
        self.client_version = "v0.14.41"
        self.cert = cert
        self.key = key
        self.host = host
        self.port = port
        self.compression = compression
        self.device_id_bytes = None
        self.device_id_str = None
        self.verbose_mode = verbose
        self.normal_mode = normal_mode

    def gen_device_id(self):

        # Get device id
        self.device_id_str = Id(self.cert).get_device_id()
        self.device_id_bytes = bytes((self.device_id_str.replace('-', '')).encode('utf-8'))
        if self.verbose_mode: print("Device id: %s\n" % self.device_id_str)
