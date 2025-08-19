# Minimal FIX server using Python's standard library
import socket
import threading

HOST = '127.0.0.1'  # localhost
PORT = 9878         # Arbitrary non-privileged port

def parse_fix_message(msg):
	# FIX fields are separated by SOH (\x01)
	fields = msg.strip().split('\x01')
	return {f.split('=')[0]: f.split('=')[1] for f in fields if '=' in f}

def build_fix_message(fields):
	# Build a FIX message from a dict
	return '\x01'.join(f'{k}={v}' for k, v in fields.items()) + '\x01'

def handle_client(conn, addr):
	print(f'Connected by {addr}')
	try:
		while True:
			data = conn.recv(4096)
			if not data:
				break
			msg = data.decode('ascii', errors='ignore')
			print(f'Received: {msg}')
			fix_fields = parse_fix_message(msg)
			# Example: respond to Logon (MsgType=A)
			if fix_fields.get('35') == 'A':
				response = {
					'8': fix_fields.get('8', 'FIX.4.2'),  # BeginString
					'35': 'A',  # MsgType=Logon
					'34': '1',  # MsgSeqNum
					'49': fix_fields.get('56', 'SERVER'),  # SenderCompID
					'56': fix_fields.get('49', 'CLIENT'),  # TargetCompID
					'98': '0',  # EncryptMethod=0 (None)
					'108': '30',  # HeartBtInt=30
				}
				fix_msg = build_fix_message(response)
				conn.sendall(fix_msg.encode('ascii'))
				print(f'Sent: {fix_msg}')
			else:
				# Echo back any other message
				conn.sendall(data)
	finally:
		conn.close()
		print(f'Disconnected {addr}')

def start_server():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((HOST, PORT))
		s.listen()
		print(f'FIX server listening on {HOST}:{PORT}')
		while True:
			conn, addr = s.accept()
			threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
	start_server()
