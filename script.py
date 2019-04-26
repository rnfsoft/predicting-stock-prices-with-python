import numpy as np
from datetime import datetime
import smtplib
import time
from selenium import webdriver
import os

from sklearn.linear_model import LinearRegression
from sklearn import preprocessing, svm, cross_validation

from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data

def fileName(file_name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)


def getStocks(n):
    driver = webdriver.Firefox(executable_path = fileName('geckodriver'))
    url = "https://finance.yahoo.com/screener/predefined/aggressive_small_caps?offset=0&count=202"
    driver.get(url)

    stock_list= []
    n += 1

    for i in range(1, n):
        ticker = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[6]/div/div/section/div/div[2]/div[1]/table/tbody/tr[' + str(i) + ']/td[1]/a')
        stock_list.append(ticker.text)
    print (stock_list)
    driver.quit()

    number = 0
    for i in stock_list:
        print("Number: " + str(number))
        try:
            predictData(i, 5)
        except:
            print("Stock: " + i + " was not predicted")
        number += 1

def predictData(stock, days):

    start = datetime(2017, 1, 1)
    end = datetime.now()

    df = get_historical_data(stock, start=start, end=end, output_format='pandas')
    if os.path.exists('./Exports'):
        csv_name = ('Exports/' + stock + '_Export.csv')
    else:
        os.mkdir("Exports")
        csv_name = ('Exports/' + stock + '_Export.csv')
    df.to_csv(csv_name)
    
    df['prediction'] = df['close'].shift(-1)
    print(df)
    df.dropna(inplace=True)

    forecast_time = int(days)
    

    #Predicting the Stock price in the future
    X = np.array(df.drop(['prediction'],1)) #  df.drop(['prediction'], axis=1)
    Y = np.array(df['prediction'])

    X = preprocessing.scale(X)
    X_prediction = X[-forecast_time:]
    X_train, X_test, Y_train, Y_test = cross_validation.train_test_split(X, Y, test_size=0.5)

    #Performing the Regression on the training data
    clf = LinearRegression()
    clf.fit(X_train, Y_train)
    prediction = (clf.predict(X_prediction))

    last_row = df.tail(1)
    print(last_row['close'])

    #Sending the SMS if the predicted price of the stock is at least 1 greater than the previous closing price
    if (float(prediction[4]) > (float(last_row['close']))+1):
        output = ("\n\nStock:" + str(stock) + "\nPrior Close:\n" + str(last_row['close']) + "\n\nPrediction in 1 Day: " + str(
            prediction[0]) + "\nPrediction in 5 Days: " + str(prediction[4]))
        sendMessage(output)


def sendMessage(text):
    username = ''
    password = ''
    vtext = 'phone@vtext.com'
    message = text

    msg = """From: %s
    To: %s
    %s""" % (username, vtext, message)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, vtext, msg)
    server.quit()

    print('Sent')

if __name__ == '__main__':
    getStocks(20)
    #predictData('YELP', 10)