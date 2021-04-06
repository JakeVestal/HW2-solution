from sklearn.linear_model import LogisticRegression
import pickle
import numpy as np
import pandas as pd

def backtest(features, response, ivv_data, n, N, alpha, lot_size, start_date,
             end_date):

    # pickle.dump(features, open("features.p", "wb"))
    # pickle.dump(response, open("response.p", "wb"))
    # pickle.dump(ivv_data, open("ivv_data.p", "wb"))
    # pickle.dump(n, open("lil_n.p", "wb"))
    # pickle.dump(N, open("big_N.p", "wb"))
    # pickle.dump(alpha, open("alpha.p", "wb"))
    # pickle.dump(lot_size, open("lot_size.p", "wb"))
    # pickle.dump(start_date, open("start_date.p", "wb"))
    # pickle.dump(end_date, open("end_date.p", "wb"))
    #
    # return "asdf"
    #
    features = pickle.load(open("features.p", "rb"))
    response = pickle.load(open("response.p", "rb"))
    ivv_data = pickle.load(open("ivv_data.p", "rb"))
    n = pickle.load(open("lil_n.p", "rb"))
    N = pickle.load(open("big_N.p", "rb"))
    alpha = pickle.load(open("alpha.p", "rb"))
    lot_size = pickle.load(open("lot_size.p", "rb"))
    start_date = pickle.load(open("start_date.p", "rb"))
    end_date = pickle.load(open("end_date.p", "rb"))
    #
    features = pd.read_json(features)
    response = pd.read_json(response)
    ivv_data = pd.read_json(ivv_data)

    # backtest = []
    #
    # for i in range(n, len(ivv_response):
    #     logisticRegr = LogisticRegression()
    #     logisticRegr.fit(
    #         np.float64(
    #             hist_data[["a", "b", "R2"]][(i-n):n]),
    #         np.float64(hist_data["response"][(i-n):n])
    #     )
    #     logisticRegr.predict(
    #         np.float64(ivv_hist)[0].reshape(1,-1)
    #     )




