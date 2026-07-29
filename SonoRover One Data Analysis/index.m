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
pr.defaultDataPath = '\\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers';
pr.defaultDataPathTesting = '\\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers\Imasonic_15287_1001\20260407 K-Plan Measurements\Output of T [Imasonic 10 ch. PCD15287_01001 ROC 75 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [KPlan_level_2]';

% set the location of the NeuroFus data sheets
pr.neuroFUSFolderLocation = 'C:\Users\marge\Radboud Universiteit\neuromod - equipment\24_NeuroFUS_steering_tables\';

% Define input parameters

% mandatory
pr.rereadNFD = false; % rereads and rebuilds the matlabs struct importing the xls data files provided by Sonic Concepts in case of new entries of transducer files
pr.devMode   = false; % circumvents the dialog box and load the data directly as defined in the p.defaultDataPathTesting

% general plotting
pl = 0;  

% optional
pr.optional = [];


%Import and prepare data

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
%setNrs = [3, 4, 7, 8];

% 5. Estimate the arrival of the pulse at the hydrophone and corresponding selection window
ringUpcycles     = 25;   % number of periods to exclude from the onset of the pulse, (skipping ring up phase)
selectionCycles  = 5;    % the number of periods to take for amplitude estimation
time             = 80;   % a certain time microseconds from the start of pulse [micro seconds]  
threshold        = 0.1;  % 10% of normalized amplitude
EPoffset         = 10.56;  % the length between the center of the membrane and the exit plane (specific for each transducer type)

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

% ── STEP 1: ensure axial scans are filtered first ──────────────────────
% Build ordered indices correctly
dims = prepData.dim(setNrs, :);   % only look at the sets we care about

% Sort set numbers so [0 0 1] scans are processed before [1 0 0] / [0 1 0]
idx_axial = setNrs(all(dims == [0 0 1], 2));   % Butterworth + reference
idx_rest  = setNrs(any(dims ~= [0 0 1], 2));   % projection-based correction

orderedSetNrs = [idx_axial, idx_rest];

% ── STEP 2: Apply Butterworth to axial scans, build focus lookup ────────
axialIndex = containers.Map('KeyType','double','ValueType','double');

for i = idx_axial
    % related to frequency, use different filtering (SCF param) for 500 kHz vs 250 kHz
    % compare with raw signal!
    % axial spatial filtering (butterworth) to mitigate of hydrophone reflection interference
    scf           = 0.15; % spatial cutoff frequecy [1/mm], used 0.1 to make the equalization curve which seems to harsh... 0.2 is better
    ripple        = 1;    % passband ripple [dB]
    passBandAtten = 40;   % stopband attentuation in [dB]

    calcData = calcData.calcSpatialFiltering(i, scf, ripple, passBandAtten);
    focus = prepData.p{i}.TD.Focus;
    axialIndex(focus) = i;
end

% ── STEP 3: Apply projection-based correction to all remaining scans ────
for i = idx_rest
    focus = prepData.p{i}.TD.Focus;

    % Check if matching axial reference exists
    if ~isKey(axialIndex, focus)
        warning(['No [0 0 1] axial scan found for focus=%.1f mm, ' ...
                 'set %d — skipping filtering.'], focus, i);
        calcData.spatialFilt{i} = calcData.ampEstimation{i};
        continue
    end

    refIdx  = axialIndex(focus);
    z_ax    = prepData.coordinates{refIdx}(:,6);   % axial positions [mm]
    amp_ax  = calcData.ampEstimation{refIdx}.amp;  % raw axial amplitude
    filt_ax = calcData.spatialFilt{refIdx}.amp;    % filtered axial amplitude

    % Correction ratio along axial axis
    ratio_ax = filt_ax ./ amp_ax;

    % Euclidean distance of each point from origin
    coords   = prepData.coordinates{i};            % Nx6
    euc_dist = sqrt(coords(:,4).^2 + coords(:,5).^2 + coords(:,6).^2);

    % Warn if any points fall outside axial scan range
    outOfRange = euc_dist < min(z_ax) | euc_dist > max(z_ax);
    if any(outOfRange)
        warning(['Set %d: %d point(s) have Euclidean distance outside ' ...
                 'axial scan range [%.1f, %.1f] mm — clamping.'], ...
                 i, sum(outOfRange), min(z_ax), max(z_ax));
    end

    % Interpolate ratio at each point's Euclidean distance
    euc_dist_clamped = max(min(euc_dist, max(z_ax)), min(z_ax));
    ratio_interp     = interp1(z_ax, ratio_ax, euc_dist_clamped, 'linear');

    % Apply multiplicative correction
    calcData.spatialFilt{i}.amp = calcData.ampEstimation{i}.amp .* ratio_interp';
