E = [0	9.17515	-1.21377	74.42677;
    1	5.26375	4.23032	74.69536;
    2	-1.85063	9.04152	74.43001;
    3	-7.23702	4.90787	74.48851;
    4	-7.62342	-2.18735	74.57948;
    5	-1.95725	-7.10118	74.63741;
    6	4.76023	-7.70600	74.45104;
    7	13.08164	6.80640	73.53600;
    8	8.01564	10.91706	73.76698;
    9	2.60681	15.24449	73.38808;
    10	-4.68014	16.31505	73.05420;
    11	-11.58872	11.39990	73.21710;
    12	-14.86089	5.29644	73.32191;
    13	-14.84342	-1.80009	73.49444;
    14	-12.53593	-8.90762	73.40644;
    15	-7.32586	-13.16293	73.47155;
    16	-0.14240	-13.32441	73.80677;
    17	7.73756	-14.55463	73.16620;
    18	12.58558	-9.88368	73.27289;
    19	15.95832	0.68605	73.27934;
    20	17.92911	13.47085	71.56873;
    21	11.75231	16.83122	72.13594;
    22	3.84088	22.90145	71.31459;
    23	-4.12984	22.59961	71.39469;
    24	-10.47700	20.46218	71.39000;
    25	-15.92944	16.13195	71.49135;
    26	-19.80051	10.87503	71.51694;
    27	-22.73930	2.71980	71.41797;
    28	-21.80103	-4.30071	71.63253;
    29	-19.44443	-11.48693	71.51898;
    30	-13.99896	-16.51187	71.80799;
    31	-6.84666	-21.74075	71.45252;
    32	-0.12947	-20.54725	72.13039;
    33	6.51767	-20.77167	71.77087;
    34	14.01201	-18.58884	71.29599;
    35	19.19171	-12.55351	71.40790;
    36	19.52075	-4.69973	72.26239;
    37	23.42927	0.81393	71.24189;
    38	19.70357	6.58249	72.06553;
    39	17.03237	24.04124	68.97041;
    40	10.45518	22.99776	70.61722;
    41	6.07532	28.57415	69.07683;
    42	-0.82419	29.71787	68.85615;
    43	-7.65115	28.38821	68.99688;
    44	-14.04628	25.92932	68.95921;
    45	-21.14059	20.68947	68.92040;
    46	-25.09007	13.95747	69.28692;
    47	-28.37858	7.13690	69.05593;
    48	-29.60455	0.59725	68.90729;
    49	-28.53804	-6.67439	69.03646;
    50	-25.79249	-12.68695	69.27329;
    51	-21.00198	-18.01283	69.70979;
    52	-17.17656	-23.86754	68.99497;
    53	-9.83676	-27.78130	68.96693;
    54	-1.41906	-28.84864	69.21519;
    55	4.91766	-26.81970	69.86788;
    56	12.80928	-26.01380	69.16795;
    57	20.33577	-20.13263	69.32628;
    58	25.82754	-13.86885	69.03327;
    59	26.00345	-6.44410	70.05208;
    60	29.84153	-1.19154	68.79726;
    61	28.54528	5.22615	69.15818;
    62	24.01640	11.44174	70.12346;
    63	21.73907	18.72244	69.29562;
    ];


figure; scatter(E(:,2),E(:,3),E(:,4)); axis square; grid minor

%%

clc; clear; close all;

% Define circle parameters
R = 35; % Radius in mm
N = 32; % Number of points

% Generate points using a Poisson Disk Sampling approach for equal spacing
theta = linspace(0, 2*pi, N+1); % Equal angular spacing
theta(end) = []; % Remove duplicate point at 2π
r = sqrt(rand(1, N)) * R; % Random radial positions with equal distribution

% Convert polar coordinates to Cartesian
x = r .* cos(theta);
y = r .* sin(theta);

% Plot the circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--'); % Draw circle boundary

% Plot the points
scatter(x, y, 'ro', 'filled');
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Randomly Distributed Points in a Circle');
grid on;
hold off;

%%
clc; clear; close all;

% Define circle parameters
R = 35;  % Circle radius in mm
N = 64;  % Number of points
minDist = R / sqrt(N); % Approximate minimum spacing

% Initialize point list
points = zeros(N, 2);
count = 0;
maxAttempts = 1000; % Limit for attempts to find a valid point

while count < N
    % Generate a random point in polar coordinates
    r = R * sqrt(rand); % Square root ensures uniform area distribution
    theta = 2 * pi * rand;
    x = r * cos(theta);
    y = r * sin(theta);
    
    % Check distance constraints
    if count == 0 || all(vecnorm(points(1:count, :) - [x, y], 2, 2) > minDist)
        count = count + 1;
        points(count, :) = [x, y];
    end
    
    % Safety break if stuck
    if count < N && count > 10 && maxAttempts < 0
        warning('Could not find enough points with minimum spacing. Try reducing minDist.');
        break;
    end
end

% Plot the results
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--'); % Draw circle boundary
scatter(points(:,1), points(:,2), 'ro', 'filled'); % Draw points
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Randomly Distributed Points with Equal Spacing in a Circle');
grid on;
hold off;

%%
clc; clear; close all;

% Define circle parameters
R = 75;  % Circle radius in mm
N = 64;  % Number of points
minDist = R / sqrt(N) * 1.5; % Increase minimum spacing for sparser distribution

% Initialize point list
points = zeros(N, 2);
count = 0;
maxAttempts = 10000; % Limit for attempts to find a valid point

while count < N
    % Generate a random point in polar coordinates
    r = R * sqrt(rand); % Square root ensures uniform area distribution
    theta = 2 * pi * rand;
    x = r * cos(theta);
    y = r * sin(theta);
    
    % Check distance constraints
    if count == 0 || all(vecnorm(points(1:count, :) - [x, y], 2, 2) > minDist)
        count = count + 1;
        points(count, :) = [x, y];
    end
    
    % Safety break if stuck
    maxAttempts = maxAttempts - 1;
    if count < N && maxAttempts <= 0
        warning('Could not find enough points with given minimum spacing. Try reducing minDist.');
        break;
    end
end

% Plot the results
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--'); % Draw circle boundary
scatter(points(:,1), points(:,2), 'ro', 'filled'); % Draw points
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Sparse Distribution of Points in a Circle');
grid on;
hold off;


%%
clc; clear; close all;

% Large circle parameters
R = 35; % Outer circle radius (mm)
N = 32; % Total number of smaller circles
r_small = 3; % Radius of smaller circles

% Define the number of rings and points per ring (approximate distribution)
rings = 5; % Number of concentric rings
points_per_ring = round(linspace(6, 20, rings)); % More points in outer rings

% Initialize storage for circle centers
circle_centers = [0, 0]; % Start with center (first small circle)

% Generate concentric rings
for i = 1:rings
    ring_radius = (i / rings) * (R - r_small); % Define radius for current ring
    theta = linspace(0, 2*pi, points_per_ring(i) + 1); % Evenly spaced angles
    theta(end) = []; % Remove duplicate last point
    
    % Convert to Cartesian coordinates
    x = ring_radius * cos(theta);
    y = ring_radius * sin(theta);
    
    % Store points
    circle_centers = [circle_centers; [x(:), y(:)]];
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Symmetrically Distributed Smaller Circles in a Larger Circle');
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small = 2.5; % Radius of smaller circles
perturbation = 1.5; % Maximum perturbation amount (mm)

