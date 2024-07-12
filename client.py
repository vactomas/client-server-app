# File transfer client

# Imports
import os
import socket
import argparse
import tqdm
import time


# Custom FileExistsError exception
class FileExistsError(Exception):
    pass


# File Transfer Client Class
class TransferClient:
    
    # Key parametres - set by parse()
    HOST = None
    PORT = None
    FILE = None
    BUFFER_SIZE = None
    FILESIZE = None
    PROGRESS = None
    
    # Init client
    def __init__(self):
        super().__init__()
        self.parser = argparse.ArgumentParser(description="File transfer client")
        self.parser.add_argument("-a", "--host", type=str, default="0.0.0.0", help="Server host address")
        self.parser.add_argument("-p", "--port", type=int, default=2222, help="Server port")
        self.parser.add_argument("-f", "--file", type=str, help="File location.")
        self.parser.add_argument("-b", "--buffer_size", type=int, default=4096, help="Set buffer size, default value 4096.")    
   
    
    # Parse arguments and set corresponding variables
    def parse(self, args=None):
        options = self.parser.parse_args(args)
        self.HOST = options.host
        self.PORT = options.port
        self.FILE = options.file
        self.BUFFER_SIZE = options.buffer_size
        return self

    
    # Connect and send
    def send(self):

        self.connect()
        self.send_file()

    
    # Connect to server
    def connect(self):

        # Create client_socket and connect to server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT))
        

    # Send file in 'insecure' mode
    def send_file(self):
        
        # Check if file exists
        if not os.path.exists(self.FILE):
            print(f"[!] Error. File {self.FILE} does not exist.")
            return
    
        # Send file
        try:
            self.client_socket.sendall(self.FILE.encode())

            time.sleep(0.1)

            # Receive confirmation from server
            response = self.client_socket.recv(self.BUFFER_SIZE).decode()
            
            if response == "File Exists":
                raise FileExistsError
            
            # Preparation for progress bar
            self.FILESIZE = os.path.getsize(self.FILE)
            self.PROGRESS = tqdm.tqdm(range(self.FILESIZE), f"Sending {self.FILE}", unit="B", unit_scale=True, unit_divisor=1024)
            
            # Send filesize info
            self.client_socket.sendall(self.FILESIZE.to_bytes(self.BUFFER_SIZE))

            time.sleep(0.1)

            # Open file and send data
            with open(self.FILE, 'rb') as file:
                for data in iter(lambda: file.read(self.BUFFER_SIZE), b''):
                    # Send data packet of size BUFFER_SIZE
                    self.client_socket.sendall(data)
                    
                    # Update progress bar
                    self.PROGRESS.update(len(data))

            self.PROGRESS.close()

            # Receive confirmation from server
            response = self.client_socket.recv(self.BUFFER_SIZE).decode()
            
            if not response == "File transfer successful":
                raise Exception("File wasn't send successfully.")

            print(f"File sent: {self.FILE}")
            
        
        # Handle FileExistsError
        except FileExistsError as e:
            print(f"File {self.FILE} already exists in the server output directory.")

        # Handle exceptions
        except Exception as e:
            print(f"[!] Error: {e}")

        # Close socket after sending file
        finally:
            self.client_socket.close()


if __name__ == "__main__":
    client = TransferClient()
    client.parse()
    client.send()