end

% calculate Pressure and metrics
calcData = calcData.calcPressure(setNrs);

% calculate Intensity
calcData = calcData.calcIntensity(setNrs);

% calculate ISPPA
calcData = calcData.calcISPPA(setNrs);

% scale with NeuroFus data
%calcData = calcData.calcISPPA2NFscale(setNrs,NFD);

if 0
    % calculate holography
    ipf = 5; % interpolation factor of amplitude and phase data [grid points]
    zv = [0:1:140]*1e-3; % [m' the vector in z-direction of the computed volume
    calcData = calcData.calcHolography(setNrs,ipf,zv);
end

if 0
    % calculate equalization curve
    nrs = [1:37]; % select which one to take into account
    type = {'max','FWHMcenter'};
    calcData = calcData.equalizationCurve(nrs,type{2});

    % spline fitting of the equalization curve
    xTransform = {'log','oneover','sqrt','none'};
    p = 0; % ploiting curvefitting
    calcData = calcData.equalizationCurveFit(xTransform([4]),p);

    % calculate the set focus versus FWHM center distance wrt exit plane
    nrs = [1:37];
    calcData = calcData.focusCurve(nrs);

    % splilefitting of the focus curve
    xTransform = {'log','oneover','sqrt','none'};
    p = 0; % plotting curvefitting
    calcData = calcData.focusCurveFit(xTransform([4]),p);

end


if 0
    % calculate the power curve with linear regression
    nrs = [1:32]; % select which one to take into account and do the fitiing
    calcData = calcData.powerCurve(nrs); % [1:20] = with attenuation [21:32] = without attenuation

    % calculate regression fits  
    xTransform = {'log','oneover','sqrt','none'};
    p = 0; % ploiting curvefitting
    calcData = calcData.powerCurveFit(xTransform([4]),p);
end


%% Visuals

% initiate object and creates postprocessing folder in the same folder as
%the raw data files
dataVisual = dataVis(prepData,calcData);

% channel testing
if 0 % signal time series videos
    % view the filtered pulse data and the pulse selection for amplitude estimation
    xAxis = {'Samples [#]','Time [mus]', 'Cycles [#]'};
    yAxis = {'Voltage [mV]','Pressure [MPa]'};
    NoF = []; % Number of Frames to record, [] = all frames available
    used_setNrs = [1];
    dataVisual.pulseSelection(used_setNrs,xAxis{2},yAxis{1},NoF);
end
%%
if 1 % axial profiles plotting also used for charaterization   
    % view all the axial profiles and compare them with the NeuroFUS data (
    % oiptionally, when available)
    setNrs = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37];
    %setNrs = 31:40;
    xAxis = {'Distance WRT exitplane [mm]', 'Lateral [mm]'};
    yAxis = {'Raw & Filt pressure [MPa]'}; %{'Voltage [mV]','Raw & Filt pressure [MPa]','Pressure [MPa]','ISPPA [W/cm2]','ISPPA scaled [W/cm2]'};
    focusPlot = {'Set Focus wrt exitplane [mm]','Set Focus wrt midbowl [mm]'};
    singleView = {true, false};
    normVal = [nan, nan, nan, nan, nan];
    for sv = 2 %1:numel(singleView)
        for i = 1:numel(setNrs)
            if isequal(prepData.dim(setNrs(i),:),[0 0 1])
                xNum = 1;
            else
                xNum = 2;
            elseif isequal(prepData.dim(used_setNrs(i),:),[0 1 0])
                xNum = 3;
            else
                fprintf('Acoustic axis: %i\n', i);
                xNum = 1; 
            end

            for y = 1:numel(yAxis)
                dataVisual.axialProfiles(used_setNrs(i),xAxis{xNum},yAxis{y},NFD,normVal,focusPlot{1},singleView{sv}, i);
            end
        end
    end
end

%%
if 0 % axial profiles for verification
    selM(1,:) = 1:10;
   % selM(2,:) = 11:20;
   % selM(3,:) = 21:30;
   % selM(4,:) = 31:40;
   used_setNrs = 9:20;
    for j = 1:numel(used_setNrs)
        %dataVisual = dataVis(prepData,calcData);
        % view all the axial profiles and compare them with the NeuroFUS data
        xAxis = {'Distance WRT exitplane [mm]'};
        yAxis = {'Voltage [mV]','Raw & Filt pressure [MPa]','Pressure [MPa]','ISPPA [W/cm2]','ISPPA scaled [W/cm2]'};
        focusPlot = {'Set Focus wrt exitplane [mm]','Set Focus wrt midbowl [mm]'};
        singleView = {true,false};
        normVal = [nan, nan, nan, nan, nan];
        for sv = 2%:numel(singleView)
            for y = 2:5%1:numel(yAxis)
                dataVisual.axialProfiles(used_setNrs(j),xAxis{1},yAxis{y},NFD,normVal,focusPlot{1},singleView{sv}, j);

            end
        end
    end