% Define number of rings and points per ring
rings = 5; % Number of concentric rings
points_per_ring = round(linspace(6, 20, rings)); % More points in outer rings

% Initialize storage for circle centers
circle_centers = [0, 0]; % Start with center circle

% Generate concentric rings
for i = 1:rings
    ring_radius = (i / rings) * (R - r_small); % Define radius for current ring
    theta = linspace(0, 2*pi, points_per_ring(i) + 1); % Evenly spaced angles
    theta(end) = []; % Remove duplicate last point
    
    % Convert to Cartesian coordinates with small random perturbation
    x = ring_radius * cos(theta) + (rand(size(theta)) - 0.5) * perturbation;
    y = ring_radius * sin(theta) + (rand(size(theta)) - 0.5) * perturbation;
    
    % Store points
    circle_centers = [circle_centers; [x(:), y(:)]];
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles with perturbation
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Perturbed Circular Symmetric Points in a Larger Circle');
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small = 1; % Radius of smaller circles
perturbation = 2; % Maximum perturbation amount (mm)

% Define number of rings and points per ring
rings = 5; % Number of concentric rings
points_per_ring = round(linspace(6, 20, rings)); % More points in outer rings

% Initialize storage for circle centers (no center element)
circle_centers = [];

% Generate concentric rings
for i = 1:rings
    ring_radius = (i / rings) * (R - r_small); % Define radius for current ring
    theta = linspace(0, 2*pi, points_per_ring(i) + 1); % Evenly spaced angles
    theta(end) = []; % Remove duplicate last point
    
    % Convert to Cartesian coordinates with small random perturbation
    x = ring_radius * cos(theta) + (rand(size(theta)) - 0.5) * perturbation;
    y = ring_radius * sin(theta) + (rand(size(theta)) - 0.5) * perturbation;
    
    % Store points
    circle_centers = [circle_centers; [x(:), y(:)]];
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles (excluding the center)
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Perturbed Circular Symmetric Points (No Center)');
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small = 2.5; % Radius of each smaller circle
minDist = 0.5 * r_small; % Minimum spacing between circles

% Initialize point storage
circle_centers = [];

% Generate random non-overlapping points
attempts = 10000; % Safety limit to prevent infinite loops
while size(circle_centers, 1) < N && attempts > 0
    % Generate a random point inside the circle
    r = R * sqrt(rand); % Uniform area distribution
    theta = 2 * pi * rand; % Random angle
    x = r * cos(theta);
    y = r * sin(theta);
    
    % Check that the new point is not too close to existing points
    if isempty(circle_centers) || all(vecnorm(circle_centers - [x, y], 2, 2) > minDist)
        circle_centers = [circle_centers; x, y]; % Store valid point
    end
    
    attempts = attempts - 1;
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Completely Random Non-Symmetric Circles');
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small = 3; % Radius of each smaller circle
minDist = 2.2 * r_small; % Minimum spacing between circles

% Initialize point storage
circle_centers = zeros(N, 2);
count = 0;
maxAttempts = 100000; % Prevent infinite loops

while count < N && maxAttempts > 0
    % Generate a random point inside the circle
    r = R * sqrt(rand); % Uniform area distribution
    theta = 2 * pi * rand; % Random angle
    x = r * cos(theta);
    y = r * sin(theta);
    
    % Check that the new point is not too close to existing points
    if count == 0 || all(vecnorm(circle_centers(1:count, :) - [x, y], 2, 2) > minDist)
        count = count + 1;
        circle_centers(count, :) = [x, y]; % Store valid point
    end
    
    maxAttempts = maxAttempts - 1;
end

if count < N
    warning('Could not place all %d circles without overlap. Try reducing minDist.', N);
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles
for i = 1:N
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Random Non-Symmetric Placement of %d Circles', N));
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small = 2.6; % Radius of each smaller circle
minDist = 1.9 * r_small; % Minimum spacing between circles

% Initialize point storage
circle_centers = zeros(N, 2);
count = 0;
maxAttempts = 100000; % Prevent infinite loops

while count < N && maxAttempts > 0
    % Generate a random point inside the circle (avoid center)
    r = R * sqrt(rand); % Uniform area distribution
    theta = 2 * pi * rand; % Random angle
    
    % Skip if point is too close to the center (avoid placing at (0,0))
    if r < r_small
        continue;
    end
    
    x = r * cos(theta);
    y = r * sin(theta);
    
    % Check that the new point is not too close to existing points
    if count == 0 || all(vecnorm(circle_centers(1:count, :) - [x, y], 2, 2) > minDist)
        count = count + 1;
        circle_centers(count, :) = [x, y]; % Store valid point
    end
    
    maxAttempts = maxAttempts - 1;
end

if count < N
    warning('Could not place all %d circles without overlap. Try reducing minDist.', N);
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles
for i = 1:N
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Random Non-Symmetric Placement of %d Circles (No Center)', N));
grid on;
hold off;

%%

clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small = 2.5; % Radius of each smaller circle
minDist = 2.2 * r_small; % Minimum spacing between circles
perturbation = 0.5; % Small perturbation for randomness

% Create a grid of points evenly distributed inside the circle
nGrid = round(sqrt(N)); % Number of grid points in each direction
thetaGrid = linspace(0, 2*pi, nGrid + 1); % Angular grid
thetaGrid(end) = []; % Remove the last value to avoid overlap

% Initialize point storage
circle_centers = [];

% Generate evenly distributed points
for rIdx = 1:nGrid
    for thetaIdx = 1:nGrid
        % Radial distance for current point
        r = (rIdx / nGrid) * (R - r_small); % Distribute radius evenly

        % Angular position for current point
        theta = (thetaIdx / nGrid) * 2 * pi; 

        % Calculate x, y coordinates
        x = r * cos(theta);
        y = r * sin(theta);

        % Apply small random perturbation
        x = x + (rand - 0.5) * perturbation;
        y = y + (rand - 0.5) * perturbation;
        
        % Only add points that are inside the circle and not near the center
        if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
            circle_centers = [circle_centers; x, y];
        end
    end
end

% Ensure exactly N points are generated
circle_centers = circle_centers(1:N, :);

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles
for i = 1:N
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Evenly Distributed Circles with Random Perturbation (%d Points)', N));
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small = 2.5; % Radius of each smaller circle
minDist = 2.2 * r_small; % Minimum spacing between circles
maxAttempts = 100000; % Prevent infinite loops
perturbation = 0.5; % Small perturbation for randomness

% Initialize point storage
circle_centers = [];
attempts = 0;

% Generate points with no overlap
while size(circle_centers, 1) < N && attempts < maxAttempts
    % Generate a random point inside the circle
    r = R * sqrt(rand); % Uniform area distribution
    theta = 2 * pi * rand; % Random angle
    x = r * cos(theta);
    y = r * sin(theta);
    
    % Apply small random perturbation to each point
    x = x + (rand - 0.5) * perturbation;
    y = y + (rand - 0.5) * perturbation;
    
    % Ensure the point is within the outer circle and not near the center
    if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
        % Check if the new point overlaps with existing points
        if all(vecnorm(circle_centers - [x, y], 2, 2) > minDist)
            % Add point if no overlap
            circle_centers = [circle_centers; x, y];
        end
    end
    
    attempts = attempts + 1;
end

% Check if the desired number of points is placed
if size(circle_centers, 1) < N
    warning('Could not place all %d circles without overlap. Try adjusting parameters.', N);
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Random Perturbation (%d Points)', N));
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 32; % Total number of smaller circles
r_small = 5; % Radius of each smaller circle
minDist = 2.2 * r_small; % Minimum spacing between circles
maxAttempts = 100000; % Prevent infinite loops
perturbation = 0.5; % Small perturbation for randomness

