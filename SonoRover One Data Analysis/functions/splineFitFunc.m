function [splineFit, dw_stat] = splineFitFunc(X,Y,transformX,p)



% % Input data
% dat = readmatrix('data_real.csv');
% x = dat(:,1);
% y = dat(:,2);

x = double(X(~isnan(X)));
y = double(Y(~isnan(X)));

% take the log of x
%transformX = 'log';
switch transformX
    case 'oneover'
        x = 1./x;
        smoothingParamErrorMinLog = -12;
        nStartingPoints = 100;
        
    case 'log'
        x = log(x);
        smoothingParamErrorMinLog = -9;
        nStartingPoints = 50;
    case 'sqrt'
        x = sqrt(x);
        smoothingParamErrorMinLog = -6;
        nStartingPoints = 40;    
    case 'none'
        smoothingParamErrorMinLog = -6;
        nStartingPoints = 40;    
    otherwise
        smoothingParamErrorMinLog = -4;
        nStartingPoints = 20;
end

% Function to calculate DW statistic for a given smoothing parameter
    function dw = calculate_dw(x, y, smoothParam)
        % Create fit options
        fo = fitoptions('Method', 'SmoothingSpline', ...
            'SmoothingParam', smoothParam);

        % Fit smoothing spline
        [splineFit, ~] = fit(x, y, 'smoothingspline', fo);

        % Calculate residuals
        y_fit = feval(splineFit, x);
        residuals = y - y_fit;

        % Calculate Durbin-Watson statistic
        dw = sum(diff(residuals).^2) / sum(residuals.^2);
    end

% Function to optimize - returns absolute difference from DW = 2
    function diff = objective_function(smoothingParamError, x, y)
        smoothParam = 1 - smoothingParamError;
        if smoothParam <= 0 || smoothParam >= 1
            diff = inf;  % Invalid smoothing parameter
        else
            dw = calculate_dw(x, y, smoothParam);
            diff = abs(dw - 2);
        end
    end

% Multi-start optimization
starting_points = logspace(smoothingParamErrorMinLog, -1, nStartingPoints);  % Logarithmically spaced points
best_error = inf;
best_param = nan;

fprintf('Starting multi-start optimization with %d starting points...\n', nStartingPoints);

% Options for fminbnd
options = optimset('TolX', 1e-6, 'Display', 'off');

% Try each starting point
for i = 1:nStartingPoints
    [opt_error, opt_diff] = fminbnd(@(p) objective_function(p, x, y), ...
        max(10.^(smoothingParamErrorMinLog), starting_points(i)/10), ...
        min(0.999, starting_points(i)*10), ...
        options);

    if opt_diff < best_error
        best_error = opt_diff;
        best_param = opt_error;
        %fprintf('New best found at iteration %d: Error = %.6f, DW diff = %.6f\n', i, best_param, best_error);
    end
end

% Use the best parameter found
smoothingParamError = best_param;
smoothingParam = 1 - smoothingParamError;

fprintf('\nOptimization complete!\n');
fprintf('Best smoothing parameter: %.6f\n', smoothingParam);
fprintf('Final DW difference from 2: %.6f\n', best_error);

% Now proceed with the original plotting code using optimized parameter
% Create fit options
fo = fitoptions('Method', 'SmoothingSpline', ...
    'SmoothingParam', smoothingParam);

% Fit smoothing spline
[splineFit, gof] = fit(x, y, 'smoothingspline', fo);

% Generate points for smooth curve
x_smooth = linspace(min(x), max(x), 200)';
y_smooth = feval(splineFit, x_smooth);

% Calculate fitted values at data points
y_fit = feval(splineFit, x);
residuals = y - y_fit;

% Calculate confidence bounds
alpha = 0.05;  % 95% confidence level
n = length(x);
dfe = gof.dfe;  % Degrees of freedom
mse = gof.sse/dfe;  % Mean squared error
t_crit = tinv(1-alpha/2, dfe);  % t-statistic

% Calculate leverage for each point using a local window
window = max(3, round(n/10));  % Adjust window size as needed
leverage = zeros(size(x_smooth));
for i = 1:length(x_smooth)
    % Find nearest points within window
    distances = abs(x - x_smooth(i));
    [~, idx] = sort(distances);
    local_idx = idx(1:min(window, length(idx)));

    % Local polynomial fit to estimate leverage
    X_local = [ones(length(local_idx), 1), x(local_idx) - x_smooth(i)];
    leverage(i) = 1/length(local_idx);  % Simplified leverage estimate
end

% Calculate prediction interval
se_pred = sqrt(mse * (1 + leverage));  % Standard error of prediction
ci_width = t_crit * se_pred;

% Calculate confidence bounds for smooth points
y_upper = y_smooth + ci_width;
y_lower = y_smooth - ci_width;

% Calculate autocorrelation manually
maxLag = min(20, length(residuals)-1);
lags = 0:maxLag;
acf = zeros(size(lags));

