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

        function pulseSelection(obj,setNrs,xAxis,yAxis,NoF)
            
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
                        
                        % filtered data
                        y = 1e3*obj.prepData.filtData{i};

                        % in case of raw data watch
                       %y = 1e3*obj.prepData.rawData{i}.data;

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

                if isempty(NoF)
                    NoF = size(y,2);
                end


                for j = 1:NoF

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

        function axialProfiles(obj,setNrs,xAxis,yAxis,NFD,normVal,focusPlot,singleView)

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
                        if isnan(normVal(1))
                            y = 1e3*obj.calcData.spatialFilt{i}.amp;
                            yl = [0 400];
                            yAxisl = yAxis;
                            ymax = max(y(:));
                        else
                            y = 1e3*obj.calcData.spatialFilt{i}.amp/normVal(1)*100;
                            yl = [0 120];
                            yAxisl = 'Relative Voltage [%]';
                            ymax = max(y(:));
                        end

                    case 'Raw & Filt pressure [MPa]'
                        if isnan(normVal(2))
                            y = 1e-6*obj.calcData.pressure{i}.amp.spatialFilt;
                            yl = [0 1];
                            y2 = 1e-6*obj.calcData.pressure{i}.amp.raw;
                            yAxisl = yAxis;
                            ymax = max(y(:));
                            ymax2 = max(y2(:));
                        else
                            y = 1e-6*obj.calcData.pressure{i}.amp.spatialFilt/normVal(2)*100;
                            yl = [0 120];
                            y2 = 1e-6*obj.calcData.pressure{i}.amp.raw/normVal(2)*100;
                            yAxisl = 'Relative Raw and filt Pressure [%]';
                            ymax = max(y(:));
                            ymax2 = max(y2(:));
                        end

                    case 'Pressure [MPa]'
                        if isnan(normVal(3))
                            y = 1e-6*obj.calcData.pressure{i}.amp.spatialFilt;
                            yl = [0 1.2];
                            yAxisl = yAxis;
                            ymax = max(y(:));
                           

                        else
                            y = 1e-6*obj.calcData.pressure{i}.amp.spatialFilt/normVal(3)*100;
                            yl = [0 120];
                            yAxisl = 'Relative Pressure [%]';
                            ymax = max(y(:));
                        end

                    case 'ISPPA [W/cm2]'
                        if isnan(normVal(4))
                            y = obj.calcData.ISPPA{i}.amp.spatialFilt;
                            yl = [0 35];
                            yAxisl = yAxis;
                            ymax = max(y(:));
                        else
                            y = obj.calcData.ISPPA{i}.amp.spatialFilt/normVal(4)*100;
                            yl = [0 120];
                            yAxisl = 'Relative ISPPA [%]';
                            ymax = max(y(:));
                        end

                    case 'ISPPA scaled [W/cm2]'
                        if isnan(normVal(5))
                            if ~isempty(obj.calcData.ISPPAsc)
                                y = obj.calcData.ISPPAsc{i}.amp.spatialFilt;
                                yl = [0 35];
                            else
                                y = [];
                            end
                            yAxisl = yAxis;
                            ymax = max(y(:));
                        else
                            if ~isempty(obj.calcData.ISPPAsc)
                                y = obj.calcData.ISPPAsc{i}.amp.spatialFilt/normVal(5)*100;
                                yl = [0 120];
                            else
                                y = [];
                            end
                        yAxisl = 'Relative ISPPAsc [%]';
                        ymax = max(y(:));

                        end
                end
                disp(['max value in graph = ', num2str(ymax)])
                if ~isempty(y)

                    if ~ singleView
                        % create figure
                        f = figure('color', [1 1 1],'position',[100,100,1600,800]);
                    end

                    % Do the plotting if y is not empty
                    if singleView
                        subplot(1,2,1)
                        plot(x,y,'Color',colorMap(ii,:)); hold on
                        leg{cm} = sprintf('SR SF F = %2.1f mm %s %s',obj.prepData.p{i}.TD.Focus,obj.prepData.p{i}.measurement.type,obj.prepData.p{i}.HP.ID);
                        cm = cm+1;
                        if exist('y2')
                            hold on
                            plot(x,y2,'Color',colorMap(ii,:),'LineStyle','--');
                            leg{cm} = sprintf('SR RAW F = %2.1f mm %s %s ',obj.prepData.p{i}.TD.Focus,obj.prepData.p{i}.measurement.type,obj.prepData.p{i}.HP.ID);
                            cm = cm + 1;
                        end
                        
                        % Stats on top values
                        [maxy,~] = max(y);
                        mv(ii) = maxy;

                        if ii == numel(setNrs)
                        
                            text(min(x)+5,1.02*mean(mv),sprintf('Mean Top Pressure = %0.4f +/- %0.4f',mean(mv),std(mv))); 
                            line([min(x),max(x)],[mean(mv) mean(mv)],'color',[0 0 0],'lineStyle','--')

                        end
                        
                        ax1 = gca;
                        box off; grid minor; axis square
                        xlabel(xAxis)
                        ylabel(yAxisl)
                        
                        title(sprintf('%s',obj.prepData.p{i}.TD.name))

                        % plot focus info
                        subplot(1,2,2);
                           
                        switch focusPlot
                            case 'Set Focus wrt exitplane [mm]'
                                SetFocus(ii) = obj.prepData.p{i}.TD.Focus;

                            case 'Set Focus wrt midbowl [mm]'

                                SetFocus(ii) = obj.prepData.p{i}.TD.Focus2;

                        end

                        EstFocus(ii) = obj.calcData.pressure{i}.amp.spatialFiltMetrics(4);
                        
                        plot(SetFocus(ii),obj.calcData.pressure{i}.amp.spatialFiltMetrics(4),'k.'); hold on; axis square; box off; grid minor

                        if ii == numel(setNrs)
                            pf1 = polyfit(SetFocus(~isnan(EstFocus)),EstFocus(~isnan(EstFocus)),1);
                            xi = linspace(0,max(SetFocus(~isnan(EstFocus))),200);
                            yi = polyval(pf1,xi);
                            plot(xi,yi,'k--')

                            mean(EstFocus(~isnan(EstFocus)) - SetFocus(~isnan(EstFocus)))
                            std(EstFocus(~isnan(EstFocus)) - SetFocus(~isnan(EstFocus)))
                        
                            title(sprintf('Set focus versus estimated focus \n mean absolute diff = %0.2f =/- %0.2f mm ',mean(abs(EstFocus(~isnan(EstFocus)) - SetFocus(~isnan(EstFocus)))),std(abs(EstFocus(~isnan(EstFocus)) - SetFocus(~isnan(EstFocus))))))

                            
                        end
    
                        xlabel(focusPlot); ylabel('Estimated FWHM center position wrt extiplane [mm]')
                    else
                        hold on
                        plot(x,y,'k');
                        leg{cm} = sprintf('SonoRover One'); 
                        if exist('y2')
                            hold on
                            plot(x,y2,'k--');
                            leg = {'SonoRover One Filt','SonoRover One Raw'};
                        end

                        if isequal(yAxis,'Pressure [MPa]')
                            % retreive metric information of profile
                            M = obj.calcData.pressure{i}.amp.spatialFiltMetrics;
                            M(1) = 1e-6*M(1);

                            % FWHM and position
                            text(M(4)-5,0.015+M(1)/2,sprintf('FWHM %2.1f mm @ z = %2.1f mm',M(5)-M(3),M(4)),'FontSize',7)    

                        elseif isequal(yAxis,'ISPPA [W/cm2]')
                            % retreive metric information of profile
                            M = obj.calcData.ISPPA{i}.amp.spatialFiltMetrics;
                           
                            % FWHM and position
                            text(M(4)-5,1+M(1)/2,sprintf('FWHM %2.1f mm @ z = %2.1f mm',M(5)-M(3),M(4)),'FontSize',7)    
                        end

                        if exist('M','var')
                            % plot Metric info
                            line([M(3),M(5)],[M(1)/2,M(1)/2],'color',[0.2 0.2 0.2])
                            line([M(4),M(4)],[0 M(1)/2],'color',[0.2 0.2 0.2])
             

                        end

                            hold off

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

                    if 0 % optional plotting of vertical annotation lines
                        for zl = 12:2:20
                            line([zl,zl],[0 120],'color',[0 0 0]); hold on
                        end

                    end

                    % % labels
                    % xlabel(xAxis)
                    % ylabel(yAxisl)

                    if ~singleView
                        title(sprintf('%s Focus = %2.1f mm \n %s',obj.prepData.p{i}.TD.name,obj.prepData.p{i}.TD.Focus,obj.prepData.p{i}.measurement.type))
                    else
                       % title(sprintf('%s',obj.prepData.p{i}.TD.name))
                    end

                    % design
                    % axis tight
                    % box off

                    % 
                    % % axis limits
                    % ylim([yl(1),yl(2)]);
                    % ylim auto

                    % legend
                    % legend(leg,'location','eastoutside');

                    grid on
                    drawnow

                    % define folder location
                    nameSingleView     = sprintf('axialProfilesSingleView %s %s.tiff',yAxis(1:7),obj.prepData.p{i}.TD.name);
                    nameContainer      = sprintf('axialProfilesContainer %s %s.tiff',yAxis(1:7),obj.prepData.p{i}.TD.name);
                    pathNameSingleView = fullfile(obj.folderLoc,nameSingleView);
                    pathNameContainer  = fullfile(obj.folderLoc,nameContainer);

                    savefig([pathNameContainer(1:end-5),num2str(cc),'.fig'])

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
                % save Mat fig
                savefig([pathNameSingleView(1:end-5),'.fig'])