% Initialize point storage
circle_centers = [];
attempts = 0;

% Generate points with no overlap
while size(circle_centers, 1) < N && attempts < maxAttempts
    % Generate a random point inside the circle
    r = R * sqrt(rand); % Uniform area distribution
    theta = 2 * pi * rand; % Random angle
    x = r * cos(theta);
    y = r * sin(theta);
    
    % Apply small random perturbation to each point
    x = x + (rand - 0.5) * perturbation;
    y = y + (rand - 0.5) * perturbation;
    
    % Ensure the point is within the outer circle and not near the center
    if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
        % If no points have been placed yet, add the first point
        if isempty(circle_centers)
            circle_centers = [x, y];
        else
            % Check if the new point overlaps with existing points
            if all(vecnorm(circle_centers - [x, y], 2, 2) > minDist)
                % Add point if no overlap
                circle_centers = [circle_centers; x, y];
            end
        end
    end
    
    attempts = attempts + 1;
end

% Check if the desired number of points is placed
if size(circle_centers, 1) < N
    warning('Could not place all %d circles without overlap. Try adjusting parameters.', N);
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Random Perturbation (%d Points)', N));
grid on;
hold off;

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small_initial = 2; % Initial radius of each smaller circle (start small)
minDist = 2.2 * r_small_initial; % Minimum spacing between circles
maxAttempts = 100000; % Prevent infinite loops
perturbation = 0.5; % Small perturbation for randomness

% Initialize point storage
circle_centers = [];
attempts = 0;
r_small = r_small_initial; % Start with small circles

% Loop to increase circle radius until overlap occurs
while true
    circle_centers = []; % Reset circle positions
    attempts = 0; % Reset attempts

    % Generate points with no overlap for the current radius
    while size(circle_centers, 1) < N && attempts < maxAttempts
        % Generate a random point inside the circle
        r = R * sqrt(rand); % Uniform area distribution
        theta = 2 * pi * rand; % Random angle
        x = r * cos(theta);
        y = r * sin(theta);
        
        % Apply small random perturbation to each point
        x = x + (rand - 0.5) * perturbation;
        y = y + (rand - 0.5) * perturbation;
        
        % Ensure the point is within the outer circle and not near the center
        if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
            % If no points have been placed yet, add the first point
            if isempty(circle_centers)
                circle_centers = [x, y];
            else
                % Check if the new point overlaps with existing points
                if all(vecnorm(circle_centers - [x, y], 2, 2) > minDist)
                    % Add point if no overlap
                    circle_centers = [circle_centers; x, y];
                end
            end
        end
        
        attempts = attempts + 1;
    end

    % If we've successfully placed N points without overlap
    if size(circle_centers, 1) == N
        % Store the radius if no overlap detected
        r_small_max = r_small;
        % Increase the radius for the next iteration
        r_small = r_small + 0.2; % Increase radius slightly
    else
        % Break the loop when overlap occurs
        break;
    end
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles with the maximum non-overlapping radius
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small_max, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Maximum Radius (%d Points)', N));
grid on;
hold off;

% Display maximum radius
disp(['Maximum radius for ' num2str(N) ' points without overlap: ', num2str(r_small_max), ' mm']);

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small_initial = 1; % Initial radius of each smaller circle (start small)
minDist = 2.2 * r_small_initial; % Minimum spacing between circles
maxAttempts = 100000; % Prevent infinite loops
perturbation = 0.5; % Small perturbation for randomness

% Initialize point storage
circle_centers = [];
attempts = 0;
r_small = r_small_initial; % Start with small circles

% Loop to increase circle radius until overlap occurs
while true
    circle_centers = []; % Reset circle positions
    attempts = 0; % Reset attempts

    % Generate points with no overlap for the current radius
    while size(circle_centers, 1) < N && attempts < maxAttempts
        % Generate a random point inside the circle
        r = R * sqrt(rand); % Uniform area distribution
        theta = 2 * pi * rand; % Random angle
        x = r * cos(theta);
        y = r * sin(theta);
        
        % Apply small random perturbation to each point
        x = x + (rand - 0.5) * perturbation;
        y = y + (rand - 0.5) * perturbation;
        
        % Ensure the point is within the outer circle and not near the center
        if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
            % If no points have been placed yet, add the first point
            if isempty(circle_centers)
                circle_centers = [x, y];
            else
                % Check if the new point overlaps with existing points
                if all(vecnorm(circle_centers - [x, y], 2, 2) > minDist)
                    % Add point if no overlap
                    circle_centers = [circle_centers; x, y];
                end
            end
        end
        
        attempts = attempts + 1;
    end

    % If we've successfully placed N points without overlap
    if size(circle_centers, 1) == N
        % Store the radius if no overlap detected
        r_small_max = r_small;
        % Increase the radius for the next iteration
        r_small = r_small + 0.2; % Increase radius slightly
    else
        % Break the loop when overlap occurs
        break;
    end
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles with the maximum non-overlapping radius
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small_max, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Maximum Radius (%d Points)', N));
grid on;
hold off;

% Display maximum radius
disp(['Maximum radius for ' num2str(N) ' points without overlap: ', num2str(r_small_max), ' mm']);


%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 32; % Total number of smaller circles
r_small_initial = 1; % Initial radius of each smaller circle (start small)
maxAttempts = 100000; % Prevent infinite loops
perturbation = 5; % Small perturbation for randomness

% Initialize point storage
circle_centers = [];
attempts = 0;
r_small = r_small_initial; % Start with small circles

% % Function to check for overlap
% function isOverlap = checkOverlap(centers, r)
%     % Check all pairs of circles for overlap
%     n = size(centers, 1);
%     isOverlap = false;
%     for i = 1:n-1
%         for j = i+1:n
%             if norm(centers(i, :) - centers(j, :)) < 2 * r
%                 isOverlap = true;
%                 return;
%             end
%         end
%     end
% end

% Loop to increase circle radius until overlap occurs
while true
    circle_centers = []; % Reset circle positions
    attempts = 0; % Reset attempts

    % Generate points with no overlap for the current radius
    while size(circle_centers, 1) < N && attempts < maxAttempts
        % Generate a random point inside the circle
        r = R * sqrt(rand); % Uniform area distribution
        theta = 2 * pi * rand; % Random angle
        x = r * cos(theta);
        y = r * sin(theta);
        
        % Apply small random perturbation to each point
        x = x + (rand - 0.5) * perturbation;
        y = y + (rand - 0.5) * perturbation;
        
        % Ensure the point is within the outer circle and not near the center
        if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
            % If no points have been placed yet, add the first point
            if isempty(circle_centers)
                circle_centers = [x, y];
            else
                % Check if the new point overlaps with existing points
                if all(vecnorm(circle_centers - [x, y], 2, 2) > 2 * r_small)
                    % Add point if no overlap
                    circle_centers = [circle_centers; x, y];
                end
            end
        end
        
        attempts = attempts + 1;
    end
    
    % Check for overlap with the current radius
    if size(circle_centers, 1) == N && ~checkOverlap(circle_centers, r_small)
        % Store the radius if no overlap detected
        r_small_max = r_small;
        % Increase the radius for the next iteration
        r_small = r_small + 0.2; % Increase radius slightly
    else
        % Break the loop when overlap occurs
        break;
    end
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles with the maximum non-overlapping radius
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small_max, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Maximum Radius (%d Points)', N));
grid on;
hold off;

