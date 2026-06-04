% test file for holography functions according to notes made with Elly at
% Fun

% 19-08-2024
% S.Fekkes @ fucused ultrasound initiative Radboud University
% adapted for new setup


% Acquistion specs
% The area of the transversal plane should be twice the size of the field trhough the plane... make sure the plane is in between the focus and the transducer
% make the dxdy twice the wavelength

% tetsdata location: H:\Hydrophone measurements\Measurements\2024\Transducers\CTX_500_026_4Ch\20240611 Julians PreStudyTesting\Output of T [NeuroFUS 4 ch. CTX-500-026] - DS [NeuroFUS 1 x 4 ch. or 1 x 2 ch. TPO senior 105-010]\P [Axial_Protocol_FreeField - Holography]
% load prepData;
% load('prepDataMat.mat'); with postprocessing software

% AXIAL PROFILE
setNr = [1];
Fs = prepData.p{setNr}.acq.fs;
f0 = prepData.p{setNr}.TD.f0;



 j = 1
amp1 = [];
amp2 = [];
amp3 = [];
amp4 = [];
 for setNr  = [1,4,5,7]


     % figure; plot(prepData.filtData{1}(prepData.ringupIndex{1}(100):prepData.postRingUpIndex{1}(100),100));


     for i = 1:1:281

         selectedWave1 = prepData.filtData{setNr}(prepData.ringupIndex{setNr}(i):prepData.postRingUpIndex{setNr}(i),i);
         selectedWave2 = prepData.dataSel.data{setNr}(prepData.ringupIndex{setNr}(i):prepData.postRingUpIndex{setNr}(i),i);
          selectedWave3 = prepData.dataSel.data{setNr}(prepData.ringupIndex{setNr}(i):prepData.postRingUpIndex{setNr}(i),i);
           selectedWave4 = prepData.dataSel.data{setNr}(prepData.ringupIndex{setNr}(i):prepData.postRingUpIndex{setNr}(i),i);

         [amp1(i,j), phase, freq] = extractAmpPhase(selectedWave1, Fs, f0);
         [amp1(i,j), phase, freq] = extractAmpPhase(selectedWave2, Fs, f0);
         [amp1(i,j), phase, freq] = extractAmpPhase(selectedWave1, Fs, f0);
         [amp1(i,j), phase, freq] = extractAmpPhase(selectedWave2, Fs, f0);

     end

     % figure;plot(amp1); hold on
     % plot(amp2,'r')

     j = j+1;
 end

za = prepData.coordinates{1}(:,6);
 
figure; plot(za,amp1(:,1),'b'); hold on
         plot(za,amp1(:,2),'r');
         plot(za,amp1(:,3),'r');
         plot(za,amp1(:,4),'r');
         title('Axial center profile'); xlabel('Z [mm]'); ylabel('Voltage [V]');
         grid minor, box off
% 
% 
% figure;
% newplot
% for i = 1:1:281
% 
%     subplot(1,2,1)
%     plot(prepData.filtData{1}(:,i))
%     hold on; plot(prepData.dataSel.data{1}(:,i),'r'); hold off
%     ylim([-0.3 0.3])
%     subplot(1,2,2)
% 
%     selectedWave1 = prepData.filtData{1}(prepData.ringupIndex{1}(i):prepData.postRingUpIndex{1}(i),i);
%     %selectedWave2 = prepData.dataSel.data{1}(prepData.ringupIndex{1}(i):prepData.postRingUpIndex{1}(i),i);
%     plot(selectedWave1)
%     [amp1, phase, freq] = extractAmpPhase(selectedWave1, Fs, f0);
%    ylim([-0.3 0.3])
%     hold on
%     line([0, numel(selectedWave1)],[amp1 amp1]); hold off
%     waitforbuttonpress
% 
% end


% TRANSVERSE PROFILE
% 1) select time based pressure signal
setNr = 3;

