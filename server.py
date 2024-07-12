# Server for file sharing app

# Imports
import os
import socket
import argparse


# Custom FileExistsError exception
class FileExistsError(Exception):
    pass


# Server class
class TransferServer(argparse.Namespace):

    # Key parametres - set by parse()
    HOST = None
    PORT = None
    SAVEDIR = None
    BUFFER_SIZE = None


    # Init self
    def __init__(self):
        super().__init__()
        self.parser = argparse.ArgumentParser(description="File transfer server")
        self.parser.add_argument("-a", "--host", type=str, default="0.0.0.0", help="Server host address")
        self.parser.add_argument("-p", "--port", type=int, default=2222, help="Server port")
        self.parser.add_argument("-s", "--savedir", type=str, default="./", help="Designated save directory. Default to current working directory.")
        self.parser.add_argument("-b", "--buffer_size", type=int, default=4096, help="Set buffer size, default value 4096.")    
   

    # Parse arguments and set corresponding variables
    def parse(self, args=None):
        options = self.parser.parse_args(args)
        self.HOST = options.host
        self.PORT = options.port
        self.SAVEDIR = options.savedir
        self.BUFFER_SIZE = options.buffer_size
        return self


    # Start server
    def start(self):
        
        # Check if SAVEDIR exists. If it doesn't, create it.
        if not os.path.exists(self.SAVEDIR):
            os.makedirs(self.SAVEDIR)
        
        # Bind server_socket and start listening for connections
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()
      
        print(f"Server is listening.\nAddress: {self.HOST}\nPort: {self.PORT}\n")
            
        # Wait for connection, then handle the client
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"[+] New connection: {client_address}")
            self.handle_client(client_socket)
            client_socket.close()


    # Handle client connection and file transfer
    def handle_client(self, client_socket):
        
        # Try to receive the data
        try:
            filename = client_socket.recv(self.BUFFER_SIZE).decode().strip()
            save_path = os.path.join(self.SAVEDIR, filename)

            # Only receive the file when it doesn't exist in the output directory
            if os.path.exists(save_path):
                client_socket.sendall(b"File Exists")
                raise FileExistsError()
            
            else:
                client_socket.sendall(b"Ready to receive file")

            # Get filesize from client
            filesize = int.from_bytes(client_socket.recv(self.BUFFER_SIZE))

            print(f"Receiving file: {filename}")

            # Receive the file
            with open(save_path, 'wb') as file:
                total_received = 0 
                while True:
                    data = client_socket.recv(self.BUFFER_SIZE)
                   
                    total_received += len(data)

                    # Check if there is still ongoing transfer
                    if not data:
                        break

                    # Write received data
                    file.write(data)

            # Throw an error if the entire file doesn't transfer
            if total_received != filesize:
                client_socket.sendall(b"Incomplete file transfer")
                raise Exception("Incomplete file transfer")

            # Send success file transfer confirmation to the client
            client_socket.sendall(b"File transfer successful")
            print(f"Received file: {filename}")
        
        # Handle FileExistsError
        except FileExistsError as e:
            print(f"[!] File {filename} already exists in the output directory.")

        # Handle other exceptions
        except Exception as e:
            print(f"[!] Error: {e}")
        
        # Close connection
        finally:
            client_socket.close()


def main():
    server = TransferServer()
    server.parse()
    server.start()


# Start check
if __name__ == '__main__':
    main()