% Display maximum radius
disp(['Maximum radius for ' num2str(N) ' points without overlap: ', num2str(r_small_max), ' mm']);

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small_initial = 1; % Initial radius of each smaller circle (start small)
maxAttempts = 100000; % Prevent infinite loops
perturbationFactor = 2; % Larger perturbation for more visible randomness

% Initialize point storage
circle_centers = [];
attempts = 0;
r_small = r_small_initial; % Start with small circles

% % Function to check for overlap
% function isOverlap = checkOverlap(centers, r)
%     % Check all pairs of circles for overlap
%     n = size(centers, 1);
%     isOverlap = false;
%     for i = 1:n-1
%         for j = i+1:n
%             if norm(centers(i, :) - centers(j, :)) < 2 * r
%                 isOverlap = true;
%                 return;
%             end
%         end
%     end
% end

% Loop to increase circle radius until overlap occurs
while true
    circle_centers = []; % Reset circle positions
    attempts = 0; % Reset attempts

    % Generate points with no overlap for the current radius
    while size(circle_centers, 1) < N && attempts < maxAttempts
        % Generate a random point inside the circle
        r = R * sqrt(rand); % Uniform area distribution
        theta = 2 * pi * rand; % Random angle
        x = r * cos(theta);
        y = r * sin(theta);
        
        % Apply noticeable random perturbation to each point
        x = x + (rand - 0.5) * perturbationFactor; % Larger perturbation
        y = y + (rand - 0.5) * perturbationFactor; % Larger perturbation
        
        % Ensure the point is within the outer circle and not near the center
        if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
            % If no points have been placed yet, add the first point
            if isempty(circle_centers)
                circle_centers = [x, y];
            else
                % Check if the new point overlaps with existing points
                if all(vecnorm(circle_centers - [x, y], 2, 2) > 2 * r_small)
                    % Add point if no overlap
                    circle_centers = [circle_centers; x, y];
                end
            end
        end
        
        attempts = attempts + 1;
    end
    
    % Check for overlap with the current radius
    if size(circle_centers, 1) == N && ~checkOverlap(circle_centers, r_small)
        % Store the radius if no overlap detected
        r_small_max = r_small;
        % Increase the radius for the next iteration
        r_small = r_small + 0.2; % Increase radius slightly
    else
        % Break the loop when overlap occurs
        break;
    end
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles with the maximum non-overlapping radius
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small_max, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Maximum Radius (%d Points)', N));
grid on;
hold off;

% Display maximum radius
disp(['Maximum radius for ' num2str(N) ' points without overlap: ', num2str(r_small_max), ' mm']);

%%
clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 32; % Total number of smaller circles
r_small_initial = 0.5; % Initial radius of each smaller circle (start small)
maxAttempts = 300000; % Prevent infinite loops
perturbationFactor = 0; % Larger perturbation for more visible randomness

% Initialize point storage
circle_centers = [];
attempts = 0;
r_small = r_small_initial; % Start with small circles

% Loop to increase circle radius until overlap occurs
while true
    circle_centers = []; % Reset circle positions
    attempts = 0; % Reset attempts

    % Generate points with no overlap for the current radius
    while size(circle_centers, 1) < N && attempts < maxAttempts
        % Generate a random point inside the circle
        r = R * sqrt(rand); % Uniform area distribution
        theta = 2 * pi * rand; % Random angle
        x = r * cos(theta);
        y = r * sin(theta);
        
        % Apply noticeable random perturbation to each point
        x = x + (rand - 0.5) * perturbationFactor; % Larger perturbation
        y = y + (rand - 0.5) * perturbationFactor; % Larger perturbation
        
        % Ensure the point is within the outer circle and not near the center
        if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
            % If no points have been placed yet, add the first point
            if isempty(circle_centers)
                circle_centers = [x, y];
            else
                % Check if the new point overlaps with existing points
                if all(vecnorm(circle_centers - [x, y], 2, 2) > 2 * r_small)
                    % Add point if no overlap
                    circle_centers = [circle_centers; x, y];
                end
            end
        end
        
        attempts = attempts + 1;
    end
    
    % Check for overlap with the current radius
    if size(circle_centers, 1) == N && ~checkOverlap(circle_centers, r_small)
        % Store the radius if no overlap detected
        r_small_max = r_small;
        % Increase the radius for the next iteration
        r_small = r_small + 0.2; % Increase radius slightly
    else
        % Break the loop when overlap occurs
        break;
    end
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles with the maximum non-overlapping radius
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small_max, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Maximum Radius (%d Points)', N));
grid on;
hold off;

% Display maximum radius
disp(['Maximum radius for ' num2str(N) ' points without overlap: ', num2str(r_small_max), ' mm']);

% % Function to check for overlap
% function isOverlap = checkOverlap(centers, r)
%     % Check all pairs of circles for overlap
%     n = size(centers, 1);
%     isOverlap = false;
%     for i = 1:n-1
%         for j = i+1:n
%             if norm(centers(i, :) - centers(j, :)) < 2 * r
%                 isOverlap = true;
%                 return;
%             end
%         end
%     end
% end

%%


clc; clear; close all;

% Large outer circle parameters
R = 30; % Outer circle radius (mm)
N = 64; % Total number of smaller circles
r_small_initial = 1; % Initial radius of each smaller circle (start small)
maxAttempts = 700000; % Prevent infinite loops
perturbationFactor = 0; % Reduced perturbation for more controlled randomness

% Initialize point storage
circle_centers = [];
attempts = 0;
r_small = r_small_initial; % Start with small circles

% Function to check for overlap
function isOverlap = checkOverlap(centers, r)
    % Check all pairs of circles for overlap
    n = size(centers, 1);
    isOverlap = false;
    for i = 1:n-1
        for j = i+1:n
            if norm(centers(i, :) - centers(j, :)) < 2 * r
                isOverlap = true;
                return;
            end
        end
    end
end

% Loop to increase circle radius until overlap occurs
while true
    circle_centers = []; % Reset circle positions
    attempts = 0; % Reset attempts

    % Generate points with no overlap for the current radius
    while size(circle_centers, 1) < N && attempts < maxAttempts
        % Generate a random point inside the circle
        r = R * sqrt(rand); % Uniform area distribution
        theta = 2 * pi * rand; % Random angle
        x = r * cos(theta);
        y = r * sin(theta);
        
        % Apply smaller random perturbation to each point
        x = x + (rand - 0.5) * perturbationFactor; % Smaller perturbation
        y = y + (rand - 0.5) * perturbationFactor; % Smaller perturbation
        
        % Ensure the point is within the outer circle and not near the center
        if sqrt(x^2 + y^2) < R && sqrt(x^2 + y^2) > r_small
            % If no points have been placed yet, add the first point
            if isempty(circle_centers)
                circle_centers = [x, y];
            else
                % Check if the new point overlaps with existing points
                if all(vecnorm(circle_centers - [x, y], 2, 2) > 2 * r_small)
                    % Add point if no overlap
                    circle_centers = [circle_centers; x, y];
                end
            end
        end
        
        attempts = attempts + 1;
    end
    
    % Check for overlap with the current radius
    if size(circle_centers, 1) == N && ~checkOverlap(circle_centers, r_small)
        % Store the radius if no overlap detected
        r_small_max = r_small;
        % Increase the radius for the next iteration
        r_small = r_small + 0.2; % Increase radius slightly
    else
        % Break the loop when overlap occurs
        break;
    end
