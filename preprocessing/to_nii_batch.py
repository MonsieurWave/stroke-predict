import os
import subprocess

main_dir = '/Volumes/stroke_hdd1/temp/'
data_dir = os.path.join(main_dir, 'all_angio')
output_dir = os.path.join(main_dir, 'nifti_all_angio')
dcm2niix_path = '/Users/julian/stroke_research/dcm2niix_11-Apr-2019_mac/dcm2niix'

def move_lesion_files(search_dir, output_sub_dir):
    nii_files = [f for f in os.listdir(search_dir) if f.endswith(".nii")]
    for file in nii_files:
        if 'VOI' in file or 'lesion' in file or 'Lesion' in file:
            file_path = os.path.join(search_dir, file)
            new_file_path = os.path.join(output_sub_dir, file)
            if not os.path.exists(new_file_path):
                subprocess.run(['cp', '-rf', file_path, new_file_path])

def to_nii_batch_conversion(data_dir, output_dir):
    subjects = [o for o in os.listdir(data_dir)
                    if os.path.isdir(os.path.join(data_dir,o))]

    for subject in subjects:
        subject_dir = os.path.join(data_dir, subject)
        modalities = [o for o in os.listdir(subject_dir)
                        if os.path.isdir(os.path.join(subject_dir,o))]

        for modality in modalities:
            modality_dir = os.path.join(subject_dir, modality)
            studies = [o for o in os.listdir(modality_dir)
                            if os.path.isdir(os.path.join(modality_dir,o))]

            for study in studies:
                study_dir = os.path.join(modality_dir, study)
                study_output_dir = os.path.join(output_dir, subject, modality)
                if not os.path.exists(study_output_dir):
                    os.makedirs(study_output_dir)

                if not os.path.exists(os.path.join(study_output_dir, study + '.nii')):
                    subprocess.run([dcm2niix_path, '-m', 'y', '-b', 'y', '-z', 'n',
                                    '-f', study, '-o', study_output_dir, study_dir], cwd = modality_dir)
            # search for lesion files at study level
            move_lesion_files(modality_dir, os.path.join(output_dir, subject))

        # search for lesion files at subject dir level
        move_lesion_files(subject_dir, os.path.join(output_dir, subject))

to_nii_batch_conversion(data_dir, output_dir)
