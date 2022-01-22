# Right atrial flattening
Author: Marta Nuñez-Garcia (marnugar@gmail.com)

## About
Implementation of the Right Atrial (RA) flattening described in 
[*Standard quasi-conformal flattening of the right and left atria*. Marta Nuñez-Garcia, Gabriel Bernardino, Ruben Doste, Jichao Zhao, Oscar Camara, and Constantine Butakoff. In Functional Imaging and Modeling of the Heart (FIMH 2019) LNCS, vol 11504.](https://link.springer.com/chapter/10.1007%2F978-3-030-21949-9_10) Please cite this reference when using this code.

Given a RA surface mesh with holes corresponding to the tricuspid valve (TV), and the superior and inferior vena cava (SVC and IVC, respectively), it produces a two-dimensional standardised representation of the input mesh as described in the paper. 

Overview:

![Example image](https://github.com/martanunez/RA_flattening/blob/master/pipeline_RA.png)

Examples using two synthetic textures on a real RA surface:

![Examples](https://github.com/martanunez/RA_flattening/blob/master/syn_examples.png)

## Code
[Python](https://www.python.org/) scripts depending (basically) on [VTK](https://vtk.org/) and [VMTK](http://www.vmtk.org/). 


## Instructions
Clone the repository:
```
git clone https://github.com/martanunez/RA_flattening

cd RA_flattening
```

## Usage
```
flat_RA.py [-h] [--meshfile PATH] [--flip FLIP]

optional arguments:
  -h, --help       show this help message and exit
  --meshfile PATH  path to input mesh
  --flip FLIP      Specifiy if a flip of the contours is required (try both cases)

```

## Usage example
```
python flat_RA.py --meshfile data/RA_clipped_lines_p5000_15.vtk --flip True

```

## Dependencies
The scripts in this repository were successfully run with:
1. Ubuntu 16.04
    - [Python](https://www.python.org/) 3.5.2
    - [VMTK](http://www.vmtk.org/) 1.4
    - [VTK](https://vtk.org/) 9.1.0

2. Ubuntu 16.04
    - [Python](https://www.python.org/) 2.7.12
    - [VMTK](http://www.vmtk.org/) 1.4
    - [VTK](https://vtk.org/) 8.1.0

  
Other required packages are NumPy and SciPy.  

### Python packages installation
To install VMTK follow the instructions [here](http://www.vmtk.org/download/). The easiest way is installing the VMTK [conda](https://docs.conda.io/en/latest/) package (it additionally includes VTK, NumPy, etc.). It is recommended to create an environment where VMTK is going to be installed and activate it:

```
conda create --name vmtk_env
conda activate vmtk_env
```
Then, install vmtk:
```
conda install -c vmtk vtk itk vmtk
```
<!-- Activate the environment when needed using:
```
conda activate vmtk_env
``` -->
**Nevertheless,** for Ubuntu, the easiest option for me was to build VMTK from source (slowly but surely). Instructions can be found [here.](http://www.vmtk.org/download/)
In brief:
```
git clone https://github.com/vmtk/vmtk.git
mkdir vmtk-build
cd vmtk-build
ccmake ../vmtk
make 
```
And edit the ~/.bashrc file,
```
gedit ~/.bashrc
```
adding the following line:  source /home/{your_path_to_vmtk}/vmtk/vmtk-build/Install/vmtk_env.sh


## Important note
You may need to slightly modify vmtkcenterlines.py from the VMTK package if you encounter the following error when running 1_mesh_standardisation.py:

```
     for i in range(len(self.SourcePoints)/3):
TypeError: 'float' object cannot be interpreted as an integer
```

Find vmtkcenterlines.py file and edit as follows:

Line 128: change ***for i in range(len(self.SourcePoints)/3):*** by ***for i in range(len(self.SourcePoints)//3):***

Line 133: change ***for i in range(len(self.TargetPoints)/3):*** by ***for i in range(len(self.TargetPoints)//3):*** 

## License
The code in this repository is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This code is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details: [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/)
