import os, torch, math
from sklearn.metrics import f1_score, accuracy_score, fbeta_score, jaccard_similarity_score, roc_auc_score, precision_score, roc_curve, auc, accuracy_score
import numpy as np
from scipy.spatial.distance import directed_hausdorff


def evaluate(probas_, y_test, n_subjects):
    # Voxel-wise statistics
    # Compute ROC curve, area under the curve, f1, and accuracy
    fpr, tpr, thresholds = roc_curve(y_test, probas_[:])
    roc_auc = auc(fpr, tpr)
    # get optimal cutOff
    threshold = cutoff_youdens_j(fpr, tpr, thresholds)
    # threshold = 0.5 # threshold choosen to evaluate f1 and accuracy of model

    jaccard = jaccard_similarity_score(y_test, probas_[:] > threshold)
    accuracy = accuracy_score(y_test, probas_[:] > threshold)
    f1 = f1_score(y_test, probas_[:] > threshold)

    # Image-wise statistics
    # y_test and probas need to be in order of subjects
    image_wise_probas = probas_.reshape(n_subjects, -1)
    image_wise_y_test = y_test.reshape(n_subjects, -1)

    thresholded_volume_deltas = []
    unthresholded_volume_deltas = []
    image_wise_error_ratios = []
    image_wise_jaccards = []
    image_wise_hausdorff = []
    image_wise_dice = []

    for subj in range(n_subjects):
        # Volume delta is defined as GT - predicted volume
        thresholded_volume_deltas.append(np.sum(image_wise_y_test[subj]) - np.sum(image_wise_probas[subj] > threshold))
        unthresholded_volume_deltas.append(np.sum(image_wise_y_test[subj])- np.sum(image_wise_probas[subj]))
        n_voxels = image_wise_y_test[subj].shape[0]
        # error ratio being defined as sum(FP + FN)/all
        image_wise_error_ratios.append(
            np.sum(abs(image_wise_y_test[subj] - (image_wise_probas[subj] > threshold))) / n_voxels
        )
        image_wise_jaccards.append(jaccard_similarity_score(y_test, probas_[:] > threshold))
        image_wise_dice.append(dice(y_test, probas_[:] > threshold))
        image_wise_hausdorff.append(directed_hausdorff(y_test, probas_[:] > threshold)[0])


    return {
        'fpr': fpr,
        'tpr': tpr,
        'thresholds': thresholds,
        'accuracy': accuracy,
        'jaccard': jaccard,
        'f1': f1,
        'roc_auc': roc_auc,
        'thresholded_volume_deltas': thresholded_volume_deltas,
        'unthresholded_volume_deltas': unthresholded_volume_deltas,
        'image_wise_error_ratios': image_wise_error_ratios,
        'image_wise_jaccards': image_wise_jaccards,
        'image_wise_hausdorff': image_wise_hausdorff,
        'image_wise_dice': image_wise_dice,
        }

def cutoff_youdens_j(fpr, tpr, thresholds):
    j_scores = tpr-fpr # J = sensivity + specificity - 1
    j_ordered = sorted(zip(j_scores, thresholds))
    return j_ordered[-1][1]

def dice(im1, im2, empty_score=1.0):
    """
    Computes the Dice coefficient, a measure of set similarity.
    Parameters
    ----------
    im1 : array-like, bool
        Any array of arbitrary size. If not boolean, will be converted.
    im2 : array-like, bool
        Any other array of identical size. If not boolean, will be converted.
    Returns
    -------
    dice : float
        Dice coefficient as a float on range [0,1].
        Maximum similarity = 1
        No similarity = 0
        Both are empty (sum eq to zero) = empty_score

    Notes
    -----
    The order of inputs for `dice` is irrelevant. The result will be
    identical if `im1` and `im2` are switched.
    """
    im1 = np.asarray(im1).astype(np.bool)
    im2 = np.asarray(im2).astype(np.bool)

    if im1.shape != im2.shape:
        raise ValueError("Shape mismatch: im1 and im2 must have the same shape.")

    im_sum = im1.sum() + im2.sum()
    if im_sum == 0:
        return empty_score

    # Compute Dice coefficient
    intersection = np.logical_and(im1, im2)

    return 2. * intersection.sum() / im_sum