Fs = prepData.p{setNr}.acq.fs;
f0 = prepData.p{setNr}.TD.f0;

% Trim data
data = prepData.dataSel.data{setNr};
startIdx = prepData.ringupIndex{setNr}(1);
endIdx   = prepData.postRingUpIndex{setNr}(1);
trimmedData = data(startIdx:endIdx,:);

% read coordinates vector [m]
x = prepData.coordinates{setNr}(:,4)*1e-3;
y = prepData.coordinates{setNr}(:,5)*1e-3;
z = prepData.coordinates{setNr}(:,6)*1e-3;

% reshape into 2D
ms = sqrt(numel(x));
X = reshape(x,[ms,ms]);
Y = reshape(y,[ms,ms]);
dxy = diff(y(1:2));

% reconstrct meshgrid for 3D grid
xv = linspace(min(x),max(x),ms);
yv = linspace(min(y),max(y),ms);

dz = 1; % resoltion in mm
zv = [0:dz:140]*1e-3; % m
%dxyi = diff(yv(1:2));

[xm,ym,zm] = meshgrid(xv,yv,zv);

intFactor = 5;
xvi = linspace(min(x),max(x),ms*intFactor);
yvi = linspace(min(y),max(y),ms*intFactor);

dxyi = diff(yvi(1:2));

[xmi,ymi,zmi] = meshgrid(xvi,yvi,zv);

xmip = squeeze(xmi(:,:,1));
ymip = squeeze(ymi(:,:,1));