end

%%
if 0 % Cross-sectional images XY of cSection
    % view
        used_setNr = [7];
        xAxis = {'Lateral [mm]'};
        yAxis = {'Elevational [mm]'};
        value = {'Voltage [mV]','Pressure [MPa]','ISPPA [W/cm2]'};
        normVal = [nan, nan, nan];%  = []; % MPa
        scaleFac = 70/30;%65/30.58; % ISPPA scaleFatcor  
        downsample = zeros([5,1]); % zeros is no downsalpling
        closeFig = false;
        colormapType = {'monotone','hot','default','viridis'}; % make other colormap! see mail
        type = {'norm','dB','none'}
        cl = [-50 0];

    for i = 2:3
        dataVisual.cSectionImages(used_setNr,xAxis{1},yAxis{1},value{i},normVal,scaleFac,downsample,colormapType{4},type{3},cl,closeFig);
    end
    dataVisual.cSectionImages(used_setNr,xAxis{1},yAxis{1},value{2},normVal,scaleFac,downsample,colormapType{4},type{2},cl,closeFig);
end

if 0 % Cross-sectional profiles
    % view 
    xAxis = {'Lateral [mm]'};
    yAxis = {'Voltage [mV]','Pressure [MPa]','ISPPA [W/cm2]'};
    normVal = [nan, nan, nan];
    ylim  = [0 1]; %[0 0.55633]; % MPa
    
    for i = 0:4
        dataVisual.cSectionProfiles(1,xAxis{1},yAxis{2},ylim,type{2},normVal);
    end
end

if 0 % Sagital of ZX cross-section
    % view
    used_setNr = [8];
    xAxis = {'Lateral [mm]'};
    yAxis = {'Axial [mm]'};
    value = {'Voltage [mV]','Pressure [MPa]','ISPPA [W/cm2]'};
    normVal = [] %  = []; % MPa
    scaleFac = 70/30;% 65/29.32; % ISPPA scaleFatcor  
    type = {'norm','dB','none'};
    closeFig = false;
    diffIm = false;
    colormapType = {'monotone','hot','default','viridis'}; % make other colormap! see mail

    for i = 2:3
        dataVisual.XZSectionImages(used_setNr,diffIm,xAxis{1},yAxis{1},value{i},normVal,scaleFac,colormapType{4},type{3},closeFig);
    end
    dataVisual.XZSectionImages(used_setNr,diffIm,xAxis{1},yAxis{1},value{3},normVal,scaleFac,colormapType{4},type{2},closeFig);
end

if 0
    value = {'Pressure [MPa]','ISPPA [W/cm2]','dB'};
    dataVisual.visualize(setNrs,value{1})


end


if 0
    % visualize 3D holography
    transverseLoc = [1,30,45,60];
    dataVisual.holography(transverseLoc,zv)
end

% visualize equalization curve
if 0
    dataVisual.equalizationCurve()
    
end

% visualize focus curve
if 0
    dataVisual.focusCurve()
end

% visualize power curve
if 0
    % Note: Attenuated and non-attenuated power distinguision is hardcoded in
    % powerCurve()!
    dataVisual.powerCurve()
end


%% Export data
expData = dataExp(prepData,calcData);

if 1
    % export pressure and ISPPA data
    fileName = 'CTX500_026-TPO_105_010_f68.7';
    setNrs = [5,6];
    localStorage = false;
    expData.press_ISPPA(setNrs,fileName,localStorage)
end

if 0 % export for characterization handshake 
    % export the equalization curve fitting piece-wise polynomial fit
    xTransform = {'log','oneover','sqrt','none'};
    expData.equalizationCurve(xTransform{4});

    % export the set focus versus FWHMcenter spline and linear fit
    xTransform = {'log','oneover','sqrt','none'};
    expData.focusCurve(xTransform{4});
end
if 0
    % export the amplitude versus pressure curve linear fit
    expData.powerCurve();

end

%% Generate Characterization Report
if 0
    generateCharacterizationReport(prepData,calcData)
end