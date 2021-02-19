FROM python:3.7

WORKDIR /home/genesis

# Install radiance
ENV RAYPATH=/home/genesis/lib
ENV PATH="/home/genesis/bin:${PATH}"
RUN curl -L https://ladybug-tools-releases.nyc3.digitaloceanspaces.com/Radiance_5.3a.fc2a2610_Linux.zip --output radiance.zip \
&& unzip -p radiance.zip | tar xz \
&& mkdir bin \
&& mkdir lib \
&& mv ./radiance-5.3.fc2a261076-Linux/usr/local/radiance/bin/* /home/genesis/bin \
&& mv ./radiance-5.3.fc2a261076-Linux/usr/local/radiance/lib/* /home/genesis/lib \
&& rm -rf radiance-5.3.fc2a261076-Linux \
&& rm radiance.zip

# Set current directory to app
WORKDIR /home/genesis/app

# copy the content of docker folder
COPY ./docker_content .
COPY ./data ./data
COPY ./final_notebooks ./final_notebooks

# install topogenesis and honeybee plus
RUN python -m pip install -e libs/honeybee
RUN python -m pip install -e libs/topoGenesis

# install the requirements
RUN pip install -r requirements.txt

# run the server in debug mode
CMD exec functions-framework --target=gate --debug