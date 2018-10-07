# External import
import base64, ssl
from _sha256 import sha256


class Id:

    def __init__(self, cert):
        self.cert = cert

    def chunk_str(self, s, chunk_size):
        return [s[i:i + chunk_size] for i in range(0, len(s), chunk_size)]

    def luhn_checksum(self, s):
        a = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
        factor = 1
        k = 0
        n = len(a)
        for i in s:
            addend = factor * a.index(i)
            factor = 1 if factor == 2 else 2
            addend = (addend // n) + (addend % n)
            k += addend
        remainder = k % n
        check_code_point = (n - remainder) % n

        return a[check_code_point]

    def read_cert(self):
        with open(self.cert, 'r') as f:
            v = ssl.PEM_cert_to_DER_cert(f.read())
            return sha256(v).digest()

    def get_device_id(self):
        cert = self.read_cert()
        s = "".join([chr(a) for a in base64.b32encode(cert)][:52])
        c = self.chunk_str(s, 13)
        k = "".join(["%s%s" % (cc, self.luhn_checksum(cc)) for cc in c])
        return "-".join(self.chunk_str(k, 7))
