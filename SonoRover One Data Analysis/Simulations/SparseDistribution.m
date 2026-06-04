

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

