"""Minimal MQTT client for MicroPython.

Compatible with:
    from umqtt.simple import MQTTClient

Designed for Raspberry Pi Pico W / Pico 2 W running MicroPython.
Supports MQTT 3.1.1 connect, publish, subscribe, ping and disconnect.
"""

try:
    import usocket as socket
except ImportError:
    import socket

try:
    import ustruct as struct
except ImportError:
    import struct

try:
    import ubinascii
except ImportError:
    ubinascii = None


class MQTTException(Exception):
    pass


def _bytes(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode()
    return str(value).encode()


class MQTTClient:
    def __init__(
        self,
        client_id,
        server,
        port=0,
        user=None,
        password=None,
        keepalive=0,
        ssl=False,
        ssl_params=None,
    ):
        self.client_id = _bytes(client_id)
        self.server = server
        self.port = port or (8883 if ssl else 1883)
        self.user = _bytes(user) if user is not None else None
        self.password = _bytes(password) if password is not None else None
        self.keepalive = keepalive
        self.ssl = ssl
        self.ssl_params = ssl_params or {}
        self.sock = None
        self.cb = None
        self.pid = 0

    def _write_str(self, value):
        value = _bytes(value)
        self.sock.write(struct.pack("!H", len(value)))
        self.sock.write(value)

    def _send_remaining_length(self, length):
        while True:
            digit = length % 128
            length //= 128
            if length > 0:
                digit |= 0x80
            self.sock.write(bytes([digit]))
            if length == 0:
                break

    def connect(self, clean_session=True):
        addr = socket.getaddrinfo(self.server, self.port)[0][-1]
        self.sock = socket.socket()
        self.sock.connect(addr)

        if self.ssl:
            try:
                import ussl as ssl_module
            except ImportError:
                import ssl as ssl_module
            self.sock = ssl_module.wrap_socket(self.sock, **self.ssl_params)

        flags = 0x02 if clean_session else 0x00
        if self.user is not None:
            flags |= 0x80
        if self.password is not None:
            flags |= 0x40

        payload_len = 2 + len(self.client_id)
        if self.user is not None:
            payload_len += 2 + len(self.user)
        if self.password is not None:
            payload_len += 2 + len(self.password)

        remaining = 10 + payload_len

        self.sock.write(b"\x10")
        self._send_remaining_length(remaining)
        self.sock.write(b"\x00\x04MQTT\x04")
        self.sock.write(bytes([flags]))
        self.sock.write(struct.pack("!H", self.keepalive))
        self._write_str(self.client_id)

        if self.user is not None:
            self._write_str(self.user)
        if self.password is not None:
            self._write_str(self.password)

        response = self.sock.read(4)
        if response is None or len(response) != 4 or response[0] != 0x20:
            raise MQTTException("Invalid MQTT CONNACK response")
        if response[3] != 0:
            raise MQTTException(response[3])

        return response[2] & 1

    def disconnect(self):
        if self.sock is not None:
            try:
                self.sock.write(b"\xe0\x00")
            finally:
                self.sock.close()
                self.sock = None

    def ping(self):
        self.sock.write(b"\xc0\x00")

    def publish(self, topic, msg, retain=False, qos=0):
        topic = _bytes(topic)
        msg = _bytes(msg)

        if qos not in (0, 1):
            raise ValueError("Only QoS 0 and QoS 1 are supported")

        packet_type = 0x30 | (qos << 1)
        if retain:
            packet_type |= 0x01

        remaining = 2 + len(topic) + len(msg)
        if qos == 1:
            remaining += 2

        self.sock.write(bytes([packet_type]))
        self._send_remaining_length(remaining)
        self._write_str(topic)

        pid = None
        if qos == 1:
            self.pid = (self.pid + 1) & 0xFFFF
            if self.pid == 0:
                self.pid = 1
            pid = self.pid
            self.sock.write(struct.pack("!H", pid))

        self.sock.write(msg)

        if qos == 1:
            while True:
                op = self.wait_msg()
                if op == 0x40:
                    return pid

        return None

    def set_callback(self, callback):
        self.cb = callback

    def subscribe(self, topic, qos=0):
        if self.cb is None:
            raise MQTTException("Set callback before subscribing")
        if qos not in (0, 1):
            raise ValueError("Only QoS 0 and QoS 1 are supported")

        topic = _bytes(topic)
        self.pid = (self.pid + 1) & 0xFFFF
        if self.pid == 0:
            self.pid = 1

        remaining = 2 + 2 + len(topic) + 1
        self.sock.write(b"\x82")
        self._send_remaining_length(remaining)
        self.sock.write(struct.pack("!H", self.pid))
        self._write_str(topic)
        self.sock.write(bytes([qos]))

        while True:
            op = self.wait_msg()
            if op == 0x90:
                return

    def wait_msg(self):
        op_data = self.sock.read(1)
        if not op_data:
            return None
        op = op_data[0]

        if op == 0xD0:  # PINGRESP
            self.sock.read(1)
            return None

        # Decode MQTT remaining length
        remaining = 0
        multiplier = 1
        while True:
            byte_data = self.sock.read(1)
            if not byte_data:
                return None
            digit = byte_data[0]
            remaining += (digit & 0x7F) * multiplier
            if (digit & 0x80) == 0:
                break
            multiplier *= 128

        if op & 0xF0 == 0x30:  # PUBLISH
            topic_len = struct.unpack("!H", self.sock.read(2))[0]
            topic = self.sock.read(topic_len)
            remaining -= 2 + topic_len

            qos = (op >> 1) & 0x03
            pid = None
            if qos:
                pid = struct.unpack("!H", self.sock.read(2))[0]
                remaining -= 2

            msg = self.sock.read(remaining)
            if self.cb is not None:
                self.cb(topic, msg)

            if qos == 1 and pid is not None:
                self.sock.write(b"\x40\x02" + struct.pack("!H", pid))
            return op

        # For PUBACK / SUBACK etc., consume payload and return packet type.
        if remaining:
            self.sock.read(remaining)
        return op

    def check_msg(self):
        if self.sock is None:
            return None
        try:
            self.sock.setblocking(False)
            return self.wait_msg()
        finally:
            self.sock.setblocking(True)
