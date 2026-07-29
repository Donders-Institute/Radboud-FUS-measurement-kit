%% Compare FUS datasets: Pressure vs Z, all focuses overlaid
% Loads one or two .mat files and plots pressure vs distance.
%
% compare_mode = 'two_files'  – two separate .mat files, matched by focus ID
% compare_mode = 'one_file'   – one .mat file, N measurements (e.g. different
%                               hydrophones), all plotted in one figure per focus

clear; clc; close all;

% ── Plot mode ─────────────────────────────────────────────────────────────
% 'overlay'   – all focuses in one figure
% 'per_focus' – one figure per focus
plot_mode = 'overlay';  % <-- choose here

% ── Compare mode ──────────────────────────────────────────────────────────
% 'two_files' – two datasets from separate .mat files
% 'one_file'  – one .mat file, labels follow cell order in data
compare_mode = 'one_file';  % <-- choose here

% ═════════════════════════════════════════════════════════════════════════
% CONFIGURATION: two_files
% ═════════════════════════════════════════════════════════════════════════
filenames1 = {
   "C:\Users\marge\Radboud Universiteit\FUS Initiative - General\Projects\CITRUS\V2\collected_data\#7\line_scans\mask_2\scf_0_09\acoustic_axis_vs_[001]\FUS_Metrology_Export_CITRUS_#7_mask_2_scf_0_09_axial.mat"
   };
filenames2 = {
  "C:\Users\marge\Radboud Universiteit\FUS Initiative - General\Projects\CITRUS\V2\collected_data\#7\line_scans\mask_2\scf_0_09\acoustic_axis_vs_[001]\FUS_Metrology_Export_CITRUS_#7_mask_2_scf_0_09_acoustic_axis.mat"
};
labels_dataset1 = {'Axial'};
labels_dataset2 = {'Acoustic axis'};

% ═════════════════════════════════════════════════════════════════════════
% CONFIGURATION: one_file
% Labels must match the cell order in data (one label per measurement)
% ═════════════════════════════════════════════════════════════════════════
filename_single = "\\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers\CTX_500_026_4Ch\2026_07_01 SSVEP ITRUSST Measurements\Output\ITRUSST_axial\f68.7\FUS_Metrology_Export_CTX500_026-TPO_105_010_f68.7.mat";

dataset_labels = {
    'Axial',...
    'Acoustic_axis'
};

% ── Save location (leave empty '' to skip saving) ─────────────────────────
save_loc = "\\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers\CTX_500_026_4Ch\2026_07_01 SSVEP ITRUSST Measurements\Output\ITRUSST_axial\f68.7";


