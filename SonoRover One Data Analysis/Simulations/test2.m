% define grid properties
Nx = 128; 		% [grid points]
Ny = 64;		% [grid points]
dx = 1e-4;		% [m]

% define input amplitude [Pa] and phase [rad] for a line source
amp_in = zeros(Nx, Ny);
amp_in(1, Ny/4:3*Ny/4) = 1;
phase_in = 0;

% define medium and source properties
f0 = 2e6;		% [Hz]
c0 = 1500;		% [m/s]

% compute pressure field
[amp_out, phase_out] = acousticFieldPropagator(amp_in, phase_in, dx, f0, c0);

% create plot axis
x_vec = 1e3 * (0:Nx-1) * dx;
y_vec = 1e3 * (-Ny/2:Ny/2 - 1) * dx;

% plot amplitude
figure;
subplot(1, 2, 1);
imagesc(y_vec, x_vec, amp_out);
axis image;
xlabel('Lateral Distance [mm]');
ylabel('Axial Distance [mm]');
title('Phase');

% plot phase
subplot(1, 2, 2);
imagesc(y_vec, x_vec, phase_out);
axis image;
xlabel('Lateral Distance [mm]');
ylabel('Axial Distance [mm]');
title('Phase');


%%
% Define matrix size
rows = 11; 
cols = 11;

% Create coordinate grid
[x, y] = meshgrid(1:cols, 1:rows);

% Define circle parameters
centerX = (cols + 1) / 2;  % X center of the circle
centerY = (rows + 1) / 2;  % Y center of the circle
radius = 5.1;                % Radius of the circle

% Create circular mask using the equation of a circle
mask = (x - centerX).^2 + (y - centerY).^2 <= radius^2;

% Display the mask
disp('Circular Binary Mask:');
disp(mask);



mask(:,1)=[];

totalMask = [fliplr(mask),mask]

% Display the mask
disp('Circular Binary Mask:');
disp(mask);

disp(totalMask)

%%

% Visualize the mask
figure
imagesc(totalMask);
colormap(gray);
axis equal;
title('11x11 Circular Binary Mask');


%%

clc; clear; close all;

% Define grid dimensions
numRows = 11; % Number of transducers in rows
numCols = 20; % Number of transducers in columns

% Define transducer element size and kerf
elementSize = 3.75;  % Size of each transducer (mm)
kerf = 0.5;          % Gap between transducers (mm)

% Calculate pitch (distance between centers of adjacent transducers)
pitch = elementSize + kerf;

% Create grid coordinates
[xGrid, yGrid] = meshgrid(0:numCols-1, 0:numRows-1);

% Convert to mm positions
xPositions = xGrid * pitch;
yPositions = yGrid * pitch;

% Visualization
figure;
hold on;
axis equal;
xlabel('X Position (mm)');
ylabel('Y Position (mm)');
title('Rectangular Transducer Array (11x20)');

% Plot each transducer as a square
for i = 1:numRows
    for j = 1:numCols
        xCorner = xPositions(i, j);
        yCorner = yPositions(i, j);
        rectangle('Position', [xCorner, yCorner, elementSize, elementSize], ...
                  'FaceColor', 'b', 'EdgeColor', 'k');
    end
end

hold off;

%%
clc; clear; close all;

% Define grid dimensions
numRows = 11; % Number of transducers in rows
numCols = 20; % Number of transducers in columns

% Define transducer element size and kerf
elementSize = 3.75;  % Size of each transducer (mm)
kerf = 0.5;          % Gap between transducers (mm)

% Calculate pitch (distance between centers of adjacent transducers)
pitch = elementSize + kerf;

% Create grid coordinates for centers
[xGrid, yGrid] = meshgrid(0:numCols-1, 0:numRows-1);

% Compute center positions
xCenters = xGrid * pitch + elementSize / 2;
yCenters = yGrid * pitch + elementSize / 2;

% Display center coordinates
disp('Center Coordinates of Transducer Elements (X, Y in mm):');
for i = 1:numRows
    for j = 1:numCols
        fprintf('(%.2f, %.2f) ', xCenters(i, j), yCenters(i, j));
    end
    fprintf('\n');
end

% Visualization
figure;
hold on;
axis equal;
xlabel('X Position (mm)');
ylabel('Y Position (mm)');
title('Transducer Array with Center Points');

% Plot transducer centers
scatter(xCenters(:), yCenters(:), 'ro', 'filled');

