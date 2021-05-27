import socket
import json

with open('settings.json', 'r') as f:
    config = json.load(f)

IP = config['server_ip']
PORT = 53


def get_domain(dns_message):
    state = 0
    expected_length = 0
    domain_string = ''
    domain_parts = []
    x = 0

    for byte in dns_message:
        if state == 1:
            domain_string += chr(byte)
            x += 1
            if x == expected_length:
                domain_parts.append(domain_string)
                domain_string = ''
                state = 0
                x = 0
            if byte == 0:
                domain_parts.append(domain_string)
                break
        else:
            state = 1
            expected_length = byte
        x += 0

    return '.'.join(domain_parts[:-1])


def response_out_from_black_list(message, address, port):
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(message, server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return data


def response_black_list(message, ip):
    packet = b''
    domain = get_domain(message[12:])
    if domain:
        # header section
        packet += message[:2] + b'\x80\x05'  # 05 - response code refused, other parameters 0
        packet += message[4:6] + message[4:6] + b'\x00\x00\x00\x00'  # number of questions entries, answers entries
        # questions section
        packet += message[12:]  # a domain name represented as a sequence of labels,
        # where each label consists of a length octet followed by that
        # number of octets
        # record section
        packet += b'\xc0\x0c'  # a domain name to which this resource record pertains
        packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
        packet += str.join('', map(lambda x: chr(int(x)), ip.split('.'))).encode('latin')  # 4bytes of IP
    return packet


def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print(f'Server is running on {IP}:{PORT}.\nWaiting requests...')

    while True:
        try:
            message, (ip, port) = sock.recvfrom(512)
        except ConnectionResetError:
            continue

        domain = get_domain(message[12:])
        if domain not in config['black_list']:
            response = response_out_from_black_list(message, config['outside_dns_server'], 53)
            sock.sendto(response, (ip, port))
        else:
            response = response_black_list(message, ip)
            sock.sendto(response, ip, port)


if __name__ == '__main__':
    run_server()
