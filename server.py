# Server for file sharing app

# Imports
import os
import socket
import argparse


# Custom FileExistsError exception
class FileExistsError(Exception):
    pass


class TransferServer(argparse.Namespace):

    # Key parametres - set by parse()
    HOST = None
    PORT = None
    PRIVATE_KEY_FILE = None
    USERNAME = None
    MODE = None
    SAVEDIR = None
    KNOWN_HOSTS_FILE = None
    BUFFER_SIZE = None


    # Init self
    def __init__(self):
        super().__init__()
        self.parser = argparse.ArgumentParser(description="File transfer server")
        self.parser.add_argument("--host", "-a", type=str, default="0.0.0.0", help="Server host address")
        self.parser.add_argument("--port", "-p", type=int, default=2222, help="Server port")
        self.parser.add_argument("--keyfile", "-k", type=str, default="./key", help="Private key file location")
        self.parser.add_argument("--user", "-u", type=str, default="user", help="Username to use while in SSH mode. Defaults to 'user'. Only set when using SSH!")
        self.parser.add_argument("--mode", "-m", type=str, default="unsecured", help="Choose file transfer mode. Options are 'unsecured' and 'ssh'")
        self.parser.add_argument("--savedir", "-s", type=str, default="./", help="Designated save directory. Default to current working directory.")
        self.parser.add_argument("--known_hosts", "-kh", type=str, default="$HOME/.ssh/known_hosts", help="Location of 'known_hosts' file. Use with SSH. Defaults to '$HOME/.ssh/known_hosts'.")
        self.parser.add_argument("--buffer_size", "-b", type=int, default=4096, help="Set buffer size, default value 4096.")    
   

    # Parse arguments and set corresponding variables
    def parse(self, args=None):
        options = self.parser.parse_args(args)
        self.HOST = options.host
        self.PORT = options.port
        self.PRIVATE_KEY_FILE = options.keyfile
        self.USERNAME = options.user
        self.MODE = options.mode
        self.SAVEDIR = options.savedir
        self.KNOWN_HOSTS_FILE = options.known_hosts
        self.BUFFER_SIZE = options.buffer_size
        return self


    # Start server
    def start(self, args=None):
        
        # Check if SAVEDIR exists. If it doesn't, create it.
        if not os.path.exists(self.SAVEDIR):
            os.makedirs(self.SAVEDIR)
        
        # Check selected mode and continue
        if self.MODE == 'unsecured':

            # Bind server_socket and start listening for connections
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.HOST, self.PORT))
            self.server_socket.listen()
      
            print(f"Server is listening.\nAddress: {self.HOST}\nPort: {self.PORT}\n")
            
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"[+] New connection: {client_address}")
                self.handle_client(client_socket)
                client_socket.close()

        elif self.MODE == 'ssh':

            pass

        else:
            print("Error. You have selected incorrect MODE.")


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

            print(f"Receiving file: {filename}")

            with open(save_path, 'wb') as file:
                while True:
                    data = client_socket.recv(self.BUFFER_SIZE)
                    
                    # Check if there is still ongoing transfer
                    if not data:
                        break

                    # Write received data
                    file.write(data)

            print(f"Received file: {filename}")
        
        # Handle FileExistsError
        except FileExistsError as e:
            print(f"File {filename} already exists in the output directory.")

        # Handle other exceptions
        except Exception as e:
            print(f"Error: {e}")
        
        # Execute following code after finishing
        finally:
            client_socket.close()


def main():
    server = TransferServer()
    server.parse()
    server.start()


# Start check
if __name__ == '__main__':
    main()

