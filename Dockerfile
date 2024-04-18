# Use Ubuntu as base image
FROM ubuntu:22.04

# Install essential packages for C++ development
RUN apt-get update -qq && apt-get install -y \
    build-essential

# Install python3
ENV PATH=$PATH:/root/.local/bin
RUN apt-get update -qq && apt-get install -y \
    python3 \
    python3-pip

# Install conan && cmake
RUN pip3 install -q --user \
    conan==2.* \
    cmake==3.23.*

# Set the working directory inside the container
WORKDIR /opt/cpptest

# Copy the source code into the container
COPY . .

# Detect default conan profile
RUN conan profile detect

# run tests script
CMD [ "python3", "tests/integration.py" ]
