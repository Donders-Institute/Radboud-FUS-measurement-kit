classdef dataCalc
    %DATACALC Summary of this class goes here
    %   Detailed explanation goes here

    properties


        % in class dataCalc variables



        % calculate amplitude
        ampEstimation = [];
        spatialFilt = [];
        holography = [];

        pressure   = [];
        intensity  = [];
        PII        = [];
        ISPPA      = [];
        ISPPAsc    = [];
        hydrophone = [];

    end

    properties (Access = private)

        % input structs previous class dataPrep
        prepData = [];


    end

    properties (Constant)

        filtOrder = 100;
    end


    methods
        function obj = dataCalc(prepData)
            % DATACALC Processes calibration data for different hydrophones
            % and generates a plot comparing the sensitivities over different calibration dates.
            %
            % Usage example:
            %   obj = dataCalc(prepData);
            %
            % Inputs:
            %   prepData - Preprocessed data that is assigned to the object (obj).
            %
            % Outputs:
            %   obj - The updated object with the processed hydrophone data and generated plot.
            %
            % This function reads calibration data for multiple hydrophones, stores them in
            % a structure, and plots sensitivity comparisons between different calibration dates.

            % Initialize hydrophone structures for different devices
            hydrophone(1).fileName{1} = 'HGL0200-2845_AG2010-1378-20_CA_20230511.txt';
            hydrophone(1).Type = 'Hydrophone HGL 0200 SN2845';
            hydrophone(1).SN = '2845';
            hydrophone(1).calDate{1} = datetime('2023-05-11');
            hydrophone(1).sensitivity{1} = obj.readCalData(hydrophone(1).fileName{1});

            % Recalibration on 26-09-2024
            hydrophone(1).fileName{2} = 'HGL0200-2845_AG2010-1378-20_CA_20240826.txt';
            hydrophone(1).calDate{2} = datetime('2024-08-26');
            hydrophone(1).sensitivity{2} = obj.readCalData(hydrophone(1).fileName{2});

            % Add a placeholder date for the next calibration
            hydrophone(1).calDate{end+1} = datetime('3000-01-01');

            % HNR 0500 2439: Initial calibration 27-09-2024
            hydrophone(2).fileName{1} = 'HNR0500-2439_xxxxxx-xxxx-xx_xx_20240827.txt';
            hydrophone(2).Type = 'Hydrophone HNR 0500 SN2439';
            hydrophone(2).SN = '2439';
            hydrophone(2).calDate{1} = datetime('2024-08-26');
            hydrophone(2).sensitivity{1} = obj.readCalData(hydrophone(2).fileName{1});

            % HGL 0200 3030: Initial calibration 20-11-2024
            hydrophone(3).fileName{1} = 'HGL0200-3030_AG2010-1446-20_CA_20241120.txt';
            hydrophone(3).Type = 'Hydrophone HGL 0200 SN3030';
            hydrophone(3).SN = '3030';
            hydrophone(3).calDate{1} = datetime('2024-11-20');
            hydrophone(3).sensitivity{1} = obj.readCalData(hydrophone(3).fileName{1});


            %--------------------------------------------------------------
            % Create a figure for sensitivity comparison
            figure('Color',[1 1 1]);

            % Plot the sensitivity values for the first hydrophone, comparing two calibration dates
            yyaxis left
            plot(1000*hydrophone(1).sensitivity{1}(:,1), 1./(1e9*hydrophone(1).sensitivity{1}(:,2)), 'r.-'); hold on;
            plot(1000*hydrophone(1).sensitivity{2}(:,1), 1./(1e9*hydrophone(1).sensitivity{2}(:,2)), 'b.-');

            % Label the left axis (Sensitivity)
            ylabel('Sensitivity (mV/MPa)');
            yyaxis right
            % Plot relative deviation between the two calibration data sets
            plot(1000*hydrophone(1).sensitivity{1}(:,1), 100*(hydrophone(1).sensitivity{2}(:,2) ./ hydrophone(1).sensitivity{1}(:,2)));
            ylim([90 110]); ylabel('Relative deviation [%]');
            box off; grid minor;

            % Add legend and labels
            legend([hydrophone(1).Type, ' ', datestr(hydrophone(1).calDate{1})], ...
                [hydrophone(1).Type, ' ', datestr(hydrophone(1).calDate{2})], ...
                ['Relative deviation [%]']);
            xlabel('Frequency [kHz]');
            xlim([0 1000]);

            %--------------------------------------------------------------
            % Connect the preprocessed data and hydrophone calibration data to the object
            obj.prepData = prepData;
            obj.hydrophone = hydrophone;
        end


        function obj = calcAmplitude(obj,setNrs,ampEstMethod)
            % CALCAMPLITUDE Estimates the amplitude and phase of signals based on the chosen method.
            %
            % This function estimates the amplitude and phase for selected signals from the data
            % based on different methods such as FFT, Phasor, Hilbert Transform, and K-wave.
            %
            % Inputs:
            %   - setNrs: A set of numbers indicating which data to process (not used directly in this function).
            %   - ampEstMethod: A method number indicating which amplitude estimation technique to use:
            %       1: FFT method
            %       2: Phasor method
            %       3: Hilbert Transform method
            %       4: K-wave method
            %
            % Outputs:
            %   - obj: The object instance with amplitude and phase estimation stored in it.
            %
            % The function processes each signal in the data set and calculates its amplitude and phase
            % using the chosen method. The results are stored in the object's `ampEstimation` property.

            % Store the chosen amplitude estimation method in the object's prepData
            obj.prepData.pr.ampEstMethod = ampEstMethod;

            % Loop over each selected dataset in the prepData
            for i = 1:size(obj.prepData.dataSel.data,2)

                % Only process if the data is not empty
                if ~isempty(obj.prepData.dataSel.data{i})

                    % Retrieve fundamental frequency and sampling frequency
                    f0 = obj.prepData.p{i}.TD.f0;
                    Fs = obj.prepData.p{i}.acq.fs;

                    % Loop over each signal in the dataset
                    for j = 1: size(obj.prepData.dataSel.data{i},2)

                        % Select the window for signal processing
                        mask   = obj.prepData.dataSel.mask{i}(:,j);  % selection window
                        t      = obj.prepData.p{i}.acq.timeVec';     % time vector

                        % Extract the signal and time based on the selection window
                        signal = obj.prepData.dataSel.data{i}(mask,j);
                        time   = obj.prepData.p{i}.acq.timeVec(mask);

                        % Skip if the signal is empty
                        if numel(signal) == 0
                            break
                        end

                        try
                            % Choose the amplitude estimation method based on user input
                            switch obj.prepData.pr.ampEstMethod

                                case 1
                                    % Amplitude estimation using FFT (Fast Fourier Transform)
                                    [~, amplitude, phase] = calcFFT(obj,obj.prepData.p{i}.acq.fs,signal);
                                    [a,b] = max(amplitude);

                                    % Store the calculated amplitude and phase
                                    obj.ampEstimation{i}.amp(j)   = a;
                                    obj.ampEstimation{i}.phase(j) = phase(b);
                                    obj.ampEstimation{i}.method = 'FFT';

                                case 2
                                    % Amplitude estimation using Phasor (complex exponential)
                                    IQ = signal .* exp(1i * 2 * pi * f0 * time);

                                    % Calculate the magnitude and phase
                                    obj.ampEstimation{i}.amp(j) = abs(mean(IQ)) * 2;  % Amplitude is doubled
                                    obj.ampEstimation{i}.phase(j) = angle(mean(IQ));
                                    obj.ampEstimation{i}.method = 'Phasor';

                                case 3
                                    % Amplitude estimation using Hilbert Transform
                                    HilbertTransform = hilbert(signal);

                                    % Calculate the magnitude and phase
                                    obj.ampEstimation{i}.amp(j)   = mean(abs(HilbertTransform));
                                    obj.ampEstimation{i}.phase(j) = angle(HilbertTransform(1));
                                    obj.ampEstimation{i}.method   = 'Hilbert transform';

                                case 4
                                    % Amplitude estimation using K-wave
                                    [obj.ampEstimation{i}.amp(j), obj.ampEstimation{i}.phase(j), ~] = extractAmpPhase(signal, Fs, f0);
                                    obj.ampEstimation{i}.method   = 'K-wave';
                            end
                        catch
                            % Catch any errors during the calculation
                            disp('could not calculate amplitude');
                        end
                    end
                end
            end
        end


        function obj = calcSpatialFiltering(obj,steNrs,scf,ripple,passBandAtten)


            % CALCSPATIALFILTERING Applies spatial low-pass filtering to amplitude data.
            %
            %   obj = CALCSPATIALFILTERING(obj, setNrs) performs spatial filtering
            %   on estimated amplitude data along the z-direction if applicable.
            %
            %   The function:
            %
            %   - Checks if the data is 1D along the z-axis or contains scan step size (dz).
            %   - Designs a Butterworth low-pass filter based on the spatial cutoff frequency.
            %   - Determines the filter order using passband ripple and stopband attenuation.
            %   - Applies zero-phase filtering using filtfilt for minimal phase distortion.
            %   - Sets negative filtered amplitudes to zero (assuming no underpressure).
            %   - Stores the filtered amplitude in the object's spatial filtering data.
            %
            %   Inputs:
            %       obj    - Object containing amplitude estimation and preprocessing data.
            %       setNrs - (Unused parameter in the provided code snippet)
            %
            %   Outputs:
            %       obj    - Updated object with spatially filtered amplitude data.

            for i = 1:size(obj.ampEstimation,2)

                if isequal(obj.prepData.dim(i,:),[0 0 1]) && isfield(obj.prepData.p{i}.scan,'dz')

                    % strore input values to object.
                    obj.spatialFilt{i}.scf           = scf;             % spatial cutoff frequecy [1/mm]
                    obj.spatialFilt{i}.ripple        = ripple;          % passband ripple [dB]
                    obj.spatialFilt{i}.passBandAtten = passBandAtten;   % stopband attentuation in [dB]

                    amp = obj.ampEstimation{i}.amp;

                    % Design the low pass filter
                    Fs              = 1/obj.prepData.p{i}.scan.dz;   % Sampling frequency [samples/mm] in z direction
                    Nyquist         = Fs/2;
                    fCutOff         = scf;              % spatial cutoff frequency scf [1/mm]

                    % Example parameters; source needs checking. filterorder
                    % determination by GPT
                    Ap = ripple;        % Passband ripple in dB
                    As = passBandAtten; % Stopband attenuation in dB

                    % Calculate filter order
                    N = ceil((log10(sqrt((10^(0.1*Ap) - 1)/(10^(0.1*As)))) / log10(fCutOff / Fs)));

                    % define filter
                    [b,a] = butter(N, fCutOff/Nyquist, 'low');

                    % do the filtering
                    filtAmplitude = filtfilt(b,a,amp);

                    % set pressures below zero to zero; no
                    % underpressures possible
                    filtAmplitude(filtAmplitude<0) =0;

                    % Storage
                    obj.spatialFilt{i}.amp = filtAmplitude;
                end
            end
        end

        function obj = calcPressure(obj,setNrs)
            % CALCPRESSURE Computes the acoustic pressure from measured hydrophone data.
            %
            %   obj = CALCPRESSURE(obj, setNrs) calculates the acoustic pressure
            %   based on hydrophone sensitivity and measured data.
            %
            %   The function:
            %
            %   - Identifies the appropriate hydrophone type for each dataset.
            %   - Retrieves the most recent calibration data prior to the measurement.
            %   - Interpolates hydrophone sensitivity at the measurement frequency.
            %   - Computes the pressure from filtered signal data and estimated amplitudes.
            %   - Applies spatial filtering corrections if available.
            %   - Performs Full Width at Half Maximum (FWHM) calculations for 1D data.
            %   - Assigns pressure units as Pascals ('Pa').
            %
            %   Inputs:
            %       obj    - Object containing measurement and calibration data.
            %       setNrs - (Unused parameter in the provided code snippet)
            %
            %   Outputs:
            %       obj    - Updated object with computed pressure values.


            for i = 1:size(obj.ampEstimation,2)

                % find hydrophone type
                h = 1;
                while ~strcmp(obj.hydrophone(h).Type,obj.prepData.p{i}.HP.ID)
                    h = h+1;
                end

                % Find calibration data
                d = 1;  % Initialize calibration date index
                timeStamp   = datetime(obj.prepData.p{i}.gen.timeStamp(1:10));  % Extract and convert timestamp from data
                calDates    = obj.hydrophone(h).calDate;  % Retrieve available calibration dates for the hydrophone
                numCalDates = numel(calDates);  % Get total number of calibration dates

                % Loop through calibration dates to find the most recent one before the measurement timestamp
                while d < numCalDates && timeStamp > calDates{d+1}
                    d = d + 1;
                end

                % Extract sensitivity data for the selected calibration date
                frequencyRange      = obj.hydrophone(h).sensitivity{d}(:,1);  % Frequency values
                sensitivityRange    = obj.hydrophone(h).sensitivity{d}(:,2);  % Sensitivity values

                % Interpolate sensitivity at the measurement frequency
                obj.pressure{i}.sensFreq = interp1(frequencyRange, sensitivityRange, obj.prepData.p{i}.TD.f0 * 1e-6, 'linear');

                % Compute pressure of the pulse data and raw amplitude values using the hydrophone sensitivity
                obj.pressure{i}.pulseData   = obj.prepData.filtData{i} ./ obj.pressure{i}.sensFreq;
                obj.pressure{i}.amp.raw     = obj.ampEstimation{i}.amp / obj.pressure{i}.sensFreq;

                % Display information about the measurement, hydrophone, and calibration used
                disp(sprintf('Measured at %s: Uses %s with sensitivity %d calibrated at %s', ...
                    datetime(obj.prepData.p{i}.gen.timeStamp(1:10)), obj.hydrophone(h).Type, ...
                    obj.pressure{i}.sensFreq, obj.hydrophone(h).calDate{d}))

                % Check if spatial filtering amplitude data exists
                if isfield(obj.spatialFilt{i}, 'amp')

                    % Apply spatial filter correction to amplitude
                    obj.pressure{i}.amp.spatialFilt = obj.spatialFilt{i}.amp / obj.pressure{i}.sensFreq;

                    % Perform FWHM (Full Width at Half Maximum) calculation if the data is 1D along z-axis
                    if isequal(obj.prepData.dim(i,:), [0 0 1])
                        z = obj.prepData.coordinates{i}(:,6); % Extract z-coordinates (in mm)
                        % Estimate spatial filtering metrics using the amplitude data
                        obj.pressure{i}.amp.spatialFiltMetrics = estMetrics(obj, z, obj.pressure{i}.amp.spatialFilt');
                    end
                end
            end

            obj.pressure{i}.Unit = 'Pa';
        end

        function obj = calcIntensity(obj,setNrs)
            % METHOD1 Summary of this method goes here
            %   Detailed explanation goes here

            for i = 1:size(obj.ampEstimation,2)

                Z = obj.prepData.p{i}.water.Z;

                obj.intensity{i}.pulseData        = obj.pressure{i}.pulseData.^2 /Z;
                obj.intensity{i}.amp.raw          = obj.pressure{i}.amp.raw.^2 /Z;

                if isfield(obj.pressure{i}.amp,'spatialFilt')
                    obj.intensity{i}.amp.spatialFilt  = obj.pressure{i}.amp.spatialFilt.^2 /Z;
                end

            end
        end

        function obj = calcISPPA(obj,setNrs)
            % CALCISPPA Computes the spatial-peak pulse-average intensity (ISPPA).
            %
            %   obj = CALCISPPA(obj, setNrs) calculates the ISPPA by adjusting the
            %   acoustic intensity values.
            %
            % The function:
            %
            %   - Computes ISPPA from the raw intensity amplitude by dividing by 2 and converting units.
            %   - If spatially filtered intensity data is available, applies the same computation.
            %   - Stores the computed ISPPA values in the object.
            %
            %   Inputs:
            %       obj    - Object containing intensity data.
            %       setNrs - (Unused parameter in the provided code snippet).
            %
            %   Outputs:
            %       obj    - Updated object with computed ISPPA values.

            for i = 1:size(obj.intensity,2)

                obj.ISPPA{i}.amp.raw          = obj.intensity{i}.amp.raw/2/100^2;
                if isfield(obj.intensity{i}.amp,'spatialFilt')
                    obj.ISPPA{i}.amp.spatialFilt  = obj.intensity{i}.amp.spatialFilt/2/100^2;

                    % calculate Metrics
                    z = obj.prepData.coordinates{i}(:,6); % Extract z-coordinates (in mm)
                    obj.ISPPA{i}.amp.spatialFiltMetrics = estMetrics(obj, z, obj.ISPPA{i}.amp.spatialFilt');

                end
            end
        end

        function obj = calcISPPA2NFscale(obj,setNrs,NFD)
            % CALCISPPA2NFSCALE Scales ISPPA values using near-field correction factors.
            %
            %   obj = CALCISPPA2NFSCALE(obj, setNrs, NFD) adjusts the ISPPA values
            %   based on NeuroFus data for Sonic Concepts transducers.
            %
            % The function:
            %
            %   - Checks if the measurement was performed using a Sonic Concepts transducer.
            %   - Identifies the corresponding transducer and amplifier from the dataset.
            %   - Searches the provided NeuroFus data (NFD) for matching transducer and amplifier IDs.
            %   - Retrieves the appropriate scale factor and applies it to raw and spatially filtered ISPPA values.
            %   - Performs Full Width at Half Maximum (FWHM) calculations for spatially filtered data if applicable.
            %   - Stores the scale factor, set power values, and transducer details in the object.
            %   - Displays a message if the transducer is not from Sonic Concepts, as scaling is only applicable for those.
            %
            %   Inputs:
            %       obj    - Object containing ISPPA data and measurement details.
            %       setNrs - (Unused parameter in the provided code snippet).
            %       NFD    - Structure containing NeuroFus data.
            %
            %   Outputs:
            %       obj    - Updated object with scaled ISPPA values and metadata.

            for i = 1:size(obj.ISPPA,2)  % Loop through each ISPPA measurement

                % Check if the amplifier manufacturer is 'Sonic Concepts'
                if isequal(obj.prepData.p{i}.amp.manufacturer, 'Sonic Concepts')

                    % Extract transducer and amplifier identifiers from their names
                    transducerID  = obj.prepData.p{i}.TD.name(end-10:end);  % Last 11 characters of transducer name
                    amplifierID   = obj.prepData.p{i}.amp.name(end-6:end-4); % Extract amplifier ID from the last 3 characters

                    td = [];  % Initialize transducer index
                    tpo = []; % Initialize amplifier index

                    % Loop through the Near Field Data (NFD) structure to find a match
                    for TD = 1:size(NFD.NFdata,1)
                        for TPO = 1:size(NFD.NFdata,2)

                            % Check if the current NFD entry has a valid file name
                            if ~isempty(NFD.NFdata(TD,TPO).fileName)

                                % Extract transducer and amplifier names from the NFD structure
                                NeuroFusName  = NFD.NFdata(TD,TPO).fileName;
                                TPOname       = NFD.NFdata(TD,TPO).properties(1).values; % Amplifier TPO name

                                % Check if the transducer and amplifier match the current measurement
                                if contains(NeuroFusName, transducerID) && contains(TPOname, amplifierID)
                                    td = TD;  % Store transducer index
                                    tpo = TPO; % Store amplifier index
                                end
                            end
                        end
                    end

                    if isempty(td) || isempty(TPO)

                        disp('No NeuroFus data found for this combination of TPO and transducer')
                    else

                        % Compute the scale factor by comparing the NFD setpoint power to the measured power
                        scaleFactor = NFD.NFdata(td,tpo).properties(2).values / obj.prepData.p{i}.amp.power;

                        % Scale the raw ISPPA amplitude using the computed scale factor
                        obj.ISPPAsc{i}.amp.raw = obj.ISPPA{i}.amp.raw * scaleFactor;

                        % Check if spatially filtered ISPPA amplitude data exists
                        if isfield(obj.ISPPA{i}.amp, 'spatialFilt')
                            % Scale the spatially filtered ISPPA amplitude
                            obj.ISPPAsc{i}.amp.spatialFilt = obj.ISPPA{i}.amp.spatialFilt * scaleFactor;

                            % Perform Full Width at Half Maximum (FWHM) calculation if the data is 1D along the z-axis
                            if isequal(obj.prepData.dim(i,:), [0 0 1]) || isfield(obj.prepData.p{i}.scan, 'dz')
                                z = obj.prepData.coordinates{i}(:,6); % Extract z-coordinates (in mm)
                                obj.ISPPAsc{i}.amp.spatialFiltMetrics = estMetrics(obj, z, obj.ISPPAsc{i}.amp.spatialFilt');
                            end
                        end

                        % Perform FWHM calculation for the pressure spatially filtered data
                        if isequal(obj.prepData.dim(i,:), [0 0 1]) && isfield(obj.prepData.p{i}.scan, 'dz')
                            z = obj.prepData.coordinates{i}(:,6); % Extract z-coordinates (in mm)
                            obj.pressure{i}.amp.spatialFiltMetrics = estMetrics(obj, z, obj.pressure{i}.amp.spatialFilt');
                        end

                        % Store calculated scale factor and relevant metadata in the object
                        obj.ISPPAsc{i}.scaleFactor              = scaleFactor;
                        obj.ISPPAsc{i}.TPOsetPointinW           = NFD.NFdata(td,tpo).properties(2).values;
                        obj.ISPPAsc{i}.TPOsetPointMeasurement   = obj.prepData.p{i}.amp.power;
                        obj.ISPPAsc{i}.TD_TPO                   = [td, tpo];
                        obj.ISPPAsc{i}.Transducer               = NFD.NFdata(td,tpo).fileName;
                        obj.ISPPAsc{i}.TPO                      = NFD.NFdata(td,tpo).properties(1).values;
                    end
                else
                    % Display a message if the transducer is not from Sonic Concepts
                    disp('Comparison only possible for Sonic Concepts transducers')
                end

            end

        end

        function obj = calcHolography(obj,setNrs,ipf,zv)

            % CALCHOLOGRAPHY Computes holographic reconstruction of the pressure field.
            %
            %   obj = CALCHOLOGRAPHY(obj, setNrs, ipf, zv) performs holographic reconstruction of the pressure field
            %   using the Angular Spectrum Method (ASM) to propagate the wave field from a 2D plane to 3D.
            %
            % The function:
            %
            %   - Checks if the data corresponds to a plane (XY plane, no Z variation).
            %   - Extracts and reshapes amplitude and phase information.
            %   - Interpolates the data to increase resolution using Fourier-based methods.
            %   - Creates a circular mask to remove outer regions of the data.
            %   - Propagates the wave field using the Angular Spectrum Method (ASM).
            %   - Converts the complex wave field back to amplitude and phase representations.
            %   - Computes pressure values using the hydrophone sensitivity.
            %   - Extracts the axial profile at the center of the grid for further analysis.
            %
            %   Inputs:
            %       obj   - Object containing the amplitude estimation and measurement data.
            %       setNrs - (Unused parameter in the provided code snippet).
            %       ipf   - Interpolation factor to increase the grid resolution.
            %       zv    - Z-positions for wave propagation (depth values).
            %
            %   Outputs:
            %       obj   - Updated object with holography data, including 3D amplitude, pressure, and axial profiles.

            for i = 1:size(obj.ampEstimation,2)

                % Check if the data corresponds to a plane (XY plane, no Z variation)
                if isequal(obj.prepData.dim(i,:),[1 1 0])

                    % Read spatial coordinates and convert from mm to meters
                    x = obj.prepData.coordinates{i}(:,4)*1e-3;
                    y = obj.prepData.coordinates{i}(:,5)*1e-3;
                    z = obj.prepData.coordinates{i}(:,6)*1e-3;

                    % make 2D grid
                    [xm,ym] = meshgrid(x,y);

                    % Determine grid size for reshaping the 2D data
                    ms = sqrt(numel(x));

                    % Create an interpolated grid with increased resolution (ipf factor)
                    xvi = linspace(min(x),max(x),ms*ipf);
                    yvi = linspace(min(y),max(y),ms*ipf);
                    [xmi,ymi,zmi] = meshgrid(xvi,yvi,zv);
                    dxyi = diff(yvi(1:2)); % Grid spacing in the interpolated data

                    % Extract and reshape amplitude and phase information
                    amp2D      = double(reshape(obj.ampEstimation{i}.amp,[ms,ms]));
                    phase2D    = double(reshape(obj.ampEstimation{i}.phase,[ms,ms]));

                    % Convert amplitude and phase into complex representation
                    complexAmp2D = amp2D .* exp(1i * phase2D);

                    % Perform interpolation to increase resolution using Fourier-based method
                    complexAmp2Di = interpft(complexAmp2D, size(complexAmp2D,1)*ipf, 1);
                    complexAmp2Di = interpft(complexAmp2Di, size(complexAmp2D,2)*ipf, 2);

                    % Create a circular mask to remove outer regions
                    [n,~] = size(complexAmp2Di);
                    [xid,yid] = meshgrid(1:n,1:n);
                    radius = n/2; % Define circular radius
                    centerID = ceil(size(complexAmp2Di)/2); % Find center index
                    distance = sqrt((xid - centerID(1)).^2 + (yid - centerID(2)).^2); % Compute distance from center
                    cirMask = distance <= radius; % Logical mask for circular region

                    % Apply the mask: Set values outside the circle to zero
                    complexAmp2Di(~cirMask) = 0;

                    % Propagate the wave field using the Angular Spectrum Method
                    z_pos = zv - z(1); % Calculate relative z positions
                    complexAmp3D = angularSpectrumCW(complexAmp2Di, dxyi, z_pos, obj.prepData.p{i}.TD.f0, obj.prepData.p{i}.water.c);

                    % Convert complex wavefield back to amplitude and phase representations
                    ASamp3D   = abs(complexAmp3D);
                    ASphase3D = angle(complexAmp3D);

                    % Store the computed holography data in the object

                    % 2D grid
                    % input plane
                    obj.holography{i}.grid.xm = xm;
                    obj.holography{i}.grid.ym = ym;

                    % 3D grid
                    obj.holography{i}.grid.xmi = xmi;
                    obj.holography{i}.grid.ymi = ymi;
                    obj.holography{i}.grid.zmi = zmi;

                    %2D input data
                    obj.holography{i}.input.amplitude2D = amp2D;
                    obj.holography{i}.input.phase2D     = phase2D;

                    % conversion to interpolated phase and amplitude planes
                    obj.holography{i}.intInput.amplitude2D = abs(complexAmp2Di);
                    obj.holography{i}.intInput.phase2D = angle(complexAmp2Di);

                    % output 3D
                    obj.holography{i}.amplitude3D   = ASamp3D;
                    obj.holography{i}.phase3D       = ASphase3D;

                    % Convert amplitude to pressure using hydrophone sensitivity
                    obj.holography{i}.pressure2D    = amp2D ./ obj.pressure{i}.sensFreq;
                    obj.holography{i}.intPressure2D = abs(complexAmp2Di) ./ obj.pressure{i}.sensFreq;
                    obj.holography{i}.pressure3D    = ASamp3D ./ obj.pressure{i}.sensFreq;

                    % Extract the axial profile at the center of the grid
                    obj.holography{i}.grid.z = squeeze(obj.holography{i}.grid.zm(ceil(n/2),ceil(n/2),:));
                    obj.holography{i}.centerAxialProfile = squeeze(obj.holography{i}.pressure3D(ceil(n/2),ceil(n/2),:));
                end
            end
        end


    end
    methods(Access = private)

        function data = readCalData(~, fileNamePath)
            % READCALDATA Extracts hydrophone sensitivity data from a calibration file.
            %
            % This function reads a calibration data file, searches for the section where the
            % actual sensitivity data starts, and extracts the frequency and sensitivity
            % values. It returns the extracted data as an array with two columns: frequency
            % and sensitivity in V/Pa.
            %
            % Inputs:
            %   - fileNamePath: The full file path to the calibration data file.
            %
            % Outputs:
            %   - data: A matrix containing frequency and sensitivity values.
            %           The first column is the frequency (MHz), and the second column
            %           is the sensitivity in V/Pa.
            %

            % Open the file for reading
            fid = fopen(fileNamePath, 'r');  % Try to open the file in read mode
            if fid == -1
                error('Could not open the file.');  % If the file couldn't be opened, show an error message
            end

            % Initialize variables
            header_end_found = false;  % Flag to mark when the header section ends
            data = [];  % Initialize the data matrix to store frequency and sensitivity values

            % Loop through the file line by line
            while ~feof(fid)  % Continue until the end of the file is reached
                line = fgetl(fid);  % Read a line from the file
                if contains(line, 'HEADER_END')  % If the line contains 'HEADER_END', stop reading the header
                    header_end_found = true;
                    continue;  % Skip the line and proceed to the next one
                end
                if header_end_found  % Start reading data after the header has ended
                    values = str2num(line);  %#ok<ST2NM>  % Convert the line into numbers
                    if numel(values) >= 3  % Ensure there are at least three values (Frequency, Sensitivity, and another value)
                        % Store the first and third columns (Freq and Sens) in the data matrix
                        data = [data; values(1), values(3)];
                    end
                end
            end

            % Close the file after processing
            fclose(fid);
        end

        function [frequency, amplitude, phase] = calcFFT(~, sampleFrequency, signal)
            % CALCFFT Calculates the FFT of a given signal and returns its frequency, amplitude, and phase.
            %
            % This function computes the Fast Fourier Transform (FFT) of the input signal and
            % returns the corresponding frequency, amplitude, and phase of the signal in the
            % frequency domain.
            %
            % Inputs:
            %   - sampleFrequency: The sampling frequency of the signal (in Hz).
            %   - signal: The signal to be transformed (in the time domain).
            %
            % Outputs:
            %   - frequency: The frequency components of the FFT (in Hz).
            %   - amplitude: The amplitude of the signal at each frequency.
            %   - phase: The phase of the signal at each frequency.

            % Length of the signal
            L = length(signal);  % Determine the number of samples in the signal

            % Compute the FFT of the signal
            Y = fft(signal);  % Perform the FFT to get the frequency-domain representation of the signal

            % Compute the two-sided power spectrum
            P2 = abs(Y/L);  % Normalize the FFT result by the signal length
            phase = angle(Y/L);  % Compute the phase of the FFT (angle in radians)

            % Convert to a single-sided spectrum
            P1 = P2(1:floor(L/2+1));  % Take the positive half of the frequency components
            P1(2:end-1) = 2*P1(2:end-1);  % Double the amplitudes for the non-DC components (except Nyquist)

            % Define the frequency domain corresponding to the FFT result
            frequency = sampleFrequency*(0:(L/2))/L;  % Define the frequency axis, scaled by the sampling frequency

            % The amplitude of the signal in the frequency domain (single-sided spectrum)
            amplitude = P1;  % Set the amplitude to the computed single-sided power spectrum
        end


        function metrics = estMetrics(obj, x, ym)
            % ESTMETRICS Estimates various metrics (maximum value, position, FWHM) for each signal in ym.
            %
            % This function calculates metrics such as the maximum value, the position of the
            % maximum, the left and right points of the Full Width at Half Maximum (FWHM), and
            % the mean FWHM position for each signal in the matrix ym.
            %
            % Inputs:
            %   - x: The vector of x-values (e.g., time or frequency values corresponding to ym).
            %   - ym: A matrix where each column represents a signal to analyze.
            %
            % Outputs:
            %   - metrics: A matrix where each column corresponds to the metrics for each signal.
            %              Each row includes [max value, position of max value, left point, FWHM, right point].
            %
            % Example:
            %   metrics = estMetrics(obj, x, ym);

            for i = 1:size(ym, 2)  % Loop through each signal in ym (column-wise)

                y = ym(:,i);  % Extract the current signal

                % Find the maximum value and its index in the signal
                [maxVal, maxIndex] = max(y);

                try
                    % Find the Full Width at Half Maximum (FWHM) points
                    % crossing() function finds the points where the signal crosses half of its maximum value
                    [ind, x0, y0, x0close, x0close] = crossing(y, x, 0.5 * y(maxIndex), 'linear');

                    % Check if there are two crossing points (i.e., FWHM)
                    if numel(x0) == 2
                        % Store the metrics: max value, position of max value, left point, mean of FWHM, and right point
                        metrics(:,i) = [maxVal, x(maxIndex), x0(1), mean(x0), x0(2)];

                        % Check if there is only one crossing point (FWHM only on one side)
                    elseif numel(x0) == 1
                        metrics(:,i) = [maxVal, x(maxIndex), x0(1), nan, max(x)];

                        % If no crossing points are found, set all metrics to NaN
                    else
                        metrics(:,i) = [maxVal, x(maxIndex), nan, nan, nan];
                        disp('No focus determination possible, setting metrics to NaN.');
                    end
                catch
                    % If there's an error in the process, return NaN for the metrics
                    metrics(:,i) = [nan, nan, nan, nan, nan];
                    disp('No focus determination possible, setting metrics to NaN.');
                end

            end
        end


    end
end

