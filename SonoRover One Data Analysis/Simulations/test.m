% Add k-Wave toolbox to your path (if not already done)
addpath(genpath('k-wave-toolbox-version-1.4'));  % Update with the correct path to k-Wave

% 1. Define grid size and simulation parameters
Nx = 128;         % Number of grid points in the x-direction
Ny = 128;         % Number of grid points in the y-direction
dx = 0.1e-3;      % Grid spacing (in meters)
dy = 0.1e-3;      % Grid spacing (in meters)

% Define grid
[kgrid] = kWaveGrid(Nx, dx, Ny, dy);

% 2. Medium properties
c0 = 1500;          % Speed of sound in the medium (m/s)
rho0 = 1000;        % Density of the medium (kg/m^3)

% 3. Define the transducer element (3mm x 3mm square)
element_size = 3e-3;  % Element size in meters
f0 = 500e3;           % Frequency (500 kHz)

% Create a source
source_mask = zeros(Nx, Ny);  % Initialize the source mask
x_start = round(Nx / 2 - element_size / 2 / dx);  % x-coordinate of the source
y_start = round(Ny / 2 - element_size / 2 / dy);  % y-coordinate of the source
source_mask(x_start:x_start+element_size/dx, y_start:y_start+element_size/dy) = 1;  % Define source region

% 4. Time-stepping parameters
dt = 1 / (2 * c0 * sqrt(1/dx^2 + 1/dy^2));  % Time step from CFL condition
t_max = 2e-6;    % Maximum simulation time (2 microseconds)
num_steps = round(t_max / dt);  % Total number of time steps

% 5. Define the source signal (sinusoidal continuous wave)
t = (0:num_steps-1) * dt;  % Time vector
source_signal = sin(2 * pi * f0 * t);  % Sinusoidal signal

% Ensure source signal has the same length as number of time steps
if length(source_signal) ~= num_steps
    source_signal = repmat(source_signal, ceil(num_steps / length(source_signal)), 1);
    source_signal = source_signal(1:num_steps); % Truncate to match num_steps
end

% 6. Set up the medium
medium.sound_speed = c0 * ones(Nx, Ny);  % Uniform sound speed
medium.density = rho0 * ones(Nx, Ny);    % Uniform density

% 7. Define the sensor (optional, if you want to record the field)
sensor_mask = zeros(Nx, Ny);
sensor_mask(round(Nx/2), round(Ny/2)) = 1;  % Place sensor at the center

% 8. Initialize the k-Wave input struct
input_args = struct;
input_args.source = source_signal;  % Source signal
input_args.source_mask = source_mask;  % Define source location
input_args.sensor_mask = sensor_mask;  % Define sensor location
input_args.medium = medium;  % Define medium properties
input_args.dt = dt;  % Time step
input_args.t_max = t_max;  % Maximum simulation time

% 9. Run the k-Wave simulation (pressure field calculation)
[~, pressure_field] = kspaceFirstOrder2D(kgrid, input_args);

% 10. Plot the pressure field at the final time step
imagesc(pressure_field(:,:,end));  % Plot the pressure field
colorbar;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Pressure Field from 3mm x 3mm Ultrasound Element (500 kHz CW)');
axis equal;