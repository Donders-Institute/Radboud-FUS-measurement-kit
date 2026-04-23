%% Compare two FUS datasets: Pressure vs Z, all focuses overlaid
% Loads two .mat files and plots data{1,i}.pressure.data vs data{1,i}.z

clear; clc; close all;

% ── File pairs to compare ─────────────────────────────────────────────────
filenames1 = {
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2025\Transducers\Imasonic_15287_1001\20250827 Characterization\Output of T [Imasonic 10 ch. PCD15287_01001 ROC 75 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [6. Verification]\export_2026-04-09_13-06-12\FUS_Metrology_Export_Verification_15278_1001.mat", ...
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2025\Transducers\Imasonic_15287_1002\20250829 Characterization\Output of T [Imasonic 10 ch. PCD15287_01002 ROC 75 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [6. Verification]\export_2026-04-09_13-02-55\FUS_Metrology_Export_Verification_15278_1002.mat", ...
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2025\Transducers\Imasonic_15473_1001\20250901 Characterization\Output of T [Imasonic 10 ch. PCD15473_01001 ROC 100 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [6. Verification]\export_2026-04-09_12-59-25\FUS_Metrology_Export_Verification_15473_1001.mat",...
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2025\Transducers\Imasonic_15473_1003\20250905 Characterization\Output of T [Imasonic 10 ch. PCD15473_01003 ROC 100 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [6. Verification]\export_2026-04-09_12-19-18\FUS_Metrology_Export_Verification_15473_1003.mat"
};
filenames2 = {
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers\Imasonic_15287_1001\20260407 K-Plan Measurements\Output of T [Imasonic 10 ch. PCD15287_01001 ROC 75 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [KPlan_level_2]\export_2026-04-08_16-40-57\FUS_Metrology_Export_K-Plan_15278_1001.mat", ...
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers\Imasonic_15287_1002\20260408 K-Plan Measurements\Output of T [Imasonic 10 ch. PCD15287_01002 ROC 75 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [KPlan_level_2]\export_2026-04-08_16-34-59\FUS_Metrology_Export_K-Plan_15278_1002.mat", ...
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers\Imasonic_15473_1001\20260408 K-Plan Measurements\Output of T [Imasonic 10 ch. PCD15473_01001 ROC 100 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [KPlan_level_2]\export_2026-04-08_16-47-46\FUS_Metrology_Export_K-Plan_15473_1001.mat", ...
    "\\?\UNC\ru.nl\WrkGrp\FUS_Hub\Hydrophone measurements\Measurements\2026\Transducers\Imasonic_15473_1003\20260408 K-Plan Measurements\Output of T [Imasonic 10 ch. PCD15473_01003 ROC 100 mm] - DS [IGT 32 ch. - 1 x 10 ch.]\P [KPlan_level_2]\export_2026-04-08_16-53-18\FUS_Metrology_Export_K-Plan_15473_1003.mat"
};

% ── Labels for the legend (one pair per file pair) ────────────────────────
labels_dataset1 = {'2025-08', '2025-08', '2025-09', '2025-09'};
labels_dataset2 = {'2026-04', '2026-04', '2026-04', '2026-04'};

% ── Save location (leave empty '' to skip saving) ─────────────────────────
save_loc = 'C:\Users\marge\Radboud Universiteit\FUS Initiative-[SHARED] Research information - Documenten\Software\K-Plan\Imasonic_measurements\time_comparison';

% ─────────────────────────────────────────────────────────────────────────
for i = 1:numel(filenames1)
    filename1 = filenames1{i};
    filename2 = filenames2{i};

    label_dataset1 = labels_dataset1{i};
    label_dataset2 = labels_dataset2{i};

    fprintf('Loading %s ...\n', filename1);
    S1 = load(filename1);
    fprintf('Loading %s ...\n', filename2);
    S2 = load(filename2);

    data1 = S1.data;
    data2 = S2.data;

    % ── Extract focus IDs ─────────────────────────────────────────────────
    nFocus1 = size(data1, 2);
    nFocus2 = size(data2, 2);

    focusIDs1 = arrayfun(@(j) data1{1,j}.focus, 1:nFocus1);
    focusIDs2 = arrayfun(@(j) data2{1,j}.focus, 1:nFocus2);

    commonFocusIDs = intersect(focusIDs1, focusIDs2);
    onlyIn1 = setdiff(focusIDs1, focusIDs2);
    onlyIn2 = setdiff(focusIDs2, focusIDs1);

    if ~isempty(onlyIn1)
        warning('File pair %d: Focus(es) %s found only in dataset 1 — skipped.', i, num2str(onlyIn1));
    end
    if ~isempty(onlyIn2)
        warning('File pair %d: Focus(es) %s found only in dataset 2 — skipped.', i, num2str(onlyIn2));
    end
    if isempty(commonFocusIDs)
        error('File pair %d: No matching focuses found between the two datasets.', i);
    end

    fprintf('Plotting %d matching focus(es): %s\n', numel(commonFocusIDs), num2str(commonFocusIDs));

    % ── Plot ──────────────────────────────────────────────────────────────
    cmap = lines(numel(commonFocusIDs));
    fig = figure('Name', sprintf('Pressure vs Dist wrt exit plane – Pair %d', i), 'NumberTitle', 'off');
    hold on; grid on; box on;

    legendEntries = {};

    for k = 1:numel(commonFocusIDs)
        fid  = commonFocusIDs(k);
        idx1 = find(focusIDs1 == fid, 1);
        idx2 = find(focusIDs2 == fid, 1);

        if ~strcmp(data1{1,idx1}.tranducer, data2{1,idx1}.tranducer)
            error('Equipment is different!: %s and %s', data1{1,idx1}.transducer, data2{1,idx1}.transducer);
        end

        % Dataset 1
        z1  = data1{1,idx1}.z;
        p1d = data1{1,idx1}.pressure.data/1e6;
        label1 = sprintf('Focus %g mm | %s', fid, label_dataset1);
        plot(z1, p1d, '-',  'Color', cmap(k,:), 'LineWidth', 1.8, 'DisplayName', label1);
        legendEntries{end+1} = label1; %#ok<AGROW>

        % Dataset 2
        z2  = data2{1,idx2}.z;
        p2d = data2{1,idx2}.pressure.data/1e6;
        label2 = sprintf('Focus %g mm | %s', fid, label_dataset2);
        plot(z2, p2d, '--', 'Color', cmap(k,:), 'LineWidth', 1.8, 'DisplayName', label2);
        legendEntries{end+1} = label2; %#ok<AGROW>
    end

    xlabel('Distance w.r.t. exit plane (mm)', 'FontSize', 12);
    ylabel('Pressure (MPa)',      'FontSize', 12);
    title(sprintf('Pressure vs Distance w.r.t. exit plane – %s - %s vs %s', data1{1,idx1}.tranducer, label_dataset1, label_dataset2), 'FontSize', 14);
    legend(legendEntries, 'Location', 'best', 'Interpreter', 'none');
    hold off;

    % ── Save ──────────────────────────────────────────────────────────────
    if ~isempty(save_loc)
        [~, name1] = fileparts(filename1);
        [~, name2] = fileparts(filename2);
        save_name = sprintf('PressureVsdistwrtep_%s_%s_vs_%s.png', data1{1,idx1}.tranducer, label_dataset1, label_dataset2);
        save_path = fullfile(save_loc, save_name);
        set(fig, 'WindowState', 'maximized');
        pause(0.5);  % allow window to fully expand before saving
        exportgraphics(fig, save_path, 'Resolution', 300);
        fprintf('Figure saved to %s\n', save_path);
    end

    fprintf('Done. %d focus(es) plotted.\n', numel(commonFocusIDs));
end