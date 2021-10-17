from cBot_perp_ftx import cBot_perp_ftx
import ta
import pandas as pd

ftx = cBot_perp_ftx(
        apiKey='',
        secret='',
        subAccountName=''
    )

# -- Strategy variable --
perpSymbol = 'ETH-PERP'
leverage = 2

# -- Price Data --
df = ftx.get_last_historical(perpSymbol, '1h', 250)

# -- indicators --
df['EMA1']=ta.trend.ema_indicator(close=df['close'], window=7)
df['EMA2']=ta.trend.ema_indicator(close=df['close'], window=30)
df['EMA3']=ta.trend.ema_indicator(close=df['close'], window=50)
df['EMA4']=ta.trend.ema_indicator(close=df['close'], window=100)
df['EMA5']=ta.trend.ema_indicator(close=df['close'], window=121)
df['EMA6']=ta.trend.ema_indicator(close=df['close'], window=200)
df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=14, smooth1=3, smooth2=3)

# -- Condition to open Market LONG --
def openLongCondition(row):
    if (row['EMA1'] > row['EMA2'] 
    and row['EMA2'] > row['EMA3'] 
    and row['EMA3'] > row['EMA4'] 
    and row['EMA4'] > row['EMA5'] 
    and row['EMA5'] > row['EMA6'] 
    and row['STOCH_RSI'] < 0.82):
        return True
    else:
        return False

# -- Condition to close Market LONG --
def closeLongCondition(row):
    if row['EMA6'] > row['EMA1']:
        return True
    else:
        return False

# -- Condition to open Market SHORT --
def openShortCondition(row):
    if ( row['EMA6'] > row['EMA5'] 
    and row['EMA5'] > row['EMA4'] 
    and row['EMA4'] > row['EMA3'] 
    and row['EMA3'] > row['EMA2'] 
    and row['EMA2'] > row['EMA1'] 
    and row['STOCH_RSI'] > 0.2 ):
        return True
    else:
        return False

# -- Condition to close Market SHORT --
def closeShortCondition(row):
    if row['EMA1'] > row['EMA6']:
        return True
    else:
        return False

# -- Get USD amount on Sub Account --
usdAmount = ftx.get_balance_of_one_coin('USD')

# -- Get actual price --
actualPrice = df.iloc[-1]['close']

# -- Check if you have no position running --
if len(ftx.get_open_position()) == 0:
    # -- Check if you have to open a LONG --
    if openLongCondition(df.iloc[-2]):
        # -- Cancel all order (stop loss) --
        ftx.cancel_all_open_order(perpSymbol)
        # -- Define the quantity max of token from your usd balance --
        quantityMax = float(usdAmount)/actualPrice
        # -- Create a market order Long --
        longOrder = ftx.place_market_order(
            perpSymbol, 
            'buy', 
            quantityMax, 
            leverage
        )
        print("Open a market LONG at", actualPrice)
        # -- Create a market stop loss -3% --
        stopLoss = ftx.place_market_stop_loss(
            perpSymbol, 
            'sell', 
            quantityMax, 
            actualPrice - 0.03 * actualPrice,
            leverage
        )
        print("Place a Stop Loss at ", actualPrice - 0.03 * actualPrice)

    elif openShortCondition(df.iloc[-2]):
        # -- Cancel all order (stop loss) --
        ftx.cancel_all_open_order(perpSymbol)
        # -- Define the quantity max of token from your usd balance --
        quantityMax = float(usdAmount)/actualPrice
        # -- Create a market order Long --
        shortOrder = ftx.place_market_order(
            perpSymbol, 
            'sell', 
            quantityMax, 
            leverage
        )
        print("Open a market SHORT at", actualPrice)
        # -- Create a market stop loss -3% --
        stopLoss = ftx.place_market_stop_loss(
            perpSymbol, 
            'buy', 
            quantityMax, 
            actualPrice + 0.03 * actualPrice,
            leverage
        )
        print("Place a Stop Loss at", actualPrice + 0.03 * actualPrice)

    else:
        print("No opportunity to take")

else:
    # -- Check if you have a LONG open --
    if ftx.get_open_position(perpSymbol)[0]['side'] == 'buy':
        # -- Check if you have to close your LONG --
        if closeLongCondition(df.iloc[-2]):
            ftx.close_all_open_position(perpSymbol)
            ftx.cancel_all_open_order(perpSymbol)
            print('Close my LONG position')
        else:
            print("A LONG is running and I don't want to stop it")
    # -- Check if you have a SHORT open --
    elif ftx.get_open_position(perpSymbol)[0]['side'] == 'sell':
        if closeShortCondition(df.iloc[-2]):
            ftx.close_all_open_position(perpSymbol)
            ftx.cancel_all_open_order(perpSymbol)
            print('Close my SHORT position')
        else:
            print("A SHORT is running and I don't want to stop it")
