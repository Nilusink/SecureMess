# SecureMess
SecureMess is a bunch of unreadable code... But also a Messenger meant for private and security-oriented use.

## Installation:
to use the server / client just put a file named **config.json** in the SecureMess directory.
The content of the file should look like this:

```Json
{
  "server_secret": "<your-server-secret>",
  "client_secret": "<your-client-secret>"
}
```
(the server doesn't need ```client_secret``` since it is used to encrypt the
text messages sent, the client needs both, since ```server_secret``` is used for
the communication between server and client)

To generate the secrets you can use **SecretGenerator.py**.

### Docker installation:
You can download a docker image of the Server and Client (terminal only since running GUIs with docker is a pain in the a**).

### Server
To run (and download) the Server you need to forward the server port (3333) to the port you wish your server to run on.

Here is an example command: 
```Bash
docker run --rm -it -p <your-port>:3333 nilusink/secure_mess_server:latest
```
If you don't have a specific port you want your server to run on, you can just use 
3333:3333 so it uses the default port. In this example we also use ```--rm```, which 
cleans up the container after running and ```-it``` (interactive terminal) so we get 
live messages. I would recommend using ```--rm```, but ```-it``` is not really needed.

### Client
When running a client, the flag ```-it``` is required, since you wouldn't be able to 
interact with the terminal without it. Since we don't need to forward a port here, 
we can forget about ```-p```.

Here is an example command:
```Bash
docker run --rm -it nilusink/secure_mess_client:latest
```

When using a docker Server and a normal Client, the ```server_secret``` in **config.json** should be the same
as the one in **docker_config.json**!

## Customization
Every client can set its own Join / leave message. To do this you have to edit **HELLO_MES**
ans **BYE_MES** found in *core/client.py*
