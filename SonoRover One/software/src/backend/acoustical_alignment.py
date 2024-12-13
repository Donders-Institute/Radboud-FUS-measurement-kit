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
(Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 0.8),
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

        # Validate and prepare output directory and files
        outfile = os.path.join(self.input_param.temp_dir_output,
                               f'sequence_{sequence.seq_number}_output_data.ini')

        self._check_file(outfile)

        # Save parameters and prepare for alignment
        self._save_params_ini()
        logger.info('Used parameters have been saved in a file.')

        self.equipment["ds"].send_sequence(self.sequence)
        logger.info('All driving system parameters are set')

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

        reduction_factor = self.sequence.ac_align["reduction_factor"]
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
                                                                    initial_line_step_size,
                                                                    reduction_factor, ax_hist)

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

        return middle_points

    def _search_alignment(self, threshold, line_length, line_step_size, reduction_factor, ax_hist):
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
        reduction_factor : float
            Factor by which line length and step size are reduced in each iteration.
        ax_hist : matplotlib.axes.Axes or array-like
            The axes on which the history plot is drawn: separate axes for x and y coordinates.

        Returns:
        --------
        list, list
            Final x and y coordinates found after iterative alignment.
        """

        found_x_coords = [0, self.input_param.coord_zero[0]]
        found_y_coords = [0, self.input_param.coord_zero[1]]

        while abs(found_x_coords[-2] - found_x_coords[-1]) > threshold or (
                abs(found_y_coords[-2] - found_y_coords[-1]) > threshold):
            iteration = len(found_x_coords) - 2
            logger.info(f"Iteration {iteration}: X difference = " +
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

            title = (f'CoM [{found_x_coords[-1]:.2f}, {found_y_coords[-1]:.2f}] [mm], Z-coord wrt' +
                     f' exit plane: {z_coord_wrt_exit_plane:.2f} \n ' +
                     f'Iter. {iteration}, Max diff. = {max_diff:.5f} mm, Line length:' +
                     f' {line_length:.1f}, stepsize: {line_step_size:.2f}')

            fig.suptitle(title)
            fig.supylabel('RMS of total acq. time per grid point [mV]')

            filename = os.path.join(self.input_param.temp_dir_output,
                                    f'acoustical_alignment_foc_{z_coord_wrt_exit_plane:.2f}_' +
                                    f'iter_{iteration}.png')

            fig.savefig(filename)

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

        logger.info(f"Scanning in {direction}-direction...")
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

        logger.info(f"Found center of mass in {direction}-direction: {center_of_mass_coord:.3f} mm")

        if self.sequence.ac_align["create_graphs"]:
            self._plot_center_of_mass_graph(direction, dest_xyz_list, rms, center_of_mass_coord,
                                            iteration, ax, ax_hist)

        return center_of_mass_coord

    def _plot_center_of_mass_graph(self, direction, dest_xyz_list, rms, center_of_mass_coord,
                                   iteration, ax, ax_hist):
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
        print(f'red line center_of_mass_coord: {center_of_mass_coord}')

        if direction == 'x':
            x_upper_lim = self.input_param.coord_zero[0] + self.sequence.ac_align["init_line_len"]/2
            x_lower_lim = self.input_param.coord_zero[0] - self.sequence.ac_align["init_line_len"]/2
        else:  # direction == 'y'
            x_upper_lim = self.input_param.coord_zero[1] + self.sequence.ac_align["init_line_len"]/2
            x_lower_lim = self.input_param.coord_zero[1] - self.sequence.ac_align["init_line_len"]/2

        ax.set_xlim(x_lower_lim - 15, x_upper_lim + 15)

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
        rows.append([measurement_nr, cluster_nr, measurement_nr, point[0],
                     point[1], point[2], 1, measurement_nr, 1,
                     point[0] - coord_zero[0],
                     point[1] - coord_zero[1],
                     point[2] - coord_zero[2]
                     ])

    # Define Excel filename
    excel_filename = output_name + '_acoustical_axis.xlsx'

    # Save the data using the _save_acoustical_axis_data method
    save_acoustical_axis_data(rows, excel_filename)
    logger.info(f"Acoustical axis coordinates saved to: {excel_filename}")


def save_acoustical_axis_data(rows, filename):
    """
    Save acoustical axis data to an Excel file.

    Parameters:
    rows (list): List of rows containing acoustical axis data.
    filename (str): Name of the Excel file to save the data.
    """
    df = pd.DataFrame(rows, columns=['Measurement number', 'Cluster number',
                                     'Indices number', 'X-coordinate [mm]',
                                     'Y-coordinate [mm]', 'Z-coordinate [mm]',
                                     'Row number', 'Column number',
                                     'Slice number',
                                     'Absolute X-coordinate [mm]',
                                     'Absolute Y-coordinate [mm]',
                                     'Absolute Z-coordinate [mm]'])

    df.to_excel(filename, index=False)

    logger.info(f"Acoustical axis coordinates saved to: {filename}")


def calculate_acoustical_axis(middle_points, z_exit_plane):
    """
    Calculate the acoustical axis based on the middle points.

    Parameters:
    middle_points (ndarray): Array of middle points [x, y, z] for the scanned z-coordinates.

    Returns:
    dict: Acoustical axis data containing the origin point and direction vector.
    """
    if len(middle_points) > 1:  # We need at least two points to determine a linear relationship
        point1 = middle_points[0]
        point2 = middle_points[-1]  # grab last point to calculate directional vector

        # Calculate direction vector and unit vector for the acoustical axis
        direction_vector = point2 - point1
        unit_vector = direction_vector / np.linalg.norm(direction_vector)
        azimuth_dir = np.degrees(np.arctan2(unit_vector[1], unit_vector[0]))
        elev_dir = np.degrees(math.atan(unit_vector[2]/(math.sqrt(math.pow(unit_vector[0], 2)
                                                                  + math.pow(unit_vector[1], 2))
                                                        )))

        average_point = np.mean(middle_points, axis=0)
        azimuth_av = np.degrees(np.arctan2(average_point[1], average_point[0]))
        elev_av = np.degrees(math.atan(average_point[2]/(math.sqrt(math.pow(average_point[0], 2)
                                                                   + math.pow(average_point[1], 2))
                                                         )))

        # Calculate the point where z-coordinate is equal to self.input_param.coord_zero[2]
        t = (z_exit_plane - point1[2]) / direction_vector[2]
        transducer_z_point = point1 + t * direction_vector

        # Store the origin and direction of the acoustical axis
        acoustical_axis = {
            'origin': transducer_z_point,
            'direction': unit_vector,
            'azimuth of direction': azimuth_dir,
            'elevation of direction': elev_dir,
            'average': average_point,
            'azimuth of average': azimuth_av,
            'elevation of average': elev_av
        }

        # Log the calculated axis details
        logger.info("Acoustical axis equation:")
        logger.info(f"Origin point: {acoustical_axis['origin']}")
        logger.info(f"Direction vector: {acoustical_axis['direction']}")
        logger.info("Direction vector angles: \n :")
        logger.info(f"    aximuth: {acoustical_axis['azimuth of direction']}")
        logger.info(f"    elevation: {acoustical_axis['elevation of direction']}")

        logger.info(f"Average vector: {acoustical_axis['average']}")
        logger.info("Average vector angles: \n :")
        logger.info(f"    aximuth: {acoustical_axis['azimuth of average']}")
        logger.info(f"    elevation: {acoustical_axis['elevation of average']}")

        logger.info("Equation: xyz_coordinate = origin + t * direction, where t is a scalar " +
                    "parameter")

        return acoustical_axis
    else:
        logger.error('At least two middle points are needed to calculate ' +
                     'the acoustical axis.')


def write_average_to_cache(acoustical_axis):
    """
    Save average acoustical axis coordinates to the cached input parameters file.

    Updates the `Absolute G code` x, y, and z coordinates in the `Input parameters` section
    of the file specified by `Path of input parameters cache` in the configuration. The
    coordinates are taken from `self.acoustical_axis['average_point']`.

    """

    cached_path = config['Characterization']['Path of input parameters cache']
    if os.path.exists(cached_path):

        cached_input = configparser.ConfigParser(interpolation=None)
        cached_input.read(cached_path)
        cached_input['Input parameters']['Absolute G code x-coordinate of relative zero [mm]'] = str(acoustical_axis['average'][0])
        cached_input['Input parameters']['Absolute G code y-coordinate of relative zero [mm]'] = str(acoustical_axis['average'][1])

        with open(cached_path, 'w') as inputfile:
            cached_input.write(inputfile)


def process_acoustical_alignment(main_sequence, coord_zero, middle_points, output_name):
    # Calculate and save acoustical axis if needed
    logger.info(f'Found middle points: {middle_points}')
    acoustical_axis = calculate_acoustical_axis(middle_points, coord_zero[2])
    write_average_to_cache(acoustical_axis)
    if main_sequence.ac_align['create_axis_file']:
        save_acoustical_axis_to_excel(main_sequence, acoustical_axis, coord_zero, output_name)
