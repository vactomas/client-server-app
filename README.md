# Client-Server File Transfer app

This app consists of two main components. The 'server.py' and the 'client.py'.

## Server

To start the server, simply run `python server.py` and the server will start with the default configuration.

To list all possible settings, run `python server.py -h`, which will list all possible arguments. These are:

 - '-h' or '--help' -> Used to list options and usage
 - '-a' or '--host' -> Sets the Server host address (IP, localhost)
 - '-p' or '--port' -> Sets the port the Server listens on
 - '-s' or '--savedir' -> Set the designated save directory
 - '-b' or '--buffer_size' -> Set buffer size

Once the server is running, it will wait for a connection from the client.

## Client

To transfer the file to the server, run `python client.py -f=file_location`. Similarly to the server, the client also gives the option to list usage and options by running `python client.py -h`.

Possible options:

 - '-h' or '--help' -> Used to list options and usage
 - '-a' or '--host' -> Sets the Server host address (IP, localhost)
 - '-p' or '--port' -> Sets the port the Server listens on
 - '-b' or '--buffer_size' -> Set buffer size to the same value as server
