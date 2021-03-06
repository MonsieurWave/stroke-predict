import os
import xgboost as xgb
import numpy as np
from vxl_xgboost.xgb_params import XGB_PARAMS

class Ram_xgb():
    """
    """
    def __init__(self, fold_dir, fold_name, n_channels = 4, n_channels_out = 1, rf = 1):
        super(Ram_xgb, self).__init__()
        self.params = XGB_PARAMS
        self.n_estimators = self.params['n_estimators']
        self.evals_result = {}
        self.trained_model = None

        self.dtrain = None
        self.dtest = None
        self.X_train = None
        self.y_train = None
        self.train_index = 0
        self.X_test = None
        self.y_test = None
        self.test_index = 0

        self.ext_mem_extension = '.txt'
        self.fold_dir = fold_dir
        self.fold_name = fold_name

    @staticmethod
    def hello_world():
        print('RAM XGB Model')
        print(XGB_PARAMS)

    @staticmethod
    def get_settings():
        return XGB_PARAMS

    def initialise_train_data(self, n_datapoints, data_dimensions):
        self.X_train = np.empty([np.sum(n_datapoints), data_dimensions])
        self.y_train = np.empty(np.sum(n_datapoints))
        self.train_index = 0

    def add_train_data(self, batch_X_train, batch_y_train):
        """
        Add a batch of training data to the whole training data pool

        Args:
            batch_X_train: batch of training data
            batch_y_train: batch of training labels
        """
        self.X_train[self.train_index : self.train_index + batch_X_train.shape[0], :] = batch_X_train
        self.y_train[self.train_index : self.train_index + batch_y_train.shape[0]] = batch_y_train
        self.train_index += batch_X_train.shape[0]

    def initialise_test_data(self, n_datapoints, data_dimensions):
        self.X_test = np.empty([np.sum(n_datapoints), data_dimensions])
        self.y_test = np.empty(np.sum(n_datapoints))
        self.test_index = 0

    def add_test_data(self, batch_X_test, batch_y_test):
        """
        Add a batch of testing data to the whole testing data pool
        All testing data is saved in a svmlight file
        """
        self.X_test[self.test_index : self.test_index + batch_X_test.shape[0], :] = batch_X_test
        self.y_test[self.test_index : self.test_index + batch_y_test.shape[0]] = batch_y_test
        self.test_index += batch_X_test.shape[0]

    def train(self):
        self.dtrain = xgb.DMatrix(self.X_train, self.y_train)

        if self.y_test.size > 0:
            self.dtest = xgb.DMatrix(self.X_test, self.y_test)
            evals = [(self.dtest, 'eval'), (self.dtrain, 'train')]
        else :
            evals = [(self.dtrain, 'train')]

        self.trained_model = xgb.train(self.params, self.dtrain,
            num_boost_round = self.n_estimators,
            evals = evals,
            early_stopping_rounds = 30,
            evals_result = self.evals_result,
            verbose_eval = False)

        return self.trained_model, self.evals_result

    def predict(self, data):
        probas_ = self.trained_model.predict(data,
                    ntree_limit = self.trained_model.best_ntree_limit)
        return probas_

    def predict_test_data(self):
        probas_ = self.predict(self.dtest)
        return probas_

    def get_test_labels(self):
        y_test = self.dtest.get_label()
        return y_test
