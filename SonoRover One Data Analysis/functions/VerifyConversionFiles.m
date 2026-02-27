
%Verification script for transducer calibration
clear all; close all; clc;
% start location
pwd = '\\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2025\Transducers\';

% Let user pick a folder
folderPath = uigetdir(pwd, 'Select a folder containing JSON files');
if folderPath == 0
    disp( ...
        'No folder selected. Script aborted.');
    return;
end

equalizationCurveFit    = load(fullfile(folderPath, 'equalizationCurveFitExport.mat'));
focusCurvatureFit       = load(fullfile(folderPath, 'focusCurvatureFitExport.mat'));
powerCurvatureFit       = load(fullfile(folderPath, 'powerCurvatureFitExport.mat'));

%%

%% line plot
FWHMCenterPosition = [equalizationCurveFit.splineFitFunc.p.breaks(1):0.1:equalizationCurveFit.splineFitFunc.p.breaks(end)]; %mm
MaxPressurePa = [0.25:0.25:2.75]*1e6; %Pa

EqualizationFactor = [];
AmplitudePercentage = [];
AmplitudePercentage2 = [];
amplFactor = [];
IGTsetFocus = [];

%MaxPressurePa = 1e6
%FWHMCenterPosition = 90



%function [amplitude, IGTsetFocus] = conversion(FWHMCenterPosition,MaxPressurePa)
for j = 1:numel(MaxPressurePa)

    for i = 1: numel(FWHMCenterPosition)

        % equalization as function of FWHM center Position
        EqualizationFactor(i,j) = feval(equalizationCurveFit.splineFitFunc,FWHMCenterPosition(i));


        % Max Pressure conversion to Amplitude
        % AmplitudePercentage(i) =  (EqualizationFactor(i)) * polyval(powerCurvatureFit.FitFunc,MaxPressurePa)
        AmplitudePercentage2(i,j) =   polyval(powerCurvatureFit.pFit,EqualizationFactor(i)*MaxPressurePa(j));

        amplFactor(i,j) = polyval(powerCurvatureFit.pFit,MaxPressurePa(j));

        % FWHM center Position mapping to IGT set Focus
        IGTsetFocus(i,j) = feval(focusCurvatureFit.splineFitFunc,FWHMCenterPosition(i));
    end
end


EqualizationFactor
AmplitudePercentage2
IGTsetFocus
amplFactor

%%

figure;


subplot(4,1,1)
plot(FWHMCenterPosition,EqualizationFactor); title('Equalization factor at natural focus') ; xlabel('FWHMcenterPosition [mm]'); ylabel('Equalization factor [-]'); grid minor; box off
subplot(4,1,2)
plot(FWHMCenterPosition,AmplitudePercentage2,'k'); title('actual amplitude set') ; xlabel('FWHMcenterPosition [mm]'); ylabel('Amplitude [%]'); grid minor; box off
subplot(4,1,3)
plot(FWHMCenterPosition,amplFactor); title('Amplitude at natural focus [-]'); xlabel('FWHMcenterPosition [mm]'); ylabel('Amplitude [%]'); grid minor; box off
subplot(4,1,4)
plot(FWHMCenterPosition,IGTsetFocus); title('IGT set focus') ; xlabel('FWHMcenterPosition [mm]'); ylabel('IGT set Focus [mm]'); grid minor; box off

figure('Color',[1 1 1],'Position', 1.0e+03 *[ 0.1465    0.3180    1.2740    0.5530])
subplot(1,2,1)
plot(FWHMCenterPosition,AmplitudePercentage2,'k'); title('Set focus versus amplitude setpoint') ; xlabel('Set focus wrt exitplane [mm]'); ylabel('Driving amplitude [%]'); grid minor; box off
line([0 100],[100 100],'color',[0 0 0],'lineStyle','--')
axis square; ylim([0 300]); xlim([0 100])
ax1 = gca;

for j = 1:numel(MaxPressurePa)
    text(equalizationCurveFit.splineFitFunc.p.breaks(end)+1,AmplitudePercentage2(end,j),sprintf('%0.2f MPa',MaxPressurePa(j)*1e-6),'FontSize', 8, 'FontWeight', 'bold')
end

%% high definition colorplot
FWHMCenterPosition = [equalizationCurveFit.splineFitFunc.p.breaks(1):0.1:equalizationCurveFit.splineFitFunc.p.breaks(end)]; %mm
MaxPressurePa = [0.25:0.02:3]*1e6; %Pa

EqualizationFactor = [];
AmplitudePercentage = [];
AmplitudePercentage2 = [];
amplFactor = [];
IGTsetFocus = [];

%function [amplitude, IGTsetFocus] = conversion(FWHMCenterPosition,MaxPressurePa)
for j = 1:numel(MaxPressurePa)

    for i = 1: numel(FWHMCenterPosition)

        % equalization as function of FWHM center Position
        EqualizationFactor(i,j) = feval(equalizationCurveFit.splineFitFunc,FWHMCenterPosition(i));


        % Max Pressure conversion to Amplitude
        % AmplitudePercentage(i) =  (EqualizationFactor(i)) * polyval(powerCurvatureFit.FitFunc,MaxPressurePa)
        AmplitudePercentage2(i,j) =   polyval(powerCurvatureFit.pFit,EqualizationFactor(i)*MaxPressurePa(j));

        amplFactor(i,j) = polyval(powerCurvatureFit.pFit,MaxPressurePa(j));

        % FWHM center Position mapping to IGT set Focus
        IGTsetFocus(i,j) = feval(focusCurvatureFit.splineFitFunc,FWHMCenterPosition(i));
    end
end

% figure



subplot(1,2,2)
AmplitudePercentage2(AmplitudePercentage2>100) = NaN;
mask = ~isnan(AmplitudePercentage2);  
imagesc([min(FWHMCenterPosition),max(FWHMCenterPosition)],1e-6*[min(MaxPressurePa),max(MaxPressurePa)],AmplitudePercentage2','AlphaData',mask'); clim([0 100]); xlabel('Set focus wrt exitplane [mm]'); ylabel('Max Pressure [MPa]'); cb = colorbar; title(cb,'Driving amplitude [%]')
set(gca, 'YDir', 'normal'); axis square; 
ax2 = gca;
box off; xlim([0 100])
colormap parula
set(gca,'Color',[1 1 1]);  % magenta for NaNs
grid minor

disp([min(FWHMCenterPosition),max(FWHMCenterPosition)])

ax2.Position(3:4) = ax1.Position(3:4); 

% save image
imwrite(frame2im(getframe(gcf)),[folderPath,'\maxPressure_Focus_Amplitude.tiff'])
savefig([folderPath,'\maxPressure_Focus_Amplitude.fig'])