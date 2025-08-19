# Minimal FIX protocol client using Python's standard library
import socket

HOST = '127.0.0.1'  # Server address
PORT = 9878         # Server port

def build_fix_message(fields):
	# Build a FIX message from a dict
	return '\x01'.join(f'{k}={v}' for k, v in fields.items()) + '\x01'

def parse_fix_message(msg):
	fields = msg.strip().split('\x01')
	return {f.split('=')[0]: f.split('=')[1] for f in fields if '=' in f}

def main():
	# Example Logon message (MsgType=A)
	logon_fields = {
		'8': 'FIX.4.2',      # BeginString
		'35': 'A',           # MsgType=Logon
		'34': '1',           # MsgSeqNum
		'49': 'CLIENT',      # SenderCompID
		'56': 'SERVER',      # TargetCompID
		'98': '0',           # EncryptMethod=0 (None)
		'108': '30',         # HeartBtInt=30
	}
	logon_msg = build_fix_message(logon_fields)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		print(f'Connected to {HOST}:{PORT}')
		print(f'Sending: {logon_msg}')
		s.sendall(logon_msg.encode('ascii'))
		data = s.recv(4096)
		response = data.decode('ascii', errors='ignore')
		print(f'Received: {response}')
		print('Parsed response:', parse_fix_message(response))

if __name__ == '__main__':
	main()
