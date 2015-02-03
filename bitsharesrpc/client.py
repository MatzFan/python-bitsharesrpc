"""
  Copyright 2014 Fabian Schuh
  Author:  Fabian Schuh <mail@xeroc.org>
  Licence: GNU Library or Lesser General Public License (LGPL)

  This file is part of bitsharesrpc.

  bitsharesrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import time
import sys

try :
    import requests
except ImportError:
    raise Exception( "Missing dependency: requests" )

try :
    import json
except ImportError:
    raise Exception( "Missing dependency: requests" )

if sys.version > '3' :
    from .market import market
else :
    from market import market

class client(object) :

    def __init__(self, url, user, pwd) :
       self.auth    = (user,pwd)
       self.url     = url
       self.headers = {'content-type': 'application/json'}
       self.market  = market(self) # custom market orders

    def rpcexec(self,payload) :
        try: 
            response = requests.post(self.url, data=json.dumps(payload), headers=self.headers, auth=self.auth)
        except:
            raise Exception("Connection failed! Check host, port, and authentication!")

        try: 
            ret = json.loads(response.text)
        except:
            raise Exception("Error parsing JSON output: %s" % response.text)
        return ret

    def wait_for_block(self):
        response = self.get_info()
        blocknum = response["result"]["blockchain_head_block_num"]
        while True:
            time.sleep(0.1)            
            response = self.get_info()
            blocknum2 = response["result"]["blockchain_head_block_num"]
            if blocknum2 != blocknum:
                return

    def query_yes_no(self, question, default="yes"):
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:    prompt = " [y/n] "
        elif default == "yes": prompt = " [Y/n] "
        elif default == "no":  prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)
        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")              

    def __getattr__(self, name) :
        def method(*args):
           r = self.rpcexec({
               "method": name,
               "params": args,
               "jsonrpc": "2.0",
               "id": 0
           })
           assert "error" not in r, "Client returns error: %s" % r
           return r
        return method
