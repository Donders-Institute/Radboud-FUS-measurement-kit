# Radboud FUS measurement kit
<a name="readme-top"></a>

<div align="center">
  <img src="/images/Radboud-logo.jpg" alt="ru_logo" width="auto"  height="65" />

  <img src="/images/fuslogo.png" alt="fus_logo" width="auto" height="67">

  <img src="/images/igtlogo.jpeg" alt="igt_logo" width="auto" height="65">
  
</div>

https://github.com/user-attachments/assets/676b7667-6fb5-469c-bd78-fa9b3e943115

<div align="center">
  
  <img src="/images/sonorover-one-extended.png" alt="sonorover-one" width="1000"  height="auto" />
  
</div>

<!-- TABLE OF CONTENTS -->

# 📗 Table of Contents

- [📖 About the Project](#about-project)
  - [🚀 Key Features](#key-features)
  - [👥 Authors](#authors)
  - [✒️ How to cite](#how-to-cite)
- [💻 Getting Started](#getting-started)
  - [🔧 Installation](#install)
  - [🔌 Compatibility](#comp)
  - [📋 Usage](#usage)
- [📊 Data Analysis](#data-analysis)
- [🧰 Configuration](#config)
  - [⚙ Main Configuration File](#main-config)
  - [📻 How to add your own equipment](#add-equip)
- [🔭 Future Features](#future-features)
- [🤝 Contributing](#contributing)
- [📝 License](#license)

<!-- PROJECT DESCRIPTION -->

# 📖 Radboud FUS measurement kit <a name="about-project"></a>

(Project id: **0003429**)

**Radboud FUS measurement kit** is a comprehensive kit allowing precise hydrophone measurements of your TUS transducers for verification, characterization and monitoring overall system performance.    

This project is facilitated by the Radboud Focused Ultrasound Initiative. For more information, please visit the [website](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus).

**⚠️ DEVELOPMENT STATUS**: This repository is currently under active development and is provided AS IS. Features may be incomplete, undergo significant changes, or contain bugs. Use at your own discretion.

<!-- Features -->

## 🚀 Key Features <a name="key-features"></a>

- **Comprehensive Measurement Solution:** Complete hardware and software package for ultrasound field characterization
- **High Precision Hydrophone Measurements:** Accurate characterization of acoustic parameters and beam profiles
- **Modular, Extensible Architecture:** Easily add new equipment with standardized interfaces
- **Seamless Hardware Integration:** Compatible with multiple driving systems, transducers, and measurement devices
- **Automated Acoustical Alignment:** Precise determination of the acoustical axis for optimal measurements
- **Open-Source Software:** Fully transparent, customizable codebase with no licensing costs
- **Complementary Data Analysis Tools:** Export and analyze measurement data with included utilities

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- AUTHORS -->

## 👥 Authors <a name="authors"></a>

👤 **[Stein Fekkes](https://www.ru.nl/en/people/fekkes-s), [FUS Initiative](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus), Radboud University**

- GitHub: [@StefFek-GIT](https://github.com/StefFek-GIT)
- [LinkedIn](https://linkedin.com/in/sfekkes)

👤 **[Margely Cornelissen](https://www.ru.nl/en/people/cornelissen-m), [FUS Initiative](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus), Radboud University**

- GitHub: [@MaCuinea](https://github.com/MaCuinea)
- [LinkedIn](https://linkedin.com/in/margely-cornelissen)

👤 **Erik Dumont, [Image Guided Therapy (IGT)](http://www.imageguidedtherapy.com/)**
- GitHub: [@erikdumontigt](https://github.com/erikdumontigt)
- [LinkedIn](https://linkedin.com/in/erik-dumont-986a814)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## ✒️ How to cite <a name="how-to-cite"></a>

If you use this kit in your research or project, please cite it as follows:

Stein Fekkes, Margely Cornelissen (Radboud University, Nijmegen, The Netherlands) & Erik Dumont (Image Guided Therapy, Pessac, France) (2025), Radboud FUS measurement kit (version 1.2), https://github.com/Donders-Institute/Radboud-FUS-measurement-kit

<!-- GETTING STARTED -->

# 💻 Getting Started <a name="getting-started"></a>

## 🔧 Installation <a name="install"></a>

### Hardware

The hardware files are stored as native solidworks files and as step format. The main assembly file: W0003510-00-01-SonoRover One.SLDASM will contain all references to part files and subassemblies. REFERENCE TO MANUAL.

### Software

#### System Architecture

Before diving into the installation, it is helpful to understand how the SonoRover One software is structured. The SonoRover One software is built on top of the standardized [Radboud FUS driving system software package](https://github.com/Donders-Institute/Radboud-FUS-driving-system-software). 

<br /> 
<div align="center">
  <img src="/images/software_architecture.png" alt="Software Architecture" width="700" height="auto" />
</div>

<br /> 

This modular approach provides:

- **Equipment Flexibility**: Easily incorporate new equipment with different communication protocols
- **Centralized Updates**: Core driving functionality can be updated independently
- **Consistent Interface**: Uniform interaction with diverse hardware components
- **Dual-Use Capability**: The same equipment configurations work in both standalone experiments and hydrophone measurements

#### Important Note

**This package is developed specifically for Windows operating systems.** While it might work in other environments with some modifications, full support is provided only for Windows.

#### Installation Steps

1. **Clone the Repository**\
   You can clone this repository using either:

   - **Git Terminal**
     ```sh
     cd my-folder
     git clone git@github.com:Donders-Institute/Radboud-FUS-measurement-kit.git
     ```

   - **GitHub Desktop**
     1. Click on 'Current repository'
     2. Click on 'Add' and select 'Clone repository...'
     3. Choose 'URL' and paste the following repository URL: [https://github.com/Donders-Institute/Radboud-FUS-measurement-kit.git](https://github.com/Donders-Institute/Radboud-FUS-measurement-kit.git)
     4. Choose your desired folder and clone the repository

2. **Download Python 3.10**\
Ensure you have Python 3.10 installed and accessible from your command line. If Python is not installed, download it from the [official Python website](https://www.python.org/downloads/release/python-31011/). It is not necessary to add Python to your system's PATH during installation, as virtual environments allow you to manage and switch between Python versions without affecting other projects or code outside the environment.

	<br /> 
	<div align="center">
	  <img src="/images/python_path.png" alt="python_path" width="auto"  height="auto" />
	</div>
	
	<br /> 

	**Note**: The script assumes that Python 3.10 is installed. If you have a different version, make sure to adjust the script accordingly or install Python 3.10.

3. **Create and setup a virtual environment**\
Open your command prompt and run the following batch file to set up the virtual environment and install the necessary dependencies. You can use input parameters to customize the environment name or directory, or Python interpreter location. You can use the default values or specify only the parameters you need by leaving others blank with "".

	```
	cd your_directory_with_cloned_repository
	create_venv.bat "[PYTHON_INTERPRETER_PATH]" [VENV_NAME] "[VENV_DIR]"
	```
		
	- PYTHON_INTERPRETER_PATH: Specify the path to the Python 3.10 interpreter if it is not in the default location. For example, C:\Path\To\Python310\python.exe.
	- VENV_NAME: Specify the name for the virtual environment (e.g., MyEnv). If not provided, it defaults to SONOROVER_ONE.
	- VENV_DIR: Specify the directory for the virtual environment (e.g., C:/Users/Me/Envs). If not provided, it defaults to C:/Users/{USERPROFILE}/Envs.
	
	Example:
	```
	create_venv.bat "C:\Path\To\Python310\python.exe" SONOROVER_ONE "C:/Users/Me/Envs"
	```

	The batch file will:
	- Create a virtual environment
	- Install the required Python packages and the default IDE, Spyder
	- Clone the Radboud FUS driving system software repository into the SonoRover One repository. **Note:** The installation script automatically clones the latest released version of the Radboud FUS driving system software. If you need a different version (e.g., development branch or specific release), please refer to the [Radboud FUS driving system software README](https://github.com/Donders-Institute/Radboud-FUS-driving-system-software/blob/release/README.md) for manual installation instructions.
	- Install the Radboud FUS driving system software package

4. **Verify Installation**\
After running the batch file, ensure that the virtual environment and dependencies are installed. You can verify this by:

	- Checking for the virtual environment folder in your VENV_DIR directory.
		<div align="left">
		  <img src="/images/verify_venv.png" alt="verify_venv" width="auto"  height="auto" />
		</div>
	
	- Confirming that the fus_driving_systems package is installed in the virtual environment site-packages folder: VENV_DIR/VENV_NAME/Lib/site-packages/.
		<div align="center">
		  <img src="/images/verify_fus_package.png" alt="verify_fus_package" width="auto"  height="auto" />
		</div>

#### Troubleshooting
If you encounter issues with the batch file not being recognized or errors during execution, ensure that:

- The batch file has the correct permissions to execute.
- The repository has been cloned correctly and contains the necessary files.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 🔌 Compatibility <a name="comp"></a>

The table below outlines compatibility between different versions of the Radboud FUS driving system software and the SonoRover One software.

| SonoRover One Version | Radboud FDS Compatibility | Python Version |
|---------------------|----------------|----------------------------|
| 1.2 (Current) | Radboud FDS v2.1 | 3.10  |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📋 Usage <a name="usage"></a>

### Hardware
REFERENCE TO MANUAL.

### Software

*Step 1: Activate your environment*\
With all dependencies installed, activate your environment in your command prompt. 

```
call [VENV_PATH]\Scripts\activate
```

*Step 2: Install an IDE*\
While your virtual environment is activated, you can install any IDE of your choice. Spyder is pre-installed by default. To install another IDE, run:

```
pip install [IDE]
```

*Step 3: Launch the IDE*\
After installing your IDE, you can launch it directly from the command line while the virtual environment is activated. For Spyder, enter:

```
spyder
```

#### Activate your virtual environment and launch the IDE at once
To simplify the process of activating the virtual environment and launching your IDE, you can use the provided [batch script](start_venv_and_ide.bat).

How to use the script:
1. Ensure that start_env_and_ide.bat is located in a convenient location, such as the root directory of your project or your desktop.
2. Run the script in one of the following ways:
	- Open start_venv_and_ide.bat in a text editor and modify the VENV_PATH and IDE variables directly if you prefer not to use command-line arguments. To run the .bat file, just double-click it.
	- Using the command prompt:
		```
		start_venv_and_ide.bat [VENV_PATH] [IDE]
		```
		- VENV_PATH: Specify the path to the virtual environment (e.g., C:/Users/Me/Envs/MyEnv). If not provided, it defaults to C:/Users/{USERPROFILE}/Envs/SONOROVER_ONE.
		- IDE: Specify the python interpreter. If not provided, it defaults to spyder.

#### Starting the Software
The SonoRover One software provides a graphical interface for hydrophone measurements. This section guides you through using the software.

The primary script is [main](/SonoRover%20One/software/src/main.py). Running this script launches the main GUI:

<div align="left">
  <img src="/images/GUI_main.png" alt="gui_main" width="1000" height="auto" />
</div>

##### Main GUI Parameters

The main interface allows you to configure the following parameters:

1. **Protocol**: Opens a dialog to select a measurement protocol
2. **COM port of positioning system**: Select the communication port for the positioning system
3. **Hydrophone**: Select the hydrophone model to use for measurements
4. **Hydrophone acquisition time [us]**: Set the signal acquisition duration per grid point
5. **PicoScope**: Select the PicoScope model for signal acquisition
6. **Picoscope sampling frequency multiplication factor**: Set the sampling rate (minimum factor is 2)
7. **Temperature of water [C]**: Record water temperature for post-processing
8. **Dissolved oxygen level of water [mg/L]**: Record for documentation purposes
9. **Absolute G code coordinates of relative zero**: Set coordinates for the reference zero point. This initially uses the mechanical alignment coordinates as its basis. After completing an acoustical alignment, the system updates the x- and y-coordinates to match the measured acoustical axis at the specified z-coordinate.
10. **Perform all protocols in sequence without waiting for user input?**: Toggle automatic sequence execution

##### Protocol Selection

When you click the "Select" button, a dialog appears with system setup parameters:

- **US Driving System**: Select the ultrasound system
- **COM port of US driving system**: Required for Sonic Concepts systems
- **Transducer**: Select the transducer model
- **Operating frequency [kHz]**: Set the operating frequency of the transducer

After setting these general parameters, you have to choose between two protocol options:

*Option 1: Select Protocol Excel File*

<div align="left">
  <img src="/images/GUI_protocol_excel.png" alt="gui_protocol_excel" width="1000" height="auto" />
</div>

This option allows you to select an Excel file containing predefined measurement protocols.
- **Path and filename of protocol excel file**: Select the Excel file containing measurement protocols
  - Template available [here](SonoRover%20One/software/example%20input/protocol%20template/template_protocol_input.xlsx)
  - **Note**: If you modify column headers in the Excel file, update the corresponding settings in the configuration file

The protocol Excel file contains the following parameters for each sequence:

| Parameter | Description |
|-----------|-------------|
| **Sequence number** | Sequential number (1 to N) |
| **Tag** | Additional information saved in output .ini file |
| **Modulation** | Select from Rectangular - no ramping, Linear, or Tukey ramp shapes |
| **Ramp duration [us]** | Duration of the ramp |
| **Pulse duration [us]** | Duration of each pulse |
| **Pulse Repetition Interval [ms]** | Total pulse period including ramping, pulse duration and off-time between two pulses |
| **Power parameter** | Select appropriate power parameter for your system:<br>- IGT: Amplitude [%], Voltage [V], or Max. pressure [MPa]<br>- Sonic Concepts: Global power [mW] |
| **Corresponding value** | Value for the selected power parameter |
| **Focus definition** | Define focus relative to exit plane or mid bowl |
| **Corresponding value** | Value for the selected focus parameter |
| **(De)phase array [degree]** | For IGT systems only: option to create sham conditions |
| **Coordinates source** | Choose between coordinate Excel file or parameter-defined grid |

If using a **coordinate Excel file**:
- Provide path to the file (examples [here](SonoRover%20One/software/example%20input/coordinate%20templates))
- Allows flexible grid point arrangement
- **Note**: Headers must match configuration settings

If using **parameters**:
- **max. ± x/y/z [mm]**: Maximum movement in each direction relative to zero point
- **direction_slices/rows/columns**: Direction settings (refer to [template](SonoRover%20One/software/example%20input/protocol%20template/template_protocol_input.xlsx))
- **step_size_x/y/z [mm]**: Grid size in each direction

*Option 2: Acoustical Alignment*

<div align="left">
  <img src="/images/GUI_protocol_ac_align.png" alt="gui_protocol_ac_align" width="1000" height="auto" />
</div>

<br />

This option performs an acoustical alignment to determine the acoustical axis through iterative measurements. The process finds the center of mass of RMS voltage values per defined location and calculates the direction vector with corresponding azimuth and elevation.

Parameters include:

| Parameter | Description |
|-----------|-------------|
| **Path of output directory** | Directory for saving output and logging files |
| **Pulse duration [us]** | Duration of each pulse |
| **Pulse Repetition Interval [ms]** | Total pulse period including ramping, pulse duration and off-time between two pulses |
| **Power setting** | Appropriate power parameter for your system |
| **Focus** | Define focus relative to exit plane or mid bowl |
| **Distance from focus wrt exit plane [mm] array** | Distances from the focus wrt exit plane to acquire middle points (negative = toward transducer) |
| **Line length [mm]** | Length of each direction scan |
| **Line stepsize [mm]** | Step size of direction scan |
| **Threshold [mm]** | Convergence threshold for determining middle points |
| **Create graphs** | Toggle creation of direction scan graphs |
| **Y axis limit [mV]** | Y-axis limit for RMS value display |
| **Create axial measurement file** | Toggle creation of coordinate file for axial scan |
| **Length of axial measurement [mm]** | Define length for axial scan |
| **Stepsize of axial measurement [mm]** | Define step size for axial scan |

**Note:** The coordinate file generated by the acoustical alignment can be used as input for a subsequent measurement. This allows you to perform an axial scan along the precisely determined acoustical axis, rather than along a mechanically aligned axis.

#### Running Measurements

After configuring all parameters, click "OK" to start the characterization process. The software will:

1. Display dialog screens to verify equipment connections
2. Create log files in the same directory as the protocol file
3. Create an output folder for measurement results
4. Begin the measurement sequence

If you selected "Perform all protocols in sequence without waiting for user input," the software will automatically proceed through all sequences defined in the protocol file.

#### Important Notes

- When performing acoustical alignment, the found X and Y values will overwrite the initial absolute G code coordinates
- Ensure the PicoScope software is not connected to the PicoScope during measurements
- Ensure Universal Gcode Sender is not connected to the positioning system

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# 📊 Data Analysis <a name="data-analysis"></a>

REFERENCE TO MANUAL

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONFIGURATION -->

# 🧰 Configuration <a name="config"></a>

The SonoRover One software uses a comprehensive configuration system to control its behavior. This section explains how to modify configuration settings and add new equipment to the system.

## ⚙️ Main Configuration File <a name="main-config"></a>

The main configuration file is located at [here](SonoRover%20One/software/src/config/characterization_config.ini). You can either modify this file directly or use the provided [create_config.py](SonoRover%20One/software/src/config/create_config.py) script to regenerate it with your changes.

### General Settings

```ini
[General]
maximum number of output filename = 1000
```

- **maximum number of output filename**: Sets the maximum number of sequentially numbered output files (1000 by default). When multiple files share the same base name, the system appends numbers (1, 2, 3...) until this limit is reached.

### Logging Configuration

```ini
[Logging]
logger name = SonoRover_One
timestamp format = %Y-%m-%d_%H-%M-%S
log level console = WARNING
log level file = INFO
initial part of log filename = log_
```

- **logger name**: Identifier for the logger instance
- **timestamp format**: Format used for timestamps in logs 
- **log level console**: Minimum severity level displayed in console (INFO, DEBUG, WARNING, ERROR, CRITICAL)
- **log level file**: Minimum severity level saved to log files (INFO, DEBUG, WARNING, ERROR, CRITICAL)
- **initial part of log filename**: Prefix for all generated log files

### Path and Directory Settings

```ini
[Characterization]
path of input parameters cache = config//characterization_input_cache.ini
cache date format = %Y/%m/%d
temporary output path = C:\Temp\General output folder
temporary logging path = C:\Temp\General output folder\logs
default protocol directory = //ru.nl//WrkGrp//FUS_Hub//Hydrophone measurements//Measurements
default output directory = //ru.nl//WrkGrp//FUS_Hub//Hydrophone measurements//Measurements//2024//General output folder
```

- **path of input parameters cache**: Location where user input parameters are cached
- **cache date format**: Date format used in the cache file
- **temporary output path**: Directory that temporarily stores measurement output. This approach allows data to be transferred to an online folder after acquisition is complete, without slowing down the measurement process. 
- **temporary logging path**: Directory that temporarily stores logging. This approach allows data to be transferred to an online folder after acquisition is complete, without slowing down the measurement process. 
- **default protocol directory**: Default location for measurement protocols displayed in GUI
- **default output directory**: Default location for saving measurement results displayed in GUI

### GUI Configuration

```ini
protocol_dialog.n_ac_align_rows = 14
protocol_dialog.stay_topmost_in_ms = 5000
input_dialog.stay_topmost_in_ms = 5000
acd_dialog.stay_topmost_in_ms = 5000
```

- **protocol_dialog.n_ac_align_rows**: Number of rows in acoustical alignment section
- **protocol_dialog.stay_topmost_in_ms**: Duration for keeping protocol dialog on top (5000ms)
- **input_dialog.stay_topmost_in_ms**: Duration for keeping input dialog on top (5000ms)
- **acd_dialog.stay_topmost_in_ms**: Duration for keeping ACD dialog on top (5000ms)

### Output Configuration

```ini
output_name_suffix = output_data
ac_align.output_name_suffix = output_data
ac_align.axis_suffix = acoustical_axis
ac_align.additional_x_lim = 15
```

- **output_name_suffix**: Suffix for output data files
- **ac_align.output_name_suffix**: Suffix for acoustical alignment output files
- **ac_align.axis_suffix**: Suffix for acoustical axis plots
- **ac_align.additional_x_lim**: Additional space added to X-axis limit of acoustical alignment plot (15 mm)

### Acquisition Equipment Configuration

```ini
picoscope.reacquire_attempts = 5
picoscope.resolution = DR_14BIT
picoscope.channel = A
picoscope.range = RANGE_500mV
picoscope.coupling = DC
picoscope.probe_multi = x1
picoscope.trigger_threshold_v = 0.5
pos_sys.reacquire_attempts = 5
```

- **picoscope.reacquire_attempts**: Number of retry attempts for acquisition (5)
- **picoscope.resolution**: Hardware resolution during acquisition (DR_14BIT)
- **picoscope.channel**: Input channel for hydrophone connection (A)
- **picoscope.range**: Voltage range setting (RANGE_500mV)
- **picoscope.coupling**: Input coupling mode (DC)
- **picoscope.probe_multi**: Probe attenuation multiplier (x1)
- **picoscope.trigger_threshold_v**: Trigger threshold voltage (0.5V)
- **pos_sys.reacquire_attempts**: Number of attempts to reconnect to positioning system (5)

### Excel Column Definitions

The configuration file defines column names used in coordinate and protocol Excel files. If you modify the headers in your Excel templates, you will need to update these settings to match.

```ini
coord_excel_columns.meas_num = Measurement number
coord_excel_columns.clus_num = Cluster number
coord_excel_columns.ind_num = Indices number
# ... more column definitions
```

```ini
prot_excel_columns.seq_num = Sequence number
prot_excel_columns.tag = Tag
prot_excel_columns.dephasing = (De)phase array [degree] (None = no (de)phasing) ONLY FOR IGT DS
# ... more column definitions
```

### Default Values
The configuration file contains default values for the GUI inputs. These values are loaded when the software starts and are used as initial values in the interface.

```ini
default.acq_time_us = 500
default.sampl_freq_multi = 50
default.pos_com_port = COM3
default.temp = 
default.dis_oxy = 
default.x_coord_zero = -62.2
default.y_coord_zero = -60.6
default.z_coord_zero = -155.528
default.perform_all_seqs = True
# ... more default settings
```

You can modify these values to match your typical usage patterns. Equipment-specific defaults (like default driving system) are determined by the Radboud-FUS-driving-system-software configuration.

### Messages
The configuration file also defines various messages displayed to users during the measurement process:

```ini
disconnection message = Ensure the following: 
     - PicoScope software is not connected to the PicoScope in use. 
     - Universal Gcode Sender is not connected to the positioning system.
continue acquisition message = Continue acquisition with the following sequence: 
```

These messages can be customized to provide clearer instructions to users of your system.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📻 Adding Your Own Equipment <a name="add-equip"></a>

### FUS Equipment

To add your own FUS equipment, refer to the [Radboud-FUS-driving-system-software README](https://github.com/Donders-Institute/Radboud-FUS-driving-system-software), as the SonoRover One software uses this as a plugin for controlling FUS equipment. 

### Hydrophone

The current software version supports the following hydrophones:
- HGL 0200 SN2845
- HGL 0200 SN3030
- HNR 0500 SN2439

To add a new hydrophone:

#### Step 1: Add to Equipment Section
Add your hydrophone to the configuration file under the `[Characterization.Equipment]` section:

```ini
[Characterization.Equipment]
hydrophones = HGL 0200 SN2845
    HGL 0200 SN3030
    HNR 0500 SN2439
    YOUR-MODEL-NAME  # Add your hydrophone model here
```

#### Step 2: Add Specific Equipment Settings
Create a new section for your hydrophone model:

```ini
[Characterization.Equipment.YOUR-MODEL-NAME]
name = Hydrophone YOUR-MODEL-NAME
sensitivity (v/pa) datasheet = config//hydrophones//YOUR-MODEL-NAME Calibration datasheet.xlsx
```

The hydrophone identifier must match one of the identifiers defined in the  `[Characterization.Equipment]` section under *hydrophones*. The `name` parameter is displayed in the GUI.

#### Step 3: Create a Sensitivity Datasheet
Create a new datasheet in the [SonoRover One\software\src\config\hydrophones](SonoRover%20One/software/src/config/hydrophones) folder, using one of the existing files as a template. This file contains the frequency-sensitivity mapping for your hydrophone.

If sensitivity values are not known, set all values to zero, but note that measurement output values will be incorrect. 

### PicoScope

Currently, only PicoScope oscilloscopes are supported. The software supports these models:
- 5442D
- 5442A
- 5244D 

To add a new PicoScope model:

#### Step 1: Extend pico.py
Extend the [pico.py](SonoRover%20One/software/src/backend/pico.py) script with a class for your PicoScope model:

```python
class ScopeYOUR_MODEL_ID(Scope5000):
    """
    Model YOUR-MODEL-ID description
    """
    def __init__(self):
        Scope5000.__init__(self)
        self.model = ModelSpecification("YOUR-MODEL-ID", "PS5000a.dll", "ps5000a")
        self.model.handle = None
        self.model.channelCount = 2
        self.model.maxGeneratorFrequency = 20e6  # 20 MHz and min = 0
        self.model.maxTimeBase = (2 ** 32) - 1
        self.model.maxLowSamplingRate = 125e6
        self.model.maxHighSamplingRate = 1e9
        self.model.EXTRange = Range.RANGE_5V
        self.model.EXTmaxADC = 32767  # PS5000A_EXT_MAX_VALUE
        # self.model.resolution = None  # set in OpenUnit
        self._clearSettings()
```

Then modify the `getScope` function to include your model:

```python
def getScope(modelName):
    """
    Returns an instance of the Scope object for the requested model.
    """
    if modelName.startswith("5242"):
        return Scope5242A()
    elif modelName.startswith("5442"):
        return Scope5442A()
    elif modelName.startswith("5244"):
        return Scope5244D()
    elif modelName.startswith("YOUR-MODEL-ID"):  # Add your model check
        return ScopeYOUR_MODEL_ID()
    raise PicoError("Unsupported model (%s)." % modelName)
```

#### Step 2: Add to Equipment Section
Add your PicoScope to the configuration file under the `[Characterization.Equipment]` section:

```ini
[Characterization.Equipment]
picoscopes = 5442D
    5242D
    5442A
    5244D
    YOUR-MODEL-NAME  # Add your PicoScope model here
```

#### Step 3: Add Specific Equipment Settings
Create a new section for your PicoScope model:

```ini
[Characterization.Equipment.YOUR-MODEL-NAME]
name = PicoScope YOUR-MODEL-NAME
pico.py identification = YOUR-MODEL-ID
```

The `pico.py identification` parameter must match the identifier used in the `getScope` function in pico.py. The `name` parameter is displayed in the GUI.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- FUTURE FEATURES -->

# 🔭 Future Features <a name="future-features"></a>

## Software

- [ ] Eliminate Excel dependencies through GUI expansion and restructuring
- [ ] Implement line scanning capability for faster acquisition
- [ ] Develop comprehensive unit test framework
- [ ] Add timer functionality
- [ ] Implement signal detection check before proceeding with measurements

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

# 🤝 Contributing <a name="contributing"></a>

Contributions, issues, and feature requests are welcome!

Feel free to check the [issues page](../../issues/).

If you have any questions, please feel free to reach out to us via email at fus@ru.nl.
We'd love to hear from you.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# 📝 License <a name="license"></a>

This project is [MIT](./LICENSE) licensed.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

