Initial template for C++ small test projects

# Project layout
```
├── CMakeLists.txt
├── README.md
├── include      # Header files
│   └── some.h
├── src          # Source files
│   └── some.cpp
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
mkdir build
cd build
conan install ..
cmake ..
make
```

# Run tests
```bash
cmake --build . --target test
```
