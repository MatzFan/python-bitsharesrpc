# python-bitsharesrpc
Python module for the BitShares client

# Requirements
* python-requests

# Configuration of the BitSahres client
The BitShares client needs the RPC interface enabled and username, password,
and port set. The relevant port for this module is the port of the
'httpd_endpoint'. Two ways exist to do so:

## Command-line parameters
    ./bitshares_client --server --httpport 5000 --rpcuser test --rpcpassword test

## Configuration file settings
    "rpc": {
	"enable": true,
	"rpc_user": "USERNAME",
	"rpc_password": "PASSWORD",
	"rpc_endpoint": "127.0.0.1:9988",
	"httpd_endpoint": "127.0.0.1:19988", <<--- PORT
	"htdocs": "./htdocs"
    },
    
# Usage
All RPC commands of the BitShares client are exposed as methods in the class
bitsharesrpc. Once an instance of bitsharesrpc is created, i.e.,

    import bitsharesrpc
    import config
    rpc = bitsharesrpc.client(config.url, config.user, config.passwd)

any rpc command can be issued using the instance via the syntax
rpc.*command*(*parameters*). Example:

    rpc.get_info()
    rpc.open_wallet("default")
    rpc.ask(account, amount, quote, price, base)
    ...

## Example to unlock the wallet
    #!/usr/bin/python
    import bitsharesrpc
    import config

    if __name__ == "__main__":
     rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
     print(rpc.wallet_open(config.wallet))
     print(rpc.unlock(999999, config.unlock))

## Example to lock the wallet

    #!/usr/bin/python
    import bitsharesrpc
    import config

    if __name__ == "__main__":
     rpc = bitsharesrpc.client(config.url, config.user, config.passwd)
     print rpc.wallet_open("delegate")
     print rpc.lock()
