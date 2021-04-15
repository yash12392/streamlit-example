from jugaad_data.nse import NSELive
import pandas as pd
import streamlit as st
import warnings, time
import datetime
from dateutil.relativedelta import *
from jugaad_data.holidays import holidays
from download import download_button

warnings.filterwarnings("ignore")

def get_live_price(ticker, expiryDate):
    
    placeholder1.info(f"Getting Live Price for Ticker: {ticker}")

    n = NSELive()
    index_fut = ['NIFTY', 'BANKNIFTY']

    if ticker not in price_dict.keys():
        if ticker not in index_fut:
            quotes = n.stock_quote_fno(ticker)
            
            for quote in quotes['stocks']:
                if quote['metadata']['instrumentType'] == 'Stock Futures':
                    if quote['metadata']['expiryDate'] == expiryDate:
                        last_px = quote['metadata']['lastPrice']
                        price_dict[ticker] = last_px
        else:
            quotes = n.eq_derivative_turnover()
            for q in quotes['value']:
                if (q['underlying'] == ticker) & (q['instrumentType'] == 'FUTIDX'):
                    last_px = q['lastPrice']
                    price_dict[ticker] = last_px
    else:
        last_px = price_dict[ticker]
                    
    return last_px

def pnl(pnl, qty, avg_rate, current_rate):
    if pnl == 0:
        return (current_rate - avg_rate)*(qty)
    else:
        return pnl

def return_live_file(df, expiryDate):

    df.columns = df.columns.str.strip(' ')
    df['Notional/BookedP/L'] = df['Unnamed: 29']
    df = df[['Script', 'BalQty', 'Amount', 'Avg Rate', 'Current Rate', 'Notional/BookedP/L']]

    df = df[df['Script'].notna()]

    df['Current Rate'] = df.apply(lambda x: get_live_price(x['Script'], expiryDate), axis=1)
    df['Notional/BookedP/L'] = df.apply(lambda x: pnl(x['Notional/BookedP/L'], x['BalQty'], x['Avg Rate'], x['Current Rate']), axis=1)

    df.reset_index(drop=True, inplace=True)

    df = df.append(df.sum(numeric_only=True), ignore_index=True)

    df['Script'].iloc[-1] = 'Total'
    df['BalQty'].iloc[-1] = 0
    df['Avg Rate'].iloc[-1] = 0
    df['Current Rate'].iloc[-1] = 0

    return df

def get_last_thursday():
    end_of_month = datetime.datetime.today() + relativedelta(day=31)
    last_thursday = end_of_month + relativedelta(weekday=TH(-1))

    holiday_list = holidays(datetime.datetime.now().year, datetime.datetime.now().month)

    if last_thursday in holiday_list:
        day_before_last_thursday = last_thursday.date() - relativedelta(days=1)
        if day_before_last_thursday in holiday_list:
            two_day_before_last_thursday = day_before_last_thursday.date() - relativedelta(days=1)
            return two_day_before_last_thursday
    else:
        return last_thursday


if __name__ == '__main__':

    global price_dict

    price_dict = {}

    st.header("Welcome :sunglasses:")

    uploaded_file = st.file_uploader(label = "Please upload the Trade File in .XLS format and Run The Code",
                                         type = ['xls'])

    last_thursday = get_last_thursday()
    max_date = datetime.datetime.today() + relativedelta(days=91)

    if uploaded_file is not None:
        date1 = st.date_input(label = 'Please Select Expiry Date', min_value = last_thursday,
                                value = last_thursday, max_value = max_date)

        expiryDate = date1.strftime("%d-%b-%Y")

        checkbox = st.checkbox(label = "Run The Code", value = False)
        placeholder1 = st.empty()
        placeholder1.info("Please Note that for NIFTY & BANKNIFTY, Nearest Expiry is taken and for Stock F&O, you can select any of the Next Two Expiries.")

        if checkbox:
            placeholder1.info("Code Has Started Running")
            time.sleep(0.5)
            
            df = pd.read_excel(uploaded_file, skiprows=8)

            placeholder1.success("The Uploaded File Has been Captured Into The Program.")

            try:
                newDf = return_live_file(df, expiryDate)
            except UnboundLocalError:
                placeholder1.error("Please Note Only Last Thursday of Trading Month Can be Selected, If Last Thursday is Holiday, Please Select Previous Working Day.")

            placeholder1.success("Your File Has Been Populated with Live Prices, You will get a Download Option Below the Table.")
            
            try:
                st.table(newDf)

                download_button_str = download_button(newDf, 'live_prices.csv', 'Click to Download!')

                st.markdown(download_button_str, unsafe_allow_html=True)
            except NameError:
                placeholder1.error("Please Note Only Last Thursday of Trading Month Can be Selected, If Last Thursday is Holiday, Please Select Previous Working Day.")

