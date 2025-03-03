function iniData = readIniFile(filename)
    % READINIFILE Reads an INI file into a MATLAB struct.
    % 
    % INPUT:
    %   filename - Path to the INI file.
    % OUTPUT:
    %   iniData  - Struct containing the parsed data.
    %
    % This function handles INI files with spaces in section names by 
    % replacing spaces with underscores for valid MATLAB field names.

    % Open the INI file for reading
    fid = fopen(filename, 'r');
    
    % Check if the file was successfully opened
    if fid == -1
        % If the file cannot be opened, throw an error
        error('Could not open the file: %s', filename);
    end
    
    % Initialize an empty struct to hold the parsed data
    iniData = struct();
    
    % Variable to keep track of the current section (e.g., [General])
    currentSection = '';
    
    % Read the file line by line
    while ~feof(fid)
        % Read the next line and remove leading/trailing whitespace
        line = strtrim(fgetl(fid));
        
        % Skip empty lines or lines starting with a comment (lines starting with ';' or '#')
        if isempty(line) || startsWith(line, ';') || startsWith(line, '#')
            continue;
        end
        
        % Check if the line is a section header (starts with '[' and ends with ']')
        if startsWith(line, '[') && endsWith(line, ']')
            % Extract the section name by removing the brackets '[' and ']'
            currentSection = line(2:end-1);
            
            % Replace spaces with underscores to make a valid MATLAB field name
            validSection = strrep(currentSection, ' ', '_');
            
            % Initialize a struct for this section in the `iniData` structure
            iniData.(validSection) = struct(); 
            continue;  % Skip to the next line to avoid processing the section name as a key-value pair
        end
        
        % Parse key-value pairs (lines with an '=' sign)
        if contains(line, '=')
            % Split the line into key and value based on the '=' sign
            tokens = strsplit(line, '=');
            key = strtrim(tokens{1});  % Trim whitespace from the key
            value = strtrim(tokens{2});  % Trim whitespace from the value
            
            % Try to convert the value into a numeric value (if possible)
            numericValue = str2double(value);
            
            % If the conversion is successful (not NaN), use the numeric value
            if ~isnan(numericValue)
                value = numericValue;
            end
            
            % Convert the key into a valid MATLAB field name
            validKey = matlab.lang.makeValidName(key);
            
            % If there is no section, add the key-value pair directly to the root structure
            % Otherwise, assign the key-value pair to the current section
            if isempty(currentSection)
                iniData.(validKey) = value;  % Root-level key-value pair
            else
                iniData.(validSection).(validKey) = value;  % Section-level key-value pair
            end
        end
    end
    
    % Close the file after processing
    fclose(fid);
end
