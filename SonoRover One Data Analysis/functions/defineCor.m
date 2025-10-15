clear all


% Stein Fekkes

% Initial version dec 2023
% Focused ultrasound initiative

% 16 jan.
% - added general output path to FUS inititative wrkgrp folder
% - auotmated file save structure based on 1,2,3-D and given filename
% - save files as xls with headers
% - save complete workspace for later use
% - save mp4 movie to see the coordinates order

clear all; clc; close all;


%% Gernral parameters


% Specify the file name
%filename = 'Coordinates_Axial_0-05-140mm';

% set output folder to store Coordinate files
defaultOutputFolder = '\\ru.nl\WrkGrp\FUS_Initiative\Hydrophone measurements\!Coordinate Templates';

headers = {'Measurement number', 'Cluster number', 'Indices number','X-coordinate [mm]','Y-coordinate [mm]','Z-coordinate [mm]','Row number','Column number','Slice number'};

%% folder creation
% Open a dialog to browse for a directory
selectedFolder = uigetdir(defaultOutputFolder, 'Select a Folder');

% Check if the user clicked 'Cancel'
if isequal(selectedFolder, 0)
    disp('User canceled the operation');
    return
else
    disp(['Selected folder: ' selectedFolder]);
end

if 1
    % transversal slices
    % centered around zero. max single sided stretch
    xr = 30; % mm
    yr = 30; % mm

    % Resolution
    dx = 0.5; % mm
    dy = dx;

    for z = 70.45 %12:2:20


        xs =[dx:dx:xr];
        ys =[dx:dy:yr];

        x = [-flip(xs),0,xs];
        y = [-flip(ys),0,ys];

        [xm,ym,zm] = meshgrid(x,y,z);

        xmtt = xm(:);
        ymtt = ym(:);
        zmtt = zm(:);

        % calculate linearIndices and row,col,slc
        linearIndicest   = [1:numel(xm)]';
        [rowt,colt,slct]   = ind2sub(size(xm),linearIndicest);
        clusterNr       = ones(size(xmtt(:)));

        % build matrix
        % Header = {'Measurement number','Cluster number,','Indices number,',...
        %     'X-coordinate [mm],','Y-coordinate [mm],','Z-coordinate [mm],',...
        %     'Row number,','Column number,','Slice number,'};

        corMatrix = [(1:numel(clusterNr))', clusterNr,linearIndicest,round(xmtt,4),round(ymtt,4),round(zmtt,4),rowt,colt,slct];

        % generate file name
        fileName = sprintf('2D_X%2.0f_Y%2.0f_R%2.1f_Z%2.1f',xr,yr,dx,z);

        outputFolder = fullfile(selectedFolder, fileName);

        % Create the new folder
        mkdir(selectedFolder, fileName);

        % Write the matrix to the CSV file
        writematrix(corMatrix, [outputFolder,'/',fileName,'.csv']);

        % Write the matrix to the CSV file
        writecell(headers, [outputFolder,'/',fileName,'.csv']);

        % Write the matrix to the CSV file
        writematrix(corMatrix, [outputFolder,'/',fileName,'.csv'],'WriteMode','append');

        % write matfile
        save([outputFolder,'/',fileName,'.mat'])

    end
end

if 0

    % Parameters
    x_min = -5;    % mm
    x_max = 30;    % mm
    z_min = 3;     % mm
    z_max = 130;   % mm
    y_val = 0;     % mm (constant, sagittal plane is x-z at fixed y)

    % Mesh resolution (adjust as needed)
    x_step = 0.5;    % mm
    z_step = 0.5;    % mm

    % Create grid in x-z plane
    [x, z] = meshgrid(x_min:x_step:x_max, z_min:z_step:z_max);
    y = y_val * ones(size(x));

    % Optional: visualize the mesh
    figure;
    mesh(x, y, z);
    xlabel('X (mm)');
    ylabel('Y (mm)');
    zlabel('Z (mm)');
    title('Sagittal Plane Mesh (X-Z Plane at Y=0)');
    axis equal tight;


    % formatting and saving
    xmtt = x(:);
    ymtt = y(:);
    zmtt = z(:);

    % calculate linearIndices and row,col,slc
    linearIndicest      = [1:numel(x)]';
    [rowt,colt,slct]    = ind2sub(size(x),linearIndicest);
    clusterNr           = ones(size(xmtt(:)));

    % build matrix
    % Header = {'Measurement number','Cluster number,','Indices number,',...
    %     'X-coordinate [mm],','Y-coordinate [mm],','Z-coordinate [mm],',...
    %     'Row number,','Column number,','Slice number,'};

    corMatrix = [(1:numel(clusterNr))', clusterNr,linearIndicest,round(xmtt,4),round(ymtt,4),round(zmtt,4),rowt,colt,slct];

    % generate file name
    fileName = sprintf('2D_X%2.0f_X%2.0f_Z%2.0f_Z%2.0f_R%2.1f_Y%2.0f',x_min,x_max,z_min,z_max,x_step,y_val);

    outputFolder = fullfile(selectedFolder, fileName);

    % Create the new folder
    mkdir(selectedFolder, fileName);

    % Write the matrix to the CSV file
    writematrix(corMatrix, [outputFolder,'/',fileName,'.csv']);

    % Write the matrix to the CSV file
    writecell(headers, [outputFolder,'/',fileName,'.csv']);

    % Write the matrix to the CSV file
    writematrix(corMatrix, [outputFolder,'/',fileName,'.csv'],'WriteMode','append');

    % write matfile
    save([outputFolder,'/',fileName,'.mat'])
end
