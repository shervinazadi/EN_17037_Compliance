# Environmental Standard Model

Here, we will develop and document the prototype of the Environmental Standard Model.

PS. Check python notebooks for the documentation of learning process

## Installation

1. Install latest release of Radiance from [here](https://github.com/LBNL-ETA/Radiance/releases)
2. Clone [Honeybee Repo](https://github.com/ladybug-tools/honeybee) on your machine
3. Install Anaconda or miniconda
4. Create conda environment ([follow this](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands))
5. install pip inside the newly created environment

```bash
conda install pip
```

6. locally install honeybee

```bash
# redirect to the local directory of honeybee
# cd honeybee
# create a symlink
python -m pip install -e .
```

7. add the path to radiance in the HB config located in: `honeybee_plus/config.json`

```json
{
  "__comment__": "Add full path to installation folder (e.g. c:\radiance, /usr/local/radiance).",
  "path_to_radiance": "<address to radiance folder>",
  "path_to_openstudio": "",
  "path_to_perl": ""
}
```

8. make sure that radiance is added to PATH, RAYPATH, and MANPATH

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
## Docker Setup

1. Install and run [Docker Desktop](https://www.docker.com/products/docker-desktop)

2A. First time build and run the image [Running your function in a container](https://github.com/GoogleCloudPlatform/functions-framework-python/tree/master/examples/cloud_run_http)

```bash
docker build -t en17037 . && docker run --rm -p 8080:8080 -e PORT=8080 en17037
```

2B. if you already built the image, only run the image [Running your function in a container](https://github.com/GoogleCloudPlatform/functions-framework-python/tree/master/examples/cloud_run_http)

```bash
docker run --rm -p 8080:8080 -e PORT=8080 en17037
```