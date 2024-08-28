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
  - [Key Features](#key-features)
  - [👥 Authors](#authors)
  - [✒️ How to cite](#how-to-cite)
- [💻 Getting Started](#getting-started)
  - [Setup](#setup)
  - [Install](#install)
  - [Usage](#usage)
- [🔭 Future Features](#future-features)
- [🤝 Contributing](#contributing)
- [📝 License](#license)

<!-- PROJECT DESCRIPTION -->

# 📖 Radboud FUS measurement kit <a name="about-project"></a>

(Project id: **0003429** )

**Radboud FUS measurement kit** is a comprehensive kit allowing precise hydrophone measurements of your TUS transducers for verification, characterization and monitoring overall system performance.    

This project is facilitated by the Radboud Focused Ultrasound Initiative. For more information, please visit the [website](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus).

<!-- Features -->

## Key Features <a name="key-features"></a>

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

Margely Cornelissen, Stein Fekkes (Radboud University, Nijmegen, The Netherlands) & Erik Dumont (Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 0.8), https://github.com/Donders-Institute/Radboud-FUS-measurement-kit

<!-- GETTING STARTED -->

# 💻 Getting Started <a name="getting-started"></a>

## Setup <a name="setup"></a>

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

## Install <a name="install"></a>

### Software

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


## Usage <a name="usage"></a>

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

<!-- FUTURE FEATURES -->

# 🔭 Future Features <a name="future-features"></a>

## Software

- [x] **Implemented driving system abstract class to easily integrate driving systems from other manufacturers**
- [x] **Cleaner, restructured and more robust code**
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

