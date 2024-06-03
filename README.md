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
  - [Usage](#usage)
- [🔭 Future Features](#future-features)
- [🤝 Contributing](#contributing)
- [📝 License](#license)

<!-- PROJECT DESCRIPTION -->

# 📖 Radboud FUS measurement kit <a name="about-project"></a>

(Project id: **0003429** )

**Radboud FUS measurement kit** is a comprehensive kit alowing precise hydrophone measurements of your TUS transducers for verification, characterization and monitoring overall system performance.    

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

- [LinkedIn](https://linkedin.com/in/erik-dumont-986a814)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## ✒️ How to cite <a name="how-to-cite"></a>

If you use this kit in your research or project, please cite it as follows:

Margely Cornelissen, Stein Fekkes (Radboud University, Nijmegen, The Netherlands) & Erik Dumont (Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (Version 0.8), [GITHUB-URL](https://github.com/Donders-Institute/Radboud-FUS-measurement-kit)

<!-- GETTING STARTED -->

## 💻 Getting Started <a name="getting-started"></a>

### Setup

#### Hardware

The hardware files are stored as native solidworks files and as step format. The main assembly file: W0003510-00-01-SonoRover One.SLDASM will contain all references to part files and subassemblies.

#### Software
Clone this repository to your desired folder:

- Git terminal

	``` sh
		cd my-folder
		git clone git@github.com:Donders-Institute/Radboud-FUS-measurement-kit.git
	```

- GitHub Desktop
	1. Click on 'Current repository'.
	2. Click on 'Add' and select 'Clone repository...'.
	3. Choose 'URL' and paste the following repository URL: [https://gitlab.socsci.ru.nl/fus-initiative/fus-driving-system-software](https://github.com/Donders-Institute/Radboud-FUS-measurement-kit.git)
	4. Choose your desired folder and clone the repository.


### Usage

#### Software

The software is provided as-is. As it is currently version 0.8, it is mainly intended for inspiration and preliminary use. We are actively working on cleaning, restructuring, and rewriting the code for a 1.0 release in the future.

The primary script is [characterizationPipeline.py](characterizationPipeline.py). Running this script launches a GUI to set the following parameters:

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

## 🔭 Future Features <a name="future-features"></a>

#### Software

- [ ] **Implemented driving system abstract class to easily integrate driving systems from other manufacturers**
- [ ] **Cleaner, restructured and more robust code**
- [ ] **Compatibility check of chosen equipment**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## 🤝 Contributing <a name="contributing"></a>

Contributions, issues, and feature requests are welcome!

Feel free to check the [issues page](../../issues/).

If you have any questions, please feel free to reach out to us via email at fus@ru.nl.
We'd love to hear from you.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📝 License <a name="license"></a>

This project is [MIT](./LICENSE) licensed.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

