import os
import random
import base64
import streamlit as st
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import yfinance as yf

########### Define your variables

#Site parameters
#tabtitle='$$$'
st.title('The Prospector')
ticker = st.text_input(label='Ticker')

#Data parameters
period = '1d'
interval = '1m'
mov_avg_window=21

#Download data
try:
    data = yf.download(tickers=ticker, period=period, interval=interval,
                       progress=False, show_errors=False)
except:
    st.error('Please enter a valid input')
    st.stop()


# if data.empty:
#     st.error('Please enter a valid input')

try:
    data.index = data.index.tz_convert('America/Los_Angeles')
except:
    st.error('Please enter a valid input')
    st.stop()

#Calculate Moving Average and Ballinger Bands
mov_avg_title = str(mov_avg_window) + 'd Moving Avg'
data[mov_avg_title] = data['Close'].rolling(window=mov_avg_window).mean()
data['Upper Band'] = data[mov_avg_title] + 1.96*data['Close'].rolling(window=mov_avg_window).std()
data['Lower Band'] = data[mov_avg_title] - 1.96*data['Close'].rolling(window=mov_avg_window).std()

#declare figure
fig = go.Figure()

fig.add_trace(go.Scatter(x=data.index, y= data[mov_avg_title],
                         line=dict(color='blue', width=.7),
                         name = mov_avg_title))
fig.add_trace(go.Scatter(x=data.index, y= data['Upper Band'],
                         line=dict(color='red', width=1.5),
                         name = 'Upper Band (Sell)'))
fig.add_trace(go.Scatter(x=data.index, y= data['Lower Band'],
                         line=dict(color='green', width=1.5),
                         name = 'Lower Band (Buy)'))

#Candlestick
fig.add_trace(go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'], name = 'market data'))

# Add titles
fig.update_layout(
    title=ticker.upper(),
    yaxis_title='Stock Price')

# X-Axes
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=15, label="15m", step="minute", stepmode="backward"),
            dict(count=45, label="45m", step="minute", stepmode="backward"),
            dict(count=3, label="3h", step="hour", stepmode="backward"),
            dict(label=period, step="all")
        ])
    )
)

#Select random buy gif
buy_path = 'assets/buy/'
files = os.listdir(buy_path)

file_ = open(buy_path + random.choice(files), "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="buy gif">',
    unsafe_allow_html=True,
)

st.plotly_chart(fig)