% ═════════════════════════════════════════════════════════════════════════
% ONE_FILE MODE
% ═════════════════════════════════════════════════════════════════════════
if strcmp(compare_mode, 'one_file')
 
    fprintf('Loading %s ...\n', filename_single);
    S    = load(filename_single);
    data = S.data;
    nMeas = size(data, 2);
 
    if numel(dataset_labels) ~= nMeas
        error('Number of labels (%d) does not match number of measurements in file (%d).', ...
            numel(dataset_labels), nMeas);
    end
 
    focusIDs = arrayfun(@(j) data{1,j}.focus, 1:nMeas);
    uniqueFocusIDs = unique(focusIDs);
 
    % ── Global y-axis limits ──────────────────────────────────────────────
    allPressuresCell = arrayfun(@(j) data{1,j}.pressure.data/1e6, 1:nMeas, 'UniformOutput', false);
    allPressures = vertcat(allPressuresCell{:});
    yMax    = max(abs(allPressures(:))) * 1.1;  % 10% headroom
    yLimits = [0, yMax];  % change to [-yMax, yMax] if negative values are expected
 
    if strcmp(plot_mode, 'overlay')
        fig = figure('Name', 'Pressure vs Dist wrt exit plane', 'NumberTitle', 'off');
        hold on; grid on; box on;
    end
 
    pageCount = 0;
 
    for f = 1:numel(uniqueFocusIDs)
        fid     = uniqueFocusIDs(f);
        fidIdxs = find(focusIDs == fid);  % all measurements for this focus
 
        if strcmp(plot_mode, 'per_focus')
            fig = figure('Name', sprintf('Focus %g mm', fid), 'NumberTitle', 'off');
            hold on; grid on; box on;
        end
 
        transducer = data{1, fidIdxs(1)}.tranducer;
 
        for m = 1:numel(fidIdxs)
            idx   = fidIdxs(m);
            z     = data{1,idx}.z;
            p     = data{1,idx}.pressure.data / 1e6;
            lbl   = sprintf('Focus %g mm | %s', fid, dataset_labels{idx});
            plot(z, p, 'LineWidth', 1.8, 'DisplayName', lbl);
        end
 
        if strcmp(plot_mode, 'per_focus')
            xlabel('Distance w.r.t. exit plane (mm)', 'FontSize', 12);
            ylabel('Pressure (MPa)', 'FontSize', 12);
            title(sprintf('Focus %g mm – %s', fid, transducer), ...
                'FontSize', 14, 'Interpreter', 'none');
            legend('Location', 'best', 'Interpreter', 'none');
            ylim(yLimits);
            hold off;
 
            % ── Save as multi-page TIFF ───────────────────────────────────
            if ~isempty(save_loc)
                save_name = sprintf('PressureVsdistwrtep_%s_acoustic_axis.tiff', transducer);
                save_path = fullfile(save_loc, save_name);
                set(fig, 'WindowState', 'maximized'); pause(0.5);
                frame = getframe(fig);
                img   = frame2im(frame);
                pageCount = pageCount + 1;
                if pageCount == 1
                    imwrite(img, save_path, 'tiff', 'WriteMode', 'overwrite', 'Compression', 'lzw');
                else
                    imwrite(img, save_path, 'tiff', 'WriteMode', 'append', 'Compression', 'lzw');
                end
                fprintf('Page %d/%d added to %s\n', pageCount, numel(uniqueFocusIDs), save_path);
            end
        end
    end
 
    if strcmp(plot_mode, 'overlay')
        transducer = data{1,1}.tranducer;
        xlabel('Distance w.r.t. exit plane (mm)', 'FontSize', 12);
        ylabel('Pressure (MPa)', 'FontSize', 12);
        title(sprintf('Pressure vs Distance – %s – hydrophone comparison', transducer), ...
            'FontSize', 14, 'Interpreter', 'none');
        legend('Location', 'best', 'Interpreter', 'none');
        ylim(yLimits);
        hold off;
 
        if ~isempty(save_loc)
            save_name = sprintf('PressureVsdistwrtep_%s_hydrophone_comparison.png', transducer);
            save_path = fullfile(save_loc, save_name);
            set(fig, 'WindowState', 'maximized'); pause(0.5);
            exportgraphics(fig, save_path, 'Resolution', 300);
            fprintf('Figure saved to %s\n', save_path);
        end
    end
 
    fprintf('Done. %d focus(es), %d measurement(s) plotted.\n', numel(uniqueFocusIDs), nMeas);
    return
end

