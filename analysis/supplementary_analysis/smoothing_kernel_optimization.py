import os, sys
sys.path.insert(0, '../')
import data_loader
from voxelwise.vxl_glm.LogReg_glm import LogReg_glm
from voxelwise.vxl_continuous.normalized_marker_model import Normalized_marker_Model_Generator
from voxelwise.wrapper_cv import launch_cv, rf_hyperopt


data_dir = '/home/klug/data/working_data/all_2016_2017'
main_dir = os.path.join(data_dir, 'smoothing_kernel_hyperopt')
main_output_dir = os.path.join(main_dir, 'models')
main_save_dir = os.path.join(main_dir, 'temp_data')

clinical_inputs, ct_inputs, ct_label, _, _, brain_masks, ids, params = data_loader.load_saved_data(data_dir)
# Order: 'wcoreg_RAPID_Tmax', 'wcoreg_RAPID_rCBF', 'wcoreg_RAPID_MTT', 'wcoreg_RAPID_rCBV'
ct_inputs = ct_inputs[..., 0]

# Ignore clinical data for now
clinical_inputs = None

# brain_masks = numpy.full(ct_label.shape, True) # do not use brain_masks
# ct_inputs, ct_label = manual_data.load(data_dir) # select data manually

n_repeats = 10
n_folds = 5

# Feature can accelerate some algorithms
# should not be used if predetermined thresholds are used
feature_scaling = True

# Smoothing before training and testing (applied before thresholding by Campbell et al)
pre_smoothing = True
threeD_smoothing = False

# Normalise channel by mean of contralateral side: can be used to obtain rCBF [1] and rCBV [3]
channels_to_normalise = False

# Add a normalization term to account for the number of voxels outside the defined brain ct_inputs a receptive field
undef_normalisation = False

# Use a flat receptive field (flat in z) - [rf_x, rf_y, 0]
flat_rf = False

# Model_Generator = Normalized_marker_Model_Generator(ct_inputs.shape, feature_scaling, normalisation_mode = 0, inverse_relation = False)
Model_Generator = LogReg_glm

model_name = 'Tmax0_glm'

for smoothing_radius in range(0, 9):
    smoothing_diameter = 1 + 2 * smoothing_radius
    if threeD_smoothing:
        smooth_model_name = model_name + '_3D_smooth_k' + str(smoothing_diameter)
        pre_smoothing = (smoothing_diameter, smoothing_diameter, smoothing_diameter)
    else:
        smooth_model_name = model_name + '_2D_smooth_k' + str(smoothing_diameter)
        pre_smoothing = (smoothing_diameter, smoothing_diameter)
    # rf is not used here
    rf_hp_start = 0; rf_hp_end = 1
    rf_hyperopt(smooth_model_name, Model_Generator, ct_inputs, ct_label, clinical_inputs, brain_masks, ids,
                feature_scaling, pre_smoothing, channels_to_normalise, undef_normalisation, flat_rf,
                    n_repeats, n_folds, main_save_dir, main_output_dir, rf_hp_start, rf_hp_end)
