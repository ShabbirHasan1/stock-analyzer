import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from django.http import JsonResponse
from sklearn import linear_model, svm, tree
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestCentroid, KNeighborsRegressor
from sklearn.neural_network import MLPRegressor

from stock_analyser import settings

matplotlib.use('TkAgg')


def simple_test():
    sql = "select trade_date,close, num_shares from time_series where company_id = %d and close is not null" % (4086)
    company_data = pd.read_sql(sql, settings.DATABASE_URL)

    company_data_modified = pre_process_data(company_data)

    print(company_data_modified.head())
    feature_train, feature_test, result_train, result_test = train_test_split(
        company_data_modified[['trade_date', 'date_int', 'num_shares']], company_data_modified['close'], test_size=0.2)

    print("train size", feature_train.shape)
    print("test size", feature_test.shape)

    apply_regression(feature_test, feature_train, result_test, result_train, company_data_modified)
    response = {}
    return JsonResponse(response)


def apply_regression(feature_test, feature_train, result_test, result_train, company_data):
    X_train = feature_train[['date_int', 'num_shares']]
    X_test = feature_test[['date_int', 'num_shares']]
    # regr = linear_model.LinearRegression()
    # regr = svm.SVR()
    # regr = linear_model.BayesianRidge()
    # regr = KNeighborsRegressor()
    # regr = GradientBoostingRegressor()
    regr = tree.DecisionTreeRegressor()
    # regr = RandomForestRegressor()
    # regr = MLPRegressor(random_state=1, max_iter=500, verbose=True)

    # reg2 = tree.DecisionTreeRegressor()
    # ereg = VotingRegressor(estimators=[('gb', regr), ('rf', reg2)])
    run_regression_and_plot(X_test, X_train, company_data, feature_test, regr, result_test, result_train)


def run_regression_and_plot(X_test, X_train, company_data, feature_test, regr, result_test, result_train):
    regr.fit(X_train, result_train)
    print("regression_done")
    print("score: ", regr.score(X_train, result_train))
    result_pred = regr.predict(X_test)
    print("mae", mean_absolute_error(result_test, result_pred))
    test = pd.DataFrame(columns=['actual', 'pred'])
    test['actual'] = result_test
    test['pred'] = result_pred

    # actual_test_data = get_actual_test_result
    print(test.tail(n=4))
    plot_results(company_data, feature_test, result_pred, result_test)
    plt.show()


def plot_results(company_data, feature_test, result_pred, result_test):
    ax = company_data.plot(x='trade_date', y='close', style='b-', grid=True)
    ax.set_xlabel("date")
    ax.set_ylabel("price")
    ax.scatter(feature_test['trade_date'], result_test, color='r')
    ax.scatter(feature_test['trade_date'], result_pred, color='g')
    ax.legend(['actual_data', 'test', 'predicted'])


def pre_process_data(company_data):
    company_data_modified = company_data.copy()
    company_data_modified['date_int'] = company_data.apply(lambda row: row['trade_date'].toordinal(), axis=1)
    return company_data_modified
