# -*- coding: utf-8 -*-
"""FinalTask_Kalbe_DS_Ghozi Murtadho

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-L0ZbpJViHJmbEGhkfkWOOSh5uTbCaYO

**<h1>Final Task</h1>**
<h2>Virtual Internship Experience Kalbe Nutrisions - Data Science</h2>

Nama : Ghozi Murtadho

Kelas : Kalbe Nutrition - Data Science


Task ini merupakan final project dari rangkaian kegiatan Virtual Internship Experience Rakamain x Kalbe Nutrition.

Data yang digunakan merupakan data penjualan. Dataset yang digunakan terdiri dari dataset customer, store, product, dan transaction.

Pada task ini akan coba dilakukan prediksi penjualan dari hari ke hari menggunakan metode ARIMA dan clustering pada pelanggan.

# Import Data
"""

from google.colab import drive
drive.mount('/content/drive')

# Import library yang akan digunakan
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
from statsmodels.tsa.arima.model import ARIMA
from pandas.plotting import autocorrelation_plot

# Import Dataset from drive
customer = pd.read_csv('/content/drive/MyDrive/02. Work/Internship /Virtual Intern Rakamin x Kalbe - Data Science/customer.csv', sep=';')
store = pd.read_csv('/content/drive/MyDrive/02. Work/Internship /Virtual Intern Rakamin x Kalbe - Data Science/store.csv', sep=';')
transaction = pd.read_csv('/content/drive/MyDrive/02. Work/Internship /Virtual Intern Rakamin x Kalbe - Data Science/transaction.csv', sep=';')
product = pd.read_csv('/content/drive/MyDrive/02. Work/Internship /Virtual Intern Rakamin x Kalbe - Data Science/product.csv', sep=';')

customer

transaction

store
store.to_csv('store.csv')

product
product.to_csv('product.csv')

"""# Data Preprocessing

## Data Cleansing

### a. Cek Duplikasi Data
"""

customer.duplicated().sum() #mengecek duplikasi data pada dataset customer

store.duplicated().sum() #mengecek duplikasi data pada dataset store

transaction.duplicated().sum() #mengecek duplikasi data pada dataset transaction

product.duplicated().sum() #mengecek duplikasi data pada dataset product

"""Dapat disimpulkan tidak terdapat data berulang atau duplikasi data pada dataset customer, store, transaction dan product.

### b. Cek Tipe Data
"""

#cek tipe kolom pada dataset customer, store, transaction dan product
customer.dtypes, store.dtypes, transaction.dtypes, product.dtypes

"""
1. Kolom **"Income"** pada dataset "customer" seharusnya menggunakan **titik** dan tipe data **float**
2. Kolom **"Latitude"** dan **"Longitude"** pada dataset "store" juga masih menggunakan koma, seharusnya **titik** dan tipe data **float**
3. Kolom **"Date"** pada dataset "transaction" diubah menjadi tipe data **datatime**"""

# data cleansing customer
customer['Income'] = customer['Income'].replace('[,]', '.', regex=True).astype('float') # ubah koma menjadi titik dan tipe data menjadi float

# data cleansing store
store['Latitude'] = store['Latitude'].replace('[,]','.', regex=True).astype('float') # ubah koma menjadi titik, dan tipe data menjadi float pada kolom Latitude
store['Longitude'] = store['Longitude'].replace('[,]','.', regex=True).astype('float') # ubah koma menjadi titik, dan tipe data menjadi float pada kolom Longitude

# data cleansing transaction
transaction['Date'] = pd.to_datetime(transaction['Date']) # ubah tipe data Date menjadi datetime

"""## Penggabungan Data"""

df = pd.merge(transaction, customer, on=['CustomerID'])
df = pd.merge(df, product.drop(columns=['Price']), on=['ProductID'])
df = pd.merge(df, store, on=['StoreID'])

df

df.dtypes

"""## Data Understanding"""

transaction['TransactionID'].value_counts()

transaction[transaction['TransactionID'] == 'TR71313']

"""Ada kemungkinan data salah input -->
Solusi : menggunakan data yang paling latest

# Machine Learning Regression (Time Series)

Tujuan dari pembuatan model machine learning ini
adalah untuk dapat memprediksi total quantity harian
dari product yang terjual.
"""

