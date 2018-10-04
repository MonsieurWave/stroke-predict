import sys
sys.path.insert(0, '../')

import os, timeit
import numpy as np
import timeit
import model_utils
import visual
import data_loader
import manual_data
from email_notification import NotificationSystem

main_dir = '/Users/julian/master/data/clinical_data_test'
# main_dir = '/home/klug/data/working_data/'
data_dir = os.path.join(main_dir, '')
model_dir = os.path.join(main_dir, 'models')
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

# Path to save the model to
model_name = 'clinical_data_test2'
model_path = os.path.join(model_dir, model_name + '.pkl')
if os.path.isfile(model_path):
    # file exists
    print('This model already exists: ', model_path)
    validation = input('Type `yes` if you wish to delete your previous model:\t')
    if (validation != 'yes'):
        raise ValueError('Model already exists. Choose another model name or delete current model')

notification_system = NotificationSystem()


CLIN, IN, OUT = data_loader.load_saved_data(data_dir)
# CLIN = None
# IN, OUT = manual_data.load(data_dir)


rf = 1
rf_dim = [rf, rf, rf]
print('Evaluating', model_name, 'with rf:', rf_dim)

main_save_dir = os.path.join(main_dir, 'hyperopt_results')
save_dir = os.path.join(main_save_dir, model_name + '_data')
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# model_utils.create(model_dir, model_name, IN, OUT, rf_dim)
# model_utils.create_external_memory(model_dir, model_name, data_dir, IN, OUT, rf_dim)

start = timeit.default_timer()
save_folds = False
# score, roc_auc, f1 = model_utils.evaluate_crossValidation(save_dir, model_dir, model_name, rf_dim, IN, OUT)
# score, roc_auc, f1 = model_utils.evaluate_crossValidation(save_dir, model_dir, model_name, rf_dim, create_folds = False, data_dir = data_dir)
score, roc_auc, f1, params = model_utils.evaluate_crossValidation(save_dir, model_dir, model_name, rf_dim,
                                    clinical_input_array = CLIN, input_data_array = IN, output_data_array = OUT, create_folds = True, save_folds = save_folds, messaging = notification_system)
# best = model_utils.xgb_hyperopt(data_dir, save_dir, rf_dim, create_folds = False)
elapsed = timeit.default_timer() - start
print('Evaluation done in: ', elapsed)

# title = model_name + ' finished Cross-Validation'
# body = 'accuracy ' + str(score) + '\n' + 'ROC AUC ' + str(roc_auc) + '\n' + 'F1 ' + str(f1) + '\n' + 'RF ' + str(rf) + '\n' + 'Time elapsed ' + str(elapsed)
body = ''

title = model_name + ' finished hyperopt'
# body = str(best) + '\n' + 'Time elapsed ' + str(elapsed)
notification_system.send_message(title, body)
