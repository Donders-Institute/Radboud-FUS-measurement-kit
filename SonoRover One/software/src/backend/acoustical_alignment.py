# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Margely Cornelissen, Stein Fekkes (Radboud University) and Erik Dumont (Image
Guided Therapy)

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

**Attribution Notice**:
If you use this kit in your research or project, please include the following attribution:
Margely Cornelissen, Stein Fekkes (Radboud University, Nijmegen, The Netherlands) & Erik Dumont
(Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 1.0),
https://github.com/Donders-Institute/Radboud-FUS-measurement-kit
"""

# Basic packages
import os

# Miscellaneous packages
import configparser
import math
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd
from scipy.integrate import cumulative_trapezoid

# Own packages
import backend.acquisition as acq
from backend.utils import get_config_value

from config.config import config_info as config
from config.logging_config import logger


class AcousticalAlignment(acq.Acquisition):

    def acoustical_alignment(self, sequence):
        """
        Perform acoustical alignment for the given sequence.

        This method acquires data and identifies the center of mass of the acoustical signal
        for a given sequence, which involves scanning the x and y coordinates around a
        given z-coordinate, iteratively narrowing down the search area.

        Parameters:
        -----------
        sequence : object
            Sequence object containing sequence number, coordinates, and other
            relevant details.
        """

        self.sequence = sequence

        output_suffix = get_config_value(logger, config, 'Characterization',
                                         'Ac_align.output_name_suffix', 'output_data')
        # Validate and prepare output directory and files
        outfile = os.path.join(self.input_param.temp_dir_output,
                               f'sequence_{sequence.seq_number}_{output_suffix}.ini')

        self._check_file(outfile)

        self.equipment["ds"].send_sequence(self.sequence)
        logger.info('All driving system parameters are set')

        # Save parameters and prepare for alignment
        self._save_params_ini()
        logger.info('Used parameters have been saved in a file.')

        # Prepare and define coordinates for alignment
        distance_from_foc = self.sequence.ac_align["distance_from_foc"]
        z_coords = self._calculate_z_coords(distance_from_foc)

        # Initialize grid parameters for scanning
        self.grid_param["nsl"] = 1  # Number of slices
        self.grid_param["nrow"] = 1  # Number of rows
        self.sequence.vect_sl = np.array([0, 0, 1])  # Slice direction vector

        # Set up parameters for iterative alignment
        middle_points = self._perform_alignment(z_coords)

        return middle_points

    def _calculate_z_coords(self, distance_from_foc):
        """
        Calculate pre- and post-focus z-coordinates for alignment.

        Parameters:
        -----------
        distance_from_foc : float array
            Distance from the focus point in millimeters.

        Returns:
        --------
        list of float
            Z-coordinates for pre-focus and post-focus alignment.
        """
        z_coords = []
        for dist in distance_from_foc:
            dist_foc = self.input_param.coord_zero[2] + self.sequence.focus_wrt_exit_plane + dist
            z_coords.append(dist_foc)

        return z_coords

    def _perform_alignment(self, z_coords):
        """
        Perform the acoustical alignment by iteratively scanning x and y coordinates.

        Parameters:
        -----------
        z_coords : list of float
            List of z-coordinates to perform the alignment.

        Returns:
        --------
        np.ndarray
            Array containing the middle points [x, y, z] for each z-coordinate.
        """

        initial_line_length = self.sequence.ac_align["init_line_len"]
        initial_line_step_size = self.sequence.ac_align["init_line_step"]
        line_n_points = round(initial_line_length / initial_line_step_size)

        if (line_n_points % 2) == 0:
            line_n_points = line_n_points + 1

        self.grid_param["ncol"] = line_n_points
        self.sequence.nslices_nrow_ncol = [self.grid_param["nsl"], self.grid_param["nrow"],
                                           self.grid_param["ncol"]]

        # TODO: reduction is disabled from the frontend
        # reduction_factor = self.sequence.ac_align["reduction_factor"]
        threshold = self.sequence.ac_align["init_threshold"]

        middle_points = np.zeros((len(z_coords), 3))

        # history plot for all middle points
        fig_hist, axes_hist = plt.subplots(len(z_coords), 2)
        fig_hist.suptitle('Focus wrt exit plane ' +
                          f'{self.sequence.focus_wrt_exit_plane:.2f} [mm]')
        fig_hist.text(0.01, 0.5, 'Pulse RMS [mV], Z wrt exit plane [mm]:', va='center',
                      rotation='vertical')

        x_x_upper_lim = self.input_param.coord_zero[0] + self.sequence.ac_align["init_line_len"]/2
        x_x_lower_lim = self.input_param.coord_zero[0] - self.sequence.ac_align["init_line_len"]/2

        y_x_upper_lim = self.input_param.coord_zero[1] + self.sequence.ac_align["init_line_len"]/2
        y_x_lower_lim = self.input_param.coord_zero[1] - self.sequence.ac_align["init_line_len"]/2

        for idx, z_coord in enumerate(z_coords):
            if len(z_coords) == 1:
                ax_hist = axes_hist
            else:
                ax_hist = axes_hist[idx]

            # set axis for x and y plots
            if len(z_coords) == idx + 1:
                ax_hist[0].set_xlabel('Elevational [mm]')
                ax_hist[1].set_xlabel('Lateral [mm]')
            else:
                ax_hist[0].get_xaxis().set_visible(False)
                ax_hist[1].get_xaxis().set_visible(False)

            z_coord_wrt_exit_plane = abs(self.input_param.coord_zero[2] - z_coord)

            ax_hist[0].set_ylabel(f'\n {z_coord_wrt_exit_plane:.1f}')

            ax_hist[0].set_xlim(x_x_lower_lim - 15, x_x_upper_lim + 15)
            ax_hist[0].set_ylim(0, self.sequence.ac_align["y_lim"])

            ax_hist[1].get_yaxis().set_visible(False)
            ax_hist[1].set_xlim(y_x_lower_lim - 15, y_x_upper_lim + 15)
            ax_hist[1].set_ylim(0, self.sequence.ac_align["y_lim"])

            logger.info("Finding acoustical axis coordinate for z = " +
                        f"{round(z_coord_wrt_exit_plane, 2)} [mm]")
            self.sequence.coord_start[2] = z_coord

            # Perform iterative search for alignment
            found_x_coords, found_y_coords = self._search_alignment(threshold, initial_line_length,
                                                                    initial_line_step_size, ax_hist)

            # Save the middle point of the scan
            middle_points[idx] = [found_x_coords[-1], found_y_coords[-1], z_coord]

            print(f"Found middle_point: {middle_points[idx]}")

            ax_hist[0].set_title(f'CoM x = {found_x_coords[-1]:.2f} [mm]')
            ax_hist[1].set_title(f'CoM y = {found_y_coords[-1]:.2f} [mm]')

        filename = os.path.join(self.input_param.temp_dir_output,
                                'acoustical_alignment_history_plot_f_wrt_ep_' +
                                f'{self.sequence.focus_wrt_exit_plane:.2f}.png'
                                )

        fig_hist.tight_layout()
        fig_hist.savefig(filename)
        plt.close()

        return middle_points

    def _search_alignment(self, threshold, line_length, line_step_size, ax_hist):
        """
        Iteratively search and converge towards the acoustical center of mass.

        Parameters:
        -----------
        threshold : float
            Threshold for convergence in millimeters.
        line_length : float
            Initial line length for scanning in millimeters.
        line_step_size : float
            Initial step size for scanning in millimeters.
        ax_hist : matplotlib.axes.Axes or array-like
            The axes on which the history plot is drawn: separate axes for x and y coordinates.

        Returns:
        --------
        list, list
            Final x and y coordinates found after iterative alignment.
        """

        found_x_coords = [0, self.input_param.coord_zero[0]]
        found_y_coords = [0, self.input_param.coord_zero[1]]

        z_wrt_exit_plane = round(self.sequence.coord_start[2] -
                                 self.input_param.coord_zero[2], 2)

        print("Acoustical alignment - focus wrt exit plane: " +
              f"{self.sequence.focus_wrt_exit_plane:.2f} [mm], z-measurement" +
              f" wrt exit plane at {z_wrt_exit_plane:.2f} [mm]", end='\n')

        while abs(found_x_coords[-2] - found_x_coords[-1]) > threshold or (
                abs(found_y_coords[-2] - found_y_coords[-1]) > threshold):
            iteration = len(found_x_coords) - 1  # start with 1
            logger.debug(f"Iteration {iteration}: X difference = " +
                         f"{abs(found_x_coords[-2] - found_x_coords[-1]):.4f} mm, " +
                         f"Y difference = {abs(found_y_coords[-2] - found_y_coords[-1]):.4f} mm")

            fig, (ax1, ax2) = plt.subplots(1, 2)

            max_diff = max(abs(found_x_coords[-2] - found_x_coords[-1]), abs(found_y_coords[-2] -
                                                                             found_y_coords[-1]))

            # Scan x and y directions
            found_x_coords.append(self._scan_and_find_center_of_mass(found_x_coords, found_y_coords,
                                                                     line_length,
                                                                     line_step_size,
                                                                     'x', iteration, max_diff,
                                                                     fig, ax1, ax_hist[0]))

            max_diff = max(abs(found_x_coords[-2] - found_x_coords[-1]), abs(found_y_coords[-2] -
                                                                             found_y_coords[-1]))
            found_y_coords.append(self._scan_and_find_center_of_mass(found_x_coords, found_y_coords,
                                                                     line_length,
                                                                     line_step_size,
                                                                     'y',
                                                                     iteration, max_diff,
                                                                     fig, ax2, ax_hist[1]))

            max_diff = max(abs(found_x_coords[-2] - found_x_coords[-1]), abs(found_y_coords[-2] -
                                                                             found_y_coords[-1]))
            z_coord_wrt_exit_plane = abs(self.input_param.coord_zero[2] -
                                         self.sequence.coord_start[2])

            title = (f'Iter. {iteration}, focus & z wrt ex. pl.: ' +
                     f'{self.sequence.focus_wrt_exit_plane:.2f}, {z_coord_wrt_exit_plane:.2f}, ' +
                     f'diff. = {max_diff:.3f} [mm] \n ' +
                     f'CoM [{found_x_coords[-1]:.2f}, {found_y_coords[-1]:.2f}], ' +
                     f'length: {line_length:.1f}, stepsize: {line_step_size:.2f} [mm]')

            fig.suptitle(title)
            fig.supylabel('RMS of total acq. time per grid point [mV]')

            filename = os.path.join(self.input_param.temp_dir_output,
                                    'acoustical_alignment_foc_wep_' +
                                    f'{self.sequence.focus_wrt_exit_plane:.2f}_z_coord_wep_plane_' +
                                    f'{z_coord_wrt_exit_plane:.2f}_iter_{iteration}.png')

            fig.savefig(filename)
            plt.close()

            # TODO: reduction is disabled from the frontend
            # if iteration != 0 and iteration % (self.sequence.ac_align['max_red_iter']) == 0:
            #     # Reduce line length and step size
            #     line_length *= reduction_factor
            #     line_step_size *= reduction_factor

            #     line_n_points = round(line_length / line_step_size)

            #     if (line_n_points % 2) == 0:
            #         line_n_points = line_n_points + 1

            #     self.grid_param["ncol"] = line_n_points
            #     self.sequence.nslices_nrow_ncol = [self.grid_param["nsl"],
            #                                        self.grid_param["nrow"],
            #                                        self.grid_param["ncol"]]

            #     logger.info(f"Reducing search area. New line_length: {line_length:.2f}mm, " +
            #                 f"new line_step_size: {line_step_size:.2f}mm")

        return found_x_coords, found_y_coords

    def _scan_and_find_center_of_mass(self, found_x_coords, found_y_coords, line_length,
                                      line_step_size, direction, iteration, max_diff, fig,
                                      ax, ax_hist):
        """
        Scan in the specified direction and find the center of mass of voltage data.

        Parameters:
        -----------
        found_x_coords : list of float
            Current x-coordinates found in the alignment process.
        found_y_coords : list of float
            Current y-coordinates found in the alignment process.
        line_length : float
            Current line length for the scan in millimeters.
        line_step_size : float
            Current step size for the scan in millimeters.
        direction : str
            'x' or 'y' indicating the direction to scan.

        Returns:
        --------
        float
            Center of mass coordinate in the specified direction.
        """

        if direction == 'x':
            self.sequence.vect_row = np.array([0, 1, 0])
            self.sequence.vect_col = np.array([line_step_size, 0, 0])
            self.sequence.coord_start[0] = found_x_coords[-1] - line_length / 2
            self.sequence.coord_start[1] = found_y_coords[-1]
        else:  # direction == 'y'
            self.sequence.vect_row = np.array([1, 0, 0])
            self.sequence.vect_col = np.array([0, line_step_size, 0])
            self.sequence.coord_start[0] = found_x_coords[-1]
            self.sequence.coord_start[1] = found_y_coords[-1] - line_length / 2

        logger.debug(f"Iteration {iteration}: Scanning in {direction}-direction...")
        print(f"Iteration {iteration}: Scanning in {direction}-direction...", end='\n')
        volt_data, dest_xyz_list = self._scan_grid()

        # Perform RMS to flatten out fluctations
        sqr_volt = np.square(volt_data)
        mean_volt = np.mean(sqr_volt, axis=3)
        rms = np.sqrt(mean_volt).flatten()

        # Calculate center of mass
        cumsum_trapz = cumulative_trapezoid(rms, initial=0).flatten()
        center_of_mass_value = cumsum_trapz[-1] / 2

        coord_index = [0 if direction == 'x' else 1]
        coords = dest_xyz_list[:, :, :, coord_index].flatten()

        center_of_mass_coord = np.interp(center_of_mass_value, cumsum_trapz, coords)

        logger.debug(f"Found center of mass in {direction}-direction: {center_of_mass_coord:.3f} mm")

        if self.sequence.ac_align["create_graphs"]:
            self._plot_center_of_mass_graph(direction, dest_xyz_list, rms, center_of_mass_coord, ax,
                                            ax_hist)

        return center_of_mass_coord

    def _plot_center_of_mass_graph(self, direction, dest_xyz_list, rms, center_of_mass_coord, ax,
                                   ax_hist):
        """
        Plot the center of mass graph for the scanned data.

        Parameters:
        -----------
        direction : str
            'x' or 'y' indicating the direction of the scan.
        dest_xyz_list : list
            List of destination coordinates during the scan.
        max_voltages : np.ndarray
            Array of maximum voltages at each grid point.
        center_of_mass_coord : float
            Calculated center of mass in the specified direction.
        """

        coord_index = [0 if direction == 'x' else 1]
        coords = dest_xyz_list[:, :, :, coord_index].flatten()

        # Plot points to save history
        ax_hist.plot(coords, rms*1000, linestyle='-', linewidth=0.5, marker='.', markersize=2)

        ax.plot(coords, rms*1000, linestyle='-', linewidth=0.5, marker='.', markersize=2)
        ax.axvline(x=center_of_mass_coord, color='r', linestyle='--', linewidth=0.5)

        if direction == 'x':
            x_upper_lim = self.input_param.coord_zero[0] + self.sequence.ac_align["init_line_len"]/2
            x_lower_lim = self.input_param.coord_zero[0] - self.sequence.ac_align["init_line_len"]/2
        else:  # direction == 'y'
            x_upper_lim = self.input_param.coord_zero[1] + self.sequence.ac_align["init_line_len"]/2
            x_lower_lim = self.input_param.coord_zero[1] - self.sequence.ac_align["init_line_len"]/2

        add_x_lim = int(get_config_value(logger, config, 'Characterization',
                                         'Ac_align.additional_x_lim', 15))
        ax.set_xlim(x_lower_lim - add_x_lim, x_upper_lim + add_x_lim)

        if direction == 'y':
            ax.get_yaxis().set_visible(False)

        ax.set_ylim(0, self.sequence.ac_align["y_lim"])
        ax.set_xlabel(f'{direction.upper()}-coordinates [mm]')


def save_acoustical_axis_to_excel(main_sequence, acoustical_axis, coord_zero, output_name):
    """
    Save acoustical axis data to an Excel file if `create_axis_file` is enabled.

    Parameters:
    sequence (object): The sequence object containing alignment parameters and details.
    """
    axial_measurement_length = main_sequence.ac_align["axis_length"]  # [mm]
    axial_measurement_step_size = main_sequence.ac_align["axis_stepsize"]  # [mm]

    # Define the range of t values based on axis length and step size
    t_values = np.arange(0, axial_measurement_length + axial_measurement_step_size,
                         axial_measurement_step_size)

    # Create rows to store data for Excel output
    rows = []
    cluster_nr = 1

    # Calculate coordinates for each t value
    for i, t in enumerate(t_values):
        point = acoustical_axis['origin'] + t * acoustical_axis['direction']

        measurement_nr = i + 1  # Measurement number
        # Store row data for each t value
        rows.append([measurement_nr, cluster_nr, measurement_nr,
                     point[0] - coord_zero[0],
                     point[1] - coord_zero[1],
                     point[2] - coord_zero[2], 1, measurement_nr, 1,
                     point[0], point[1], point[2],
                     ])

    # Define Excel filename
    axis_suffix = get_config_value(logger, config, 'Characterization', 'Ac_align.axis_suffix',
                                   'acoustical_axis')

    excel_filename = output_name + f'_{axis_suffix}.csv'

    # Save the data using the _save_acoustical_axis_data method
    save_acoustical_axis_data(rows, excel_filename)


def save_acoustical_axis_data(rows, filename):
    """
    Save acoustical axis data to an Excel file.

    Parameters:
    rows (list): List of rows containing acoustical axis data.
    filename (str): Name of the Excel file to save the data.
    """

    coord_columns = get_config_value(logger, config, 'Characterization', 'coord_excel_columns', '').split('\n')
    
    df = pd.DataFrame(rows, columns=coord_columns)

    df.to_csv(filename, index=False)

    logger.info(f"Acoustical axis coordinates saved to: {filename}")


def calculate_acoustical_axis(middle_points, z_exit_plane, temp_dir_output):
    """
    Calculate the acoustical axis based on the middle points.

    Parameters:
    middle_points (ndarray): Array of middle points [x, y, z] for the scanned z-coordinates.

    Returns:
    dict: Acoustical axis data containing the origin point and direction vector.
    """
    if len(middle_points) < 2:  # We need at least two points to determine a linear relationship
        logger.error('At least two middle points are needed to calculate ' +
                     'the acoustical axis.')

    average_point = np.mean(middle_points, axis=0)  # centroid used for best linear fit in 3D
    azimuth_av = np.degrees(np.arctan2(average_point[1], average_point[0]))
    elev_av = np.degrees(math.atan(average_point[2]/(math.sqrt(math.pow(average_point[0], 2)
                                                               + math.pow(average_point[1], 2))
                                                     )))

    # Best linear fit
    # Subtract the centroid to get the centered points
    centered_points = middle_points - average_point

    # Perform Singular Value Decomposition (SVD) to find the principal component
    _, _, vh = np.linalg.svd(centered_points)
    direction_vector = vh[0]  # First singular vector gives the direction of the best-fit line
    azimuth_dir = np.degrees(np.arctan2(direction_vector[1], direction_vector[0]))
    elev_dir = np.degrees(math.atan(direction_vector[2]/(math.sqrt(
        math.pow(direction_vector[0], 2) + math.pow(direction_vector[1], 2)))))

    # Calculate the point where z-coordinate is equal to exit plane z coordinate
    t = (z_exit_plane - average_point[2]) / direction_vector[2]
    transducer_z_point = average_point + t * direction_vector

    # Line through the origin in the direction of the direction_vector
    line_length = float(get_config_value(logger, config, 'Characterization',
                                         'Maximum distance wrt exit plane', 140))
    stepsize = float(get_config_value(logger, config, 'Characterization',
                                      'Stepsize for distance wrt exit plane', 0.5))
    n_points = int(math.ceil(line_length*stepsize))
    t = np.linspace(0, line_length, n_points)
    line = transducer_z_point + t[:, None] * direction_vector

    # Plot points and best-fit line
    plt.figure()
    plt.scatter(middle_points[:, 2] - z_exit_plane, middle_points[:, 0], color='black',
                label="Middle x-coordinates")
    plt.scatter(middle_points[:, 2] - z_exit_plane, middle_points[:, 1], color='grey',
                label="Middle y-coordinates")
    plt.plot(line[:, 2] - z_exit_plane, line[:, 0], color='black', label="Fitted SVD x-coordinates")
    plt.plot(line[:, 2] - z_exit_plane, line[:, 1], color='grey', label="Fitted SVD y-coordinates")

    plt.hlines(average_point[0], 0, line_length, colors='black', linestyles='--',
               label="Average x-coordinate")
    plt.hlines(average_point[1], 0, line_length, colors='grey', linestyles='--',
               label="Average y-coordinate")

    plt.xlabel('Distance wrt exit plane [mm]')
    plt.ylabel('X-/Y-coordinates [mm]')
    plt.title(f'Azimuth {azimuth_dir:.2f}, Elevation {elev_dir:.2f} [degrees]')
    plt.legend(bbox_to_anchor=(1.01, 1.01))
    plt.grid()

    plt.savefig(os.path.join(temp_dir_output, 'acoustical_aligment_linear_fit.png'))
    plt.close()

    # Store the origin and direction of the acoustical axis
    acoustical_axis = {
        'origin': transducer_z_point,
        'direction': direction_vector,
        'azimuth of direction': round(azimuth_dir, 2),
        'elevation of direction': round(elev_dir, 2),
        'average': np.round(average_point, 2),
        'azimuth of average': round(azimuth_av, 2),
        'elevation of average': round(elev_av, 2)
    }

    # Log the calculated axis details
    logger.info("Acoustical axis equation:")
    logger.info(f"Origin point: {acoustical_axis['origin']}")
    logger.info(f"Direction vector: {acoustical_axis['direction']}")
    logger.info("Direction vector angles: \n :")
    logger.info(f"    azimuth: {acoustical_axis['azimuth of direction']}")
    logger.info(f"    elevation: {acoustical_axis['elevation of direction']}")

    logger.info(f"Average vector: {acoustical_axis['average']}")
    logger.info("Average vector angles: \n :")
    logger.info(f"    azimuth: {acoustical_axis['azimuth of average']}")
    logger.info(f"    elevation: {acoustical_axis['elevation of average']}")

    logger.info("Equation: xyz_coordinate = origin + t * direction, where t is a scalar " +
                "parameter")

    return acoustical_axis


def write_average_to_cache(acoustical_axis):
    """
    Save average acoustical axis coordinates to the cached input parameters file.

    Updates the `Absolute G code` x, y, and z coordinates in the `Input parameters` section
    of the file specified by `Path of input parameters cache` in the configuration. The
    coordinates are taken from `self.acoustical_axis['average_point']`.

    """

    cached_path = get_config_value(logger, config, 'Characterization',
                                   'Path of input parameters cache',
                                   'config//characterization_input_cache.ini')
    if os.path.exists(cached_path):

        cached_input = configparser.ConfigParser(interpolation=None)
        cached_input.read(cached_path)
        cached_input['Input parameters']['Absolute G code x-coordinate of relative zero [mm]'] = str(acoustical_axis['average'][0])
        cached_input['Input parameters']['Absolute G code y-coordinate of relative zero [mm]'] = str(acoustical_axis['average'][1])

        with open(cached_path, 'w') as inputfile:
            cached_input.write(inputfile)


def process_acoustical_alignment(main_sequence, coord_zero, middle_points, output_name,
                                 temp_dir_output):
    # Calculate and save acoustical axis if needed
    logger.debug(f'Found middle points: {middle_points}')
    acoustical_axis = calculate_acoustical_axis(middle_points, coord_zero[2], temp_dir_output)
    write_average_to_cache(acoustical_axis)
    if main_sequence.ac_align['create_axis_file']:
        save_acoustical_axis_to_excel(main_sequence, acoustical_axis, coord_zero, output_name)
