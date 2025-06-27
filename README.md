# Bla Bla Bla Protocol

The connection should work as follows:
```mermaid
sequenceDiagram
    Client_1->>Server: Starts connection with the Server
    Server->>Client_1: Accepts the connection
    Client_2->>Server: Starts connection with the Server
    Server->>Client_2: Accepts the connection
```

After the socket connection is established, the encryption keys should be set up. The procces goes as follows:
```mermaid
sequenceDiagram
    Client_1->>Server: Sends rsa public key to the Server created by Client_1
    Server->>Client_1: Sends rsa-encrypted aes key for communication with Client_1 during in the rest of the connection
    Client_2->>Server: Sends rsa public key to the Server created by Client_2
    Server->>Client_2: Sends rsa-encrypted aes key for communication with Client_2 during the rest of the connection
    Client_1->>Server: Sends aes encrypted message
    Server->>Client_1: Sends aes encrypted message
    Client_2->>Server: Sends aes encrypted message
    Server->>Client_2: Sends aes encrypted message
```

The rest of the connection should go on as follows:
```mermaid
sequenceDiagram    
    Client_1->>Server: Sends a message to the Server
    Server->>Client_1: Confirms the message was sent
    Server->>Client_2: Sends the message to Client_2
    Client_2->>Server: Confirms the message was received
    Server->>Client_1: Confirms the message was received by Client_2
    Client_2->>Server: [WHEN WINDOW IS OPEN] Confirms the message was read
    Server->>Client_1: Confirms the message was read by Client_2

    Client_2->>Server: Sends a message to the Server
    Server->>Client_2: Confirms the message was sent
    Server->>Client_1: Sends the message to Client_2
    Client_1->>Server: Confirms the message was received
    Server->>Client_2: Confirms the message was received by Client_2
    Client_1->>Server: [WHEN WINDOW IS OPEN] Confirms the message was read
    Server->>Client_2: Confirms the message was read by Client_2

    Client_1->>Server: Sends leaving request 
    Server->>Client_2: Sends leaving confirmation
    Server->>Client_1: Sends leaving confirmation  
    Client_1->>Server: Closes connection 
    Client_2->>Server: Closes connection 

```

# Bla Bla Bla Chat
A cross-platform chat application designed to run on a local network using sockets, following a client-server architecture.

## Development Setup
To set up the development environment, follow the steps below.

1. Create a Virtual Environment
Ensure you are in the root directory of the project and that a requirements.txt file is present. Python must be installed. Then, create a virtual environment named .venv:

```bash
python -m venv .venv
```

2. Activate the Virtual Environment
Activate the environment according to your operating system:

#### On Windows (Command Prompt):
```cmd
.venv\Scripts\activate
```

#### On Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

#### On macOS/Linux:
```bash
source .venv/bin/activate
```

3. Install Project Dependencies
With the virtual environment activated, install all required dependencies using:

```bash
pip install -r requirements.txt
```

In case any error arises, try updating pip. If the error persists, try removing the versions from requirements.txt, leaving only the name of the dependencies, but be aware that version compatibility issues might arise. 

### Starting the application
In order to start the application locally for testing purposes, execute start_on_windows.bat (for Windows users) or start_on_linux.sh (for Linux users). Those scripts will open three terminal windows: one for the server to control the chat and two clients to interact with it.

## User Instructions
To use this application as an end user, no development setup is required, though Python programming language should be installed. Simply run the provided executables or follow the usage instructions in the appropriate section. This segment of the documentation will be expanded with step-by-step guide.

For the application to work, you must [NO FIM VAMOS TER QUE MANDAR O USUÁRIO INSTALAR TUDO OU ENTÃO GERAMOS EXECUTÁVEIS]

### Starting the application