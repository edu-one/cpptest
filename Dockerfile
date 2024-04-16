# Use Ubuntu as base image
FROM ubuntu:latest

# Install essential packages for C++ development
RUN apt-get update -qq && apt-get install -y \
    build-essential \
    cmake

# Install python3
ENV PATH=$PATH:/root/.local/bin
RUN apt-get update -qq && apt-get install -y \
    python3 \
    python3-pip

# Install conan
RUN pip3 install -q --user conan==2.*

# Set the working directory inside the container
WORKDIR /opt/cpptest

# Copy the C++ source code into the container
COPY . .

# Command to run the compiled program
CMD ["conan", "config",  "install", "templates/command/new/dv_cpptest"]
CMD [ "conan", "install", ".", "--build=missing" ]