% ═════════════════════════════════════════════════════════════════════════
% TWO_FILES MODE
% ═════════════════════════════════════════════════════════════════════════
for i = 1:numel(filenames1)

    label_dataset1 = labels_dataset1{i};
    label_dataset2 = labels_dataset2{i};
    fprintf('Loading %s ...\n', filenames1{i});
    S1 = load(filenames1{i});
    fprintf('Loading %s ...\n', filenames2{i});
    S2 = load(filenames2{i});
    data1 = S1.data;
    data2 = S2.data;

    % ── Determine focus IDs ───────────────────────────────────────────────
    focusIDs1 = arrayfun(@(j) data1{1,j}.focus, 1:size(data1,2));
    focusIDs2 = arrayfun(@(j) data2{1,j}.focus, 1:size(data2,2));

    commonFocusIDs = intersect(focusIDs1, focusIDs2);
    onlyIn1 = setdiff(focusIDs1, focusIDs2);
    onlyIn2 = setdiff(focusIDs2, focusIDs1);

    if ~isempty(onlyIn1)
        warning('Pair %d: Focus(es) %s only in dataset 1 — skipped.', i, num2str(onlyIn1));
    end
    if ~isempty(onlyIn2)
        warning('Pair %d: Focus(es) %s only in dataset 2 — skipped.', i, num2str(onlyIn2));
    end
    if isempty(commonFocusIDs)
        error('Pair %d: no matching focuses found between the two datasets.', i);
    end

    fprintf('Plotting %d focus(es): %s\n', numel(commonFocusIDs), num2str(commonFocusIDs));

    % ── Global y-axis limits ──────────────────────────────────────────────
    allPressures = [];
    for k = 1:numel(commonFocusIDs)
        idx1 = find(focusIDs1 == commonFocusIDs(k), 1);
        idx2 = find(focusIDs2 == commonFocusIDs(k), 1);
        allPressures = [allPressures; data1{1,idx1}.pressure.data/1e6; data2{1,idx2}.pressure.data/1e6]; %#ok<AGROW>
    end
    yMax    = max(abs(allPressures(:))) * 1.1;  % 10% headroom
    yLimits = [0, yMax];  % change to [-yMax, yMax] if negative values are expected

    % ── Plot ──────────────────────────────────────────────────────────────
    cmap = lines(numel(commonFocusIDs));
    if strcmp(plot_mode, 'overlay')
        fig = figure('Name', sprintf('Pressure vs Dist wrt exit plane – Pair %d', i), 'NumberTitle', 'off');
        hold on; grid on; box on;
    end

    pageCount = 0;

    for k = 1:numel(commonFocusIDs)
        fid  = commonFocusIDs(k);
        idx1 = find(focusIDs1 == fid, 1);
        idx2 = find(focusIDs2 == fid, 1);
        transducer = data1{1,idx1}.tranducer;

        if strcmp(plot_mode, 'per_focus')
            fig = figure('Name', sprintf('Focus %g mm – Pair %d', fid, i), 'NumberTitle', 'off');
            hold on; grid on; box on;
        end

        % Check that both datasets come from the same transducer
        if ~strcmp(data1{1,idx1}.tranducer, data2{1,idx2}.tranducer)
            error('Equipment is different!: %s and %s', data1{1,idx1}.tranducer, data2{1,idx2}.tranducer);
        end

        % Dataset 1
        z1  = data1{1,idx1}.z;
        p1d = data1{1,idx1}.pressure.data / 1e6;
        lbl1 = sprintf('Focus %g mm | %s', fid, label_dataset1);
        plot(z1, p1d, '-',  'Color', cmap(k,:), 'LineWidth', 1.8, 'DisplayName', lbl1);

        % Dataset 2
        z2  = data2{1,idx2}.z;
        p2d = data2{1,idx2}.pressure.data / 1e6;
        lbl2 = sprintf('Focus %g mm | %s', fid, label_dataset2);
        plot(z2, p2d, '--', 'Color', cmap(k,:), 'LineWidth', 1.8, 'DisplayName', lbl2);

        % ── Axis labels, title, legend ────────────────────────────────────
        if strcmp(plot_mode, 'per_focus')
            xlabel('Distance w.r.t. exit plane (mm)', 'FontSize', 12);
            ylabel('Pressure (MPa)', 'FontSize', 12);
            title(sprintf('Focus %g mm – %s – %s vs %s', fid, transducer, label_dataset1, label_dataset2), ...
                'FontSize', 14, 'Interpreter', 'none');
            legend('Location', 'best', 'Interpreter', 'none');
            ylim(yLimits);
            hold off;

            % ── Save as multi-page TIFF ───────────────────────────────────
            if ~isempty(save_loc)
                save_name = sprintf('PressureVsdistwrtep_%s_%s_vs_%s.tiff', ...
                    transducer, label_dataset1, label_dataset2);
                save_path = fullfile(save_loc, save_name);
                set(fig, 'WindowState', 'maximized'); pause(0.5);
                frame = getframe(fig);
                img   = frame2im(frame);
                pageCount = pageCount + 1;
                if pageCount == 1
                    imwrite(img, save_path, 'tiff', 'WriteMode', 'overwrite', 'Compression', 'lzw');
                else
                    imwrite(img, save_path, 'tiff', 'WriteMode', 'append', 'Compression', 'lzw');
                end
                fprintf('Page %d/%d added to %s\n', pageCount, numel(commonFocusIDs), save_path);
            end
        end
    end

    if strcmp(plot_mode, 'overlay')
        transducer = data1{1,1}.tranducer;
        xlabel('Distance w.r.t. exit plane (mm)', 'FontSize', 12);
        ylabel('Pressure (MPa)', 'FontSize', 12);
        title(sprintf('Pressure vs Distance – %s – %s vs %s', transducer, label_dataset1, label_dataset2), ...
            'FontSize', 14, 'Interpreter', 'none');
        legend('Location', 'best', 'Interpreter', 'none');
        ylim(yLimits);
        hold off;

        % ── Save as PNG ───────────────────────────────────────────────────
        if ~isempty(save_loc)
            save_name = sprintf('PressureVsdistwrtep_%s_%s_vs_%s.png', ...
                transducer, label_dataset1, label_dataset2);
            save_path = fullfile(save_loc, save_name);
            set(fig, 'WindowState', 'maximized'); pause(0.5);
            exportgraphics(fig, save_path, 'Resolution', 300);
            fprintf('Figure saved to %s\n', save_path);
        end
    end

    fprintf('Done. %d focus(es) plotted.\n', numel(commonFocusIDs));
end