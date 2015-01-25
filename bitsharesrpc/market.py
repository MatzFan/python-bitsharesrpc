import bitsharesrpc

class market( bitsharesrpc.client ) :
    def __init__(self, url, user, pwd) :
        bitsharesrpc.client.__init__(self, url, user, pwd)

    def get_asset_id(self, asset):
        return self.blockchain_get_asset(asset)["result"]["id"]

    def get_tx_history( self, name, asset ):
        return self.history(name, asset)["result"]

    def get_precision(self, asset):
        return self.blockchain_get_asset(asset)["result"]["precision"]

    def get_centerprice(self, quote, base):
        return float(self.blockchain_market_status(quote, base)["result"]["center_price"]["ratio"])

    def get_lowest_ask(self, asset1, asset2):
        return float(self.blockchain_market_order_book(asset1, asset2)["result"][1][0]["market_index"]["order_price"]["ratio"])

    def get_lowest_bid(self, asset1, asset2):
        return float(self.blockchain_market_order_book(asset1, asset2)["result"][0][0]["market_index"]["order_price"]["ratio"])
        
    def cancel_bids_less_than(self, account, quote, base, price):
        cancel_args = self.get_bids_less_than(account, quote, base, price)[0]
        response = self.batch("wallet_market_cancel_order", cancel_args)
        return cancel_args

    def get_median(self, asset):
        response = self.blockchain_get_feeds_for_asset(asset)
        feeds = response["result"]
        return feeds[len(feeds)-1]["median_price"]

    def cancel_bids_out_of_range(self, account, quote, base, price, tolerance):
        cancel_args = self.get_bids_out_of_range(account, quote, base, price, tolerance)[0]
        response = self.request("batch", ["wallet_market_cancel_order", cancel_args])
        return cancel_args

    def cancel_asks_out_of_range(self, account, quote, base, price, tolerance):
        cancel_args = self.get_asks_out_of_range(account, quote, base, price, tolerance)[0]
        response = self.request("batch", ["wallet_market_cancel_order", cancel_args])
        return cancel_args

    def get_balance(self, account, asset):
        asset_id = self.get_asset_id(asset) 
        response = self.wallet_account_balance(account, asset)
        if not response:
            return 0
        if "result" not in response() or response()["result"] == None:
            return 0
        asset_array = response()["result"][0][1]
        amount = 0
        for item in asset_array:
            if item[0] == asset_id:
                amount = item[1]
                return amount / self.get_precision(asset)
        return 0

    def cancel_all_orders(self, account, quote, base):
        cancel_args = self.get_all_orders(account, quote, base)
        #response = self.request("batch", ["wallet_market_cancel_order", [cancel_args[0]] ])
        for i in cancel_args[0] :
            response = self.wallet_market_cancel_order(i)
        return cancel_args[1]

    def ask_at_market_price(self, name, amount, base, quote, confirm=False) :
        last_fill      = -1
        response       = self.blockchain_market_order_book(quote, base)
        quotePrecision = self.get_precision(quote)
        basePrecision  = self.get_precision(base)
        orders = []
        for order in response["result"][0]: # bid orders
            order_price  = float(order["market_index"]["order_price"]["ratio"])*(basePrecision / quotePrecision) 
            order_amount = float(order["state"]["balance"]/quotePrecision) / order_price  # denoted in BASE
            if amount >= order_amount : # buy full amount
              orders.append([name, order_amount, base, order_price, quote])
              amount -= order_amount
            elif amount < order_amount: # partial
              orders.append([name, amount, base, order_price, quote])
              break
        for o in orders :
            print( "Selling %15.8f %s for %12.8f %s @ %12.8f" %(o[1], o[2], o[1]*o[3], o[4], o[3]) )
        orders = [ i for i in orders ]
        if not confirm or self.query_yes_no( "I dare you confirm the orders above: ") :
            return self.batch("ask", orders)

    def bid_at_market_price(self, name, amount, base, quote, confirm=False) :
        last_fill      = -1
        response       = self.blockchain_market_order_book(quote, base)
        quotePrecision = self.get_precision(quote)
        basePrecision  = self.get_precision(base)
        orders = []
        for order in response["result"][1]: # ask orders
            order_price  = float(order["market_index"]["order_price"]["ratio"])*(basePrecision / quotePrecision) 
            order_amount = float(order["state"]["balance"]/quotePrecision) / order_price  # denoted in BASE
            if amount >= order_amount : # buy full amount
              orders.append([name, order_amount, base, order_price, quote])
              amount -= order_amount
            elif amount < order_amount: # partial
              orders.append([name, amount, base, order_price, quote])
              break
        for o in orders :
            print( "Buying %15.8f %s for %12.8f %s @ %12.8f" %(o[1], o[2], o[1]*o[3], o[4], o[3]) )
        orders = [ i for i in orders ]
        if not confirm or self.query_yes_no( "I dare you confirm the orders above: ") :
            return self.batch("bid", orders)

    def submit_bid(self, account, amount, quote, price, base):
        response = self.bid(account, amount, quote, price, base)
        if response.status_code != 200:
            log.info("%s submitted a bid" % account)
            log.info(response)
            return False
        else:
            return response
    def submit_ask(self, account, amount, quote, price, base):
        response = self.ask(account, amount, quote, price, base)
        if response.status_code != 200:
            log.info("%s submitted an ask" % account)
            log.info(response)
            return False
        else:
            return response

    def get_bids_less_than(self, account, quote, base, price):
        quotePrecision = self.get_precision( quote )
        basePrecision = self.get_precision( base )
        response = self.wallet_market_order_list(quote, base, -1, account)
        order_ids = []
        quote_shares = 0
        if "result" not in response or response["result"] == None:
            return [[], 0]
        for pair in response["result"]:
            order_id = pair[0]
            item = pair[1]
            if item["type"] == "bid_order":
                if float(item["market_index"]["order_price"]["ratio"])* (basePrecision / quotePrecision) < price:
                    order_ids.append(order_id)
                    quote_shares += int(item["state"]["balance"])
                    log.info("%s canceled an order: %s" % (account, str(item)))
        cancel_args = [item for item in order_ids]
        return [cancel_args, float(quote_shares) / quotePrecision]

    def get_bids_out_of_range(self, account, quote, base, price, tolerance):
        quotePrecision = self.get_precision( quote )
        basePrecision = self.get_precision( base )
        response = self.wallet_market_order_list(quote, base, -1, account)
        order_ids = []
        quote_shares = 0
        if "result" not in response or response["result"] == None:
           return [[], 0]
        for pair in response["result"]:
            order_id = pair[0]
            item = pair[1]
            if item["type"] == "bid_order":
                if abs(price - float(item["market_index"]["order_price"]["ratio"]) * (basePrecision / quotePrecision)) > tolerance:
                    order_ids.append(order_id)
                    quote_shares += int(item["state"]["balance"])
                    log.info("%s canceled an order: %s" % (account, str(item)))
        cancel_args = [item for item in order_ids]
        return [cancel_args, float(quote_shares) / quotePrecision]

    def get_asks_out_of_range(self, account, quote, base, price, tolerance):
        quotePrecision = self.get_precision( quote )
        basePrecision = self.get_precision( base )
        response = self.wallet_market_order_list(quote, base, -1, account)
        order_ids = []
        base_shares = 0
        if "result" not in response or response["result"] == None:
           return [[], 0]
        for pair in response["result"]:
            order_id = pair[0]
            item = pair[1]
            if item["type"] == "ask_order":
                if abs(price - float(item["market_index"]["order_price"]["ratio"]) * (basePrecision / quotePrecision)) > tolerance:
                    order_ids.append(order_id)
                    base_shares += int(item["state"]["balance"])
        cancel_args = [item for item in order_ids]
        return [cancel_args, base_shares / basePrecision]

    def cancel_all_orders(self, account, quote, base):
        cancel_args = self.get_all_orders(account, quote, base)
        for i in cancel_args[0] :
            response = self.wallet_market_cancel_order(i)
        return cancel_args[1]

    def get_all_orders(self, account, quote, base):
        response = self.wallet_market_order_list(quote, base, -1, account)
        order_ids = []
        orders = []
        if "result" in response :
           for item in response["result"]:
               order_ids.append(item[0])
               orders.append(item[1])
           orderids = [item for item in order_ids]
           return [ orderids, orders ]
        return

    def get_last_fill (self, quote, base):
        last_fill = -1
        response = self.blockchain_market_order_history(quote, base, 0, 1)
        for order in response["result"]:
            last_fill = float(order["ask_price"]["ratio"]) 
        return last_fill

    def get_price(self, quote, base):
        response = self.blockchain_market_order_book(quote, base, 1)
        order = response["result"]
        quotePrecision = self.get_precision(quote)
        basePrecision  = self.get_precision(base)
        lowest_bid  = float(order[0][0]["market_index"]["order_price"]["ratio"])*(basePrecision / quotePrecision)
        highest_ask = float(order[1][0]["market_index"]["order_price"]["ratio"])*(basePrecision / quotePrecision)
        return (lowest_bid+highest_ask)/2

    def ask_at_market_price(self, name, amount, base, quote, confirm=False) :
        last_fill      = -1
        response       = self.blockchain_market_order_book(quote, base)
        quotePrecision = self.get_precision(quote)
        basePrecision  = self.get_precision(base)
        orders = []
        for order in response["result"][0]: # bid orders
            order_price  = float(order["market_index"]["order_price"]["ratio"])*(basePrecision / quotePrecision) 
            order_amount = float(order["state"]["balance"]/quotePrecision) / order_price  # denoted in BASE
            if amount >= order_amount : # buy full amount
              orders.append([name, order_amount, base, order_price, quote])
              amount -= order_amount
            elif amount < order_amount: # partial
              orders.append([name, amount, base, order_price, quote])
              break
        for o in orders :
            print( "Selling %15.8f %s for %12.8f %s @ %12.8f" %(o[1], o[2], o[1]*o[3], o[4], o[3]) )
        orders = [ i for i in orders ]
        if not confirm or self.query_yes_no( "I dare you confirm the orders above: ") :
            return self.batch("ask", orders)

    def bid_at_market_price(self, name, amount, base, quote, confirm=False) :
        last_fill      = -1
        response       = self.blockchain_market_order_book(quote, base)
        quotePrecision = self.get_precision(quote)
        basePrecision  = self.get_precision(base)
        orders = []
        for order in response["result"][1]: # ask orders
            order_price  = float(order["market_index"]["order_price"]["ratio"])*(basePrecision / quotePrecision) 
            order_amount = float(order["state"]["balance"]/quotePrecision) / order_price  # denoted in BASE
            if amount >= order_amount : # buy full amount
              orders.append([name, order_amount, base, order_price, quote])
              amount -= order_amount
            elif amount < order_amount: # partial
              orders.append([name, amount, base, order_price, quote])
              break
        for o in orders :
            print( "Buying %15.8f %s for %12.8f %s @ %12.8f" %(o[1], o[2], o[1]*o[3], o[4], o[3]) )
        orders = [ i for i in orders ]
        if not confirm or self.query_yes_no( "I dare you confirm the orders above: ") :
            return self.batch("bid", orders)
