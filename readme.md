# EN 17037 Compliance

This repository contains open-source computational workflows for assessing the "Exposure to sunlight" and "View out" criteria as defined in the European standard EN 17037 "Daylight in Buildings", issued by the European Committee for Standardization. In addition to these factors, the standard document also addresses daylight provision and protection from glare, both of which fall out of the scope of this project. The purpose of the standard is stated as "encouraging building designers to assess and ensure successfully daylit spaces". The standard document proposes verification methods for performing such assessments, albeit without recommending a simulation procedure for computing the aforementioned criteria. The workflows prepared here are arguably the first attempt to standardize these assessment methods using de-facto open-source standard technologies currently used in practice. This project aims at establishing that the compliance check can be systematically performed on a 3D model by a novel simulation tool developed by the authors.

### Environment Preparation

1. Install latest release of Radiance from [here](https://github.com/LBNL-ETA/Radiance/releases)
2. Install Anaconda or miniconda
3. Create conda environment ([follow this](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands))
4. Clone [Honeybee Repo](https://github.com/ladybug-tools/honeybee)
5. locally install honeybee

```bash
# redirect to the local directory of honeybee
# cd honeybee
# create a symlink
python -m pip install -e .
```

6. add the path to radiance in the HB config located in: `honeybee_plus/config.json`

```json
{
  "__comment__": "Add full path to installation folder (e.g. c:\radiance, /usr/local/radiance).",
  "path_to_radiance": "<address to radiance folder>",
  "path_to_openstudio": "",
  "path_to_perl": ""
}
```

7. make sure that radiance is added to PATH, RAYPATH, and MANPATH

```bash
# to test if the paths are installed correctly:
# the result of this command should include: <installation address>/radiance/bin
echo $PATH
# the result of this command should include: <installation address>/radiance/lib
echo $RAYPATH
# the result of this command should include: <installation address>/radiance/man
echo $MANPATH

# if this is not the case, you should add those paths to the command line profile file (such as .bash_profile, or .zshenv depending on the type of your command line)
```