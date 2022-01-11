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

To generate the secrets you can use **SecretGenerator.py**.
