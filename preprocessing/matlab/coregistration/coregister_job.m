% matlabbatch = coregister_job(reference, main_image, images_to_co_coregister)% ARGUMENTS : 
% reference : image to co-register to
% main_image : image to co-register
% images-to-coregister : cell array of images to apply the same co-registration
% to

% The function takes a reference file and a main_image file and passes them to
% matlabbatch for coregistration

function matlabbatch = coregister_job(reference, main_image, images_to_co_coregister)
% 
matlabbatch{1}.spm.spatial.coreg.estwrite.ref = {reference};
matlabbatch{1}.spm.spatial.coreg.estwrite.source = {main_image};

if (~ isempty(images_to_co_coregister))
    matlabbatch{1}.spm.spatial.coreg.estwrite.other = images_to_co_coregister;
end

matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.cost_fun = 'nmi';
matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.sep = [4 2];
matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.tol = [0.02 0.02 0.02 0.001 0.001 0.001 0.01 0.01 0.01 0.001 0.001 0.001];
matlabbatch{1}.spm.spatial.coreg.estwrite.eoptions.fwhm = [7 7];
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.interp = 4;
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.wrap = [0 0 0];
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.mask = 0;
matlabbatch{1}.spm.spatial.coreg.estwrite.roptions.prefix = 'coreg_';
