import MetaTrader5 as mt
import pandas as pd
import plotly.express as px
from datetime import datetime

mt.initialize()

##### Real
# login = 47824549
# password = "TyVAWetE"
# server = "OctaFX-Real2"

# ##### Demo
# login = 211630405
# password = "e#Y#a$Ez"
# server = "OctaFX-Demo"

# login = 78725701
# password = "Robot123"
# server = "Exness-MT5Trial7"

# ##### Demo
login = 48051634
password = "YhuSEhur"
server = "OctaFX-Demo"

tp_pip = 150
sl_pip = 0.0
lot = 0.01

mt.login(login, password, server)

account_info = mt.account_info()
print(account_info)

print()
print("Login: ", account_info.login)
print("Balance: ", account_info.balance)
print("Equity: ", account_info.equity)

num_symbols = mt.symbols_total()
print("No. of symbols: ", num_symbols)

symbols = mt.symbols_get()

print(mt.positions_total())


def get_current_price(symbol, type):
    return mt.symbol_info_tick(symbol).ask if type == 0 else mt.symbol_info_tick(symbol).bid


def get_current_profit():
    profit = 0
    positions = mt.positions_get()
    for position in positions:
        profit += position.profit
    return profit


def is_position_exist(symbol, buy_or_sell):
    positions = mt.positions_get()
    if buy_or_sell == 'BUY':
        type = 0
    else:
        type = 1
    for position in positions:
        if position.symbol == symbol and position.type == type:
            return True;
    return False


def get_pending_order_by_comment(comment):
    orders = mt.orders_get()
    for order in orders:
        if order.comment == comment:
            return True
    return False


def get_position_by_comment(comment):
    positions = mt.positions_get()
    for position in positions:
        if position.comment == comment:
            return True
    return False


def is_position_or_pending_order_exists(comment):
    if get_pending_order_by_comment(comment) or get_position_by_comment(comment):
        return True
    return False


def close_all_positions():
    positions = mt.positions_get()
    for position in positions:
        request = {
            "action": mt.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "position": position.ticket,
            "type": 1 if position.type == 0 else 0,
            "price": mt.symbol_info_tick(position.symbol).ask if type == 0 else mt.symbol_info_tick(
                position.symbol).bid,
            "deviation": 20,
            "type_time": mt.ORDER_TIME_GTC,
            # "type_filling": mt.ORDER_FILLING_RETURN,
        }
        order = mt.order_send(request)

    positions = mt.positions_get()
    if len(positions) == 0:
        print("All position closed")
        return True
    return False


def close_all_pending_orders():
    orders = mt.orders_get()
    for order in orders:
        if order.type == mt.ORDER_TYPE_BUY_LIMIT or order.type == mt.ORDER_TYPE_SELL_LIMIT or \
                order.type == mt.ORDER_TYPE_BUY_STOP or order.type == mt.ORDER_TYPE_SELL_STOP:
            close_request = {
                "action": mt.TRADE_ACTION_REMOVE,
                "symbol": order.symbol,
                "type": mt.ORDER_TYPE_CLOSE_BY,
                "order": order.ticket,
                "magic": order.magic,
                "comment": "Close all pending orders"
            }
            result = mt.order_send(close_request)
            if result.retcode != mt.TRADE_RETCODE_DONE:
                print(f"Failed to close order {order.ticket}. Error code: {result.retcode}")

    orders = mt.orders_get()
    if len(orders) == 0:
        print("All pending orders closed")
        return True
    return False


def place_order(symbol, order_type, stop_loss_pip=sl_pip, target_pip=tp_pip, comment="", lot_size=lot,
                action=mt.TRADE_ACTION_DEAL, price=None):
    point = mt.symbol_info(symbol).point
    ask_price = mt.symbol_info_tick(symbol).ask
    bid_price = mt.symbol_info_tick(symbol).bid

    decimal_count = len(str(ask_price).split('.')[1])

    if action == mt.TRADE_ACTION_PENDING and price is not None:
        if order_type == mt.ORDER_TYPE_BUY_STOP or order_type == mt.ORDER_TYPE_BUY_LIMIT:
            sl = price - stop_loss_pip * point
            tp = price + target_pip * point
        if order_type == mt.ORDER_TYPE_SELL_STOP or order_type == mt.ORDER_TYPE_SELL_LIMIT:
            sl = price + stop_loss_pip * point
            tp = price - target_pip * point
    else:
        if order_type == mt.ORDER_TYPE_BUY:
            sl = ask_price - stop_loss_pip * point
            tp = ask_price + target_pip * point
        if order_type == mt.ORDER_TYPE_SELL:
            sl = bid_price + stop_loss_pip * point
            tp = bid_price - target_pip * point

    sl = round(sl, decimal_count)
    tp = round(tp, decimal_count)

    if price is None:
        price = mt.symbol_info_tick(symbol).ask if order_type == 0 else mt.symbol_info_tick(symbol).bid
    price = round(price, decimal_count)

    request = {
        "action": action,
        "symbol": symbol,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": 0.0,
        "tp": tp,
        "deviation": 6,
        "magic": 199621147,
        "comment": comment,
        "type_time": mt.ORDER_TIME_GTC
    }

    order = mt.order_send(request)
    if order.retcode == mt.TRADE_RETCODE_DONE:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print((dt_string + " Order placed: " + symbol + " " + ("BUY" if order_type == 0 else "SELL")) + " " + str(action))

        return order, sl, tp, ask_price, bid_price, price
    return None, None, None, None, None, None