end

% Plot the large outer circle
figure;
hold on;
viscircles([0, 0], R, 'LineStyle', '--', 'Color', 'b'); % Outer boundary

% Plot the smaller circles with the maximum non-overlapping radius
for i = 1:size(circle_centers, 1)
    viscircles(circle_centers(i, :), r_small_max, 'EdgeColor', 'r'); % Smaller circles
end

% Formatting
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title(sprintf('Non-Overlapping Circles with Maximum Radius (%d Points)', N));
grid on;
hold off;

% Display maximum radius
disp(['Maximum radius for ' num2str(N) ' points without overlap: ', num2str(r_small_max), ' mm']);


%%
% Parameters
R = 30; % Radius of the circle
n_points = 64; % Number of points

% Create a vector of angles from 0 to 2*pi, divided into n_points intervals
angles = linspace(0, 2*pi, n_points+1); % +1 to close the circle

% Convert polar coordinates to Cartesian coordinates
x = R * cos(angles); % x-coordinates
y = R * sin(angles); % y-coordinates

% Plot the points on the circular surface
figure;
scatter(x, y, 'filled');
axis equal; % To ensure the aspect ratio is equal
title('64 Points Evenly Distributed on a Circular Surface');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the circle
n_points = 64; % Number of points

% Create a vector of angles from 0 to 2*pi, divided into n_points intervals
angles = linspace(0, 2*pi, n_points+1); % +1 to close the circle

% Convert polar coordinates to Cartesian coordinates
x = R * cos(angles); % x-coordinates
y = R * sin(angles); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta);
y_surface = R * sin(theta);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the 64 points on the surface
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points on the Surface of a Circle');
xlabel('X-axis');
ylabel('Y-axis');
grid on;


%%

% Parameters
R = 30; % Radius of the circle
n_points = 64; % Number of points

% Generate random points within the circle
theta = 2*pi * rand(1, n_points); % Random angles between 0 and 2*pi
r = R * sqrt(rand(1, n_points)); % Random radial distances (scaled by sqrt to ensure uniform distribution)

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the 64 points on the surface
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points Distributed Over the Inner Surface of a Circle');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the circle
n_points = 64; % Number of points

% Calculate the number of points per radial ring
n_rings = floor(sqrt(n_points)); % Number of radial rings to divide the surface into
points_per_ring = ceil(n_points / n_rings); % Number of points per ring

% Generate the evenly distributed points
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Loop through each radial ring
for i = 1:n_rings
    radius = R * (i / n_rings); % Radial distance for the current ring
    angles = linspace(0, 2*pi, points_per_ring + 1); % Angles for this ring
    angles(end) = []; % Remove the last duplicate angle to avoid overlap
    
    % Append the points for this ring
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the evenly distributed points on the surface
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Evenly Distributed Points Over the Inner Surface of a Circle');
xlabel('X-axis');
ylabel('Y-axis');
grid on;


%%
% Parameters
R = 30; % Radius of the circle
n_points = 64; % Number of points

% Define the number of concentric rings and angular sections
n_rings = ceil(sqrt(n_points)); % Number of rings
n_points_per_ring = ceil(n_points / n_rings); % Points per ring

% Generate points
theta = []; % Store angles
r = []; % Store radial distances

% Loop through each ring
for i = 1:n_rings
    % Radial distance for the current ring
    radius = R * (i / n_rings); 
    % Define angle step size (angular distribution)
    angles = linspace(0, 2*pi, n_points_per_ring + 1); % Angles for this ring
    angles(end) = []; % Remove the last duplicate angle
    
    % Append the points for this ring
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the sparsely distributed points on the surface
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Sparse Points Distributed Over the Inner Surface of a Circle');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the circle
n_points = 64; % Number of points

% Generate random angles and radial distances
theta = 2 * pi * rand(1, n_points); % Random angles between 0 and 2*pi
r = R * sqrt(rand(1, n_points)); % Random radial distances, sqrt to ensure uniform distribution

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the randomly distributed points on the surface
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Randomly Distributed Points Over the Inner Surface of a Circle');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Number of points
n_circles = 4; % Number of concentric circles

% Points per circle
points_per_circle = n_points / n_circles; 

% Generate the circles and distribute points
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Loop through each circle
for i = 1:n_circles
    radius = R * (i / n_circles); % Radial distance for the current circle
    angles = linspace(0, 2*pi, points_per_circle + 1); % Angles for this circle
    angles(end) = []; % Remove the last duplicate angle
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the 64 points over the 4 concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points Evenly Distributed Over 4 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Number of points
n_circles = 4; % Number of concentric circles

% Points per circle
points_per_circle = n_points / n_circles;

% Generate the circles and distribute points
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Loop through each circle
for i = 1:n_circles
    radius = R * (i / n_circles); % Radial distance for the current circle
    angles = linspace(0, 2*pi, points_per_circle + 1); % Angles for this circle
    angles(end) = []; % Remove the last duplicate angle to avoid overlap
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the 64 points over the 4 concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Distance Over 4 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;


%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Total number of points
n_circles = 4; % Number of concentric circles

% Points per circle
points_per_circle = n_points / n_circles; 

