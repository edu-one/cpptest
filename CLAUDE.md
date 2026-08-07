# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not** a C++ project — it is a **Conan 2 project template** (`conan new dv/cpptest`) plus the
integration suite that proves the template still generates working projects.

Two levels are always in play:

- **Outer repo** (root): the template distribution + `tests/integration.py` + CI/Docker to run it.
- **Inner template** (`templates/command/new/dv/cpptest/`): Jinja2-templated files that Conan renders
  into a user's new project. Files here are *not* compiled or linted by this repo's CI — the only way
  they get exercised is by the integration suite generating and building a real project from them.

The template is delivered to users via `conan config install`, which copies the repo into
`$(conan config home)/templates/`. `.conanignore` controls what is excluded from that copy
(`tests/*`, `Dockerfile`, `README.md`, `LICENSE`, `.github/*`, …) — if you add root-level files that
should not ship to users' Conan homes, add them there.

## Commands

Run the integration suite (the only test suite in this repo):

```bash
python3 tests/integration.py                                    # all tests
python3 tests/integration.py TestTemplate.test_hyphenated_name_build_and_test   # one test
python3 tests/integration.py -v                                 # verbose
```

Prerequisites: `conan>=2`, `cmake>=3.23`, a C++20 toolchain. The suite is safe to run locally — it
never touches your real `~/.conan2` (see "Isolated Conan home" below).

Run the suite in a clean container (mirrors the Linux leg of CI; CI also runs a native Windows leg):

```bash
docker build -t cpptest . && docker run --rm cpptest
```

Install the template locally to try it by hand:

```bash
rm -rf "$(conan config home)/templates/command/new/dv/cpptest"   # stale copies shadow the new one
conan config install .
mkdir /tmp/demo && cd /tmp/demo && conan new dv/cpptest -d name=demo -d version=0.1.0
```

## Template variables: `{{name}}` vs `{{package_name}}`

Conan injects both. Using the wrong one is the defect class this repo has already been bitten by
(`test_hyphenated_name_generation` is the regression guard):

- `{{name}}` — the raw Conan package name; may contain `-`, `.`, `+`. Use in **file names**, the
  `name =` field in `conanfile.py`, CMake target/project names, URLs.
- `{{package_name}}` — the same name sanitized to a valid identifier (`-`/`.`/`+` → `_`). Use in
  **every C++ and Python identifier position**: include guards, namespaces, the `conanfile.py` class
  name.

A name like `my-lib` renders `include/my-lib.h` containing `namespace dv::my_lib`. Any new identifier
introduced into the template must use `{{package_name}}`, and any new file name must use `{{name}}`.

Note that template source files literally have `{{name}}` in their paths on disk
(`include/{{name}}.h`, `src/{{name}}.cpp`, `tests/unit/{{name}}_test.cpp`) — quote them in shell
commands.

## Generated-project contract

`conanfile.py` and `CMakeLists.txt` in the template must stay in agreement, and the suite asserts it:

- `package_info()` advertises `cpp_info.libs = ["{{name}}"]`, so `CMakeLists.txt` **must** carry
  matching `install(TARGETS …)` / `install(FILES include/{{name}}.h …)` rules. Missing install rules
  produce a `conan create` that exits 0 with an *empty* package — `assert_package_nonempty()` exists
  because that regression already happened once.
- Tests are gated by the `WITH_TESTS` CMake option, fed from the Conan `with_tests` option via the
  toolchain, and stripped from `package_id()` so it doesn't fragment the binary cache. The tests
  subtree is also guarded by `PROJECT_IS_TOP_LEVEL` so consumers vendoring the project don't build it.
- C++20 is pinned in three places that must move together: `configure()` sets
  `settings.compiler.cppstd`, `validate()` calls `check_min_cppstd(self, 20)`, and CMake declares
  `target_compile_features(… cxx_std_20)`.
- gtest is a `test_requires`, discovered via `gtest_discover_tests`.

## CMake preset selection is generator-dependent

The *configure* preset differs by platform while build/test presets do not:

| | configure | build / ctest |
|---|---|---|
| Windows (multi-config VS generator) | `conan-default` | `conan-release` |
| Linux (single-config) | `conan-release` | `conan-release` |

`TestTemplate.CONFIGURE_PRESET` encodes this via `sys.platform`. Keep the template's `README.md`
build instructions consistent with it when it changes.

## Integration suite structure

`tests/integration.py` is plain `unittest`, one class, with shared helpers
(`generate_project` → `build_and_test_project` → `create_package` → `assert_package_nonempty`) and
per-concern tests so a build failure and a rendering failure are distinguishable. Two things about it
are deliberate and easy to break:

- **Isolated Conan home**: `setUpClass` points every subprocess at
  `tests/build/conan-home/suite<pid>` via `CONAN_HOME`. It lives under the repo's `build/` tree, *not*
  the OS temp dir — a `CONAN_HOME` under `%TEMP%` on Windows escalates MSBuild's MSB8029 into a failed
  try-compile and breaks every from-source build.
- **Class-scoped, not per-test**: the isolated home doubles as the shared Conan package cache. Wiping
  it per test forces gtest to rebuild from source in every test that runs `conan install`/`conan
  create`.

All subprocesses go through `run_checked()` (or `_run_class_setup_command()` in class setup, where no
`self` exists), which captures and reports stdout/stderr on failure — use them rather than bare `run`.