% Annotate transducer centers
for i = 1:numRows
    for j = 1:numCols
        text(xCenters(i, j), yCenters(i, j), sprintf('(%d,%d)', i, j), ...
            'FontSize', 8, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
    end
end

hold off;

%%
clc; clear; close all;

% Define grid dimensions
numRows = 11; % Number of transducers in rows
numCols = 20; % Number of transducers in columns

% Define transducer element size and kerf
elementSize = 3.75;  % Size of each transducer (mm)
kerf = 0.5;          % Gap between transducers (mm)

% Calculate pitch (distance between centers of adjacent transducers)
pitch = elementSize + kerf;

% Create grid coordinates for transducer centers
[xGrid, yGrid] = meshgrid(0:numCols-1, 0:numRows-1);
xCenters = xGrid * pitch + elementSize / 2;
yCenters = yGrid * pitch + elementSize / 2;

% Define focal point in 3D space
xFocus = mean(xCenters(:));  % X center of the array
yFocus = mean(yCenters(:));  % Y center of the array
zFocus = 60;                 % 60 mm depth

% Calculate distances to focus
distances = sqrt((xCenters - xFocus).^2 + (yCenters - yFocus).^2 + zFocus^2);

% Display distances
disp('Distance of each element to the focus (mm):');
disp(distances);

% Visualization
figure;
hold on;
axis equal;
xlabel('X Position (mm)');
ylabel('Y Position (mm)');
zlabel('Z Position (mm)');
title('Transducer Array and Focus Point');

% Plot transducer centers
scatter3(xCenters(:), yCenters(:), zeros(size(xCenters(:))), 'bo', 'filled');

% Plot focus point
scatter3(xFocus, yFocus, zFocus, 100, 'r', 'filled');

% Draw lines from each element to the focus
for i = 1:numRows
    for j = 1:numCols
        plot3([xCenters(i, j), xFocus], [yCenters(i, j), yFocus], [0, zFocus], 'k-');
    end
end

legend('Transducer Elements', 'Focus Point', 'Lines to Focus');
grid on;
hold off;

%%

clc; clear; close all;

% Define grid dimensions
numRows = 11; % Number of transducers in rows
numCols = 20; % Number of transducers in columns

% Define transducer element size and kerf
elementSize = 3.75;  % Size of each transducer (mm)
kerf = 0.5;          % Gap between transducers (mm)

% Calculate pitch (distance between centers of adjacent transducers)
pitch = elementSize + kerf;

% Create grid coordinates for transducer centers
[xGrid, yGrid] = meshgrid(0:numCols-1, 0:numRows-1);
xCenters = xGrid * pitch + elementSize / 2;
yCenters = yGrid * pitch + elementSize / 2;

% Define focal point in 3D space
xFocus = mean(xCenters(:));  % X center of the array
yFocus = mean(yCenters(:));  % Y center of the array
zFocus = 60;                 % 60 mm depth

% Calculate distances to focus
distances = sqrt((xCenters - xFocus).^2 + (yCenters - yFocus).^2 + zFocus^2);

% Given parameters
wavelength = 3.75; % Wavelength in mm

% Compute phase difference in radians
phaseDifference = (2 * pi * distances) / wavelength;

% Display phase difference
disp('Phase difference of each element (radians):');
disp(phaseDifference);

% Visualization
figure;
imagesc(phaseDifference);
colorbar;
xlabel('Transducer Column');
ylabel('Transducer Row');
title('Phase Difference (radians)');

%%

clc; clear; close all;

% Define grid dimensions
numRows = 11; % Number of transducers in rows
numCols = 20; % Number of transducers in columns

% Define transducer element size and kerf
elementSize = 3.75;  % Size of each transducer (mm)
kerf = 0.5;          % Gap between transducers (mm)

% Calculate pitch (distance between centers of adjacent transducers)
pitch = elementSize + kerf;

% Create grid coordinates for transducer centers
[xGrid, yGrid] = meshgrid(0:numCols-1, 0:numRows-1);
xCenters = xGrid * pitch + elementSize / 2;
yCenters = yGrid * pitch + elementSize / 2;

% Define focal point in 3D space
xFocus = mean(xCenters(:));  % X center of the array
yFocus = mean(yCenters(:));  % Y center of the array
zFocus = 60;                 % 60 mm depth

% Calculate distances to focus
distances = sqrt((xCenters - xFocus).^2 + (yCenters - yFocus).^2 + zFocus^2);

% Given parameters
wavelength = 3.75; % Wavelength in mm

% Compute phase difference in radians
phaseDifference = mod((2 * pi * distances) / wavelength, 2 * pi);  % Wrap between 0 and 2π

% Display phase difference
disp('Wrapped Phase Difference (radians) between 0 and 2π:');
disp(phaseDifference);

% Visualization
figure;
imagesc(phaseDifference);
colorbar;
caxis([0 2*pi]); % Limit color range from 0 to 2π
xlabel('Transducer Column');
ylabel('Transducer Row');
title('Wrapped Phase Difference (0 to 2π radians)');


