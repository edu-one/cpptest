C++ small test projects template
===============================

# Usage
## Installation
```
rm -rf ~/.conan2/templates/command/new/dv/cpptest  # remove old template if exists
conan config install git@github.com:valden/cpptest.git --type git
```
## Create new project from template
```
mkdir my_project && cd my_project
conan new dv/cpptest -d name=my_project
```

# Development
Template itself is located in the `templates/command/new/dv/cpptest` directory.

>📝
> For sure I thought about inpersonating the project by using special variables like `{{org}}` (instead of `dv`) and so on. But it leads to lots of variables: `org`, `header` (each organization has own file header), `url`, `author`, etc. In that case we'll have to specify lot of variables each time we want to use it. So I decided to keep it simple. 
> If you want to change the template, just fork it and adapt it to your needs.