% Center the residuals
centered_residuals = residuals - mean(residuals);

% Calculate autocorrelation for each lag
variance = var(centered_residuals);
n = length(centered_residuals);

for k = 1:length(lags)
    lag = k - 1;
    valid_length = n - lag;
    autocovariance = sum(centered_residuals(1:valid_length) .* centered_residuals(1+lag:valid_length+lag)) / n;
    acf(k) = autocovariance / variance;
end

 dw_stat = sum(diff(residuals).^2) / sum(residuals.^2);

if p
    % Create figure
    figure('Position', [100 100 800 900]);  % Made figure taller to accommodate third subplot

    % Main plot with confidence bounds
    subplot(3,1,1);  % Changed from 2,1 to 3,1
    plot(x, y, 'bo', 'DisplayName', 'Data');
    hold on;
    plot(x_smooth, y_smooth, 'r-', 'LineWidth', 2, 'DisplayName', 'Smoothing Spline');
    plot(x_smooth, y_upper, 'r:', 'LineWidth', 1, 'DisplayName', '95% Confidence');
    plot(x_smooth, y_lower, 'r:', 'LineWidth', 1, 'HandleVisibility', 'off');
    xlabel('x');
    ylabel('y');
    title(sprintf('Smoothing Spline Fit (Smoothing Parameter = %.3f)', smoothingParam));
    legend('show');
    grid on;

    % Residuals plot
    subplot(3,1,2);  % Changed from 2,1 to 3,1
    plot(x, residuals, 'bo-');
    hold on;
    plot(xlim, [0 0], 'k--');  % Zero line
    xlabel('x');
    ylabel('Residuals');
    title('Residuals');
    grid on;

    % Autocorrelation plot
    subplot(3,1,3);
    stem(lags, acf, 'filled', 'MarkerSize', 4);
    hold on;

    % Add confidence bounds
    conf_bound = 1.96/sqrt(length(residuals));
    plot(xlim, [conf_bound conf_bound], 'r--', 'LineWidth', 1);
    plot(xlim, [-conf_bound -conf_bound], 'r--', 'LineWidth', 1);

    xlabel('Lag');
    ylabel('Autocorrelation');
    title('Residual Autocorrelation Function');
    grid on;

    % Display goodness of fit metrics
    fprintf('\nGoodness of Fit Metrics:\n');
    fprintf('R-squared: %.6f\n', gof.rsquare);
    fprintf('Adjusted R-squared: %.6f\n', gof.adjrsquare);
    fprintf('RMSE: %.6f\n', gof.rmse);

    % Calculate manual RMSE for verification
    rmse_manual = sqrt(mean((y - y_fit).^2));
    fprintf('Manual RMSE verification: %.6f\n', rmse_manual);

    % Additional fit statistics
    fprintf('\nFit Statistics:\n');
    fprintf('Degrees of Freedom: %d\n', gof.dfe);
    fprintf('Sum of Squares due to Error (SSE): %.6f\n', gof.sse);
    fprintf('Mean Squared Error (MSE): %.6f\n', mse);

    % Calculate additional metrics
    mean_y = mean(y);
    ss_total = sum((y - mean_y).^2);
    ss_residual = sum(residuals.^2);
    ss_regression = ss_total - ss_residual;

    fprintf('\nAdditional Statistics:\n');
    fprintf('Number of data points: %d\n', n);
    fprintf('Sum of Squares Total (SST): %.6f\n', ss_total);
    fprintf('Sum of Squares Regression (SSR): %.6f\n', ss_regression);
    fprintf('Mean Absolute Error (MAE): %.6f\n', mean(abs(residuals)));
    fprintf('Max Absolute Error: %.6f\n', max(abs(residuals)));

    % Analyze residuals
    fprintf('\nResidual Analysis:\n');
    fprintf('Mean of residuals: %.6f\n', mean(residuals));
    fprintf('Standard deviation of residuals: %.6f\n', std(residuals));
    fprintf('Skewness of residuals: %.6f\n', skewness(residuals));
    fprintf('Kurtosis of residuals: %.6f\n', kurtosis(residuals));

    % Print significant autocorrelations
    fprintf('\nAutocorrelation Analysis:\n');
    fprintf('Lag\tACF\tSignificant?\n');
    for i = 1:length(lags)
        is_significant = abs(acf(i)) > conf_bound;
        if is_significant
            significance = 'Yes';
        else
            significance = 'No';
        end
        fprintf('%d\t%.3f\t%s\n', lags(i), acf(i), significance);
    end

    % Calculate Durbin-Watson statistic
    dw_stat = sum(diff(residuals).^2) / sum(residuals.^2);
    fprintf('\nDurbin-Watson statistic: %.3f\n', dw_stat);
    text(0.95, 0.95, sprintf('Durbin-Watson: %.3f', dw_stat), ...
        'Units', 'normalized', ...
        'HorizontalAlignment', 'right', ...
        'VerticalAlignment', 'top', ...
        'FontSize', 10);

end

end
