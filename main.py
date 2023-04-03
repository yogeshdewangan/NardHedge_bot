import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import MetaTrader5 as mt

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import trader

import logging

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s')
s = Service(ChromeDriverManager().install())
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=s, chrome_options=options)
driver.maximize_window()

sl_pip = 40
tp_pip = 120


def start():
    driver.get("https://www.investing.com/technical/technical-summary")

    technical_summary_table = driver.find_element(By.XPATH, value='//*[@id="technical_summary_container"]/table')
    technical_summary_rows = technical_summary_table.find_elements(By.TAG_NAME, value="tr")

    technical_summary_rows = technical_summary_rows[1:]

    currency_pairs_dic = {}
    pair_index = 0
    summary_index = 2
    for index in range(0, len(technical_summary_rows) // 3):
        found = False
        if "Moving Averages:" in technical_summary_rows[pair_index].text:
            currency_pair = technical_summary_rows[pair_index].text.split('\n')[0].replace('/', '')
            current_price = technical_summary_rows[pair_index].text.split('\n')[1]
            found = True

        if "Summary:" in technical_summary_rows[summary_index].text and found:
            strong_buy_count = technical_summary_rows[summary_index].text.count("Strong Buy")
            strong_sell_count = technical_summary_rows[summary_index].text.count("Strong Sell")
            if strong_buy_count == 4:
                buy_or_sell = "BUY"
            elif strong_sell_count == 4:
                buy_or_sell = "SELL"
            else:
                buy_or_sell = "Neutral"
            pair_index = pair_index + 3
            summary_index = summary_index + 3
            if buy_or_sell != "Neutral":
                currency_suggestion_list = {"price": current_price, "BuyOrSell": buy_or_sell}
                currency_pairs_dic[currency_pair] = currency_suggestion_list

    driver.get("https://www.investing.com/technical/commodities-technical-summary")

    technical_summary_table = driver.find_element(By.XPATH, value='//*[@id="technical_summary_container"]/table')
    technical_summary_rows = technical_summary_table.find_elements(By.TAG_NAME, value="tr")

    technical_summary_rows = technical_summary_rows[1:]

    pair_index = 0
    summary_index = 2
    for index in range(0, len(technical_summary_rows) // 3):
        found = False
        if "Moving Averages:" in technical_summary_rows[pair_index].text:
            commodity = technical_summary_rows[pair_index].text.split('\n')[0]
            if commodity == "Gold":
                commodity = "XAUUSD"
            if commodity == "Silver":
                commodity = "XAGUSD"
            if commodity == "Copper":
                commodity = "XCUUSD"
            if commodity == 'Natural Gas':
                commodity = 'XTIUSD'
            current_price = technical_summary_rows[pair_index].text.split('\n')[1]
            found = True

        if "Summary:" in technical_summary_rows[summary_index].text and found:
            strong_buy_count = technical_summary_rows[summary_index].text.count("Strong Buy")
            strong_sell_count = technical_summary_rows[summary_index].text.count("Strong Sell")
            if strong_buy_count == 4:
                buy_or_sell = "BUY"
            elif strong_sell_count == 4:
                buy_or_sell = "SELL"
            else:
                buy_or_sell = "Neutral"
            pair_index = pair_index + 3
            summary_index = summary_index + 3
            if buy_or_sell != "Neutral":
                currency_suggestion_list = {"price": current_price, "BuyOrSell": buy_or_sell}
                currency_pairs_dic[commodity] = currency_suggestion_list

    return currency_pairs_dic


def buy_pending(price, lot, comment):
    buy_order_type = mt.ORDER_TYPE_BUY_STOP
    buy_sl_pip = sl_pip
    buy_tp_pip = tp_pip
    buy_action = mt.TRADE_ACTION_PENDING
    return trader.place_order(symbol, buy_order_type, buy_sl_pip, buy_tp_pip,
                       comment, lot, buy_action, price)


def sell_pending(price, lot, comment):
    sell_order_type = mt.ORDER_TYPE_SELL_STOP
    sell_sl_pip = sl_pip
    sell_tp_pip = tp_pip
    sell_action = mt.TRADE_ACTION_PENDING
    return trader.place_order(symbol, sell_order_type, sell_sl_pip, sell_tp_pip,
                       comment, lot, sell_action, price)


def check_and_close_all_pending_and_active_position_if_target_price_hit(symbol1, buy_target_price1, sell_target_price1):
    current_price_ask = trader.get_current_price(symbol1, 0)
    current_price_bid = trader.get_current_price(symbol1, 1)
    if current_price_ask > buy_target_price1 or current_price_bid < sell_target_price1 :
        trader.close_all_positions()
        trader.close_all_pending_orders()
        return True
    return False


def place_pending_order(previous_order_comment, next_order_comment, lot, order_type):
    if order_type == "sell_pending":
        if trader.get_position_by_comment(previous_order_comment) and not trader.is_position_or_pending_order_exists(next_order_comment):
            order, sl, tp, ask_price, bid_price, price = sell_pending(sell_price, lot, next_order_comment)
            return order
    if order_type == "buy_pending":
        if trader.get_position_by_comment(previous_order_comment) and not trader.is_position_or_pending_order_exists(next_order_comment):
            order, sl, tp, ask_price, bid_price, price = buy_pending(buy_price, lot, next_order_comment)
            return order



if __name__ == '__main__':

    api_endpoint = 'https://api.telegram.org/bot5323691147:AAGFEy7Z88lylRzF5390eI6KnGLRqA4HTfw/sendmessage?chat_id' \
                   '=-635280485&text="signal" '
    while True:
        # try:
        #     profit = trader.get_current_profit()
        #     # print("Profit: " + str(profit))
        #     if profit > 5:
        #         trader.close_all_positions()
        # except:
        #     print('Unable to get profit or close positions')
        #     time.sleep(600)
        #
        # from datetime import datetime
        #
        # day = datetime.today().isoweekday()
        # if day == 6 or day == 7:
        #     continue
        symbol = ""
        buy_or_sell = ""
        pair_dic = start()
        print(pair_dic)
        if pair_dic != {}:
            for pair in pair_dic:
                symbol = pair
                buy_or_sell = pair_dic[symbol]["BuyOrSell"]
                break
        # symbol= 'EURUSD'
        # buy_or_sell = "SELL"
        print(symbol + " " + buy_or_sell)

        if symbol is not None:
            symbol = symbol.replace('/', '')

            point = mt.symbol_info(symbol).point

            buy_price = 0.0
            sell_price = 0.0
            buy_target_price = 0.0
            sell_target_price = 0.0

            if buy_or_sell == "BUY":
                ########### FIRST ORDER ##############
                order_type = mt.ORDER_TYPE_BUY
                lot = 1.0
                action = mt.TRADE_ACTION_DEAL
                if not trader.is_position_or_pending_order_exists("1 order"):
                    order, sl, tp, ask_price, bid_price, price = trader.place_order(symbol, order_type, sl_pip, tp_pip,
                                                                             "1 order", lot, action)
                if order is not None:
                    buy_price = ask_price
                    buy_target_price = tp
                    buy_price = price

                    ########### SECOND ORDER #############
                    sell_price = sl
                    lot = 1.4
                    if not trader.is_position_or_pending_order_exists("2 order"):
                        order, sl, tp, ask_price, bid_price, price = sell_pending(sell_price, 1.4, "2 order")
                        if order is not None:
                            sell_target_price = tp
                            sell_price = price

                            while True:
                                try:
                                    if check_and_close_all_pending_and_active_position_if_target_price_hit(symbol, buy_target_price, sell_target_price): break

                                    if place_pending_order("9 order", "10 order", 7.7, "sell_pending") is not None: continue
                                    if place_pending_order("8 order", "9 order", 5.8, "buy_pending") is not None: continue
                                    if place_pending_order("7 order", "8 order", 4.4, "sell_pending") is not None: continue
                                    if place_pending_order("6 order", "7 order", 3.3, "buy_pending") is not None: continue
                                    if place_pending_order("5 order", "6 order", 2.5, "sell_pending") is not None: continue
                                    if place_pending_order("4 order", "5 order", 1.9, "buy_pending") is not None: continue
                                    if place_pending_order("3 order", "4 order", 1.4, "sell_pending") is not None: continue
                                    if place_pending_order("2 order", "3 order", 1.0, "buy_pending") is not None: continue

                                except Exception as e:
                                    print(e)
                                time.sleep(.5)

            if buy_or_sell == "SELL":
                ########### FIRST ORDER ##############
                order_type = mt.ORDER_TYPE_SELL
                lot = 1.0
                action = mt.TRADE_ACTION_DEAL
                if not trader.is_position_or_pending_order_exists("1 order"):
                    order, sl, tp, ask_price, bid_price, price = trader.place_order(symbol, order_type, sl_pip, tp_pip,
                                                                                "1 order", lot, action)
                if order is not None:
                    sell_price = bid_price
                    sell_target_price = tp
                    sell_price = price

                    ########### SECOND ORDER #############
                    buy_price = sl
                    lot = 1.4
                    if  not trader.is_position_or_pending_order_exists("2 order"):
                        order, sl, tp, ask_price, bid_price, price = buy_pending(buy_price, 1.4, "2 order")
                        if order is not None:
                            buy_target_price = tp
                            buy_price = price

                            while True:
                                try:
                                    if check_and_close_all_pending_and_active_position_if_target_price_hit(symbol, buy_target_price, sell_target_price): break

                                    if place_pending_order("9 order", "10 order", 7.7, "buy_pending") is not None: continue
                                    if place_pending_order("8 order", "9 order", 5.8, "sell_pending") is not None: continue
                                    if place_pending_order("7 order", "8 order", 4.4, "buy_pending") is not None: continue
                                    if place_pending_order("6 order", "7 order", 3.3, "sell_pending") is not None: continue
                                    if place_pending_order("5 order", "6 order", 2.5, "buy_pending") is not None: continue
                                    if place_pending_order("4 order", "5 order", 1.9, "sell_pending") is not None: continue
                                    if place_pending_order("3 order", "4 order", 1.4, "buy_pending") is not None: continue
                                    if place_pending_order("2 order", "3 order", 1.0, "sell_pending") is not None: continue

                                except Exception as e:
                                    print(e)
                                time.sleep(.5)

        time.sleep(1)
