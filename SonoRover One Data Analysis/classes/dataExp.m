classdef dataExp    %DATACALC Summary of this class goes here
    %   Detailed explanation goes here

    properties


        % in class dataExport variables

        % from dataprep
        prepData = [];
        calcData = [];



    end

    properties (Access = private)

        % input structs previous class dataPrep
        ob = [];
        folderLoc  = [];
        data = [];
    end



    methods
        function obj = dataExp(prepData, calcData)
            % dataExp - This function creates a directory for storing processed data.
            %
            % Syntax: obj = dataExp(prepData, calcData)
            %
            % Inputs:
            %    prepData - Preprocessed data structure (input to the function).
            %    calcData - Calculated data structure (input to the function).
            %
            % Outputs:
            %    obj - The updated object containing postprocessed data and folder location.
            %
            % Description:
            %    This function constructs a directory path based on the current timestamp and
            %    specified data location. It creates a folder in which processed results will
            %    be saved. The folder is named based on a base name ("export") combined with
            %    the current timestamp, ensuring that folders are uniquely named.
            %
            % Example:
            %    obj = dataExp(prepData, calcData);  % Generates and stores results in a folder.

            % Store the input data into the object
            obj.prepData = prepData;  % Store the preprocessed data
            obj.calcData = calcData;  % Store the calculated data

            % Create storage location for postprocessing results

            % Define the base folder name for exporting results
            baseFolderName = 'export';

            % Get the current date and time as a timestamp string
            timestamp = datestr(now, 'yyyy-mm-dd_HH-MM-SS');  % Format as 'yyyy-mm-dd_HH-MM-SS'

            % Combine base folder name with timestamp to create a unique folder name
            folderName = sprintf('%s_%s', baseFolderName, timestamp);

            % Define the location where the folder will be created (based on raw data folder)
            desiredLocation = prepData.rawData{1}.folderName;  % Get the folder name from raw data

            % Full path for the new folder
            fullFolderPath = fullfile(desiredLocation, folderName);

            % Check if the folder already exists
            if ~exist(fullFolderPath, 'dir')
                % If the folder doesn't exist, create it
                mkdir(fullFolderPath);  % Create the folder
                fprintf('Folder created: %s\n', fullFolderPath);  % Output the folder creation message
            else
                % If the folder already exists, inform the user
                fprintf('Folder already exists: %s\n', fullFolderPath);  % Output the existing folder message
            end

            % Store the folder location in the object
            obj.folderLoc = fullFolderPath;  % Store the folder location for later use
        end

        function obj = press_ISPPA(obj, setNrs, fileName, localStorage)
            % press_ISPPA - This function exports pressure and ISPPA data for
            %               metrology purposes and saves the results in a .mat file.
            %
            % Syntax: obj = press_ISPPA(obj, fileName)
            %
            % Inputs:
            %    obj - The current object containing the necessary data for processing.
            %    fileName - The base name for the exported .mat file.
            %
            % Outputs:
            %    obj - The updated object with the processed and exported data.
            %
            % Description:
            %    This function extracts metrology data, pressure data, and ISPPA
            %    values, organizes them into a structured format, and then saves
            %    the data into a .mat file for further use. The resulting file is
            %    stored in a folder defined by the object.
            %
            % Example:
            %    obj = press_ISPPA(obj, 'resultFileName');  % Export pressure and ISPPA data

            % Extracting general information for each measurement
            
            j = 1;
            for i = setNrs
                % Store general metadata for each measurement
                data{j}.exportTimeStamp = datetime;  % Current date and time
                data{j}.metrologySetup = obj.prepData.pr.metrologySetup;  % Metrology setup
             %SF   data{j}.measurementTimeStamp = obj.prepData...;% measurement date and time

                % Extract specific measurement information
                data{j}.type = obj.prepData.p{i}.measurement.type;  % Measurement type
                data{j}.amp = obj.prepData.p{i}.amp.name;  % Amplifier name                
                data{j}.power = obj.prepData.p{i}.amp.power;  % Amplifier power
                data{j}.powerUnit = obj.prepData.p{i}.amp.powerUnit;  % Unit for power
                data{j}.tranducer = obj.prepData.p{i}.TD.name;  % Transducer name
                data{j}.focus = obj.prepData.p{i}.TD.Focus;  % Transducer focus
                data{j}.focusUnit = obj.prepData.p{i}.TD.FocusUnit;  % Unit for focus

                % Added 01/10/2025
                data{j}.fs = obj.prepData.p{i}.acq.fs;
                data{j}.fc = obj.prepData.p{i}.TD.f0; 
                data{j}.fUnit = 'Hz';
                data{j}.phase = obj.calcData.ampEstimation{i}.phase; 
                data{j}.phaseUnit = 'Rad';

                if isprop(obj.calcData, 'holography')
                    if i <= numel(obj.calcData.holography)
                        if ~isempty(obj.calcData.holography{i})
                            data{j}.holography.grid.x   = single(obj.calcData.holography{i}.grid.xmi);
                            data{j}.holography.grid.y   = single(obj.calcData.holography{i}.grid.ymi);
                            data{j}.holography.grid.z   = single(obj.calcData.holography{i}.grid.zmi);
                            data{j}.holography.pressure = single(obj.calcData.holography{i}.pressure3D);
                        end
                    end
                end

                % Store coordinates of the measurement setup
                data{j}.x = obj.prepData.coordinates{i}(:,4);  % X coordinates
                data{j}.y = obj.prepData.coordinates{i}(:,5);  % Y coordinates
                data{j}.z = obj.prepData.coordinates{i}(:,6);  % Z coordinates
                data{j}.corUnit = 'mm';  % Unit for coordinates (millimeters)
                j = j+1;
            end

            j = 1;
            % Pressure data processing
            for i = setNrs
                % Filtered pressure data
                if isfield(obj.calcData.pressure{i}.amp,'spatialFilt')
                    data{j}.pressure.data = obj.calcData.pressure{i}.amp.spatialFilt;
                elseif isfield(obj.calcData.pressure{i}.amp,'raw')
                    data{j}.pressure.data = obj.calcData.pressure{i}.amp.raw;
                
                else
                    data{j}.pressure.data = [];
                end
                
                data{j}.pressure.unit = 'Pa';  % Unit for pressure (Pascal)
                j = j+1;
            end

            j = 1;
            % ISPPA (Spatial Peak Pulse Average Intensity) data processing
            for i = setNrs
                if isfield(obj.calcData.ISPPA{i}.amp,'spatialFilt')
                    data{j}.ISPPA.data = obj.calcData.ISPPA{i}.amp.spatialFilt;  % Filtered ISPPA data
                elseif isfield(obj.calcData.ISPPA{i}.amp,'raw')
                    data{j}.ISPPA.data = obj.calcData.ISPPA{i}.amp.raw;  % Filtered ISPPA data
                else
                    data{j}.ISPPA.data = [];
                end

                data{j}.ISPPA.unit = 'W/cm2';  % Unit for ISPPA (Watt per square centimeter)
                j = j+1;
            end

            % Save the data in a .mat file
            if localStorage
                name = sprintf('FUS_Metrology_Export_%s', fileName);  % Construct the file name
                save(fullfile([name, '.mat']), 'data','-v7.3');  % Save the data to a .mat file
            
            else

                name = sprintf('FUS_Metrology_Export_%s', fileName);  % Construct the file name
                save(fullfile(obj.folderLoc, [name, '.mat']), 'data');  % Save the data to a .mat file
            end
        end

        function obj = equalizationCurve(obj,xTransform)

            if isfield(obj.calcData.equalizationCurvatureFit,'splineFit')

                for i = 1:numel(obj.calcData.equalizationCurvatureFit.splineFit)

                    if strcmp(obj.calcData.equalizationCurvatureFit.splineFit(i).xTransform,xTransform)

                        % re-arrange struct since cfit types are not converted to
                        % jsonData
                        
                        D = obj.calcData.equalizationCurvatureFit.splineFit(i);
                        D = rmfield(D,'struct');
                        D.FitParams = obj.calcData.equalizationCurvatureFit.splineFit(i).struct.p;
                        D.equalizationCurvature = obj.calcData.equalizationCurvature; 
                        
                        % convert to json
                        jsonData = jsonencode(D);

                        % filname
                        fileName = sprintf('equalizationCurveFitExport.json');

                        % Save to file
                        fid = fopen(fullfile(obj.folderLoc,fileName), 'w');
                        fprintf(fid, '%s', jsonData);
                        fclose(fid);

                        % save spline struct to mat file for feval
                        % verificatio purposes
                        splineFitFunc = obj.calcData.equalizationCurvatureFit.splineFit(i).struct;
                        save(fullfile(obj.folderLoc, 'equalizationCurveFitExport.mat'), 'splineFitFunc');
                    end
                end
            end

            % % import check
            % jsonData = fileread(fullfile(obj.folderLoc,fileName));
            % data = jsondecode(jsonData);

        end

        function obj = powerCurve(obj)

            % re-arrange struct since cfit types are not converted to
            % jsonData
            D.powerCurvature      = obj.calcData.powerCurvature;
            pFit                  = obj.calcData.powerCurvatureFit.quadraticFit.data.fit;
           
            D.FitParams.coefs(1)  = pFit(3);
            D.FitParams.coefs(2)  = pFit(2);
            D.FitParams.coefs(3)  = pFit(1);

            % same structure as the ppf but now for a linear inter val
            D.FitParams.breaks(1) = 0;
            D.FitParams.breaks(2) = 2e6;

            %D = rmfield(D,'pFit');

            % convert to json
            jsonData = jsonencode(D);

            % filname
            fileName = sprintf('powerCurveFitExport.json');

            % Save to file
            fid = fopen(fullfile(obj.folderLoc,fileName), 'w');
            fprintf(fid, '%s', jsonData);
            fclose(fid);

            % save fit struct to mat file for feval
            % verificatio purposes
            save(fullfile(obj.folderLoc, 'powerCurvatureFitExport.mat'), 'pFit');


        end

        function obj = focusCurve(obj,xTransform)

            if isfield(obj.calcData.focusCurvatureFit,'splineFit')

                for i = 1:numel(obj.calcData.focusCurvatureFit.splineFit)

                    if strcmp(obj.calcData.focusCurvatureFit.splineFit(i).xTransform,xTransform)

                        % re-arrange struct since cfit types are not converted to
                        % jsonData
                        D = obj.calcData.focusCurvatureFit.splineFit(i);
                        D = rmfield(D,'struct');
                        D.FitParams = obj.calcData.focusCurvatureFit.splineFit(i).struct.p;
                        D.focusCurvature = obj.calcData.focusCurvature;

                        % convert to json
                        jsonData = jsonencode(D);

                        % filname
                        fileName = sprintf('focusCurveFitExport.json');

                        % Save to file
                        fid = fopen(fullfile(obj.folderLoc,fileName), 'w');
                        fprintf(fid, '%s', jsonData);
                        fclose(fid);

                        % save spline struct to mat file for feval
                        % verificatio purposes
                        splineFitFunc =  obj.calcData.focusCurvatureFit.splineFit.struct;
                        save(fullfile(obj.folderLoc, 'focusCurvatureFitExport.mat'), 'splineFitFunc');

                    end
                end
            end

            if isfield(obj.calcData.focusCurvatureFit,'linFit')

                % re-arrange struct since cfit types are not converted to
                % jsonData
                D.focusCurvature      = obj.calcData.focusCurvature;
                D.linFit              = obj.calcData.focusCurvatureFit.linFit;
                D.FitParams.intercept = D.linFit.mdl.Coefficients.Estimate(1);
                D.FitParams.slope     = D.linFit.mdl.Coefficients.Estimate(2);
                D = rmfield(D,'linFit');

                % convert to json
                jsonData = jsonencode(D);

                % filname
                fileName = sprintf('focusCurveFitExport.json');

                % Save to file
                fid = fopen(fullfile(obj.folderLoc,fileName), 'w');
                fprintf(fid, '%s', jsonData);
                fclose(fid);

            end

        end
    end
end
