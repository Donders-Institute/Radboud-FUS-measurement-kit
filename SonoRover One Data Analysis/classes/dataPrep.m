classdef dataPrep
    % DATAPREP will read and prepare the measurements for further
    % postprocessing and parameters etsimation

    % Modifications
    % 22-nov-2023   SFS     Initial version


    %   Detailed explanation goes here

    properties
        pr          = [];
        pl          = [];
        p           = [];
        rawData     = [];
        coordinates = [];
        dim         = [];
        filtData    = [];
        ampData     = [];
        normAmpData = [];
        normAmpDataForRingup = [];
        startIndex  = [];
        startIndexEst = [];
        reflectIndex= [];
        preReflectionIndex =[];
        postRingUpIndex = [];
        endIndex    = [];
        ringupIndex = [];
        timeIndex = [];
        preTimeIndex = [];
        dataSel     = [];

    end

    properties (Access = private)

        coef            = [];
        setNrs          = [];
        scanNrs         = [];
        threshold       = [];
        filtOrder       = 100;
        filterBandwidth = 100e3;


    end

    methods

        %% Function: Constructor for dataPrep class
        % This constructor initializes an instance of the dataPrep class,
        % loads acquisition data, applies filtering, calculates amplitude,
        % and normalizes the data.

        %% Constructor definition
        function [obj, setNrs] = dataPrep(pr,pl)
            % DATAPREP Construct an instance of this class
            %
            % This class loads acquisition data from the hydrophone
            % XYZ-stage measurement device and returns voltage
            % timeseries for each XYZ-position

            obj.pr      = pr;  % Store the input parameter pr in the object

            % Display waitbar to show progress
            f = waitbar(0,'Load Data');
            [obj, setNrs] = obj.dataRead(pl); % Read data

            waitbar(.33,f,'Filter Data');
            obj = obj.filterData(pl); % Apply filtering

            waitbar(.67,f,'Calculate amplitude');
            obj = obj.amplitudeData(pl); % Compute amplitude

            waitbar(1,f,'Normalize data');
            obj = obj.normalizeData(pl); % Normalize data

            close(f) % Close the waitbar
        end

        %% Function: Read raw data and process it into a structured format
        % This function reads raw data from hydrophone measurements stored in .raw files,
        % extracts relevant metadata, and structures it into MATLAB arrays.

        function [obj, setNrs] = dataRead(obj,pl)
            % Read an structure's raw data into a matrix
            %
            % Input: file path to the folder containing .raw data files.
            % The file path is set in parameters defined in index.m.

            warning('off', 'MATLAB:table:ModifiedAndSavedVarnames')
            choice = 'Yes';
            c = 1;

            if obj.pr.devMode
                % Load data from default testing path
                unsortedfiles = dir(fullfile(obj.pr.defaultDataPathTesting,'*.raw'));
                fileList = natsortfiles(unsortedfiles); % Sort files
            else
                % Select folder interactively and load data
                while strcmp(choice, 'Yes')
                    selectedFolder = uigetdir(obj.pr.defaultDataPath, 'Select a Folder');
                    unsortedfiles = dir(fullfile(selectedFolder,'*.raw'));
                    files = natsortfiles(unsortedfiles);

                    if c==1
                        fileList = files;
                    else
                        l = length(fileList);
                        l2 = length(files);
                        fileList(l+1:l+l2) = files;
                    end

                    choice = questdlg('Add another folder?', 'Import files', 'Yes', 'No', 'No');
                    files = [];
                    c = c+1;
                end
            end

            % Loop through each file and read its contents
            for i = 1:length(fileList)
                fileName = fileList(i).name(1:end-4); % Extract file name
                obj = collectMapIniStruct(obj, i, fileList(i).folder, fileName); % Read .ini file

                % Open and read raw file
                fID = fopen(fullfile(fileList(i).folder, [fileList(i).name]));
                data = fread(fID, [obj.p{i}.acq.samples, Inf], 'single');
                fclose(fID);

                % Construct data structure
                D{i}.data = single(data);
                D{i}.name = fileList(i).name;
                D{i}.size = size(data);
                D{i}.precision = 'single';
                D{i}.folderName = fileList(i).folder;

                if pl && i == 1
                    figure('position',[100,100,1800,500],'Color','white')
                    subplot(2,3,1)
                    plot(D{i}.data(:, [1:floor(D{i}.size(2)/10):D{i}.size(2)]));
                    axis tight; box off; grid minor
                    title('10 raw data [hydrophone voltage traces] plots equally spaced');
                    xlabel('Sample points [#]'); ylabel('Voltage [V]')
                end

                % Read corresponding CSV file
                csvFileName = [fileList(i).name(1:end-4), '.csv'];
                cor = table2array(readtable(fullfile(fileList(i).folder, csvFileName)));

                % Determine measurement direction based on coordinate variation
                dim = ones(1,3);
                if std(cor(:,4)) == 0, dim(1) = 0; end
                if std(cor(:,5)) == 0, dim(2) = 0; end
                if std(cor(:,6)) == 0, dim(3) = 0; end
                obj.dim(i,:) = dim;

                % add sacan info
                dz = diff(cor(:,6));
                obj.p{i}.scan.dz = dz(1);

                % Assign measurement direction labels
                switch num2str(dim)
                    case '0  0  1', dirstr = 'Axial profile Z-dir';
                    case '0  1  0', dirstr = 'Elevation profile Y-dir';
                    case '1  0  0', dirstr = 'Lateral profile X-dir';
                    case '1  1  0', dirstr = 'Transversal plane XY-dir';
                    case '0  1  1', dirstr = 'Longitudinal plane YZ-dir';
                    case '1  0  1', dirstr = 'Frontal plane XZ-dir';
                    case '1  1  1', dirstr = 'Volumetric XYZ-dir';
                end

                % Display file info
                fprintf('Read %s | Samples: %d, Scans: %d, Dimension: %s\n', fileName, D{i}.size(1), D{i}.size(2), dirstr);

                % Store coordinate data
                obj.coordinates{i} = cor;

                if pl && i == 1
                    subplot(2,3,2); plot3(cor(:,4), cor(:,5), cor(:,6), '.b');
                    axis equal tight; box off; grid minor
                    title('XYZ measurement points from CSV file');
                    xlabel('X [mm]'); ylabel('Y [mm]'); zlabel('Z [mm]');

                    subplot(2,3,3); plot(cor(:,4), cor(:,5), '.b');
                    axis equal tight; box off; grid minor
                    title('XY plot'); xlabel('X [mm]'); ylabel('Y [mm]');
                end
            end

            setNrs = 1:numel(fileList);
            fprintf('Number of loaded sequences: %d \n', max(setNrs));
            obj.rawData = D;
        end
        %% Function: Band-pass filter for data
        % This function applies a band-pass filter to the raw data to isolate
        % a specific frequency range around the target frequency.

        function obj = filterData(obj,pl)
            % Apply band-pass filter to each dataset
            for i = 1:size(obj.rawData,2)

                % Define Nyquist frequency and filter cutoff frequencies
                Nyquist = obj.p{i}.acq.fs / 2;
                fLow = obj.p{i}.TD.f0 - obj.filterBandwidth / 2;
                fHigh = obj.p{i}.TD.f0 + obj.filterBandwidth / 2;

                % Design the bandpass filter using FIR with Kaiser window
                filter_coefficients = fir1(obj.filtOrder, [fLow/Nyquist, fHigh/Nyquist], 'bandpass', kaiser(obj.filtOrder+1, 5));

                % Apply zero-phase filtering to avoid phase distortion
                obj.filtData{i} = filtfilt(filter_coefficients, 1, obj.rawData{i}.data);

                % Plot comparison of raw vs. filtered data if pl flag is enabled
                if pl && i == 1
                    gcf;
                    subplot(2,3,4);
                    plot(obj.rawData{i}.data(1:500,1)); hold on;
                    plot(obj.filtData{i}(1:500,1), 'r'); hold off;
                    axis tight; box off; grid minor;
                    title('Raw vs Band-pass Filtered Time Series');
                    xlabel('Samples'); ylabel('Voltage [V]');
                end
            end
        end

        %% Function: Calculate amplitude data
        % This function computes the envelope of the filtered data to estimate the amplitude.

        function obj = amplitudeData(obj,pl)
            % Iterate over each filtered dataset
            for i = 1:size(obj.filtData,2)

                % Compute the amplitude envelope using the envelope function
                obj.ampData{i} = envelope(obj, obj.filtData{i});

                % Plot filtered signal vs. amplitude envelope if pl flag is enabled
                if pl && i == 1
                    gcf;
                    subplot(2,3,5);
                    plot(obj.filtData{i}(:,1)); hold on;
                    plot(obj.ampData{i}(:,1), 'r'); hold off;
                    axis tight; box off; grid minor;
                    title('Envelope Estimation of Filtered Time Series');
                    xlabel('Samples'); ylabel('Voltage [V]');
                end
            end
        end

        %% Function: Normalize amplitude data
        % This function normalizes the amplitude data to a specified range.

        function obj = normalizeData(obj,pl)
            % Iterate over each amplitude dataset
            for i = 1:size(obj.ampData,2)

                % Normalize the amplitude data to a range of [0,1]
                obj.normAmpData{i} = normalize(obj.ampData{i}, 1, "range");

                % Plot original amplitude vs. normalized amplitude if pl flag is enabled
                if pl && i == 1
                    gcf;
                    subplot(2,3,6);
                    plot(obj.ampData{i}(:,1)); hold on;
                    plot(obj.normAmpData{i}(:,1), 'r'); hold off;
                    axis tight; box off; grid minor;
                    title('Normalized Amplitude Data of Envelope Time Series');
                    xlabel('Samples'); ylabel('Voltage [V]');
                end
            end
        end

        %% Function: Estimate pulse start index and derivatives
        % This function estimates the start index of a pulse by thresholding the normalized amplitude envelope.
        % It also calculates various indices related to the pulse's timing based on the speed of sound and the Z-coordinate.

        function obj = pulseIndexEst(obj,setNrs,pl,ringUpcycles,selectionCycles,time, threshold,EPoffset)

            % Overwrite input arguments with provided values
            obj.pr.ringUpcycles     = ringUpcycles;      % Number of periods to exclude from onset (ring-up phase)
            obj.pr.selectionCycles  = selectionCycles;   % Number of periods for amplitude estimation
            obj.pr.time             = time;              % Time in microseconds from pulse start
            obj.pr.threshold        = threshold;         % Threshold for amplitude detection (e.g., 10% of normalized amplitude)
            obj.pr.EPoffset         = EPoffset;          % Distance from membrane center to exit plane

            % Optional plotting
            if pl; end

            % Process each measurement set
            for i = setNrs

                % Estimate start index for each scan based on thresholding
                for j = 1:size(obj.normAmpData{i},2)
                    % Extract single amplitude dataset
                    singleAmpData  = obj.normAmpData{i}(:,j);
                    % Find first index where amplitude exceeds threshold (after initial 100 samples)
                    obj.startIndexEst{i}(j) =  100 + find(singleAmpData(100:end) > obj.pr.threshold,1,'first');
                end

                % Calculate start index based on Z-coordinate and speed of sound
                z               = obj.pr.EPoffset + obj.coordinates{i}(:,6); % Adjust for exit plane offset
                t               = z * 1e-3 / obj.p{i}.water.c; % Time delay due to sound speed
                startIndexSOS   = round(t * obj.p{i}.acq.fs); % Convert to sample index

                % Plot estimated vs. calculated start index if plotting enabled
                if pl
                    figure('Color','white');
                    if obj.dim(i,3) == 1
                        plot(z, obj.startIndexEst{i}'); hold on;
                        plot(z, startIndexSOS, '.-r');
                        xlabel('Axial distance [mm]');
                    else
                        plot(z, obj.startIndexEst{i}'); hold on;
                        plot(z, startIndexSOS, '.-r');
                        xlabel('Number of measurements');
                    end
                    grid minor; box off;
                    legend('Estimation based on thresholding', 'Estimation based on Z-Coordinate');
                    ylabel('Start Sample [-]');
                end

                % Store calculated start index
                obj.startIndex{i} = startIndexSOS;

                % Compute related indices for further analysis
                obj.reflectIndex{i}         = 3 * obj.startIndex{i};
                obj.preReflectionIndex{i}   = 3 * obj.startIndex{i} - obj.p{i}.acq.samplesPerPeriod * obj.pr.selectionCycles;
                obj.endIndex{i}             = obj.startIndex{i} + floor(obj.p{i}.pulse.duration / 1e3 * obj.p{i}.acq.fs);
                obj.ringupIndex{i}          = obj.startIndex{i} + obj.p{i}.acq.samplesPerPeriod * obj.pr.ringUpcycles;
                obj.postRingUpIndex{i}      = obj.ringupIndex{i} + obj.p{i}.acq.samplesPerPeriod * obj.pr.selectionCycles;
                obj.timeIndex{i}            = obj.startIndex{i} + 1e-6 * obj.pr.time * obj.p{i}.acq.fs;
                obj.preTimeIndex{i}         = obj.timeIndex{i} - obj.p{i}.acq.samplesPerPeriod * obj.pr.selectionCycles;
            end
        end

        %% determine pulse selection window for amplitude estimation
        function obj = pulseWindow(obj,setNrs,mask,pl)
            % This function determines the pulse selection window based on the chosen mask type.
            % The mask is used to extract relevant portions of the signal for amplitude estimation.
            %
            % Inputs:
            %   setNrs - Indices of datasets to process
            %   mask - Selected mask type
            %   pl - Plot flag (unused in current function)
            %
            % Outputs:
            %   obj - Updated object containing selection masks and extracted data

            obj.pr.mask = mask;  % Store selected mask type

            % Iterate over each dataset in setNrs
            for i = setNrs

                % Pre-allocate selection mask
                mask = false(size(obj.filtData{i}));

                % Determine the start and end indices based on the selected mask type
                switch obj.pr.mask
                    case 1 % Mask 1: Between end of ring-up period and end of pulse
                        disp('Mask 1: Between end of ring-up period and end of pulse')
                        start_Index = obj.ringupIndex{i};
                        end_Index = obj.endIndex{i};

                    case 2 % Mask 2: Between 3TOF minus selectionCycles and 3TOF
                        disp('Mask 2: Between 3TOF minus selectionCycles and 3TOF')
                        % Ensure no negative indices
                        preReflectionIndexCor = obj.preReflectionIndex{i};
                        preReflectionIndexCor(obj.preReflectionIndex{i} < 1) = 1;
                        start_Index = preReflectionIndexCor;
                        end_Index = obj.reflectIndex{i};

                    case 3 % Mask 3: Between end of ring-up period and end of ring-up period + selectionCycles
                        disp('Mask 3: Between end of ring-up period and end of ring-up period + selectionCycles')
                        start_Index = obj.ringupIndex{i};
                        end_Index = obj.postRingUpIndex{i};

                    case 4 % Mask 4: Between a specific time selection - selectionCycles to a specific time
                        disp('Mask 4: Between specific time selection - selectionCycles to specific time')
                        start_Index = obj.preTimeIndex{i};
                        end_Index = obj.timeIndex{i};
                end

                % Build selection mask
                for j = 1:size(mask, 2)
                    mask(start_Index(j):end_Index(j), j) = true;
                end

                % Store mask and extracted data
                obj.dataSel.mask{i} = mask;
                obj.dataSel.data{i} = zeros(size(obj.filtData{i}), 'single');
                obj.dataSel.data{i}(:,:) = obj.dataSel.mask{i}(:,:) .* obj.filtData{i};
            end
        end

    end

    methods(Access = private)

        %% in class functions

        function envSignal = envelope(obj, signal)
            % ENVELOPE Computes the envelope of an AC signal using the Hilbert transform.
            % This function estimates the instantaneous amplitude of a given signal.
            %
            % Syntax:
            %   envSignal = envelope(obj, signal)
            %
            % Inputs:
            %   signal    - A matrix representing the input signal.
            %
            % Outputs:
            %   envSignal - A matrix containing the amplitude envelope of the input signal.
            %
            % Example:
            %   envSignal = obj.envelope(signal);

            envSignal = abs(hilbert(signal));
        end

        % function normSignal = normalize(obj,signal)
        %
        %     % normalizes a signal to max = 1
        %     % input:    signal = matrix
        %     % output:   normSignal = matrix
        %
        %     normSignal = signal./max(signal(:));
        % end

        function filtSignal = signalFilter(obj, signal, kernelWidth, kernelStep)
            % signalFilter applies a 1D sliding window filter to a given signal using a custom kernel.
            %
            % Usage example:
            %   filtSignal = signalFilter(obj, dataArray(1:2500), 100, 10);
            %
            % Inputs:
            %   signal        - A 1D array containing the signal data to be filtered.
            %   kernelWidth   - The width of the kernel, determining the range of values to be considered in the filter.
            %   kernelStep    - The step size used to define the range of values in the kernel.
            %
            % Outputs:
            %   filtSignal    - A 1D array containing the filtered signal.
            %
            % The function performs a sliding window operation across the input signal using a custom kernel.
            % For each position in the signal, a kernel is applied and coefficients are computed using the LSQfit function.
            % The filtered signal is then constructed based on the computed coefficients.

            % Initialize the output filtered signal as an array of zeros with the same size as the input signal
            filtSignal = zeros(size(signal));

            % Define the kernel as a range from -kernelWidth to +kernelWidth with steps of kernelStep
            kernel = -kernelWidth:kernelStep:kernelWidth;

            % Apply the sliding window operation over the signal, starting from the position of kernelWidth and ending
            % at numel(signal)-kernelWidth-1 to avoid indexing out of bounds
            for i = kernelWidth:numel(signal)- kernelWidth-1

                % Extract a segment of the signal based on the current position and the kernel range
                signalKernel = signal(1+i+kernel);

                % Use the LSQfit function to fit the signal segment (kernel) and compute the coefficients
                coefs = LSQfit(obj, signalKernel) / kernelStep;

                % Store the second coefficient (likely representing the filtered value) in the output signal
                filtSignal(i) = coefs(2);
            end
        end

        function coefs = LSQfit(obj, y, x)
            % LSQfit performs a least squares (LSQ) fit to a set of data points, optionally using specified x-values.
            %
            % Usage example:
            %   coefs = LSQfit(obj, signal);
            %   inter = coefs(1);   % Intercept of the fitted line
            %   slope = coefs(2);   % Slope of the fitted line
            %
            % Inputs:
            %   y - A vector of dependent variable values (e.g., signal data).
            %   x - A vector of independent variable values (e.g., time or position).
            %         If not provided, a default sequence from 1 to the length of y is used.
            %
            % Outputs:
            %   coefs - A vector of coefficients from the least squares fit.
            %           coefs(1) is the intercept, and coefs(2) is the slope.
            %
            % The function calculates a simple linear regression model: y = intercept + slope * x
            % It returns the coefficients that minimize the squared error between the model and the data points.

            % If only y is provided (i.e., x is not specified), generate a default x-vector from 1 to numel(y)
            if nargin == 2
                x = 1:numel(y);
            end

            % Construct the design matrix A for the linear system
            % The first column of A is all ones (for the intercept), the second column is the x values
            A = [ones(size(x)); x];

            % Solve the least squares problem A*coefs = y by calculating the coefficients
            coefs = (A*A') \ A * y;
        end

        function obj = collectMapIniStruct(obj, i, dataFolder, fileName)
            % collectMapIniStruct reads and collects configuration parameters from the SonoRover One device
            % and maps them into a structure for further processing.
            %
            % Usage example:
            %   obj = collectMapIniStruct(obj, i, 'path/to/folder', 'configFileName');
            %
            % Inputs:
            %   obj         - The current object instance (for storing the processed data).
            %   i           - An index for storing the result in the object (obj.p{i}).
            %   dataFolder  - The folder containing the .ini configuration file.
            %   fileName    - The name of the .ini configuration file (without extension).
            %
            % Outputs:
            %   obj         - The updated object with the collected data in obj.p{i}.
            %
            % The function reads a configuration file, extracts various parameters, 
            % and stores them in a structured format. The data includes general information, 
            % measurements, water properties, amplifier and transducer settings, pulse details, 
            % acquisition parameters, and hydrophone data.
            
            % Clear previous structures to avoid data conflicts.
            S = [];
            s = [];

            % Read the .ini configuration file from the specified folder and file name
            S = readIniFile(fullfile(dataFolder, [fileName, '.ini']));

            % General information: timestamp from the configuration
            s.gen.timeStamp = S.General.timestamp;

            % Measurement data: sequence type and sequence number
            s.measurement.type = S.Sequence.tag;
            s.measurement.sequenceNr = S.Sequence.sequenceNumber;

            % Water information: temperature, dissolved oxygen level, and computed values (speed of sound, density)
            s.water.T = S.General.temperatureOfWater__c_;
            s.water.Tunit = 'Degrees Celcius';
            s.water.DO = S.General.dissolvedOxygenLevelOfWater_mg_l_;
            [s.water.c, s.water.rho] = cwater(S.General.temperatureOfWater__c_);
            s.water.Z = s.water.c * s.water.rho;  % Speed of sound * density
            s.water.cUnit = 'm/s';
            s.water.DOunit = 'mg/L';

            % Amplifier information: name, manufacturer, and power-related data
            s.amp.name = S.Equipment.drivingSystem_name;
            s.amp.manufacturer = S.Equipment.drivingSystem_manufact;
            if isequal(S.Equipment.drivingSystem_manufact, 'Sonic Concepts')
                s.amp.power = S.Sequence.sc_GlobalPower_w_;
                s.amp.powerUnit = 'W';
            elseif isequal(S.Equipment.drivingSystem_manufact, 'IGT')
                s.amp.power = S.Sequence.igt_Amplitude___;
                s.amp.powerUnit = '%';
                s.amp.maxPressure = S.Sequence.igt_MaximumPressureInFreeWater_mpa_;
                s.amp.maxPressureUnit = 'MPa';
            end

            % Transducer information: name, ID, frequency, and focal properties
            s.TD.name = S.Equipment.transducer_name;
            s.TD.ID = S.Equipment.transducer_serial_number;
            s.TD.f0 = S.Equipment.transducer_fund_freq * 1e3;  % Convert from kHz to Hz
            s.TD.f0Unit = 'Hz';
            s.TD.Focus = S.Sequence.focusWrtExitPlane_mm_;
            s.TD.FocusUnit = 'mm';
            s.TD.focalRange = [S.Equipment.transducer_min_foc, S.Equipment.transducer_max_foc];
            s.TD.focalRangeUnit = 'mm';

            % Oscilloscope information: name and ID
            s.OS.name = S.Acquisition.picoscope;
            s.OS.ID = S.Acquisition.picoscopePico_pyIdentification;

            % Pulse information: duration of the pulse in milliseconds
            s.pulse.duration = S.Sequence.pulseDuration_ms_;
            s.pulse.Unit = 'ms';

            % Acquisition parameters: sampling frequency, duration, and number of samples
            s.acq.fs = S.Acquisition.samplingFrequency_hz_;
            s.acq.fsUnit = 'Hz';
            s.acq.duration = S.Acquisition.hydrophoneAcquisitionTime_us_;
            s.acq.durationUnit = 'us';
            s.acq.samples = S.Acquisition.amountOfSamplesPerAcquisition;
            s.acq.samplesPerPeriod = S.Acquisition.samplingFrequencyMultiplicationFactor;
            s.acq.timeVec = [0:1/s.acq.fs:s.acq.samples/s.acq.fs];  % Time vector for the acquisition

            % Hydrophone information: ID and sensitivity in V/Pa
            s.HP.ID = S.Acquisition.hydrophone;
            s.HP.sensitivity = S.Acquisition.sensitivity_v_pa_CorrespondingToUsedFreq_;
            s.HP.sensitivityUnit = 'v/Pa';

            % Store the collected data in the object at the specified index
            obj.p{i} = s;
        end

    end
end










