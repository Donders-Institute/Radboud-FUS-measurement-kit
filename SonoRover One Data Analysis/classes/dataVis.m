classdef dataVis
    %UNTITLED Summary of this class goes here
    %   Detailed explanation goes here

    properties
        prepData = [];
        calcData = [];
        NFD  = [];



    end
    properties (Access = private)
        coef = [];

        % video parameters
        fps = 20;
        folderLoc  = [];

    end

    methods

        function obj = dataVis(prepData,calcData)
            %UNTITLED Construct an instance of this class
            %   Detailed explanation goes here
            %obj.Property1 = inputArg1 + inputArg2;

            obj.prepData = prepData;
            obj.calcData = calcData;

            % Create storage location for postprocessing results

            % Define the base folder name
            baseFolderName = 'postProcessing';

            % Get the current date and time
            timestamp = datestr(now, 'yyyy-mm-dd_HH-MM-SS');

            % Combine to create the folder name
            folderName = sprintf('%s_%s', baseFolderName, timestamp);

            % Define the desired location for the folder
            desiredLocation = prepData.rawData{1}.folderName;

            % Full path for the folder
            fullFolderPath = fullfile(desiredLocation, folderName);

            % Check if the folder already exists
            if ~exist(fullFolderPath, 'dir')
                % Create the folder
                mkdir(fullFolderPath);
                fprintf('Folder created: %s\n', fullFolderPath);
            else
                fprintf('Folder already exists: %s\n', fullFolderPath);
            end

            obj.folderLoc = fullFolderPath;

        end

        function pulseSelection(obj,setNrs,xAxis,yAxis)


            % temporary local folder location
            folderLocTemp = 'C:\Users\Public\Videos';  % A known writable directory


            for i = setNrs % for every seqcence

                % initiate videofile
                name                = sprintf('pulseSelectionSequence%d.mp4',obj.prepData.p{i}.measurement.sequenceNr);
                pathName            = fullfile(folderLocTemp,name);
                videoFile           = VideoWriter(pathName,'MPEG-4');
                videoFile.FrameRate = obj.fps;
                videoFile.Quality   = 75;
                open(videoFile);

                % create figure
                f = figure('color', [1 1 1],'position',[100,100,1500,400]);

                switch xAxis

                    case 'Samples [#]'
                        x = 1:obj.prepData.p{i}.acq.samples;

                    case 'Time [mus]'
                        x = 1e6*obj.prepData.p{i}.acq.timeVec(1:end-1);

                    case 'Cycles [#]'
                        x = (1:obj.prepData.p{i}.acq.samples)./obj.prepData.p{i}.acq.samplesPerPeriod;
                end

                switch yAxis

                    case 'Voltage [mV]'
                        y = 1e3*obj.prepData.filtData{i};
                        ys = 1e3*obj.prepData.dataSel.data{i};
                        yl = max(abs(y(:)));
                        amp = 1e3*obj.calcData.ampEstimation{i}.amp;

                    case 'Pressure [MPa]'
                        y = 1e-6*obj.calcData.pressure{i}.pulseData;
                        yl = max(abs(y(:)));
                        ys = y;
                        ys(~obj.prepData.dataSel.mask{i}) = 0;
                        amp = 1e-6*obj.calcData.pressure{i}.amp.raw;

                end

                for j = 1:size(y,2)

                    % do the plotting
                    plot(x,y(:,j),'b'); hold on
                    plot(x,ys(:,j),'r'); hold off

                    % amplitude line
                    line([min(x),max(x)],[amp(j), amp(j)],'color',[0 0 0])

                    % labels
                    xlabel(xAxis)
                    ylabel(yAxis)
                    title(sprintf('%3.0f: %s Z = %2.1f mm ',j,obj.prepData.p{i}.TD.name,obj.prepData.coordinates{1}(j,6)))

                    % Opmaak
                    axis tight
                    box off
                    grid minor

                    % axis limits
                    ylim([-yl yl]);

                    % legend
                    legend('Time series','Selection for amplitude estimation','Amplitude estimation using selection')

                    drawnow

                    % frame grabbing
                    writeVideo(videoFile,getframe(gcf));

                end
                % clean up
                close(f)
                close(videoFile)

                % Move file
                movefile(pathName,fullfile(obj.folderLoc,name));

            end

        end

        function axialProfiles(obj,setNrs,xAxis,yAxis,NFD,singleView)

            cc = 1; % counter for tiff composition
            cm = 1;

            if singleView
                % create figure
                f = figure('color', [1 1 1],'position',[100,100,1200,800]);

                % Creat colormap
                colorMap = createColorMap(obj,numel(setNrs)+1,1,1);
            end

            ii = 1;
            for i = setNrs % for every sequence


                switch xAxis

                    case 'Distance WRT exitplane [mm]'

                        x = obj.prepData.coordinates{i}(:,6) ; % z [mm]
                end

                switch yAxis

                    case 'Voltage [mV]'
                        y = 1e3*obj.calcData.spatialFilt{i}.amp;
                        yl = [0 400];

                    case 'Raw & Filt pressure [MPa]'
                        y = 1e-6*obj.calcData.pressure{i}.amp.spatialFilt;
                        yl = [0 1];
                        y2 = 1e-6*obj.calcData.pressure{i}.amp.raw;

                    case 'Pressure [MPa]'
                        y = 1e-6*obj.calcData.pressure{i}.amp.spatialFilt;
                        yl = [0 1];

                    case 'ISPPA [W/cm2]'
                        y = obj.calcData.ISPPA{i}.amp.spatialFilt;
                        yl = [0 35];

                    case 'ISPPA scaled [W/cm2]'
                        if ~isempty(obj.calcData.ISPPAsc)
                            y = obj.calcData.ISPPAsc{i}.amp.spatialFilt;
                            yl = [0 35];
                        else
                            y = [];
                        end
                end

                if ~isempty(y)

                    if ~ singleView
                        % create figure
                        f = figure('color', [1 1 1],'position',[100,100,1200,800]);
                    end

                    %do the plotting if y is not empty
                    if singleView
                        plot(x,y,'Color',colorMap(ii,:)); hold on
                        leg{cm} = sprintf('SR SF F = %2.1f mm %s %s',obj.prepData.p{i}.TD.Focus,obj.prepData.p{i}.measurement.type,obj.prepData.p{i}.HP.ID);
                        cm = cm+1;
                        if exist('y2')
                            hold on
                            plot(x,y2,'Color',colorMap(ii,:),'LineStyle','--');
                            leg{cm} = sprintf('SR RAW F = %2.1f mm %s %s ',obj.prepData.p{i}.TD.Focus,obj.prepData.p{i}.measurement.type,obj.prepData.p{i}.HP.ID);
                            cm = cm + 1;
                        end
                    else
                        plot(x,y,'k');
                        leg{cm} = sprintf('SonoRover One');
                        if exist('y2')
                            hold on
                            plot(x,y2,'k--');
                            leg = {'SonoRover One Filt','SonoRover One Raw'};
                        end

                    end

                    if isequal(yAxis,'ISPPA scaled [W/cm2]')
                        hold on

                        idx = obj.calcData.ISPPAsc{i}.TD_TPO;

                        if ~singleView
                            plot(x,NFD.NFdata(idx(1),idx(2)).z_ISPPA(:,ii),'k--')
                            leg{cm} = sprintf('SonoRover One');

                            % retreive metric information of profile
                            M = obj.calcData.ISPPAsc{i}.amp.spatialFiltMetrics;

                            % plot Metric info
                            line([M(3),M(5)],[M(1)/2,M(1)/2],'color',[0.2 0.2 0.2])
                            line([M(4),M(4)],[0 M(1)/2],'color',[0.2 0.2 0.2])

                            % FWHM and position
                            text(M(4)-5,1+M(1)/2,sprintf('FWHM %2.1f mm @ z = %2.1f mm',M(5)-M(3),M(4)),'FontSize',7)
                            leg = {'SonoRover One','S.C. reference'};

                        else
                            % NFD data
                            
                            plot(x,NFD.NFdata(idx(1),idx(2)).z_ISPPA(:,ii),'color',colorMap(ii,:),'LineStyle','--')
                            leg{cm} = sprintf('NF F = %2.1f mm ',obj.prepData.p{i}.TD.Focus);
                            cm = cm+1;
                        end

                    end

                    % labels
                    xlabel(xAxis)
                    ylabel(yAxis)

                    if ~singleView
                        title(sprintf('%s Focus = %2.1f mm ',obj.prepData.p{i}.TD.name,obj.prepData.p{i}.TD.Focus))
                    else
                        title(sprintf('%s',obj.prepData.p{i}.TD.name))
                    end

                    % design
                    axis tight
                    box off


                    % axis limits
                    ylim(yl);

                    % legend
                    legend(leg,'location','eastoutside');

                    grid on
                    drawnow

                    % define folder location
                    nameSingleView     = sprintf('axialProfilesSingleView %s %s.tiff',yAxis(1:7),obj.prepData.p{i}.TD.name);
                    nameContainer      = sprintf('axialProfilesContainer %s %s.tiff',yAxis(1:7),obj.prepData.p{i}.TD.name);
                    pathNameSingleView = fullfile(obj.folderLoc,nameSingleView);
                    pathNameContainer  = fullfile(obj.folderLoc,nameContainer);

                    if ~singleView && ~isempty(y)

                        if cc==1
                            % writing anb appending tiff
                            imwrite(frame2im(getframe(gcf)),pathNameContainer)

                        else
                            % append tiff
                            imwrite(frame2im(getframe(gcf)),pathNameContainer,"WriteMode","append")
                        end

                        close(f)
                        cc = cc+1;
                    end
                end
                ii = ii+1;
            end
            if singleView && ~isempty(y)

                imwrite(frame2im(getframe(gcf)),pathNameSingleView)
                close(f)
            end

        end

        function holography(obj,transverseLoc,zv)

            % Axial comparision graphs
            f = figure('color', [1 1 1],'position',[100,100,800,800]);

            l = 1;
            for i = 1:size(obj.prepData.dim,1)

                if isequal(obj.prepData.dim(i,:),[0 0 1]) % axial profiles

                    z = obj.prepData.coordinates{i}(:,6);
                    y = obj.calcData.pressure{i}.amp.spatialFilt;

                    plot(z,y*1e-6); hold on

                    folderNames = split(obj.prepData.rawData{i}.folderName, '\');
                    leg{l} = [folderNames{end},' ',obj.prepData.p{i}.measurement.type];

                end

                if isequal(obj.prepData.dim(i,:),[1 1 0]) % axial / 3D holography profiles
                    z = obj.calcData.holography{i}.grid.z*1e3;
                    y = obj.calcData.holography{i}.centerAxialProfile;
                    plot(z,y*1e-6)

                    folderNames = split(obj.prepData.rawData{i}.folderName, '\');
                    leg{l} = [folderNames{end},' ',obj.prepData.p{i}.measurement.type];
                end

                l = l+1;

            end
            title('Native verus Holography derived center axial profiles')
            xlabel('Z [mm]'); ylabel('Pressure [MPa]')
            box off
            grid minor
            legend(leg,'Interpreter', 'none')


            %2D input amplitude and phase
            k = 2;
            f = figure('color', [1 1 1],'position',[100,100,1800,800]);
            subplot(2,3,1); % amplitude
            imagesc(obj.calcData.holography{k}.input.amplitude2D); axis equal tight ; title('Raw input Voltage'); c = colorbar; title(c, 'Voltage [V]'); 

            subplot(2,3,2); % phase
            imagesc(obj.calcData.holography{k}.input.phase2D); axis equal tight;colorbar; title('Raw input Phase');c = colorbar; title(c, 'Phase [RAD]');

            subplot(2,3,3); % pressure
            imagesc(obj.calcData.holography{k}.pressure2D); axis equal tight; title('Interpolated raw input pressure');c = colorbar; title(c, 'Pressure [Pa]');

            xm = squeeze(obj.calcData.holography{k}.grid.xmi(:,:,1));
            ym = squeeze(obj.calcData.holography{k}.grid.ymi(:,:,1));

            subplot(2,3,4); % amplitude
            pcolor(xm,ym,obj.calcData.holography{k}.intInput.amplitude2D); shading interp; axis equal tight ;title('Interpolated trimmed input voltage');c = colorbar; title(c, 'Voltage [V]');

            subplot(2,3,5); % phase
            pcolor(xm,ym,obj.calcData.holography{k}.intInput.phase2D); shading interp; axis equal tight;title('Interpolated trimmed phase');c = colorbar; title(c, 'Phase [RAD]');
              
            subplot(2,3,6); % pressure
            pcolor(xm,ym,obj.calcData.holography{k}.intPressure2D); shading interp; axis equal tight; title('Interpolated trimmed pressure');c = colorbar; title(c, 'Pressure [Pa]');



            colormap hot



            % 2D cross-section comparisons
            nr = 0;
            for i = 1:size(obj.prepData.dim,1)
                if isequal(obj.prepData.dim(i,:),[1 1 0])
                    nr = nr+1;
                    ii(nr) = i;
                end
            end

            f = figure('color', [1 1 1],'position',[100,100,1800,800]);

            sp = 1;
            for k = ii
                for j = transverseLoc

                    subplot(numel(ii),numel(transverseLoc),sp)

                    xm = squeeze(obj.calcData.holography{k}.grid.xm(:,:,j));
                    ym = squeeze(obj.calcData.holography{k}.grid.ym(:,:,j));
                    pressure2D = squeeze(obj.calcData.holography{k}.pressure3D(:,:,j));
                    pcolor(xm,ym,pressure2D)

                    axis equal tight
                    shading interp
                    colormap hot
                    title(sprintf('Z-position = %2.1f mm',1e3*zv(j)))

                    % if sp<4
                    %     title(sprintf('Pressure [Mpa] @ Z = %2.0f mm ',transverseLoc(sp)))
                    % elseif sp
                    %     title(sprintf('REFERENCE Pressure [Mpa] @ Z = %2.0f mm ',transverseLoc(sp-3)))
                    % else
                    %
                    % end

                    xlabel('Lateral [mm]')
                    ylabel('Elevational [mm]')
                    clim([0 max(obj.calcData.holography{k}.pressure3D(:))])

                    sp = sp+1;
                end
            end
            colorbar

            % 2D coronal and sagital views trough center
            for i = 1:size(obj.prepData.dim,1)
                if isequal(obj.prepData.dim(i,:),[1 1 0])

                    xmi = obj.calcData.holography{i}.grid.xmi;
                    ymi = obj.calcData.holography{i}.grid.ymi;
                    zmi = obj.calcData.holography{i}.grid.zmi;

                    f = figure('color', [1 1 1],'position',[100,100,1800,1000]);
                    subplot(1,3,3)
                    zSlices = [2:10:140]*1e-3;
                    h = slice(xmi, ymi, zmi, (obj.calcData.holography{i}.pressure3D), [], [], zSlices,'cubic'); hold on
                    set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
                    colormap(hot);
                    axis equal;  %alpha(0.5)
                    xlabel('Lateral');
                    ylabel('Elevational');
                    zlabel('Axial');
                    clim([0 max(obj.calcData.holography{k}.pressure3D(:))])
                    view(45,15)
                    subplot(1,3,1)
                    ySlices = [0]*1e-3;
                    h = slice(xmi, ymi, zmi, (obj.calcData.holography{i}.pressure3D), [], ySlices,[],'cubic'); hold on
                    set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
                    colormap(hot);
                    axis equal;  %alpha(0.5)
                    xlabel('Lateral');
                    ylabel('Elevational');
                    zlabel('Axial');
                    view(0,0)
                    clim([0 max(obj.calcData.holography{k}.pressure3D(:))])
                    subplot(1,3,2)
                    xSlices = [0]*1e-3;
                    h = slice(xmi, ymi, zmi, (obj.calcData.holography{i}.pressure3D), xSlices, [],[],'cubic'); hold on
                    set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
                    colormap(hot);
                    axis equal;  %alpha(0.5)
                    xlabel('Lateral');
                    ylabel('Elevational');
                    zlabel('Axial');
                    view(90,0)
                    clim([0 max(obj.calcData.holography{k}.pressure3D(:))])

                end
            end
            colorbar

            % verschilplaatsjes voor maie
            % f = figure('color', [1 1 1],'position',[100,100,1800,1000]);
            %
            % subplot(1,2,1)
            % ySlices = [0]*1e-3;
            % h = slice(xm, ym, zm, (obj.calcData.holography{5}.pressure3D - obj.calcData.holography{2}.pressure3D), [], ySlices,[],'cubic'); hold on
            % set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
            % colormap(jet);
            % axis equal;  %alpha(0.5)
            % xlabel('Lateral');
            % ylabel('Elevational');
            % zlabel('Axial');
            % view(0,0)
            % clim([-2e5 2e5])
            %
            % subplot(1,2,2)
            % ySlices = [0]*1e-3;
            % h = slice(xm, ym, zm, (obj.calcData.holography{8}.pressure3D - obj.calcData.holography{2}.pressure3D), [], ySlices,[],'cubic'); hold on
            % set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
            % colormap(jet);
            % axis equal;  %alpha(0.5)
            % xlabel('Lateral');
            % ylabel('Elevational');
            % zlabel('Axial');
            % view(0,0)
            % clim([-2e5 2e5])
            %
            % f = figure('color', [1 1 1],'position',[100,100,1800,1000]);
            %
            % subplot(1,2,1)
            % ySlices = [0]*1e-3;
            % h = slice(xm, ym, zm, 100*((obj.calcData.holography{5}.pressure3D - obj.calcData.holography{2}.pressure3D)./(obj.prepData.p{i}.amp.maxPressure*1e6)), [], ySlices,[],'cubic'); hold on
            % set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
            % colormap(jet);
            % axis equal;  %alpha(0.5)
            % xlabel('Lateral');
            % ylabel('Elevational');
            % zlabel('Axial');
            % view(0,0)
            % clim([-16 16])
            %
            % subplot(1,2,2)
            % ySlices = [0]*1e-3;
            % h = slice(xm, ym, zm, 100*((obj.calcData.holography{8}.pressure3D - obj.calcData.holography{2}.pressure3D)./(obj.prepData.p{i}.amp.maxPressure*1e6)), [], ySlices,[],'cubic'); hold on
            % set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
            % colormap(jet);
            % axis equal;  %alpha(0.5)
            % xlabel('Lateral');
            % ylabel('Elevational');
            % zlabel('Axial');
            % view(0,0)
            % clim([-16 16])

        end
    end

    methods(Access = private)
        %% in class functions

        function colorsHSV = createColorMap(obj,Hues, saturationValue,brightnessVal)
            hueValues = linspace(0, 1, Hues)';
            colorsHSV = hsv2rgb([hueValues, saturationValue * ones(Hues, 1), brightnessVal * ones(Hues, 1)]);
        end
    end


end