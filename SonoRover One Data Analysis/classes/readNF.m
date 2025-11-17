classdef readNF
    %READNF Class for reading and processing neuroFUS data from Excel files.
    %   This class is designed to load and process data files related to 
    %   the neuroFUS project. It reads data from Excel files, extracts relevant 
    %   data areas, interpolates ISPPA values, and organizes the data into a 
    %   structured format for further analysis.

    % Author: Stein Fekkes, February 2024, Focused Ultrasound Initiative

    properties
        % neuroFUSFolderLocation: The folder path where the neuroFUS Excel files are stored.
        neuroFUSFolderLocation = [];
        
        % NFdata: A struct array to store all data extracted from the Excel files.
        NFdata = [];
    end

    methods
        % Constructor to initialize the class and set the folder location
        function obj = readNF(neuroFUSFolderLocation)
            % Initialize the neuroFUSFolderLocation property with the provided input.
            obj.neuroFUSFolderLocation = neuroFUSFolderLocation;

            % Define the file names, data areas, and properties areas for 2-channel and 4-channel configurations.
            % second dimension of struct is type of TPO
            % 1 = TPO-105-010
            % 2 = TPO-203-035
            
            %%%%%%%%%%%%%%%%%%%%%% 2-CHANNELS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%

            %CTX-500-006 2-Ch. Focal Steering - Verification - RMA2230209-1
            obj.NFdata(1,1).fileName        = 'CTX-500-006 2-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-105-010';
            obj.NFdata(1,1).dataArea        = 'N19:X80';
            obj.NFdata(1,1).propertiesArea  = 'R5:T16';

            obj.NFdata(1,2).fileName        = 'CTX-500-006 2-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-203-035';
            obj.NFdata(1,2).dataArea        = 'K19:R80';
            obj.NFdata(1,2).propertiesArea  = 'O5:Q16';

            % CTX-250-009 2-Ch. Focal Steering - Verification - RMA2230209-1
            obj.NFdata(2,1).fileName        = 'CTX-250-009 2-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-105-010';
            obj.NFdata(2,1).dataArea        = 'P19:AB82';
            obj.NFdata(2,1).propertiesArea  = 'T5:V16';

            obj.NFdata(2,2).fileName        = 'CTX-250-009 2-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-203-035';
            obj.NFdata(2,2).dataArea        = 'N19:X82';
            obj.NFdata(2,2).propertiesArea  = 'R5:T16';

            %CTX-250-014 2-Ch. Focal Steering - Verification - RMA2230209-1
            obj.NFdata(3,1).fileName        = 'CTX-250-014 2-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-105-010';
            obj.NFdata(3,1).dataArea        = 'P19:AB82';
            obj.NFdata(3,1).propertiesArea  = 'T5:V16';

            obj.NFdata(3,2).fileName        = 'CTX-250-014 2-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-230-035';
            obj.NFdata(3,2).dataArea        = 'P19:AB82';
            obj.NFdata(3,2).propertiesArea  = 'T5:V16';

            %%%%%%%%%%%%%%%%%%%%%% 4-CHANNELS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%

            % CTX-250-001 4-Ch. Focal Steering - Verification - RMA2230209-1
            obj.NFdata(4,1).fileName        = 'CTX-250-001 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-105-010';
            obj.NFdata(4,1).dataArea        = 'P19:AB80';
            obj.NFdata(4,1).propertiesArea  = 'T5:V16';

            obj.NFdata(4,2).fileName        = 'CTX-250-001 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-203-035';
            obj.NFdata(4,2).dataArea        = 'P19:AB80';
            obj.NFdata(4,2).propertiesArea  = 'T5:V16';

            %CTX-250-026 4-Ch. Focal Steering - Verification - RMA2230209-1
            obj.NFdata(5,1).fileName        = 'CTX-250-026 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-105-010';
            obj.NFdata(5,1).dataArea        = 'P19:AB80';
            obj.NFdata(5,1).propertiesArea  = 'T5:V16';

            obj.NFdata(5,2).fileName        = 'CTX-250-026 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-203-035';
            obj.NFdata(5,2).dataArea        = 'P19:AB80';
            obj.NFdata(5,2).propertiesArea  = 'T5:V16';

            %CTX-500-024 4-Ch. Focal Steering - Verification - RMA2230209-1 %
            obj.NFdata(6,1).fileName        = 'CTX-500-024 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-105-010 (Updated)';
            obj.NFdata(6,1).dataArea        = 'P19:AB80';
            obj.NFdata(6,1).propertiesArea  = 'S5:U16';

            obj.NFdata(6,2).fileName        = 'CTX-500-024 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-203-035';
            obj.NFdata(6,2).dataArea        = 'P19:AB80';
            obj.NFdata(6,2).propertiesArea  = 'S5:U16';

            %CTX-500-026 4-Ch. Focal Steering - Verification - RMA2230209-1
            obj.NFdata(7,1).fileName        = 'CTX-500-026 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-105-010';
            obj.NFdata(7,1).dataArea        = 'P19:AB80';
            obj.NFdata(7,1).propertiesArea  = 'T5:V16';

            obj.NFdata(7,2).fileName        = 'CTX-500-026 4-Ch. Focal Steering - Verification - RMA2230209-1 - TPO-203-035';
            obj.NFdata(7,2).dataArea        = 'P19:AB80';
            obj.NFdata(7,2).propertiesArea  = 'T5:V16';

            % DPX
            obj.NFdata(8,2).fileName        = 'DPX-500-022 4-Ch. Focal Steering';
            obj.NFdata(8,2).dataArea        = 'T20:AJ121';
            obj.NFdata(8,2).propertiesArea  = 'T5:V16';

           
            
            % Continue to configure additional file names and areas...

            % Call the method to read data from Excel files after setting up configuration
            obj = obj.readNFxls();

        end

        function obj = readNFxls(obj)
            %READNF Construct an instance of this class
            %   Detailed explanation goes here

            for i = 1:size(obj.NFdata,1)

                for j = 1:size(obj.NFdata,2)

                    try

                        % read xls files
                        data = [];
                        text = [];
                        [data, text, ~]  = xlsread(fullfile(obj.neuroFUSFolderLocation,[obj.NFdata(i,j).fileName,'.xlsx']),'Sheet1', obj.NFdata(i,j).dataArea);
                        
                        [~, ~, properties] = xlsread(fullfile(obj.neuroFUSFolderLocation,[obj.NFdata(i,j).fileName,'.xlsx']),'Sheet1', obj.NFdata(i,j).propertiesArea);

                        % extract ISPPA data for all foci
                        obj.NFdata(i,j).x      = data(2:end,1);
                        obj.NFdata(i,j).x_name = text{1};
                        obj.NFdata(i,j).foci   = data(1,2:end)';
                        obj.NFdata(i,j).ISPPA  = data(2:end,2:end);

                        % interpolated values used for comparison
                        obj.NFdata(i,j).z = [0:0.5:140];
                        obj.NFdata(i,j).z_ISPPA = interp1(obj.NFdata(i,j).x,obj.NFdata(i,j).ISPPA,obj.NFdata(i,j).z);


                        % extract properties matrix
                        obj.NFdata(i,j).properties = cell2struct(properties',{'name','values','unit'});
                        disp(['Import ',obj.NFdata(i,j).fileName,' SUCCES'])
                    catch
                        disp(['Import ',obj.NFdata(i,j).fileName,' FAILED'])
                    end

                end
            end
        end







        


    end
end

