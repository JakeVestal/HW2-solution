from sklearn.linear_model import LogisticRegression
import pickle
import numpy as np
import pandas as pd

def backtest(hist_data, n, lot_size):

    ivv_hist = pd.read_json(pickle.load(open("ivv_hist.p", "rb")))
    hist_data = pickle.load(open("hist_data.p", "rb"))
    features = pickle.load(open("features.p", "rb"))
    bonds_hist = pd.read_json(pickle.load(open("bonds_hist.p", "rb")))


    n = 30

    backtest = []

    for i in range(n, len(ivv_response):
        logisticRegr = LogisticRegression()
        logisticRegr.fit(
            np.float64(
                hist_data[["a", "b", "R2"]][(i-n):n]),
            np.float64(hist_data["response"][(i-n):n])
        )
        logisticRegr.predict(
            np.float64(ivv_hist)[0].reshape(1,-1)
        )


