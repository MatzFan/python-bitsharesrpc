# python-bitsharesrpc
Python module for the BitShares client

# Requirements
* python-requests

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
