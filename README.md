# SecureMess
SecureMess is a bunch of unreadable code... But also a Messanger meant for private and security-oriented use.

## Installation:
to use the server / client just put a file named **config.json** in the SecureMess directory.
The content of the file should look like this:

```Json
{
  "server_secret": "<your-server-secret>",
  "client_secret": "<your-client-secret>"
}
```
(the server doesn't need *client_secret* since it is used to encrypt the
text messages sent, the client needs both, since *server_secret* is used for
the communication between server and client)

To generate the secrets you can use **SecretGenerator.py**.

## Customization
Every client can set its own Join / leave message. To do this you have to edit **HELLO_MES**
ans **BYE_MES** found in *core/client.py*
