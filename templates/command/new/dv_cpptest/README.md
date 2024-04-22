{{name}} C++ small test project
===============================

# Project layout
```
├── CMakeLists.txt
├── README.md
├── include      # Header files
│   └── {{name}}.h
├── src          # Source files
│   └── {{name}}.cpp
├── tests        # Various tests
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
conan install . --build=missing
cmake --preset conan-debug
cmake --build --preset conan-debug
```

# Run tests
```bash
ctest --preset conan-debug
```


>📝
> Based on the template https://github.com/valden/cpptest
