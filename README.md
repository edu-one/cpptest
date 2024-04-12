C++ small test projects template
===============================

# Usage
## Installation
```
rm -rf ~/.conan2/templates/command/new/dv_cpptest  # remove old template if exists
conan config install git@github.com:valden/cpptest.git --type git
```
## Create new project from template
```
mkdir my_project && cd my_project
conan new dv_cpptest -d name=my_project -d version=0.1
```

# Development
Template itself is located in the `templates/command/new/dv_cpptest` directory.