% 2) first extract the amplitude an phase
[amp, phase, freq] = extractAmpPhase(trimmedData', Fs, f0);

AMP = double(reshape(amp,[ms,ms]));
PHASE = double(reshape(phase,[ms,ms]));

figure; subplot(1,2,1); imagesc(AMP); axis equal tight
        subplot(1,2,2); imagesc(PHASE); axis equal tight

complex_pressure = AMP.*exp(1i*PHASE);
complexPressure_i = interpft(complex_pressure,size(complex_pressure,1)*intFactor,1);
complexPressure_i = interpft(complexPressure_i,size(complexPressure_i,2)*intFactor,2);

figure; subplot(1,2,1); imagesc(abs(complexPressure_i)); axis equal tight
        subplot(1,2,2); imagesc(angle(complexPressure_i)); axis equal tight


% circular mask in case of square deformatity      
[n,~] = size(complexPressure_i);
[xid,yid] = meshgrid(1:n,1:n);
radius = n/2;
centerID = ceil((size(complexPressure_i))/2);
distance = sqrt((xid - centerID(1)).^2 + (yid - centerID(2)).^2); % Distance from center
cirMask = distance <= radius;                          % Circular mask

% Apply the mask to the data
complexPressure_i(~cirMask) = 0;   % Set values outside the circle to zero
figure; subplot(1,2,1); imagesc(abs(complexPressure_i)); axis equal tight
        subplot(1,2,2); imagesc(angle(complexPressure_i)); axis equal tight

% do the AS 
z_pos = zv  - z(1);
c0 = prepData.p{setNr}.water.c;
pressure = angularSpectrumCW(complexPressure_i, dxyi, z_pos, f0, c0);

% apply mask in 3D
sp = size(pressure);
cirMask3D = repmat(cirMask,[1,1,sp(3)]);
pressure(~cirMask3D) = 0;

% convert to amplitude
AS_amp = abs(pressure);
AS_phase = angle(pressure);

Z = 40;
% figure; subplot(1,2,1); imagesc(abs(pressure(:,:,Z) )); axis equal tight
%         subplot(1,2,2); imagesc(angle(pressure(:,:,Z) )); axis equal tight

figure; subplot(1,2,1); s = pcolor(xmip,ymip,AS_amp(:,:,Z)); axis equal
s.FaceColor  = 'interp';
s.EdgeColor = 'none';
axis tight; title('Hydrophone Amplitude [V]'); colorbar
subplot(1,2,2); s = pcolor(xmip,ymip,AS_phase(:,:,Z)); axis equal
s.FaceColor  = 'interp';
s.EdgeColor = 'none';
axis tight; title('Hydrophone phase [Rad]');colorbar

% extract axial profile from 3D volume
ASaxialProfile = squeeze(AS_amp(303,303,:));

figure; plot(za,amp1(:,1),'b'); hold on
         plot(za,amp1(:,2),'r');
         plot(zv*1e3,ASaxialProfile,'g')
         title('Axial center profile'); xlabel('Z [mm]'); ylabel('Voltage [V]');
         grid minor, box off



% 3D Visuals
figure;
zSlices = [0:10:140]*1e-3;
h = slice(xmi, ymi, zmi, (AS_amp), [], [], zSlices,'cubic'); hold on
set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
colormap(hot);
axis equal;  %alpha(0.5)
xlabel('Lateral');
ylabel('Elevational');
zlabel('Axial');




% isosurface
figure
[F,V] = isosurface(xmi,ymi,zmi,AS_amp,1.5e-3);
p = patch('Faces',F,'Vertices',V);
isonormals(AS_amp, p);
set(p, 'FaceColor', [1 0 0 ], 'EdgeColor', 'none');

daspect([1 1 1]); % Corrects aspect ratio
%view(3); % Sets the view to 3D

%view(az(vi),42)

axis equal;
xlabel('Lateral X [mm] ');
ylabel('Elevational Y [mm]');
zlabel('Axial Z [mm]');

xlim([min(xv),max(xv)])
ylim([min(yv),max(yv)])
zlim([min(zv),max(zv)])

camlight('headlight');

%% 3D result movies

name = 'FreeFieldR75';
setNrs = 1;
%close(videoFile)
if 1
    % Plot the isosurface
    for i = setNrs

        videoFile           = VideoWriter(sprintf('Movies\\FUS_Metrology_3D_Hlography_%s_%s_Set_%d.mp4',name,prepData.p.transducer.type{i},i),'MPEG-4');
        videoFile.FrameRate = 15;
        videoFile.Quality   = 25;
        open(videoFile);

        f = figure('color', [1 1 1],'Position',[50 50 1000 1000]); hold on

        % Pressure
        inputValues1 = AS_amp/2.691E-007; % adapt for new hydprophone!!!!!

        % conversion to dB
        Pressure_dB = 20*log10(inputValues1./max(inputValues1(:))); % Amplitude so 20*10log(A/A0) A^2 = P

        dB = [-20:0.20:-3];
        az = [-22: -37/numel(dB): -59];
        cmap = colormap(hot(numel(dB)));

        vi = 1;
        for v = dB
            cla
            % subplot(1,2,1) % Pressure
            [F,V] = isosurface(xmi,ymi,zmi,Pressure_dB,v);
            p = patch('Faces',F,'Vertices',V);
            isonormals(Pressure_dB, p);
            set(p, 'FaceColor', cmap(vi,:), 'EdgeColor', 'none');

            daspect([1 1 1]); % Corrects aspect ratio
            %view(3); % Sets the view to 3D

            view(az(vi),42)

            axis equal;
            xlabel('Lateral X [mm] ');
            ylabel('Elevational Y [mm]');
            zlabel('Axial Z [mm]');
            camlight('headlight');

            clim([min(dB) 0])

            vi = vi+1;

            xlim([min(xv),max(xv)])
            ylim([min(yv),max(yv)])
            zlim([min(zv),max(zv)])

            title(sprintf(' %s %s 3D isosurface of\n 20*10log(Pressure ratio) and 10*10log(ISPPA ratio) %.1f dB',name,prepData.p.transducer.type{i},v));
            drawnow
            writeVideo(videoFile,getframe(gcf));

        end
        close(f)
        close(videoFile)

    end
end

%% Holgraphy build movie

%% 3D result movies

%name = 'First Holography Build';
setNrs = 1;
close(videoFile)

    % Plot the isosurface
    for i = setNrs

        videoFile           = VideoWriter(sprintf('Movies\\FUS_Metrology_3D_Hlography_%s_%s_Set_%d.mp4',name,prepData.p.transducer.type{i},i),'MPEG-4');
        videoFile.FrameRate = 15;
        videoFile.Quality   = 25;
        open(videoFile);

        f = figure('color', [1 1 1],'Position',[50 50 1000 1000]); hold on

        % Pressure
        pressure = AS_amp/2.691E-007;

        % conversion to dB

        Pressure_dB = 20*log10(pressure./max(pressure(:))); % Amplitude so 20*10log(A/A0) A^2 = P

        ps = [0:0.01:0.5]*1e6;


        cmap = colormap(jet);
        pcmap = linspace(min(pressure(:)),max(pressure(:)),size(cmap,1));

        pnr = 50;
        pcmap(pnr)
        prange = [1:121];


        av = linspace(0,-30,50);
        el = linspace(90,10,50);

        for k = 1:50
            cla

            h = slice(xm, ym, zm, (pressure), [], [], [z(1)],'cubic'); hold on
            set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
            title(sprintf(' %s %s 3D isosurface of',name,prepData.p.transducer.type{i}));
            colormap(jet)
            axis equal;
            xlabel('Lateral X [m] ');
            ylabel('Elevational Y [m]');
            zlabel('Axial Z [m]');
            camproj('perspective');
            cb = colorbar;
            cb.Title.String = 'Pressure [Pa]';

            %camlight('headlight');

            xlim(0.5*[min(xv),max(xv)])
            ylim(0.5*[min(yv),max(yv)])
            zlim([min(zv),max(zv)])

            view(av(k),el(k))
            drawnow
            writeVideo(videoFile,getframe(gcf));

        end

        av = linspace(-30,-60,50);
        el = linspace(10,10,50);
        vi = 1;
        for nrs = 1:50
        cla
            s = z(1)+[-0.001 * nrs :0.001 :0.001 * nrs]

            % plot holography slice first
            h = slice(xm, ym, zm, (pressure), [], [], [s],'cubic'); hold on
            set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
            alpha(0.1)
            view(av(vi),el(vi))
            vi = vi+1;
            title(sprintf(' %s %s 3D isosurface',name,prepData.p.transducer.type{i}));
            drawnow
            writeVideo(videoFile,getframe(gcf));
        end

        pnrv = 50:2:256;

        av = linspace(-60,-120,numel(pnrv));
        el = linspace(10,10,numel(pnrv));
        vi = 1;
   
        for pnr = pnrv
            cla

            % plot holography slice first
            h = slice(xm, ym, zm, (pressure), [], [], [s],'cubic'); hold on
            set(h, 'EdgeColor', 'none','FaceColor','interp'); % Remove edges for better visualization
            alpha(0.1)
            drawnow

            % subplot(1,2,1) % Pressure
            [F,V] = isosurface(xm(:,:,prange),ym(:,:,prange),zm(:,:,prange),pressure(:,:,prange),pcmap(pnr));
            p = patch('Faces',F,'Vertices',V);
            isonormals(pressure, p);
            set(p ,'FaceColor',[cmap(pnr,:)] ,'EdgeColor', 'none');

            daspect([1 1 1]); % Corrects aspect ratio

            axis equal;
            xlabel('Lateral X [m] ');
            ylabel('Elevational Y [m]');
            zlabel('Axial Z [m]');
            camlight('headlight');

            xlim(0.5*[min(xv),max(xv)])
            ylim(0.5*[min(yv),max(yv)])
            zlim([min(zv),max(zv)])

            view(av(vi),el(vi))

            vi = vi+1;
            drawnow
            title(sprintf(' %s %s 3D isosurface',name,prepData.p.transducer.type{i}));
            drawnow
            writeVideo(videoFile,getframe(gcf));

        end
        close(f)
        close(videoFile)

    end