%                close(f)
            end

        end

        function cSectionImages(obj,setNrs,xAxis,yAxis,value,normVal,scaleFac,ds,colormapType,type,cl,closeFig)

            ii = 1;
            for i = setNrs % for every sequence

            % c section coordinates 
            x = obj.prepData.coordinates{i}(:,4) ; % x [mm]
            y = obj.prepData.coordinates{i}(:,5) ; % y [mm]
            z = unique(obj.prepData.coordinates{i}(:,6)) ; % z [mm]
            
                switch value

                    case 'Voltage [mV]'
                        if isnan(normVal(1))
                            v = 1e3*obj.calcData.ampEstimation{i}.amp;
                       

                        else
                            v = 1e3*obj.calcData.ampEstimation{i}.amp/normVal(1)*100;
         
                            valuel =[0 100];
                        end

                    case 'Pressure [MPa]'
                        if isnan(normVal(2))
                            v = sqrt(scaleFac)*1e-6*obj.calcData.pressure{i}.amp.raw;                          
                    
                        else
                            v = 1e-6*obj.calcData.pressure{i}.amp.raw/normVal(2)*100;
                         
                            valuel =[0 100];
                        end

                    case 'ISPPA [W/cm2]'
                        if isnan(normVal(3))
                            v = scaleFac*obj.calcData.ISPPA{i}.amp.raw;
                                              
                        else
                            v = obj.calcData.ISPPA{i}.amp.raw/normVal(3)*100;
                         
                            valuel =[0 100];
                        end
                end
                


                % create figure
                f = figure('color', [1 1 1],'position',[100,100,850,800]);
                
                % reshape vector in matrix
                xm = double(reshape(x,[sqrt(size(x,1)),sqrt(size(x,1))]));
                ym = double(reshape(y,[sqrt(size(y,1)),sqrt(size(y,1))]));                
                vm = double(reshape(v,[sqrt(size(x,1)),sqrt(size(x,1))]));

                mvm = max(vm(:));
                disp(mvm);

                  % conversion to db
                switch type
                    case 'dB'

                       
                    if strcmp(value,'ISPPA [W/cm2]') 
                       vm = 10*log10(vm ./ mvm + eps);  % eps prevents log(0)
                       
                    elseif strcmp(value,'Pressure [MPa]')

                       vm = 20*log10(vm ./ mvm + eps);  % eps prevents log(0)

                    end
                        valuel = [-50 0];
                        value = '[  dB  ]';

                    
                    case 'norm'

                        vm = vm./normVal * 100;
                        valuel = 'Normalized [%]';
                        cl = [-100 100];
                        if diffIm
                            cl = [-100 100];
                        end

                    otherwise
                                          

                end

                if numel(ds)>=i
                    if ds(i)
                        xm = xm(1:2:end,1:2:end);
                        ym = ym(1:2:end,1:2:end);
                        vm = vm(1:2:end,1:2:end);
                    end
                end

                pcolor(xm,ym,(vm)) ; shading interp; 
      
                % labels
                xlabel(xAxis)
                ylabel(yAxis)

                if exist('valuel','var')
                    clim([cl])
                else
                    clim auto
                end


                if strcmp(colormapType,'hot')
                    colormap hot;
                elseif strcmp(colormapType,'monotone') 
                    n = 256; % number of colors in the colormap
                    cmap = [linspace(1,1,n)', linspace(1,0,n)', linspace(1,0,n)']; % R:1→1, G:1→0, B:1→0
                    colormap(cmap);
                elseif strcmp(colormapType,'viridis')
                    viridis = [
                        0.2670, 0.0049, 0.3294;
                        0.2832, 0.1415, 0.4586;
                        0.254,  0.265,  0.530;
                        0.163,  0.471,  0.558;
                        0.135,  0.656,  0.466;
                        0.477,  0.821,  0.318;
                        0.993,  0.906,  0.144
                        ];

                    cmap = colormap(interp1(1:size(viridis,1), viridis, linspace(1,size(viridis,1),256)));
                    colormap(cmap);

                else

                    colormap;             
                end

                c = colorbar;
                ylabel(c,value)

                title(sprintf('%s Focus = %2.1f mm z = %2.1f mm \n %s',obj.prepData.p{i}.TD.name,obj.prepData.p{i}.TD.Focus,z,obj.prepData.p{i}.measurement.type))

                % design
                axis equal tight
                box off
                drawnow

                % define folder location
                nameSingleViewFig     = sprintf('cSection z = %2.1f mm %s %s %s.fig',z,value(1:8),obj.prepData.p{i}.TD.name,obj.prepData.p{i}.measurement.type);
                nameSingleViewTiff     = sprintf('cSection z = %2.1f mm %s %s %s.tiff',z,value(1:8),obj.prepData.p{i}.TD.name,obj.prepData.p{i}.measurement.type);  
                pathNameSingleViewFig = fullfile(obj.folderLoc,nameSingleViewFig);
                pathNameSingleViewTiff = fullfile(obj.folderLoc,nameSingleViewTiff);
                
                % saving matlab fig
                savefig(pathNameSingleViewFig)

                % saving tiff
                imwrite(frame2im(getframe(gcf)),pathNameSingleViewTiff)
                
                if closeFig
                    close(f)
                end

                ii = ii+1;
            end
            
        end
        
        function cSectionProfiles(obj,setNrs,xAxis,yAxis,yl,normVal)

            % create figure
            f = figure('color', [1 1 1],'position',[100,100,850,800]);

            ii = 1;
            for i = setNrs % for every sequence

            % c section coordinates 
            x = obj.prepData.coordinates{i}(:,4) ; % x [mm]
            y = obj.prepData.coordinates{i}(:,5) ; % y [mm]
            z = unique(obj.prepData.coordinates{i}(:,6)) ; % z [mm]
            
                switch yAxis

                    case 'Voltage [mV]'
                        if isnan(normVal(1))
                            v = 1e3*obj.calcData.ampEstimation{i}.amp;
                            vl = [0 400];
                        else
                            v = 1e3*obj.calcData.ampEstimation{i}.amp/normVal(1)*100;
                            vl = [0 120];
                            yAxisl = yAxis;
                            yAxisl = 'Relative Pressure [%]';
                        end

                    case 'Pressure [MPa]'
                        if isnan(normVal(2))
                            v = 1e-6*obj.calcData.pressure{i}.amp.raw;
                            vl = [0 1];
                            yAxisl = yAxis;
                        else
                            v = 1e-6*obj.calcData.pressure{i}.amp.raw/normVal(2)*100;
                            vl = [0 120];
                            yAxisl = 'Relative Pressure [%]';
                        end

                    case 'ISPPA [W/cm2]'
                        if isnan(normVal(3))
                            v = obj.calcData.ISPPA{i}.amp.raw;
                            vl = [0 35];
                            yAxisl = yAxis;
                        else
                            v = obj.calcData.ISPPA{i}.amp.raw/normVal(3)*100;
                            vl = [0 120];
                            yAxisl = 'Relative Pressure [%]';
                        end
                end
                



                
                % reshape vector in matrix
                xm = double(reshape(x,[sqrt(size(x,1)),sqrt(size(x,1))]));
                ym = double(reshape(y,[sqrt(size(x,1)),sqrt(size(x,1))]));                
                vm = double(reshape(v,[sqrt(size(x,1)),sqrt(size(x,1))]));

                % select X profile
                ix = ceil(0.5*size(vm,1));
                plot(xm(ix,:),vm(ix,:));hold on
                %plot(ym(:,ix),vm(:,ix))

         
                % labels
                xlabel(xAxis)
                ylabel(yAxisl)

                if isempty(yl)
                    ylim auto
                else
                    ylim(yl)
                end


                title(sprintf('%s Focus = %2.1f mm z = %2.1f mm',obj.prepData.p{i}.TD.name,obj.prepData.p{i}.TD.Focus,z));

                leg{ii} = obj.prepData.p{i}.measurement.type;

                % design
                box off
                grid on
                drawnow

                ii = ii+1;
            end

            legend(leg)

                % define folder location
                nameSingleViewFig     = sprintf('cSectionProfile z = %2.1f mm %s .fig',z,obj.prepData.p{i}.TD.name);
                nameSingleViewTiff     = sprintf('cSectionProfile z = %2.1f mm %s .tiff',z,obj.prepData.p{i}.TD.name);  
                pathNameSingleViewFig = fullfile(obj.folderLoc,nameSingleViewFig);
                pathNameSingleViewTiff = fullfile(obj.folderLoc,nameSingleViewTiff);
                
                % saving matlab fig
                savefig(pathNameSingleViewFig)

                % saving tiff
                imwrite(frame2im(getframe(gcf)),pathNameSingleViewTiff)
                close(f)                          
            
        end

        function XZSectionImages(obj,setNrs,diffIm,xAxis,yAxis,value,normVal,scaleFac,colormapType,type,closeFig)

            
            ii = 1;
            for i = setNrs % for every sequence

                % XZ section coordinates
                x = obj.prepData.coordinates{i}(:,4) ; % x [mm]
                y = obj.prepData.coordinates{i}(:,5) ; % y [mm]
                z = obj.prepData.coordinates{i}(:,6) ; % z [mm]

                switch value

                    case 'Voltage [mV]'

                        v = 1e3*obj.calcData.ampEstimation{i}.amp;
                        
                        if diffIm
                            v1 = 1e3*obj.calcData.ampEstimation{setNrs(1)}.amp;
                            v2 = 1e3*obj.calcData.ampEstimation{setNrs(2)}.amp;
                            v = v1-v2;
                        else
                            v = 1e3*obj.calcData.ampEstimation{i}.amp;
                        end

                    case 'Pressure [MPa]'

                        if diffIm
                            v1 = 1e-6*obj.calcData.pressure{setNrs(1)}.amp.raw;
                            v2 = 1e-6*obj.calcData.pressure{setNrs(2)}.amp.raw;
                            v = v1-v2;
                        else
                            v = sqrt(scaleFac)*1e-6*obj.calcData.pressure{i}.amp.raw;
                            fprintf('Max pressure = %0.2f MPa\n',max(v(:)));
                            
                        end

                    case 'ISPPA [W/cm2]'

                        if diffIm
                            v1 = obj.calcData.ISPPA{setNrs(1)}.amp.raw;
                            v2 = obj.calcData.ISPPA{setNrs(2)}.amp.raw;
                            v = v1-v2;
                        else
                            v = scaleFac*obj.calcData.ISPPA{i}.amp.raw;
                            fprintf('Max ISPPA = %0.2f W/cm2\n',max(v(:)));
                            
                        end

                end

                % reshape vector data in 2D shape
                rs = [numel(unique(z)),numel(unique(x))];
                xm = double(reshape(x,rs));
                ym = double(reshape(z,rs));                
                vm = double(reshape(v,rs));
                mvm = max(vm(:));
                                

                % conversion to db
                if strcmp(type,'dB')

                    if strcmp(value,'ISPPA [W/cm2]')

                        vm = 10*log10(vm ./ mvm + eps);  % eps prevents log(0)

                    elseif strcmp(value,'Pressure [MPa]')

                        vm = 20*log10(vm ./ mvm + eps);  % eps prevents log(0)

                    end
                    valuel = [-50 0];
                    value = '[  dB  ]';
                end

                % create figure
                f = figure('color', [1 1 1],'position',[100,100,400,800]);

                % actual plot
                pcolor(xm,ym,(vm)) ; shading interp; hold on

                % if exist('valuel','var')
                %     clim([cl])
                % else
                    clim auto
                % end

                % plot acoustical axis center line
                line([0 0],[ 0 max(z(:))],'LineWidth', 1.5, 'LineStyle', '--', 'Color', 'k')

                if strcmp(type,'dB')

                    % find position of maximum pressure
                    [max_val, linear_idx] = max(vm(:));               % Find max value and its linear index
                    [row, col] = ind2sub(size(vm), linear_idx);       % Convert to (row, col)

                    % cooridinates
                    x_max = xm(row, col);
                    y_max = ym(row, col);

                    fprintf('Zsp = %0.1f mm\n',y_max);

                    plot(x_max,y_max,'ko','markersize',7,'MarkerFaceColor',[0 0 0])

                    % calculate contour
                    C3 = contourc(unique(xm), unique(ym), vm, [1 -3]);  % Only -3 dB
                    C6 = contourc(unique(xm), unique(ym), vm, [1 -6]);  % Only -6 dB

                    C = C3;
                    k = 1;
                    con3 = [];
                    while k < size(C, 2)
                        level = C(1, k);
                        numPoints = C(2, k);

                        xx = C(1, k+1 : k+numPoints);
                        yy = C(2, k+1 : k+numPoints);

                        con3{length(con3)+1} = struct('level', level, 'x', xx, 'y', yy);

                        k = k + numPoints + 1;
                    end

                    C = C6;
                    k = 1;
                    con6 = [];
                    while k < size(C, 2)
                        level = C(1, k);
                        numPoints = C(2, k);

                        xx = C(1, k+1 : k+numPoints);
                        yy = C(2, k+1 : k+numPoints);

                        con6{length(con6)+1} = struct('level', level, 'x', xx, 'y', yy);

                        k = k + numPoints + 1;
                    end
                    
                    % select the bigest contour
                    for j = 1:size(con3,2)
                        % contour sample count
                        sc(j) = size(con3{j}.x,2);

                    end
                    [~,m3] = max(sc);

                    % select the bigest contour
                    for j = 1:size(con6,2)
                        % contour sample count
                        sc(j) = size(con6{j}.x,2);

                    end
                    [~,m6] = max(sc);
        
                    % select positive x coordinates
                    xcp3 = con3{m3}.x>=0;
                    xcp6 = con6{m6}.x>=0;

                    xc3 = con3{m3}.x(xcp3);
                    yc3 = con3{m3}.y(xcp3);
                    xc6 = con6{m6}.x(xcp6);
                    yc6 = con6{m6}.y(xcp6);

                    % FWHM center
                    FWHM3 = range(yc3);
                    FWHM6 = range(yc6);
                                        
                    fprintf('Lax-3dB = %0.1f mm\n',FWHM3);
                    fprintf('Lax-6dB = %0.1f mm\n',FWHM6);

                    fprintf('Llat-3dB = %0.1f mm\n',2*(max(xc3(:))));
                    fprintf('Llat-6dB = %0.1f mm\n',2*(max(xc6(:))));

                    % FWHMcenter
                    FWHM3center = FWHM3/2+min(yc3);
                    FWHM6center = FWHM6/2+min(yc6);

                    fprintf('Zc-3dB = %0.1f mm\n',FWHM3center);
                    fprintf('Zc-6dB = %0.1f mm\n',FWHM6center);
                    
                    plot(0,FWHM3center,'ko','markersize',7,'MarkerFaceColor','none')
                    plot(0,FWHM6center,'ko','markersize',7,'MarkerFaceColor','none')

                    % plot one-sided contour
                    plot(xc3,yc3,'k.')
                    plot(xc6,yc6,'LineStyle','none','Marker','.','Color',[0.5 0.5,0.5])

                    % calculate volume of -3D asuming circle symmetry around
                    % the acoustical axis

                    % Remove duplicates
                    [y3_unique, idy3] = unique(yc3);
                    x3 = xc3(idy3);

                    [y6_unique, idy6] = unique(yc6);
                    x6 = xc6(idy6);

                    % figure; plot(yc3,xc3)
                    % figure; plot(y3_unique,x3,'.r'); hold on

                    % sort
                    [y3_sorted, sortIdy3] = sort(y3_unique);
                    x3_sorted = x3(sortIdy3);

                    [y6_sorted, sortIdy6] = sort(y6_unique);
                    x6_sorted = x6(sortIdy6);


                    % intergrate
                    volume3 = pi * trapz(y3_sorted, x3_sorted.^2);
                    volume6 = pi * trapz(y6_sorted, x6_sorted.^2);
                    fprintf('Volume -3dB contour = %0.1f mm3\n',volume3);
                    fprintf('Volume -6dB contour = %0.1f mm3\n',volume6);

                    cl = [-30,0];
                    %value = 'dB';

                end

                % labels
                xlabel(xAxis);
                ylabel(yAxis); 

                
                
                if strcmp(colormapType,'hot')
                    colormap hot;
                elseif strcmp(colormapType,'monotone') 
                    n = 256; % number of colors in the colormap
                    cmap = [linspace(1,1,n)', linspace(1,0,n)', linspace(1,0,n)']; % R:1→1, G:1→0, B:1→0
                    colormap(cmap);
                elseif strcmp(colormapType,'viridis')
                    viridis = [
                        0.2670, 0.0049, 0.3294;
                        0.2832, 0.1415, 0.4586;
                        0.254,  0.265,  0.530;
                        0.163,  0.471,  0.558;
                        0.135,  0.656,  0.466;
                        0.477,  0.821,  0.318;
                        0.993,  0.906,  0.144
                        ];

                    cmap = colormap(interp1(1:size(viridis,1), viridis, linspace(1,size(viridis,1),256)));
                    colormap(cmap);

                else

                    colormap;             
                end

                % design
                axis equal tight
                box off
                drawnow

                c = colorbar;
                
                ylabel(c,value)
                %clim(cl)
                clim auto
  
                
                title(sprintf('%s Focus = %2.1f mm \n %s',obj.prepData.p{i}.TD.name,obj.prepData.p{i}.TD.Focus,obj.prepData.p{i}.measurement.type))

                % define folder location
                nameSingleViewFig     = sprintf('XZSection y = %2.1f mm %s %s %s.fig',y(1),value(1:8),obj.prepData.p{i}.TD.name,obj.prepData.p{i}.measurement.type);
                nameSingleViewTiff     = sprintf('XZSection y = %2.1f mm %s %s %s.tiff',y(1),value(1:8),obj.prepData.p{i}.TD.name,obj.prepData.p{i}.measurement.type);  
                pathNameSingleViewFig = fullfile(obj.folderLoc,nameSingleViewFig);
                pathNameSingleViewTiff = fullfile(obj.folderLoc,nameSingleViewTiff);
                
                % saving matlab fig
                savefig(pathNameSingleViewFig)

                % saving tiff
                imwrite(frame2im(getframe(gcf)),pathNameSingleViewTiff)
                
                if closeFig
                    close(f)
                end

                if diffIm
                    break
                end

                ii = ii+1;
            end
                
        end

        function visualize(obj,setNrs,value)

            ii = 1;
            for i = setNrs % for every sequence

                switch value

                    case 'Pressure [MPa]'

                        %v = 1e-6*obj.calcData.pressure.{i}.amp.raw;

                    case 'ISPPA [W/cm2]'

                    case 'dB'

                end


                ii = ii+1;
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

                    xm = squeeze(obj.calcData.holography{k}.grid.xmi(:,:,j));
                    ym = squeeze(obj.calcData.holography{k}.grid.ymi(:,:,j));
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
                    view(45,15);
                    colorbar
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
           
        end

        function equalizationCurve(obj)
            
            % Curve fitting graphs
            f = figure('color', [1 1 1],'position',[50,50,1600,800]);

            subplot(2,2,1); hold on
         
            for i = 1:numel(obj.calcData.pressure)
                
                if isfield(obj.calcData.pressure{i}.amp,'equalized')
                    if ~isnan(obj.calcData.pressure{i}.amp.equalized)

                        % disctance wrt exit plane
                        x = obj.prepData.coordinates{i}(:,6);  % z [mm]

                        % IGT set focus
                        % leg{i} = num2str(obj.calcData.pressureCurve.F(i));

                        plot(x,obj.calcData.pressure{i}.amp.spatialFilt)

                        % plot max
                        plot(obj.calcData.pressure{i}.amp.spatialFiltMetrics(2),obj.calcData.pressure{i}.amp.spatialFiltMetrics(1),'kx')
                        % plot FWHM
                        plot(obj.calcData.pressure{i}.amp.spatialFiltMetrics(4),obj.calcData.pressure{i}.amp.spatialFiltMetrics(1),'k.')

                    end
                end
            end
            
            %lg = legend(leg); lg.Title.String = 'IGT set focus';

            % plot norm pressure line
            line([min(x),max(x)],[obj.calcData.pressureCurve.normPressure,obj.calcData.pressureCurve.normPressure],'color',[0 0 0])
                        
            xlabel('Distance wrt exit plane [mm]'); ylabel('Pressure [Pa]'); title(sprintf('Axial profiles [Pressure @ natural focus is %.1f [Pa] ]',obj.calcData.pressureCurve.normPressure)); grid minor;

            subplot(2,2,2)
            plot(obj.calcData.pressureCurve.x,obj.calcData.pressureCurve.y,'k.');
            xlabel([obj.calcData.pressureCurve.type,' wrt exit plane [mm]']); ylabel('Max Pressure [Pa]'); title('Pressure curve'); grid minor; axis square; box off

            subplot(2,2,4)
            plot(obj.calcData.equalizationCurvature.x,obj.calcData.equalizationCurvature.y,'k.')
            xlabel([obj.calcData.pressureCurve.type,' wrt exit plane [mm]']); ylabel('Equalization Factor'); title('Equalization curve'); grid minor; axis square; box off
            leg{1} = 'Raw data point'; ylim([0.5,1.5])

            subplot(2,2,3) % application of equalization curves on axial profiles
            hold on;
            for i = 1:numel(obj.calcData.pressure)

                if isfield(obj.calcData.pressure{i}.amp,'equalized')
                    if ~isnan(obj.calcData.pressure{i}.amp.equalized)

                        % disctance wrt exit plane
                        x = obj.prepData.coordinates{i}(:,6);  % z [mm]

                        % IGT set focus

                        % if ~isnan(obj.calcData.pressure{i}.amp.equalized)
                        %     leg2{j} = num2str(obj.calcData.pressureCurve.F(i));
                        %     j = j+1;
                        % end

                        plot(x,obj.calcData.pressure{i}.amp.equalized)
                    end
                end

            end

            % plot norm pressure line
            line([min(x),max(x)],[obj.calcData.pressureCurve.normPressure,obj.calcData.pressureCurve.normPressure],'color',[0 0 0])

            xlabel('Distance wrt exit plane [mm]'); ylabel('Pressure [Pa]'); title('Equalized axial profiles'); grid minor;
            %lg2 = legend(leg2,'location','best'); lg2.Title.String = 'IGT set focus';


            % add fit visualization
            if isfield(obj.calcData.equalizationCurvatureFit,'splineFit')
                if isfield(obj.calcData.equalizationCurvatureFit.splineFit,'struct')
                    hold on

                    colors = lines(numel(obj.calcData.equalizationCurvatureFit.splineFit));
                    subplot(2,2,4); hold on
                    for i = 1: numel(obj.calcData.equalizationCurvatureFit.splineFit)
                        plot( obj.calcData.equalizationCurvatureFit.splineFit(i).data.x, obj.calcData.equalizationCurvatureFit.splineFit(i).data.y,'Color', [0 0 0]);

                        title('Equalization curve with piecewise polynomial fit');

                        %The Durbin-Watson (DW) statistic is a test used in regression analysis to detect the presence of autocorrelation (serial correlation) in the residuals of a model.
                        %It helps determine whether residuals (errors) from a fitted model are independent or show patterns over time. The statistic is mainly used in time series analysis and regression models where data points are sequentially dependent.
                        % DW Value	Interpretation
                        % ≈ 2	No autocorrelation (ideal case)
                        % < 2	Positive autocorrelation (errors are correlated)
                        % > 2	Negative autocorrelation (alternating pattern in errors)
                        % ≈ 0	Strong positive autocorrelation (errors increase/decrease together)
                        % ≈ 4	Strong negative autocorrelation (errors alternate in sign)

                        leg{1+i} = sprintf('X transform: %s. | Durbin-Watson = %2.2f',obj.calcData.equalizationCurvatureFit.splineFit(i).xTransform,obj.calcData.equalizationCurvatureFit.splineFit(i).DurbinWatson);
                    end
                    legend(leg,'location','best');

                end
            end

            % define folder location
            nameSingleView     = sprintf('equalizationCurveFitting %s.tiff',obj.prepData.p{1}.TD.name);
            pathNameSingleView = fullfile(obj.folderLoc,nameSingleView);

            % save image
            imwrite(frame2im(getframe(gcf)),pathNameSingleView)
            % save Mat fig
            savefig([pathNameSingleView(1:end-5),'.fig'])




        end

        function powerCurve(obj)
            
            % Create figure
            f = figure('color', [1 1 1],'position',[50,50,1600,1000]);

            % define folder location
            nameSingleView     = sprintf('Amplitude Versus Max Pressure %s.tiff',obj.prepData.p{1}.TD.name);
            pathNameSingleView = fullfile(obj.folderLoc,nameSingleView);
            % Plot axial profiles with attenuation
            subplot(2,3,1)
            for i = obj.calcData.powerCurvature.setNrs(1:20)
                plot(obj.prepData.coordinates{i}(:,6),obj.calcData.pressure{i}.amp.spatialFilt,'k'); hold on
                % plot max
                [maxP,iMaxP] = max(obj.calcData.pressure{i}.amp.spatialFilt);
                xMaxP = obj.prepData.coordinates{i}(iMaxP,6);
                plot(xMaxP,maxP,'kx')
                text(10+xMaxP,maxP,sprintf('%s %% Amplitude',obj.prepData.p{i}.amp.power))
            end
            ylabel('Pressure [Pa]'); xlabel('Distance wrt exit plane [mm]');  title('Axial pressure profiles with attenuation sheet @ natural focus' ); grid minor; axis square; box off;
           
            % Plot axial profiles without attenuation
            subplot(2,3,4)
            for i = obj.calcData.powerCurvature.setNrs(21:32)
                plot(obj.prepData.coordinates{i}(:,6),obj.calcData.pressure{i}.amp.spatialFilt,'k'); hold on
                % plot max
                [maxP,iMaxP] = max(obj.calcData.pressure{i}.amp.spatialFilt);
                xMaxP = obj.prepData.coordinates{i}(iMaxP,6);
                plot(xMaxP,maxP,'kx')
                text(10+xMaxP,maxP,sprintf('%s %% Amplitude',obj.prepData.p{i}.amp.power))
            end
            xlim([0,140])
            ylabel('Pressure [Pa]'); xlabel('Distance wrt exit plane [mm]');  title('Axial pressure profiles  @ natural focus' ); grid minor; axis square; box off;
           
            subplot(2,3,2)
            plot(obj.calcData.powerCurvatureFit.meanAttFactor.x,(obj.calcData.powerCurvatureFit.meanAttFactor.y),'k.'); hold on
            plot(obj.calcData.powerCurvatureFit.meanAttFactor.xi,(obj.calcData.powerCurvatureFit.meanAttFactor.yi),'k-');
            plot(obj.calcData.powerCurvatureFit.meanAttFactor.xi(13:end),(obj.calcData.powerCurvatureFit.meanAttFactor.yi(13:end)),'kx');
            yl = ylim;
            line([35 35],yl,'color',[0 0 0], 'lineStyle','--');
            line([60 60],yl,'color',[0 0 0], 'lineStyle','--');
            
            legend('Estimated attenuation','','Extrapolated attenuation using 35% - 60% mean value','Box','off','FontSize',8)
      
            ylabel('Attenuation factor [-]'); xlabel( 'Amplitude [%]');  title('Atttenuation factor @ natural focus' ); grid minor; axis square; box off;

            subplot(2,3,5)
            % Amplitude(pressure)
            plot(obj.calcData.powerCurvature.x(1:32),obj.calcData.powerCurvature.y(1:32),'k.'); hold on
            plot(obj.calcData.powerCurvature.x(33:end),obj.calcData.powerCurvature.y(33:end),'kx');
            xlabel('Max Pressure [Pa]'); ylabel('Amplitude [% max]');  title(nameSingleView(1:end-5));  axis square
            hold on

            plot(obj.calcData.powerCurvatureFit.quadraticFit.data.x,obj.calcData.powerCurvatureFit.quadraticFit.data.y,'b-'); hold on
            plot(obj.calcData.powerCurvatureFit.linFit.data.x,obj.calcData.powerCurvatureFit.linFit.data.y,'g.-'); % Linear fit on all data
            plot(obj.calcData.powerCurvatureFit.rawLinFit.data.x,obj.calcData.powerCurvatureFit.rawLinFit.data.y,'r.-'); % Linear fit on raw(only measured) data
            % plot(obj.calcData.powerCurvatureFit.splineFit.data.x,obj.calcData.powerCurvatureFit.splineFit.data.y,'b-')
            ylim([0 100]); 
            
            x = [0,obj.calcData.powerCurvature.x(21:end)];
            y = [0,obj.calcData.powerCurvature.y(21:end)];
            y1 = obj.calcData.powerCurvatureFit.rawLinFit.data.y;
            y2 = obj.calcData.powerCurvatureFit.linFit.data.y;
            y3 = obj.calcData.powerCurvatureFit.quadraticFit.data.y;

            % f = figure('color', [1 1 1],'position',[50,50,1600,1800]);
            % subplot(1,2,1);
            % plot(x,y,'k.-'); hold on
            % plot(x,y1,'r.-')
            % plot(x,y2,'g.-')
            % plot(x,y3,'b.-')
            xlabel('Pressure setpoint [Pa]'); ylabel('Amplitude setpoint'); grid minor; box off; axis square; 
            subplot(2,3,6);
            plot(x,y1./y*100-100,'r.-'); hold on
            plot(x,y2./y*100-100,'g.-');
            plot(x,y3./y*100-100,'b.-');
            ylim([-10 10]);xlabel('Pressure setpoint [Pa]'); ylabel('Amplitude setpoint [% deviation of measured points]'); grid minor; box off; axis square; 
            legend('Lineair fit on measured points','Linear fit using complete set','Quatratic fit using complete set')
            


            % visualize formula
            % Create the equation string
         %  equation_str = sprintf('Amplitude(%%) = %.6d * Pressure(Pa)^2 + %.6d * Pressure(Pa) + %.6d ', obj.calcData.powerCurvatureFit.pFit.pf(1), obj.calcData.powerCurvatureFit.pFit.pf(2),obj.calcData.powerCurvatureFit.pFit.pf(3));

            % Display the equation on the plot
         %   text(0.8 * (0 + 1e6), 80, equation_str, 'FontSize', 12, 'Color', 'blue', 'HorizontalAlignment', 'center');


            % save image
            imwrite(frame2im(getframe(gcf)),pathNameSingleView)
            % save Mat fig
            savefig([pathNameSingleView(1:end-5),'.fig'])
        end

        function focusCurve(obj)
    
            % Create figure
            f = figure('color', [1 1 1],'position',[50,50,600,600]);
            
            % define folder location
            nameSingleView     = sprintf('Set Focus Versus FWHM center %s.tiff',obj.prepData.p{1}.TD.name);
            pathNameSingleView = fullfile(obj.folderLoc,nameSingleView);

            % setFocus(FWHMcenter)
            plot(obj.calcData.focusCurvature.x,obj.calcData.focusCurvature.y,'k.');
            xlim([0,140])
            xlabel('FWHM center wrt exit plane [mm]'); ylabel('Set Focus [mm]');  title(nameSingleView); grid minor; axis square
            leg{1} = 'Focus curvature datapoints';
                
            if isfield(obj.calcData.focusCurvatureFit,'splineFit')
                hold on

                colors = lines(numel(obj.calcData.equalizationCurvatureFit.splineFit));

                for i = 1: numel(obj.calcData.focusCurvatureFit.splineFit)
                    plot( obj.calcData.focusCurvatureFit.splineFit(i).data.x, obj.calcData.focusCurvatureFit.splineFit(i).data.y,'Color', [0 0 0]);

                    title('Focus curve with piecewise polynomial fit');

                    %The Durbin-Watson (DW) statistic is a test used in regression analysis to detect the presence of autocorrelation (serial correlation) in the residuals of a model.
                    %It helps determine whether residuals (errors) from a fitted model are independent or show patterns over time. The statistic is mainly used in time series analysis and regression models where data points are sequentially dependent.
                    % DW Value	Interpretation
                    % ≈ 2	No autocorrelation (ideal case)
                    % < 2	Positive autocorrelation (errors are correlated)
                    % > 2	Negative autocorrelation (alternating pattern in errors)
                    % ≈ 0	Strong positive autocorrelation (errors increase/decrease together)
                    % ≈ 4	Strong negative autocorrelation (errors alternate in sign)

                    leg{1+i} = sprintf('X transform: %s. | Durbin-Watson = %2.2f',obj.calcData.equalizationCurvatureFit.splineFit(i).xTransform,obj.calcData.equalizationCurvatureFit.splineFit(i).DurbinWatson);
                end
                
            end
            if isfield(obj.calcData.focusCurvatureFit,'linFit')

                hold on

                plot(obj.calcData.focusCurvatureFit.linFit.x,obj.calcData.focusCurvatureFit.linFit.y,'k--')
                

                % visualize formula
                % Create the equation string
                equation_str = sprintf('Amplitude(%%) = %.6d + %.6d * Pressure(Pa)', obj.calcData.focusCurvatureFit.linFit.mdl.Coefficients.Estimate(1), obj.calcData.focusCurvatureFit.linFit.mdl.Coefficients.Estimate(2));

                % Display the equation on the plot
                text(70, 120, equation_str, 'FontSize', 12, 'Color', [0 0 0], 'HorizontalAlignment', 'center');

                leg{2+i} = 'Linear Fit';
                xlim([0 140])
            end
            legend(leg)
            % save image
            imwrite(frame2im(getframe(gcf)),pathNameSingleView)
            % save Mat fig
            savefig([pathNameSingleView(1:end-5),'.fig'])

        end
    end

    methods(Access = private)
        %% in class functions

        function colorsHSV = createColorMap(~,Hues, saturationValue,brightnessVal)
            hueValues = linspace(0, 1, Hues)';
            colorsHSV = hsv2rgb([hueValues, saturationValue * ones(Hues, 1), brightnessVal * ones(Hues, 1)]);
        end

        % function plotting()
        % 
        % 
        % end

    end


end