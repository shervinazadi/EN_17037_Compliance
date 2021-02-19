# starting from https://hub.docker.com/layers/ladybugtools/honeybee-radiance/1.33.0/images/sha256-2b133d61ff2707a1f842903b9192e46a9f7ab88680edb3375721a1c1d18fdda6?context=explore that includes, python + radiance installation 
FROM ladybugtools/honeybee-radiance:1.33.0

# Set current directory to app
WORKDIR /app

# copy the content of docker folder
COPY ./docker_content .

# install the requirements
RUN pip install -r requirements.txt

# copy the honeybee and topogenesis
COPY ../topoGenesis ./topoGenesis
COPY ../honeybee ./honeybee

# install topogenesis and honeybee plus
RUN python -m pip install -e ./topoGenesis
RUN python -m pip install -e ./honeybee

# run the server in debug mode
CMD exec functions-framework --target=gate --debug