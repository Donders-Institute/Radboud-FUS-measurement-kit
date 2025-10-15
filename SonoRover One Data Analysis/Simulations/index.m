

clear; close all; clc;

% Add k-Wave to the path if necessary
addpath(genpath('k-wave-toolbox-version-1.4'));

% Define the simulation grid
Nx = 128;   % number of grid points in x-direction
Ny = 128;   % number of grid points in y-direction
Nz = 128;   % number of grid points in z-direction
dx = 0.3e-3; % grid point spacing [m] (0.3 mm)
dy = dx;
dz = dx;

% Create k-Wave grid
kgrid = kWaveGrid(Nx, dx, Ny, dy, Nz, dz);

% Define medium properties (water)
medium.sound_speed = 1500;  % [m/s] speed of sound in water
medium.density = 1000;      % [kg/m^3] density of water
medium.alpha_coeff = 0.002; % attenuation coefficient [dB/(MHz^y cm)]
medium.alpha_power = 2;     % frequency exponent

% Define transducer properties
f0 = 500e3;     % Frequency 500 kHz
lambda = medium.sound_speed / f0;
n_elements_x = 1; % Matrix transducer: 8x8 elements
n_elements_y = 1;
element_spacing = lambda / 2; % Spacing between elements

% Define the source mask (matrix transducer)
source_mask = zeros(Nx, Ny, Nz);
x_start = round(Nx/2 - (n_elements_x * element_spacing) / (2 * dx));
y_start = round(Ny/2 - (n_elements_y * element_spacing) / (2 * dy));
z_start = round(Nz/4); % Place transducer near the surface

for i = 0:n_elements_x-1
    for j = 0:n_elements_y-1
        x_idx = x_start + round(i * element_spacing / dx);
        y_idx = y_start + round(j * element_spacing / dy);
        source_mask(x_idx, y_idx, z_start) = 1;
    end
end

% Define the source signal (continuous wave)
source.p_mask = source_mask;
source_freq = f0;
source_mag = 1e6; % Pressure magnitude [Pa]
source.p = source_mag * sin(2 * pi * source_freq * kgrid.t_array);

% Set absorbing boundaries to reduce reflections
PML_size = 10;
PML_alpha = 2;

% Define sensor positions to record pressure field
sensor.mask = zeros(Nx, Ny, Nz);
sensor.mask(:, :, round(Nz/2)) = 1; % Measure field in the central plane

% Define the k-Wave simulation input structure
kgrid.makeTime(medium.sound_speed);

% Run the simulation
sensor_data = kspaceFirstOrder3D(kgrid, medium, source, sensor, ...
    'PMLSize', PML_size, 'PMLAlpha', PML_alpha, ...
    'PlotLayout', true, 'PlotPML', false);

% Visualize the pressure field
figure;
p_max = max(sensor_data(:));
imagesc(kgrid.y_vec * 1e3, kgrid.x_vec * 1e3, squeeze(sensor_data(:, :, round(Nz/2))));
xlabel('y [mm]');
ylabel('x [mm]');
title('Pressure Field at z = Nz/2');
colorbar;

%%

% Define figure
figure;
hold on;
grid on;
axis equal;
xlabel('X Position [mm]');
ylabel('Y Position [mm]');
zlabel('Z Position [mm]');
title('3D Matrix Transducer Element Organization');

% Extract transducer element positions
[x_idx, y_idx, z_idx] = ind2sub(size(source_mask), find(source_mask));

% Convert to physical coordinates
x_pos = (x_idx - Nx/2) * dx * 1e3; % Convert to mm
y_pos = (y_idx - Ny/2) * dy * 1e3; % Convert to mm
z_pos = z_idx * dz * 1e3;          % Convert to mm

% Plot transducer elements as 3D scatter points
scatter3(x_pos, y_pos, z_pos, 100, 'filled', 'r'); 

% Set visualization properties
view(3); % 3D perspective
legend('Active Transducer Elements');


%%



% Define the simulation grid
Nx = 128; Ny = 128; Nz = 128;  % Grid points
dx = 0.3e-3; dy = dx; dz = dx; % Grid spacing (0.3 mm)
kgrid = kWaveGrid(Nx, dx, Ny, dy, Nz, dz);

