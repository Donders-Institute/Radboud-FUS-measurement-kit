%Perform metrology data processingcolormap
%
% DESCRIPTION:
%     index.m is the parent container for all classes and fucntions used withing this metrology kit
%
% USAGE:
%     Use this file to prepare the input to run the individual classes
%
% INPUTS:
%     [-]
%
% OPTIONAL INPUTS:
%     [-]
%
% OUTPUTS:
%     Depends on class outputs
%
% ABOUT:
%     Author       - Stein Fekkes
%     Date         - December 2024
%     Version      - 0.8
%
% REFERENCES:
%     [-]
%
% DEPENDENCIES
%
% TOOLBOXES     - natsortFiles
%               - crossing
%               - k-wave-toolbox
%
% This function is part of the RU-Metrology Toolbox (https://www.ru.nl/en/
% donders-institute/research/research-facilities/
% focused-ultrasound-initiative-fus)
%
% LICENSE
% distributed in the hope that it will be useful, but WITHOUT ANY
% WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
% FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
% more details.
%
% Copyright (C) 2024-2025 Stein Fekkes & Margely Cornelissen
%
% See also: [-]


%% Initialize environment

% MATLAB workspace and command cleaning
clear; close all; clear classes; clc

% add toolboxes
addpath(genpath('Toolboxes'))

% add functions and classes
addpath('functions')
addpath('classes')

% add external data inclusing Socic concepts data and hydrophone data
addpath(genpath('externalData'))

% set default pathname t6o SonoRover One data
pr.metrologySetup = 'SonoRover One';
pr.defaultDataPath = '\\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2025\Transducers';
pr.defaultDataPathTesting = 'SonoRover One\DPX\';

% set the location of the NeuroFus data sheets
pr.neuroFUSFolderLocation = 'C:\Users\sfekk\Radboud Universiteit\neuromod - equipment\24_NeuroFUS_steering_tables\';

%% Define input parameters

% mandatory
pr.rereadNFD = false; % rereads and rebuilds the matlabs struct importing the xls data files provided by Sonic Concepts in case of new entries of transducer files
pr.devMode   = true; % circumvents the dialog box and load the data directly as defined in the p.defaultDataPathTesting

% general plotting
pl = 0;  

% optional
pr.optional = [];


%% Import and prepare data

% Initialize a flag to determine if the NeuroFUs calibration xls data
% sheets profided by Sonic Concepts should be re-read from the source.
if ~exist('externalData\NFD.mat', 'file') || pr.rereadNFD
    % If the file does not exist or the reread flag is true:
    % Call the function readNF() to read the data from the source.
    % In case of adding new definition files, please open class readNF and
    % add the filename and dataArea.
    NFD = readNF(pr.neuroFUSFolderLocation);

    % Save the variable NFD to a file named 'NFD.mat' for future use.
    save('externalData\NFD', 'NFD');
else
    % If the file exists and reread is false:
    % Load the data from 'NFD.mat' into the workspace.
    load('externalData\NFD.mat');
end

% read and prepare metrology data
% 1. Read raw data, coordinates and config file
% 2. Bandpass filter to remove AC noise and DC offset
% 3. envelope estimation, (Hilbert transform)
% 4. envelope nomalization for startIndex estimation
[prepData, setNrs] = dataPrep(pr,pl);


%% Data selection

% adapt setNrs
% setNrs = [1:3,4];

% 5. Estimate the arrival of the pulse at the hydrophone and corresponding selection window
ringUpcycles     = 25;   % number of periods to exclude from the onset of the pulse, (skipping ring up phase)
selectionCycles  = 5;    % the number of periods to take for amplitude estimation
time             = 80;   % a certain time microseconds from the start of pulse [micro seconds]  
threshold        = 0.1;  % 10% of normalized amplitude
EPoffset         = 7.3;  % the length between the center of the membrane and the exit plane (specific for each transducer type)

%  Exit plane    Hydrophone position
%  Trigger       Start Pulse                                                 End Pulse    End of measurement
%    |----------------|--pulse ringup cycles---|---------------------------------|-----------------|
%
%
%                    1TOF             2TOF             3TOF (>3TOF: Hydrophone reflection)
%    |------1TOF------|----------------|----------------|

% MASK 1:                                      |---------------------------------|
% MASK 2:                         |---selectionCycles---|
% MASK 3:                                      |----selectionCycles-----|
% MASK 4:                                            |----selectionCycles-----|

prepData = prepData.pulseIndexEst(setNrs,pl,ringUpcycles,selectionCycles,time,threshold,EPoffset);

% Choose the selection window for the amplitude estimation
% 6. determine window of pulse

% mask 1 = in between end of ring up period and end of pulse
% mask 2 = in between 3TOF minus selectionCycles and 3TOF
% mask 3 = in between end of ring up period and end of ring up period + selectionCyles
% mask 4 = at a certain time selection - selectionCycles to certain time.
mask = 4;

prepData = prepData.pulseWindow(setNrs,mask,pl);

%% data calculations

% initiate object
calcData = dataCalc(prepData);

% Amplitude estimation can be performed using different methods;
% ampEstMethod 1: FFT
% ampEstMethod 2: Phasor
% ampEstMethod 3: Hilbert transform
% ampEstMethod 4: K-wave
ampEstMethod = 4;

calcData = calcData.calcAmplitude(setNrs,ampEstMethod);

% axial spatial filtering (butterworth) to mitigate of hydrophone reflection interference
scf           = 0.25; % spatial cutoff frequecy [1/mm]
ripple        = 1;    % passband ripple [dB]
passBandAtten = 40;   % stopband attentuation in [dB]

calcData = calcData.calcSpatialFiltering(setNrs,scf,ripple,passBandAtten);

% calculate Pressure and metrics
calcData = calcData.calcPressure(setNrs);

% calculate Intensity
calcData = calcData.calcIntensity(setNrs);

% calculate ISPPA
calcData = calcData.calcISPPA(setNrs);

% scale with NeuroFus data
calcData = calcData.calcISPPA2NFscale(setNrs,NFD);

% calculate holography
ipf = 5; % interpolation factor of amplitude and phase data
zv = [0:1:140]*1e-3; % [m' the vector in z-direction of the computed volume 
calcData = calcData.calcHolography(setNrs,ipf,zv);

%% Visuals

% initiate object and creates postprocessing folder in the same folder as
% the raw data files
dataVisual = dataVis(prepData,calcData);

if 0
    % view the filtered pulse data and the pulse selection for amplitude estimation
    xAxis = {'Samples [#]','Time [mus]', 'Cycles [#]'};
    yAxis = {'Voltage [mV]','Pressure [MPa]'};
    dataVisual.pulseSelection(setNrs,xAxis{2},yAxis{2});
end

if 1
    % view all the axial profiles and compare them with the NeuroFUS data
    xAxis = {'Distance WRT exitplane [mm]'};
    yAxis = {'Voltage [mV]','Raw & Filt pressure [MPa]','Pressure [MPa]','ISPPA [W/cm2]','ISPPA scaled [W/cm2]'};
    singleView = {true,false};
    for sv = 1:numel(singleView)
        for y = 1:numel(yAxis)
            dataVisual.axialProfiles(setNrs,xAxis{1},yAxis{y},NFD,singleView{sv});
        end
    end
end
if 0
    % visualize 3D holography
    transverseLoc = [1,20,65,100];
    dataVisual.holography(transverseLoc,zv)
end


%% Export data
expData = dataExp(prepData,calcData);

% export pressure and ISPPA data
fileName = 'DPX_Export';
expData.press_ISPPA(fileName)




