# Radboud FUS measurement kit
<a name="readme-top"></a>

<div align="center">
  <img src="/images/Radboud-logo.jpg" alt="ru_logo" width="auto"  height="70" />

  <img src="/images/fuslogo.png" alt="fus_logo" width="auto" height="70">

  <img src="/images/igtlogo.jpeg" alt="igt_logo" width="auto" height="70">
  
</div>

<div align="center">
  
  <img src="/images/sonorover-one.png" alt="sonorover-one" width="1000"  height="auto" />
  
</div>

<!-- TABLE OF CONTENTS -->

# 📗 Table of Contents

- [📖 About the Project](#about-project)
  - [🚀 Key Features](#key-features)
  - [👥 Authors](#authors)
  - [✒️ How to cite](#how-to-cite)
- [💻 Getting Started](#getting-started)
  - [🔧 Installation](#install)
  - [📋 Usage](#usage)
- [🧰 Configuration](#config)
  - [⚙ Main Configuration File](#main-config)
  - [📻 How to add your own equipment](#add-equip)
- [🔭 Future Features](#future-features)
- [🤝 Contributing](#contributing)
- [📝 License](#license)

<!-- PROJECT DESCRIPTION -->

# 📖 Radboud FUS measurement kit <a name="about-project"></a>

(Project id: **0003429** )

**Radboud FUS measurement kit** is a comprehensive kit allowing precise hydrophone measurements of your TUS transducers for verification, characterization and monitoring overall system performance.    

This project is facilitated by the Radboud Focused Ultrasound Initiative. For more information, please visit the [website](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus).

<!-- Features -->

## 🚀 Key Features <a name="key-features"></a>

- **Affordable**
- **High quality**

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

Margely Cornelissen, Stein Fekkes (Radboud University, Nijmegen, The Netherlands) & Erik Dumont (Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 1.0), https://github.com/Donders-Institute/Radboud-FUS-measurement-kit

<!-- GETTING STARTED -->

# 💻 Getting Started <a name="getting-started"></a>

## 🔧 Installation <a name="install"></a>

### Hardware

The hardware files are stored as native solidworks files and as step format. The main assembly file: W0003510-00-01-SonoRover One.SLDASM will contain all references to part files and subassemblies.

### Software

#### Important Note

**This package is developed specifically for Windows operating systems.** While it might work in other environments with some modifications, full support is provided only for Windows.

Clone this repository to your desired folder:

- Git terminal

	``` sh
		cd my-folder
		git clone git@github.com:Donders-Institute/Radboud-FUS-measurement-kit.git
	```

- GitHub Desktop
	1. Click on 'Current repository'.
	2. Click on 'Add' and select 'Clone repository...'.
	3. Choose 'URL' and paste the following repository URL: [https://github.com/Donders-Institute/Radboud-FUS-measurement-kit.git](https://github.com/Donders-Institute/Radboud-FUS-measurement-kit.git)
	4. Choose your desired folder and clone the repository.

**Seamless Integration and Compatibility**: The current SonoRover One software utilizes a standardized [focused ultrasound driving system software package](https://github.com/Donders-Institute/Radboud-FUS-driving-system-software). This approach allows you to easily incorporate equipment with different communication protocols into the Radboud FUS driving system software, making it available in the SonoRover One system. By following an abstract communication structure, the software can seamlessly operate with equipment from various manufacturers, ensuring consistent, centralized updates and eliminating the need for direct management of communication protocols in both standalone and experimental settings.

Open your command prompt and run the following batch file to set up the virtual environment and install the necessary dependencies. You can use input parameters to customize the environment name or Python interpreter location.

```
cd your_directory_with_cloned_repository
install_dependencies.bat [VENV_NAME] [PYTHON_INTERPRETER_PATH]
```
	
- VENV_NAME: Specify the name for the virtual environment (e.g., MyEnv). If not provided, it defaults to SONOROVER_ONE.
- PYTHON_INTERPRETER_PATH: Specify the path to the Python 3.10 interpreter if it’s not in the default location. For example, C:\Path\To\Python310\python.exe.

The batch file will:

- Create a virtual environment.
- Install the required Python packages.
- Clone the Radboud FUS driving system software repository into the SonoRover One repository.
- Install the Radboud FUS driving system software package. 
- Set up necessary environment variables.

After running the batch file, ensure that the virtual environment is activated and dependencies are installed. You can verify this by:

- Checking for the virtual environment in your WORKON_HOME directory.
- Confirming that the required packages are installed.

#### Notes
- **Python Version**: The script assumes that Python 3.10 is installed. If you have a different version, make sure to adjust the script accordingly or install Python 3.10.
- **Environment Variables**: The batch file sets environment variables temporarily for the session and permanently if they are not already set. Ensure that WORKON_HOME is correctly configured as needed.

#### Troubleshooting
If you encounter issues with the batch file not being recognized or errors during execution, ensure that:

- The batch file has the correct permissions to execute.
- The repository has been cloned correctly and contains the necessary files.


## 📋 Usage <a name="usage"></a>

### Software

With all dependencies installed, activate your environment in your command prompt. 

```
workon [VENV_NAME]
```

While the virtual environment is activated, you can install Spyder or any other IDE of your choice. To install Spyder, run:

```
pip install spyder
```

After installing Spyder, you can launch it directly from the command line within the activated virtual environment by running:

```
spyder
```

#### Activate your virtual environment and launch the IDE at once
To simplify the process of activating the virtual environment and launching your IDE, you can use the provided [batch script](start_venv_and_ide.bat).

How to use the script:
1. Ensure that start_env_and_ide.bat is located in a convenient location, such as the root directory of your project or your desktop.
2. Run the script in one of the following ways:
	- Open start_venv_and_ide.bat in a text editor and modify the VENV_NAME and IDE variables directly if you prefer not to use command-line arguments. To run the .bat file, just double-click it.
	- Using the command prompt:
		```
		start_venv_and_ide.bat [VENV_NAME] [IDE]
		```
		- VENV_NAME: Specify the name for the virtual environment (e.g., MyEnv). If not provided, it defaults to SONOROVER_ONE.
		- IDE: Specify the python interpreter. IF not provided, it defaults to spyder.

#### Primary script
The primary script is  [main](/SonoRover%20One/software/src/main.py). 
Running this script launches a GUI to set the following parameters:

1. **Path and filename of protocol excel file**: Select the required protocol Excel file. Refer to the example template [here](SonoRover%20One/software/example%20input/protocol%20template/template_protocol_input.xlsx). This file contains sequences with various foci, power outputs, timing parameters, and/or coordinate grids. It is specific to a driving system-transducer combination.  
   **Note**: If you change the headers in the Excel file, you must also update the corresponding headers in the code.
   - **Sequence**: The sequence number, ranging from 1 to the total number of sequences in the Excel file.
   - **Modulation**: Choose from Square, Linear, or Tukey ramp shapes from the dropdown.
   - **Ramp duration [us]**
   - **Ramp duration step size [us]**: Temporal resolution of ramping, applicable only for the IGT system.
   - **Pulse duration [us]**
   - **Pulse Repetition Frequency [Hz]**
   - **Pulse Repetition Interval [ms]**
   - **Pulse Train Duration [ms]**
   - **Isppa [W/cm²], Global power [mW], or Amplitude [%]**: Select the applicable power parameter for the chosen driving system from the dropdown. Amplitude is used for the IGT system; Isppa or global power is used for the Sonic Concepts system. It is recommended to use global power for the Sonic Concepts system.  
     **Note**: If Isppa is chosen, a conversion table in an Excel file (e.g., [here](SonoRover%20One/software/example%20input/protocol%20template/isppa_to_global_power_template.xlsx)) is required with global power in mW and intensity in W/cm2. If you change the headers in the Excel file, you must also update the corresponding headers in the code.
   - **Corresponding value**: The value for the selected power parameter.
   - **Path and filename of Isppa to Global power conversion Excel**: Provide the path to the Isppa-global power conversion table. This parameter is skipped if Isppa is not selected.
   - **Focus [mm]**
   - **Coordinates based on Excel file or parameters on the right?**: Choose to define a grid using a coordinate Excel file or by defining grid sizes in this file from the dropdown. Coordinate file examples are [here](SonoRover%20One/software/example%20input/coordinate%20templates).  
     **Note**: Coordinate files allow more flexibility in grid point arrangement. All grids are based on a chosen zero point (for example: focus or exit plane). Headers in the Excel file must match those used in the code.
   - **Path and filename of coordinate Excel**: Provide the path to the coordinate Excel file. This parameter is skipped if 'Coordinates based on Excel file' is not selected.
   
   **Note**: if 'Parameters on the right' is not chosen as input parameter, below parameters are skipped.
   - **max. ± x [mm] w.r.t. relative zero**: The maximum movement in the ±x direction in mm relative to the chosen zero point.
   - **max. ± y [mm] w.r.t. relative zero**: The maximum movement in the ±y direction in mm relative to the chosen zero point.
   - **max. ± z [mm] w.r.t. relative zero**: The maximum movement in the ±z direction in mm relative to the chosen zero point.
   - **direction_slices**: Choose the direction of the slices from the dropdown. Refer to the example image in the [protocol template](SonoRover%20One/software/example%20input/protocol%20template/template_protocol_input.xlsx).
   - **direction_rows**: Choose the direction of the rows from the dropdown. Refer to the example image in the [protocol template](SonoRover%20One/software/example%20input/protocol%20template/template_protocol_input.xlsx).
   - **direction_columns**: Choose the direction of the columns from the dropdown. Refer to the example image in the [protocol template](SonoRover%20One/software/example%20input/protocol%20template/template_protocol_input.xlsx).
   - **step_size_x [mm]**: The grid size in the x-direction.
   - **step_size_y [mm]**: The grid size in the y-direction.
   - **step_size_z [mm]**: The grid size in the z-direction.

2. **US Driving System**
3. **Transducer**
4. **Operating frequency [kHz]**
5. **COM port of US driving system**: Required for Sonic Concepts driving system.
6. **COM port of positioning system**
7. **Hydrophone acquisition time [us]**
8. **Picoscope sampling frequency multiplication factor**: Minimum multiplication factor is 2.
9. **Absolute G code x-coordinate of relative zero**: The x-coordinate of the chosen zero point.
10. **Absolute G code y-coordinate of relative zero**: The y-coordinate of the chosen zero point.
11. **Absolute G code z-coordinate of relative zero**: The z-coordinate of the chosen zero point.
12. **Perform all protocols in sequence without waiting for user input?**: If yes, the characterization will proceed through all sequences in the protocol Excel file without stopping for input between sequences.

After all parameters are set, click 'ok' to start the characterization. Log files and an output folder will be created in the same directory as the protocol Excel file.

![image](https://github.com/Donders-Institute/Radboud-FUS-measurement-kit/assets/134381864/dcc80f2d-cc04-42ec-afbc-a19f55aed547)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONFIGURATION -->

# 🧰 Configuration <a name="config"></a>

The SonoRover One software uses a comprehensive configuration system to control its behavior. This section explains how to modify configuration settings and add new equipment to the system.

## ⚙️ Main Configuration File <a name="main-config"></a>

The main configuration file is located at `Radboud-FUS-measurement-kit/SonoRover_One/software/src/config/characterization_config.ini`. You can either modify this file directly or use the provided `create_config.py` script to regenerate it with your changes.

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
- **log level console**: Minimum severity level displayed in console (WARNING, ERROR, CRITICAL)
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
- **temporary output path**: Directory for temporary measurement output
- **temporary logging path**: Directory for temporary log files
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
- **ac_align.axis_suffix**: Suffix for acoustical axis files
- **ac_align.additional_x_lim**: Additional space added to X-axis limit of acoustical alignment plot (15mm)

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

The configuration file defines column names used in coordinate and protocol Excel files. If you modify the headers in your Excel templates, you'll need to update these settings to match.

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
Create a new datasheet in the `Radboud-FUS-measurement-kit\SonoRover One\software\src\config\hydrophones` folder, using one of the existing files as a template. This file contains the frequency-sensitivity mapping for your hydrophone.

If sensitivity values are not known, set all values to zero, but note that measurement output values will be incorrect. 

### PicoScope

Currently, only PicoScope oscilloscopes are supported. The software supports these models:
- 5442D
- 5442A
- 5244D 

To add a new PicoScope model:

#### Step 1: Extend pico.py
Extend the `Radboud-FUS-measurement-kit/SonoRover_One/software/src/backend/pico.py` script with a class for your PicoScope model:

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

- [ ] **Compatibility check of chosen equipment**

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

