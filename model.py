import pickle
import pandas as pd
from sklearn import linear_model
from sklearn.metrics import r2_score

def calc_features(bonds_hist):

    ###### For teaching & debugging ############################################
    # --------------------------------------------------------------------------
    #
    # pickle.dump(bonds_hist, open("bonds_hist.p", "wb"))
    # bonds_hist = pickle.load(open("bonds_hist.p", "rb"))
    # --------------------------------------------------------------------------
    ############################################################################

    bonds_hist = pd.read_json(bonds_hist)

    def bonds_fun(yields_row):
        maturities = pd.DataFrame([1 / 12, 2 / 12, 3 / 12, 6 / 12, 1, 2])
        linreg_model = linear_model.LinearRegression()
        linreg_model.fit(maturities, yields_row[1:])
        modeled_bond_rates = linreg_model.predict(maturities)
        return [yields_row["Date"].date(), linreg_model.coef_[0],
                linreg_model.intercept_,
                r2_score(yields_row[1:], modeled_bond_rates)]

    features = bonds_hist[
        ["Date", "1 mo", "2 mo", "3 mo", "6 mo", "1 yr", "2 yr"]
    ].apply(bonds_fun, axis=1,result_type='expand')

    features.columns = ["Date", "a", "b", "R2"]

    return features.to_json()

def calc_response(ivv_hist, alpha, n):
    ###### For teaching & debugging ############################################
    # --------------------------------------------------------------------------
    # pickle.dump(ivv_hist, open("ivv_hist.p", "wb"))
    # pickle.dump(alpha, open("alpha.p", "wb"))
    # pickle.dump(n, open("n.p", "wb"))
    #
    # ivv_hist = pd.read_json(pickle.load(open("ivv_hist.p", "rb")))
    # alpha = pickle.load(open("alpha.p", "rb"))
    # n = pickle.load(open("n.p", "rb"))
    # --------------------------------------------------------------------------
    ############################################################################

    ivv_hist = pd.read_json(ivv_hist)

    response = pd.DataFrame({'Date': ivv_hist['Date'], 'response': ""})

    for i in range(n, len(ivv_hist) - n + 1):
        response._set_value(
            i, 'response', ivv_hist['Open'][i]*(1+alpha) <= max(
                ivv_hist['High'][i:i+n]
            )
        )

    response = response[response['response']!=""]
    response['response'] = response['response'].astype(int)

    return response.to_json()
