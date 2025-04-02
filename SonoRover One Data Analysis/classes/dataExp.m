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

        function obj = press_ISPPA(obj, fileName)
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
            for i = 1:numel(obj.prepData.p)
                % Store general metadata for each measurement
                data{i}.exportDate = datetime;  % Current date and time
                data{i}.metrologySetup = obj.prepData.pr.metrologySetup;  % Metrology setup

                % Extract specific measurement information
                data{i}.type = obj.prepData.p{i}.measurement.type;  % Measurement type
                data{i}.amp = obj.prepData.p{i}.amp.name;  % Amplifier name
                data{i}.power = obj.prepData.p{i}.amp.power;  % Amplifier power
                data{i}.powerUnit = obj.prepData.p{i}.amp.powerUnit;  % Unit for power
                data{i}.tranducer = obj.prepData.p{i}.TD.name;  % Transducer name
                data{i}.focus = obj.prepData.p{i}.TD.Focus;  % Transducer focus
                data{i}.focusUnit = obj.prepData.p{i}.TD.FocusUnit;  % Unit for focus

                % Store coordinates of the measurement setup
                data{i}.x = obj.prepData.coordinates{1}(:,4);  % X coordinates
                data{i}.y = obj.prepData.coordinates{1}(:,5);  % Y coordinates
                data{i}.z = obj.prepData.coordinates{1}(:,6);  % Z coordinates
                data{i}.corUnit = 'mm';  % Unit for coordinates (millimeters)
            end

            % Pressure data processing
            for i = 1:numel(obj.calcData.pressure)
                data{i}.pressure.data = obj.calcData.pressure{i}.amp.spatialFilt;  % Filtered pressure data
                data{i}.pressure.unit = 'Pa';  % Unit for pressure (Pascal)
            end

            % ISPPA (Spatial Peak Pulse Average Intensity) data processing
            for i = 1:numel(obj.calcData.ISPPA)
                data{i}.ISPPA.data = obj.calcData.ISPPA{i}.amp.spatialFilt;  % Filtered ISPPA data
                data{i}.ISPPA.unit = 'W/cm2';  % Unit for ISPPA (Watt per square centimeter)
            end

            % Save the data in a .mat file
            name = sprintf('FUS_Metrology_Export_%s', fileName);  % Construct the file name
            save(fullfile(obj.folderLoc, [name, '.mat']), 'data');  % Save the data to a .mat file

        end

    end
end

