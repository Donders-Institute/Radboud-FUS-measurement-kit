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
- [⭐️ Show your support](#support)
- [🙏 Acknowledgements](#acknowledgements)
- [📝 License](#license)

<!-- PROJECT DESCRIPTION -->

# 📖 Radboud FUS measurement kit <a name="about-project"></a>

> Describe your project in 1 or 2 sentences.

(Project id: **0003429** )

**Radboud FUS measurement kit** is a...

This project is facilitated by the Radboud Focused Ultrasound Initiative. For more information, please visit the [website](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus).

<!-- Features -->

## Key Features <a name="key-features"></a>

> Describe between 1-3 key features of the application.

- **Affordable**
- **High quality**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- AUTHORS -->

## 👥 Authors <a name="authors"></a>

👤 **[Stein Fekkes](https://www.ru.nl/en/people/fekkes-s), [FUS Initiative](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus), Radboud University**

- GitHub: [@StefFek-GIT](https://github.com/githubhandle)
- LinkedIn: [LinkedIn](https://linkedin.com/in/sfekkes)

👤 **[Margely Cornelissen](https://www.ru.nl/en/people/cornelissen-m), [FUS Initiative](https://www.ru.nl/en/donders-institute/research/research-facilities/focused-ultrasound-initiative-fus), Radboud University**

- GitHub: [@MaCuinea](https://github.com/MaCuinea)
- LinkedIn: [LinkedIn](https://linkedin.com/in/margely-cornelissen)

👤 **Erik Dumont, [Image Guided Therapy (IGT)](http://www.imageguidedtherapy.com/)**

- GitHub: [@githubhandle](https://github.com/githubhandle)
- LinkedIn: [LinkedIn](https://linkedin.com/in/erik-dumont-986a814)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## ✒️ How to cite <a name="how-to-cite"></a>

If you use this hardware in your research or project, please cite it as follows:

[ADD CITATION]

If you use this software in your research or project, please cite it as follows:

Margely Cornelissen (Radboud University, Nijmegen, The Netherlands) & Erik Dumont (Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit software (Version 0.8), [GITHUB-URL]

<!-- GETTING STARTED -->

## 💻 Getting Started <a name="getting-started"></a>

> Describe how a new developer could make use of your project.

To get a local copy up and running, follow these steps.

### Prerequisites

In order to run this project you need:

<!--
Example command:

```sh
 gem install rails
```
 -->

### Setup

#### Hardware

#### Software
Clone this repository to your desired folder:

- Git terminal

	``` sh
		cd my-folder
		git clone git@github.com:MaCuinea/Radboud-FUS-measurement-kit.git
	```

- GitHub Desktop
	1. Click on 'Current repository'.
	2. Click on 'Add' and select 'Clone repository...'.
	3. Choose 'URL' and paste the following repository URL: [https://gitlab.socsci.ru.nl/fus-initiative/fus-driving-system-software](https://github.com/MaCuinea/Radboud-FUS-measurement-kit.git)
	4. Choose your desired folder and clone the repository.


### Usage

#### Hardware

#### Software

The software is shared being as-is. Due to it being a 0.8 version, the current version of the software is mainly for inspiration purposes. Currently, we are cleaning up, restructuring and rewritting the code to eventually release a 1.0 version. 

The main script is [characterizationPipeline.py](characterizationPipeline.py). When running this script, a GUI pops up to set the following parameters:
1. 'Path and filename of protocol excel file' - a procotol excel file is required as input. This excel file contains one or multiple sequences ranging from different foci, power outputs, timing parameters and/or coordinate grids. This file is specific for a drivin system-transducer combination.
  Note: The headers of the excel file can only be changed when the headers used in the code are modified as well.
  a. Sequence
  b. Modulation - drop down
  c. Ramp duration [us]
  d. Ramp duration step size [us]
  e. Pulse duration [us]
  f. Pulse Repetition Frequency [Hz]
  g. Pulse Repetition Interval [ms]
  h. Pulse Train Duration [ms]
  i. Isppa [W/cm2], Global power [mW] or Amplitude [%] - drop down
  j. Corresponding value
  k. Path and filename of Isppa to Global power conversion excel
  l. Focus [mm]
  m. Coordinates based on excel file or parameters on the right?
  n. Path and filename of coordinate excel
  o. max. + x [mm] w.r.t. relative zero
  p. max. - x [mm] w.r.t. relative zero
  q. max. + y [mm] w.r.t. relative zero
  r. max. - y [mm] w.r.t. relative zero
  s. max. + z [mm] w.r.t. relative zero
  t. max. - z [mm] w.r.t. relative zero
  u. direction_slices
  v. direction_rows
  w. direction_columns
  x. step_size_x [mm]
  y. step_size_y [mm]
  z. step_size_z [mm]

![image](https://github.com/MaCuinea/Radboud-FUS-measurement-kit/assets/134381864/d5067c99-ecb0-47d8-8cb6-f6ff2761c694)

2. US Driving System
3. Transducer
4. Operating frequency [kHz]
5. COM port of US driving system
6. COM port of positioning system
7. Hydrophone acquisition time [us]
8. Picoscope sampling frequency multiplication factor
9. Absolute G code x-coordinate of relative zero
10. Absolute G code y-coordinate of relative zero
11. Absolute G code z-coordinate of relative zero
12. Perform all protocols in sequence without waiting for user input?

![image](https://github.com/MaCuinea/Radboud-FUS-measurement-kit/assets/134381864/dcc80f2d-cc04-42ec-afbc-a19f55aed547)

input: excel file
multiple sequences with same equipment
amplitude for IGT
Isppa or global power for SC

coordinate excel or defining your own grid.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- FUTURE FEATURES -->

## 🔭 Future Features <a name="future-features"></a>

> Describe 1 - 3 features you will add to the project.

- [ ] **[new_feature_1]**
- [ ] **[new_feature_2]**
- [ ] **[new_feature_3]**

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## 🤝 Contributing <a name="contributing"></a>

Contributions, issues, and feature requests are welcome!

Feel free to check the [issues page](../../issues/).

If you have any questions, please feel free to reach out to us via email at fus@ru.nl.
We'd love to hear from you..

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- SUPPORT -->

## ⭐️ Show your support <a name="support"></a>

> Write a message to encourage readers to support your project

If you like this project...

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGEMENTS -->

## 🙏 Acknowledgments <a name="acknowledgements"></a>

> Give credit to everyone who inspired your codebase.

I would like to thank...

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## 📝 License <a name="license"></a>

This project is [MIT](./LICENSE) licensed.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

