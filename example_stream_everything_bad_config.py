#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: example_stream_everything_bad_config.py
#
# Part of ‘UNICORN Binance WebSocket API’
# Project website: https://github.com/oliver-zehentleitner/unicorn-binance-websocket-api
# Documentation: https://oliver-zehentleitner.github.io/unicorn-binance-websocket-api
# PyPI: https://pypi.org/project/unicorn-binance-websocket-api/
#
# Author: Oliver Zehentleitner
#         https://about.me/oliver-zehentleitner
#
# Copyright (c) 2019, Oliver Zehentleitner
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import logging
import os
import requests
import sys
import time
import threading

try:
    from binance.client import Client
except ImportError:
    print("Please install `python-binance`!")
    sys.exit(1)

print("This is a bad config and will cause a lot of reconnects")
exit(0)


# https://docs.python.org/3/library/logging.html#logging-levels
logging.basicConfig(level=logging.INFO,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")


def print_stream_data_from_stream_buffer(binance_websocket_api_manager):
    while True:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if oldest_stream_data_from_stream_buffer is not False:
            pass
        else:
            time.sleep(0.01)


binance_api_key = ""
binance_api_secret = ""

channels = {'aggTrade', 'trade', 'kline_1m', 'kline_5m', 'kline_15m', 'kline_30m', 'kline_1h', 'kline_2h', 'kline_4h',
            'kline_6h', 'kline_8h', 'kline_12h', 'kline_1d', 'kline_3d', 'kline_1w', 'kline_1M', 'miniTicker',
            'ticker', 'bookTicker', 'depth5', 'depth10', 'depth20', 'depth', 'depth@100ms'}
arr_channels = {'!miniTicker', '!ticker', '!bookTicker'}
markets = []

try:
    binance_rest_client = Client(binance_api_key, binance_api_secret)
    binance_websocket_api_manager = BinanceWebSocketApiManager()
except requests.exceptions.ConnectionError:
    print("No internet connection?")
    sys.exit(1)

# start a worker process to move the received stream_data from the stream_buffer to a print function
worker_thread = threading.Thread(target=print_stream_data_from_stream_buffer, args=(binance_websocket_api_manager,))
worker_thread.start()

data = binance_rest_client.get_all_tickers()
for item in data:
    markets.append(item['symbol'])

binance_websocket_api_manager.set_private_api_config(binance_api_key, binance_api_secret)
userdata_stream_id = binance_websocket_api_manager.create_stream(["!userData"], ["arr"])
arr_stream_id = binance_websocket_api_manager.create_stream(arr_channels, "arr")

number_of_channels = len(channels)
subscription_limit_per_stream = binance_websocket_api_manager.get_limit_of_subscriptions_per_stream()
markets_per_stream = int(subscription_limit_per_stream / number_of_channels)
stream_list_of_all_markets = []

temp_markets = []
for market in markets:
    temp_markets.append(market)
    if len(temp_markets) == markets_per_stream:
        stream_list_of_all_markets.append(binance_websocket_api_manager.create_stream(channels, temp_markets))
        temp_markets = []
if len(temp_markets) != 0:
    stream_list_of_all_markets.append(binance_websocket_api_manager.create_stream(channels, temp_markets))

while True:
    binance_websocket_api_manager.print_summary()
    time.sleep(1)