% Generate the circles and distribute points
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Loop through each circle
for i = 1:n_circles
    radius = R * (i / n_circles); % Radial distance for the current circle
    angle_between_points = 2 * pi / points_per_circle; % Equal angular separation
    
    % Generate the angles for this circle
    angles = (0:points_per_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the evenly distributed points over the 4 concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Distance Over 4 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Total number of points
n_circles = 5; % Number of concentric circles

% Calculate the arc length between points for the outermost circle
arc_length = 2 * pi * R / n_points; % Arc length for each point (constant across circles)

% Number of points per circle will be calculated based on arc_length
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Loop through each circle
for i = 1:n_circles
    radius = R * (i / n_circles); % Radial distance for the current circle
    points_per_circle = round(2 * pi * radius / arc_length); % Calculate points based on arc length

    % Angle between points for this circle
    angle_between_points = 2 * pi / points_per_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_per_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the evenly distributed points over the 4 concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Length Distance Over 4 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Total number of points
n_circles = 5; % Number of concentric circles

% Calculate the arc length between points for the outermost circle
arc_length = 2 * pi * R / n_points; % Arc length for each point (constant across circles)

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Calculate total points based on arc length for each circle
points_so_far = 0; % Keep track of the total points
total_points = n_points;

% Loop through each circle and distribute points
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = R * (i / n_circles); 

    % Calculate the number of points for this circle based on arc length
    points_on_this_circle = round(2 * pi * radius / arc_length); 

    % Adjust the number of points on each circle to ensure total points equals 64
    remaining_points = total_points - points_so_far;
    if i == n_circles
        points_on_this_circle = remaining_points; % Last circle takes remaining points
    end
    points_so_far = points_so_far + points_on_this_circle;

    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the evenly distributed points over the concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Length Distance Over 5 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Total number of points
n_circles = 5; % Number of concentric circles

% Calculate the arc length between points for the outermost circle
arc_length = 2 * pi * R / n_points; % Arc length for each point (constant across circles)

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Calculate total points based on arc length for each circle
points_so_far = 0; % Keep track of the total points
total_points = n_points;

% Loop through each circle and distribute points
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = R * (i / n_circles); 

    % Calculate the number of points for this circle based on arc length
    points_on_this_circle = round(2 * pi * radius / arc_length); 

    % Adjust the number of points on each circle to ensure total points equals 64
    remaining_points = total_points - points_so_far;
    if i == n_circles
        points_on_this_circle = remaining_points; % Last circle takes remaining points
    end
    points_so_far = points_so_far + points_on_this_circle;

    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
    
    % Display the number of points for the current circle
    fprintf('Circle %d: %d points\n', i, points_on_this_circle);
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the evenly distributed points over the concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Length Distance Over 5 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Total number of points
n_circles = 5; % Number of concentric circles

% Calculate the overall arc length for the outermost circle (based on total points)
arc_length = 2 * pi * R / n_points; % Constant arc length between points across all circles

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Calculate points distribution across circles
points_so_far = 0; % Keep track of the total points
total_points = n_points;
points_per_circle = zeros(1, n_circles); % Store points per circle

% Loop through each circle and distribute points to keep arc length equal
for i = 1:n_circles
    radius = R * (i / n_circles); % Radius for the current circle

    % Calculate the number of points for this circle based on arc length
    points_on_this_circle = round(2 * pi * radius / arc_length); 
    
    % Adjust the number of points on each circle to ensure total points equals 64
    remaining_points = total_points - points_so_far;
    if i == n_circles
        points_on_this_circle = remaining_points; % Last circle takes remaining points
    end
    points_so_far = points_so_far + points_on_this_circle;
    points_per_circle(i) = points_on_this_circle; % Store points for this circle
    
    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Display points distribution across circles
disp('Points distribution across circles:');
for i = 1:n_circles
    fprintf('Circle %d: %d points\n', i, points_per_circle(i));
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the evenly distributed points over the concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Length Distance Over 5 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Total number of points
n_circles = 5; % Number of concentric circles

% Calculate the overall arc length for the outermost circle (based on total points)
arc_length = 2 * pi * R / n_points; % Constant arc length between points across all circles

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Initialize array to store the points per circle
points_per_circle = zeros(1, n_circles); 

% Calculate points distribution across circles
total_circumference = sum(2 * pi * (R * (1:n_circles) / n_circles)); % Total circumference of all circles
point_ratio = (2 * pi * (R * (1:n_circles) / n_circles)) / total_circumference; % Proportional ratio for each circle

% Distribute points based on ratio
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = R * (i / n_circles); 
    
    % Calculate the proportionate number of points for this circle
    points_on_this_circle = round(point_ratio(i) * n_points); 
    
    % Ensure total points across all circles adds up to exactly 64
    if i == n_circles
        points_on_this_circle = n_points - sum(points_per_circle); % Last circle takes the remaining points
    end
    
    points_per_circle(i) = points_on_this_circle; % Store points for this circle
    
    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Display points distribution across circles
disp('Points distribution across circles:');
for i = 1:n_circles
    fprintf('Circle %d: %d points\n', i, points_per_circle(i));
end

% Convert polar coordinates to Cartesian coordinates
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the evenly distributed points over the concentric circles
scatter(x, y, 100, 'r', 'filled'); % Red points

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Length Distance Over 5 Concentric Circles');
xlabel('X-axis');
ylabel('Y-axis');
grid on;

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 64; % Total number of points
n_circles = 4; % Number of concentric circles
perturbation_factor = 0.0; % Perturbation factor (percentage of the radius)

% Calculate the overall arc length for the outermost circle (based on total points)
arc_length = 2 * pi * R / n_points; % Constant arc length between points across all circles

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Initialize array to store the points per circle
points_per_circle = zeros(1, n_circles); 

% Calculate points distribution across circles
total_circumference = sum(2 * pi * (R * (1:n_circles) / n_circles)); % Total circumference of all circles
point_ratio = (2 * pi * (R * (1:n_circles) / n_circles)) / total_circumference; % Proportional ratio for each circle

% Distribute points based on ratio
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = R * (i / n_circles); 
    
    % Calculate the proportionate number of points for this circle
    points_on_this_circle = round(point_ratio(i) * n_points); 
    
    % Ensure total points across all circles adds up to exactly 64
    if i == n_circles
        points_on_this_circle = n_points - sum(points_per_circle); % Last circle takes the remaining points
    end
    
    points_per_circle(i) = points_on_this_circle; % Store points for this circle
    
    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Apply perturbation
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Apply perturbation to the x and y positions
perturbation_x = rand(size(x)) * perturbation_factor * R * 2 - perturbation_factor * R; % Random X perturbation
perturbation_y = rand(size(y)) * perturbation_factor * R * 2 - perturbation_factor * R; % Random Y perturbation

% Add perturbation to original x and y coordinates
x_perturbed = x + perturbation_x;
y_perturbed = y + perturbation_y;

% Display points distribution across circles
disp('Points distribution across circles:');
for i = 1:n_circles
    fprintf('Circle %d: %d points\n', i, points_per_circle(i));
end

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the perturbed points over the concentric circles
scatter(x_perturbed, y_perturbed, 100, 'r', 'filled'); % Red points with perturbation

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('64 Points with Equal Arc Length Distance and Perturbation');
xlabel('X-axis');
ylabel('Y-axis');

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 33; % Total number of points
max_circles = 10; % Max number of circles to test
perturbation_factor = 0.2; % Perturbation factor (percentage of the radius)

% Function to calculate the difference in arc length and radius
calculate_diff = @(n_circles) ...
    sum(abs(2*pi*(R*(1:n_circles)/n_circles) / round(n_points / n_circles) - diff([0 R*(1:n_circles)/n_circles])));

% Try different values of n_circles from 2 to max_circles
best_n_circles = 2; % Initialize with 2 circles
min_diff = inf; % Initialize with a large difference

for n_circles = 2:max_circles
    % Calculate the total difference in arc lengths and radii
    diff_value = calculate_diff(n_circles);
    
    % Store the optimal number of circles based on the minimum difference
    if diff_value < min_diff
        min_diff = diff_value;
        best_n_circles = n_circles;
    end
end

% Display the best number of circles
disp(['Optimal number of circles: ', num2str(best_n_circles)]);

% Recalculate with the best number of circles
n_circles = best_n_circles;

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Initialize array to store the points per circle
points_per_circle = zeros(1, n_circles); 

% Calculate the circumference for each circle
circumferences = 2 * pi * (R * (1:n_circles) / n_circles); 

% Normalize the points to distribute evenly over each circle's circumference
total_circumference = sum(circumferences); % Total circumference of all circles
point_ratio = circumferences / total_circumference; % Proportional ratio for each circle

% Distribute points based on the calculated ratio
remaining_points = n_points; % Remaining points to distribute equally
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = R * (i / n_circles); 
    
    % Calculate the proportionate number of points for this circle
    points_on_this_circle = round(point_ratio(i) * n_points); 
    
    % Ensure total points across all circles adds up to exactly 32
    if i == n_circles
        points_on_this_circle = remaining_points - sum(points_per_circle); 
    end
    
    points_per_circle(i) = points_on_this_circle; % Store points for this circle
    
    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Apply perturbation
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Apply perturbation to the x and y positions
perturbation_x = rand(size(x)) * perturbation_factor * R * 2 - perturbation_factor * R; % Random X perturbation
perturbation_y = rand(size(y)) * perturbation_factor * R * 2 - perturbation_factor * R; % Random Y perturbation

% Add perturbation to original x and y coordinates
x_perturbed = x + perturbation_x;
y_perturbed = y + perturbation_y;

% Display points distribution across circles
disp('Points distribution across circles:');
for i = 1:n_circles
    fprintf('Circle %d: %d points\n', i, points_per_circle(i));
end

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the perturbed points over the concentric circles
scatter(x_perturbed, y_perturbed, 100, 'r', 'filled'); % Red points with perturbation

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('Optimized Distribution of Points with Equal Arc Length and Perturbation');
xlabel('X-axis');
ylabel('Y-axis');


%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 33; % Total number of points
max_circles = 10; % Max number of circles to test
perturbation_factor = 0.05; % Fixed perturbation factor (percentage of total area)

% Function to calculate the difference in arc length and radius
calculate_diff = @(n_circles) ...
    sum(abs(2*pi*(R*(1:n_circles)/n_circles) / round(n_points / n_circles) - diff([0 R*(1:n_circles)/n_circles])));

% Try different values of n_circles from 2 to max_circles
best_n_circles = 2; % Initialize with 2 circles
min_diff = inf; % Initialize with a large difference

for n_circles = 2:max_circles
    % Calculate the total difference in arc lengths and radii
    diff_value = calculate_diff(n_circles);
    
    % Store the optimal number of circles based on the minimum difference
    if diff_value < min_diff
        min_diff = diff_value;
        best_n_circles = n_circles;
    end
end

% Display the best number of circles
disp(['Optimal number of circles: ', num2str(best_n_circles)]);

% Recalculate with the best number of circles
n_circles = best_n_circles;

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Initialize array to store the points per circle
points_per_circle = zeros(1, n_circles); 

% Calculate the circumference for each circle
circumferences = 2 * pi * (R * (1:n_circles) / n_circles); 

% Normalize the points to distribute evenly over each circle's circumference
total_circumference = sum(circumferences); % Total circumference of all circles
point_ratio = circumferences / total_circumference; % Proportional ratio for each circle

% Distribute points based on the calculated ratio
remaining_points = n_points; % Remaining points to distribute equally
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = R * (i / n_circles); 
    
    % Calculate the proportionate number of points for this circle
    points_on_this_circle = round(point_ratio(i) * n_points); 
    
    % Ensure total points across all circles adds up to exactly 32
    if i == n_circles
        points_on_this_circle = remaining_points - sum(points_per_circle); 
    end
    
    points_per_circle(i) = points_on_this_circle; % Store points for this circle
    
    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Apply fixed perturbation
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Apply fixed perturbation to the x and y positions
perturbation_x = rand(size(x)) * perturbation_factor * 2 * R - perturbation_factor * R; % Fixed random X perturbation
perturbation_y = rand(size(y)) * perturbation_factor * 2 * R - perturbation_factor * R; % Fixed random Y perturbation

% Add perturbation to original x and y coordinates
x_perturbed = x + perturbation_x;
y_perturbed = y + perturbation_y;

% Display points distribution across circles
disp('Points distribution across circles:');
for i = 1:n_circles
    fprintf('Circle %d: %d points\n', i, points_per_circle(i));
end

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the perturbed points over the concentric circles
scatter(x_perturbed, y_perturbed, 100, 'r', 'filled'); % Red points with perturbation

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('Optimized Distribution of Points with Equal Arc Length and Fixed Perturbation');
xlabel('X-axis');
ylabel('Y-axis');

%%
% Parameters
R = 30; % Radius of the outer circle
n_points = 32; % Total number of points
max_circles = 10; % Max number of circles to test
perturbation_value = 1; % Absolute perturbation value (fixed distance in units)

% Function to calculate the difference in arc length and radius
calculate_diff = @(n_circles) ...
    sum(abs(2*pi*(R*(1:n_circles)/n_circles) / round(n_points / n_circles) - diff([0 R*(1:n_circles)/n_circles])));

% Try different values of n_circles from 2 to max_circles
best_n_circles = 2; % Initialize with 2 circles
min_diff = inf; % Initialize with a large difference

for n_circles = 2:max_circles
    % Calculate the total difference in arc lengths and radii
    diff_value = calculate_diff(n_circles);
    
    % Store the optimal number of circles based on the minimum difference
    if diff_value < min_diff
        min_diff = diff_value;
        best_n_circles = n_circles;
    end
end

% Display the best number of circles
disp(['Optimal number of circles: ', num2str(best_n_circles)]);

% Recalculate with the best number of circles
n_circles = best_n_circles;

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Initialize array to store the points per circle
points_per_circle = zeros(1, n_circles); 

% Calculate the circumference for each circle
circumferences = 2 * pi * (R * (1:n_circles) / n_circles); 

% Normalize the points to distribute evenly over each circle's circumference
total_circumference = sum(circumferences); % Total circumference of all circles
point_ratio = circumferences / total_circumference; % Proportional ratio for each circle

% Distribute points based on the calculated ratio
remaining_points = n_points; % Remaining points to distribute equally
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = R * (i / n_circles); 
    
    % Calculate the proportionate number of points for this circle
    points_on_this_circle = round(point_ratio(i) * n_points); 
    
    % Ensure total points across all circles adds up to exactly 32
    if i == n_circles
        points_on_this_circle = remaining_points - sum(points_per_circle); 
    end
    
    points_per_circle(i) = points_on_this_circle; % Store points for this circle
    
    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Apply fixed absolute perturbation
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Apply fixed absolute perturbation to the x and y positions
perturbation_x = rand(size(x)) * 2 * perturbation_value - perturbation_value; % Fixed absolute X perturbation
perturbation_y = rand(size(y)) * 2 * perturbation_value - perturbation_value; % Fixed absolute Y perturbation

% Add perturbation to original x and y coordinates
x_perturbed = x + perturbation_x;
y_perturbed = y + perturbation_y;

% Display points distribution across circles
disp('Points distribution across circles:');
for i = 1:n_circles
    fprintf('Circle %d: %d points\n', i, points_per_circle(i));
end

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the perturbed points over the concentric circles
scatter(x_perturbed, y_perturbed, 100, 'r', 'filled'); % Red points with perturbation

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('Optimized Distribution of Points with Equal Arc Length and Absolute Perturbation');
xlabel('X-axis');
ylabel('Y-axis');

%%
% Parameters
R = 30; % Radius of the outermost circle
n_points = 32; % Total number of points (excluding center point)
perturbation_value = 0; % Absolute perturbation value (fixed distance in units)
min_radius = 0; % Minimum radius of the first circle
max_radius = R; % Maximum radius (outermost circle)

% Automatically calculate the number of concentric circles based on point distribution
n_circles = floor(log(n_points) / log(2)); % Estimate the number of circles, heuristic based on points

% Generate radii for each circle
circle_radii = linspace(min_radius, max_radius, n_circles);

% Initialize arrays for storing angles and radial distances
theta = []; % Store angles for the points
r = []; % Store radial distances for the points

% Initialize array to store the points per circle
points_per_circle = zeros(1, n_circles); 

% Calculate the circumference for each circle
circumferences = 2 * pi * circle_radii; 

% Normalize the points to distribute evenly over each circle's circumference
total_circumference = sum(circumferences); % Total circumference of all circles
point_ratio = circumferences / total_circumference; % Proportional ratio for each circle

% Distribute points based on the calculated ratio
remaining_points = n_points; % Remaining points to distribute equally
for i = 1:n_circles
    % Calculate the radius for the current circle
    radius = circle_radii(i); 
    
    % Calculate the proportionate number of points for this circle
    points_on_this_circle = round(point_ratio(i) * n_points); 
    
    % Ensure total points across all circles adds up to exactly 32
    if i == n_circles
        points_on_this_circle = remaining_points - sum(points_per_circle); 
    end
    
    points_per_circle(i) = points_on_this_circle; % Store points for this circle
    
    % Calculate the angle between points for this circle
    angle_between_points = 2 * pi / points_on_this_circle; 
    
    % Generate the angles for this circle
    angles = (0:points_on_this_circle-1) * angle_between_points; 
    
    % Append the points for this circle
    theta = [theta, angles]; 
    r = [r, repmat(radius, 1, length(angles))];
end

% Apply fixed absolute perturbation
x = r .* cos(theta); % x-coordinates
y = r .* sin(theta); % y-coordinates

% Apply fixed absolute perturbation to the x and y positions
perturbation_x = rand(size(x)) * 2 * perturbation_value - perturbation_value; % Fixed absolute X perturbation
perturbation_y = rand(size(y)) * 2 * perturbation_value - perturbation_value; % Fixed absolute Y perturbation

% Add perturbation to original x and y coordinates
x_perturbed = x + perturbation_x;
y_perturbed = y + perturbation_y;

% Display points distribution across circles
disp('Points distribution across circles:');
for i = 1:n_circles
    fprintf('Circle with radius %.2f: %d points\n', circle_radii(i), points_per_circle(i));
end

% Create the figure
figure;

% Plot the circular surface (filled circle)
theta_surface = linspace(0, 2*pi, 100); % More points for the surface
x_surface = R * cos(theta_surface);
y_surface = R * sin(theta_surface);
fill(x_surface, y_surface, 'b', 'FaceAlpha', 0.2); % 'FaceAlpha' makes the surface slightly transparent
hold on;

% Plot the perturbed points over the concentric circles
scatter(x_perturbed, y_perturbed, 100, 'r', 'filled'); % Red points with perturbation

% Format the plot
axis equal; % To ensure the aspect ratio is equal
title('Optimized Distribution of Points (Without Center Point)');
xlabel('X-axis');
ylabel('Y-axis');

%%
% Number of points and minimum distance
n_points = 30;
radius = 30;
min_distance = 3; % Minimum distance between points

% Initialize the array
points = [];
attempts = 0;
max_attempts = 1000;

% Generate points using Poisson disk sampling
while length(points) < n_points && attempts < max_attempts
    % Generate a random angle
    angle = 2*pi*rand;
    distance = rand * radius; % Random radius
    
    if distance > min_distance && distance < radius
        points = [points; distance * cos(angle), distance * sin(angle)];
    end
    attempts = attempts + 1;
end

% Plot the points
figure;
scatter(points(:,1), points(:,2), 50, 'filled');
title('Sparse Distribution of Points (Poisson Disk Sampling)');
axis equal;
xlabel('X');
ylabel('Y');

%%
% Parameters for spiral distribution
n_points = 30;
radius = 30;
spiral_growth = 0.5; % Control the spiral growth rate

% Generate points along an Archimedean spiral
theta = linspace(0, 2*pi, n_points);
r = spiral_growth * theta; % Radial distance increases with theta
r = min(r, radius); % Ensure points are within the desired radius

% Convert to Cartesian coordinates
x = r .* cos(theta);
y = r .* sin(theta);

% Plot the spiral distribution
figure;
scatter(x, y, 50, 'filled');
title('Spiral Distribution of Points');
axis equal;
xlabel('X');
ylabel('Y');

%%

% Key Features of the Fibonacci Spiral Distribution:
% Angular Distribution: The points are distributed in terms of angular separation using the "golden angle," which is approximately 137.5 degrees. This ensures that the points are spaced evenly around the circle in terms of angle, but not symmetrically in the sense of regular or predictable intervals like in a regular polygon.
% 
% Radial Distribution: The radial distance increases as r = radius * sqrt((1:n_points) / n_points), meaning the points are distributed more densely in the center and sparser as you move outward. However, this distribution is not symmetric because the points are not uniformly spaced; they follow a spiral pattern.
% 
% Symmetry:
% No rotational symmetry: The distribution does not exhibit rotational symmetry around the circle's center. If you rotate the spiral, the points will not match up with their original positions.
% No mirror symmetry: The distribution does not mirror along any axis, so there are no symmetric pairs of points relative to any line through the center.
% The Fibonacci spiral is designed to optimize space without creating symmetrical or periodic patterns, which is why it’s often used in contexts like seed arrangements in plants or in acoustics for avoiding constructive interference (like in loudspeaker arrays). If you're looking for a more symmetric distribution, you might want to look at regular angular spacing or other patterns like lattice or grid distributions.
% 

% Parameters for Fibonacci spiral distribution
n_points = 64;
radius = 30;

% Golden angle in radians (approximately 137.5 degrees)
golden_angle = pi * (3 - sqrt(5));

% Generate points using Fibonacci spiral
theta = golden_angle * (1:n_points); % Angular position of points
r = radius * sqrt(1:n_points) / sqrt(n_points); % Radial distance increases

% Convert to Cartesian coordinates
x = r .* cos(theta);
y = r .* sin(theta);

% Plot the Fibonacci spiral distribution
figure;
plot(x,y,'.-r')
scatter(x, y, 50, 'filled');
title('Golden Spiral Distribution of Points');
axis equal;
xlabel('X');
ylabel('Y');

%%
% Parameters for Fibonacci spiral distribution
n_points = 32;  % Total number of points
radius = 30;    % Radius of the circle

% Golden angle in radians (approximately 137.5 degrees)
golden_angle = pi * (3 - sqrt(5));

% Generate points using Fibonacci spiral
theta = golden_angle * (1:n_points); % Angular position of points
r = radius * sqrt((1:n_points) / n_points); % Radial distance increases

% Convert to Cartesian coordinates
x = r .* cos(theta);
y = r .* sin(theta);


% Create a figure
figure;

% Plot the outer circle with radius 30
theta_circle = linspace(0, 2*pi, 100); % Angle for a full circle
x_circle = radius * cos(theta_circle);
y_circle = radius * sin(theta_circle);
plot(x_circle, y_circle, 'b--'); % Outer circle in blue dashed line

% Plot the Fibonacci spiral distribution
hold on;
scatter(x, y, 50, 'filled', 'r'); % Scatter plot of points

% Formatting the plot
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Golden Spiral Distribution with Outer Radius Circle');
grid on;


% Parameters for Fibonacci spiral distribution
n_points = 16;  % Total number of points
radius = 15;    % Radius of the circle

% Golden angle in radians (approximately 137.5 degrees)
golden_angle = pi * (3 - sqrt(5));

% Generate points using Fibonacci spiral
theta = golden_angle * (1:n_points); % Angular position of points
r = radius * sqrt((1:n_points) / n_points); % Radial distance increases

% Convert to Cartesian coordinates
x = r .* cos(theta);
y = r .* sin(theta);


% Create a figure
hold on

% Plot the outer circle with radius 30
theta_circle = linspace(0, 2*pi, 100); % Angle for a full circle
x_circle = radius * cos(theta_circle);
y_circle = radius * sin(theta_circle);
plot(x_circle, y_circle, 'b--'); % Outer circle in blue dashed line

% Plot the Fibonacci spiral distribution
hold on;
scatter(x, y, 50, 'filled', 'b'); % Scatter plot of points

% Formatting the plot
axis equal;
xlabel('X (mm)');
ylabel('Y (mm)');
title('Golden Spiral Distribution with Outer Radius Circle');
grid on;


%%
