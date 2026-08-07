{{name}} C++ small test project
===============================

# Project layout
```
├── .github
│   └── workflows
│       └── unit-tests.yml
├── CMakeLists.txt
├── README.md
├── include      # Header files
│   └── {{name}}.h
├── src          # Source files
│   └── {{name}}.cpp
├── tests        # Various tests
│   ├── CMakeLists.txt
│   ├── integration
│   ├── performance
│   └── unit
├── conanfile.py # Conan package manager file
```

# Due to dependencies are managed by Conan, you need to install it first
```bash
pip install -r requirements.txt
```

# Build
```bash
conan install . -s build_type=Debug --build=missing
# Configure preset is generator-dependent:
#   Windows (multi-config generator): cmake --preset conan-default
#   Linux (single-config generator):  cmake --preset conan-debug
cmake --preset conan-default
cmake --build --preset conan-debug
```

# Run tests
```bash
ctest --preset conan-debug
```


>📝
> Based on the template https://github.com/edu-one/cpptest