df_regression = df.groupby(['Date']).agg({
    'Qty' : 'sum'
}).reset_index()

df_regression

decomposed = seasonal_decompose(df_regression.set_index('Date'))

plt.figure(figsize=(8, 8))

plt.subplot(311)
decomposed.trend.plot(ax=plt.gca())
plt.title('Trend')
plt.subplot(312)
decomposed.seasonal.plot(ax=plt.gca())
plt.title('Sesonality')
plt.subplot(313)
decomposed.trend.plot(ax=plt.gca())
plt.title('Residuals')

plt.tight_layout()

cut_off = round(df_regression.shape[0] * 0.9)
df_train = df_regression[:cut_off]
df_test = df_regression[cut_off:].reset_index(drop=True)
df_train.shape, df_test.shape

df_train

df_test

plt.figure(figsize=(20,5))
sns.lineplot(data=df_train, x=df_train['Date'], y=df_train['Qty'])
sns.lineplot(data=df_test, x=df_test['Date'], y=df_test['Qty'])

autocorrelation_plot(df_regression['Qty']) #melakukan uji statisioneritas menggunakan autocorrelation function

def rmse(y_actual, y_pred):

  print(f'RMSE value {mean_squared_error(y_actual, y_pred)**0.5}')

def eval(y_actual, y_pred):
  rmse(y_actual, y_pred)
  print(f'MAE value {mean_absolute_error(y_actual, y_pred)}')

# ARIMA Model
df_train = df_train.set_index('Date')
df_test = df_test.set_index('Date')

y = df_train['Qty']

ARIMAmodel = ARIMA(y, order = (40, 2, 2))
ARIMAmodel = ARIMAmodel.fit()

y_pred = ARIMAmodel.get_forecast(len(df_test))

y_pred_df = y_pred.conf_int()
y_pred_df['predictions'] = ARIMAmodel.predict(start =y_pred_df.index[0], end =y_pred_df.index[-1])
y_pred_df.index = df_test.index
y_pred_out = y_pred_df['predictions']
eval(df_test['Qty'], y_pred_out)

plt.figure(figsize = (20, 5))
plt.plot(df_train['Qty'])
plt.plot(df_test['Qty'], color='red')
plt.plot(y_pred_out, color='black', label = 'ARIMA Predictions')
plt.legend()



"""# Machine Learning Clustering

Tujuan dari pembuatan model machine learning ini
adalah untuk dapat membuat cluster
customer-customer yang mirip.
"""

df.head()

# Identifikasi kolom-kolom yang redundent/corelasi tinggi
df.corr()

"""kolom yang tidak redundant dan minim ketergantungan dengan kolom lain akan dijadikan featur untuk parameter klustering. Adapun kolom tersebut adalaah kolom "TransactionID" dan "Qty"."""

df_cluster = df.groupby(['CustomerID']).agg({
    'TransactionID' : 'count',
    'Qty' : 'sum'
}).reset_index()

df_cluster.head()

data_cluster = df_cluster.drop(columns=['CustomerID']) # Karena kolom tidak digunakan untuk klusterisasi

data_cluster_normalize = preprocessing.normalize(data_cluster)

data_cluster_normalize

K = range(2,8)
fits = []
score = []

for k in K:
  model = KMeans(n_clusters = k, random_state = 0, n_init='auto').fit(data_cluster_normalize)

  fits.append(model)

  score.append(silhouette_score(data_cluster_normalize, model.labels_, metric = 'euclidean'))

# menentukan jumlah cluster
sns.lineplot(x= K, y =score)

fits[2]

df_cluster['cluster_label'] = fits[1].labels_

df_cluster.groupby(['cluster_label']).agg({
    'CustomerID' : 'count',
    'TransactionID' : 'mean',
    'Qty' : 'mean',
})

"""**Hasil Clustering**

- cluster 0 = jumlah customer banyak, transaksi yang dilakukan banyak dan Jumlah quantity produk yang dibeli sedang
- cluster 1 = jumlah customer sedikit, transaksi yang dilakukan sedang dan Jumlah quantity poroduk yang dibeli sedikit
- cluster 2 = jumlah customer sedang, transaksi yang dilakukan sedikit dan Jumlah quantity produk yang dibeli banyak
"""