% Define medium properties (water)
medium.sound_speed = 1500;  % [m/s] speed of sound in water
medium.density = 1000;      % [kg/m^3] density of water
medium.alpha_coeff = 0.002; % Attenuation coefficient [dB/(MHz^y cm)]
medium.alpha_power = 2;     % Frequency exponent

% Define transducer properties
f0 = 500e3;     % Frequency 500 kHz
lambda = medium.sound_speed / f0;
n_elements_x = 8; % Matrix transducer: 8x8 elements
n_elements_y = 8;
element_spacing = lambda / 2; % Spacing between elements

% Define the source mask (matrix transducer)
source_mask = zeros(Nx, Ny, Nz);
x_start = round(Nx/2 - (n_elements_x * element_spacing) / (2 * dx));
y_start = round(Ny/2 - (n_elements_y * element_spacing) / (2 * dy));
z_start = round(Nz/4); % Place transducer near the surface

for i = 0:n_elements_x-1
    for j = 0:n_elements_y-1
        x_idx = x_start + round(i * element_spacing / dx);
        y_idx = y_start + round(j * element_spacing / dy);
        source_mask(x_idx, y_idx, z_start) = 1;
    end
end

% Define the source signal (short pulse)
source.p_mask = source_mask;
source_mag = 1e6; % Pressure magnitude [Pa]
source.p = source_mag * sin(2 * pi * f0 * kgrid.t_array) .* (kgrid.t_array < 3 / f0);

% Define the k-Wave simulation time
kgrid.makeTime(medium.sound_speed);

% Set absorbing boundaries
PML_size = 10;
PML_alpha = 2;

% Define a 3D sensor mask to record pressure over time
sensor.mask = zeros(Nx, Ny, Nz);
sensor.mask(:, :, round(Nz/2)) = 1; % Measure at the middle plane

% Run the k-Wave simulation
sensor_data = kspaceFirstOrder3D(kgrid, medium, source, sensor, ...
    'PMLSize', PML_size, 'PMLAlpha', PML_alpha, ...
    'PlotLayout', true, 'PlotPML', false);

%% **Visualization of the Propagation of Pressure Field**

figure;
for t = 1:10:length(kgrid.t_array)  % Loop over time steps
    imagesc(kgrid.x_vec * 1e3, kgrid.y_vec * 1e3, squeeze(sensor_data(:, :, round(Nz/2), t)));
    xlabel('X Position [mm]');
    ylabel('Y Position [mm]');
    title(['Propagation of Pressure Field at Time = ', num2str(kgrid.t_array(t) * 1e6), ' \mus']);
    colorbar;
    colormap(jet);
    caxis([-max(abs(sensor_data(:))), max(abs(sensor_data(:)))]);
    pause(0.05); % Pause to create animation effect
end


%%

% create empty array

%rect = makeCartRect(rect_pos, Lx, Ly, theta, num_points, plot_rect)

karray = kWaveArray;


[xm,ym] = meshgrid([-4:4],[-4:4]);

positions  = 3.5*1e-3*[xm(:),ym(:)];
rotation = [0];


for i = 1:numel(xm)
    
    karray.addRectElement(positions(i,:),3e-3,3e-3,rotation)

end

kgrid = kWaveGrid(10, 0.5e-3, 10,0.5e-3)

source.p_mask = karray.getArrayBinaryMask(kgrid);

% set source signals, one for each physical array element
f1 = 100e3;
f2 = 200e3;
f3 = 500e3;
sig1 = toneBurst(1/kgrid.dt, f1, 3);
sig2 = toneBurst(1/kgrid.dt, f2, 5);
sig3 = toneBurst(1/kgrid.dt, f3, 5);

% combine source signals into one array
source_signal = zeros(2, max(length(sig1), length(sig2)));
source_signal(1, 1:length(sig1)) = sig1;
source_signal(2, 1:length(sig2)) = sig2;
source_signal(3, 1:length(sig3)) = sig3;


% get distributed source signals (this automatically returns a weighted
% source signal for each grid point that forms part of the source)
source.p = karray.getDistributedSourceSignal(kgrid, source_signal);

karray.getElementPositions
karray.plotArray(1)