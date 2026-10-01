# Notice of deprecation

This repository is no longer actively maintained.

# Conan Recipes

This repo regroups [conan](https://conan.io/) recipes for Zenoh C/CPP bindings and implementations: [Zenoh-C](https://github.com/eclipse-zenoh/zenoh-c), [Zenoh-CPP](https://github.com/eclipse-zenoh/zenoh-cpp) and [Zenoh-Pico](https://github.com/eclipse-zenoh/zenoh-pico).

All Zenoh Conan recipes are maintained in this repository. They will be updated with new Zenoh releases as they come, as well as some new features depending on identified use-cases. **Always use the latest commit from the main branch**.

## Recipes in this repo

- rust: Installs an official pre-built Rust toolchain (rustc/cargo). Used as a `tool_requires` by zenoh-c so the compiler version is pinned instead of relying on whatever is installed on the host. Native hosts only: Windows x86_64 (MSVC or GNU), Linux x86_64, macOS x86_64 and armv8. Cross-compiling zenoh-c to other Linux ARM targets still needs extra `rust-std` components that this recipe does not ship.
- zenoh-c: Builds Zenoh-C from source. Pulls `rust/1.97.1` automatically (matching zenoh-c 1.10.1's `rust-toolchain.toml`). No preinstalled Rust toolchain is required.
- zenoh-pico: Builds Zenoh-Pico from source.
- zenoh-cpp: Installs the Zenoh-CPP header-library. Depending on which backend library to be used, installation will require one of Zenoh-Pico or Zenoh-C Conan packages to be installed beforehand.

## Why model Rust as a Conan recipe

Zenoh-C is a C API, but the library is built with Cargo. The usual approach is “install rustup on the machine and hope `rustc` matches `rust-toolchain.toml`”. That splits the toolchain from the rest of the C/C++ graph (CMake, compilers, zenoh-c, zenoh-cpp) and makes CI and developer laptops diverge.

Shipping official `rustc`/`cargo` tarballs as `rust/1.97.1` and pulling them with `tool_requires` keeps everything in Conan:

- The Rust version is a package reference, not a host accident. zenoh-c 1.10.1 pulls `rust/1.97.1` to match its `rust-toolchain.toml`.
- Consumers do not need a preinstalled toolchain. The rust package fetches, caches, and reuses the same binaries on every machine.
- Windows MSVC vs GNU, Linux, and macOS each resolve the matching official tarball through `package_id` / `conandata.yml`, instead of documenting per-OS rustup commands.
- The lock is the Conan graph: one profile, one cache. C++ packages that `require` zenohc inherit a reproducible native library without talking to rustup.

The trade-off is that Conan owns the toolchain path. That is the point: Rust is treated as a build tool like CMake, not as an implicit environment dependency.

## Installation

Building the recipes requires Conan. Please visit the official Conan website for installation instructions.

Create the rust package first so zenoh-c can resolve `tool_requires("rust/1.97.1")`.

```shell
conan create rust/all --version 1.97.1
conan create zenoh-c/all --version 1.10.1
conan create zenoh-cpp/all --version 1.10.1

# zenoh-pico is standalone and does not depend on the packages above
conan create zenoh-pico/all --version 1.10.1
```

> **Note about Windows:** zenoh-c runs Cargo, which compiles and immediately executes `build-script-build.exe` helpers that spawn `rustc`/`cargo`. Windows Defender and other endpoint protection (for example CrowdStrike Falcon) often block that `CreateProcess` with Access Denied (Win32 5). Folder or process exclusions in Defender usually do not help. Build zenoh-c in WSL or on Linux/macOS instead.

## Usage

To use the installed Zenoh project in your Conan package, you first need to add it to your recipe's `requirements` function. Below is an example to add `zenoh-c 1.10.1` as a dependency.

```python
from conan import ConanFile
# other imports

class MyPackage(ConanFile):
    
    # other conan recipe attributes and functions
    
    def requirements(self):
        self.requires("zenohc/1.10.1")

    # rest of the recipe
```

It is also possible to configure options for the dependency. For more details, please refer to the official Conan documentation, or read further below for an example with Zenoh-CPP.

**Note:** Depending on the project you wish to use, you will probably also need to setup a `CMakeLists` file for your package. Please refer to the recipe's respective `test_package/CMakeLists.txt` for a basic template.

## Specifying a backend for Zenoh-CPP

Depending on which backend you choose between zenoh-c and zenoh-pico, you will have to install the library through its respective Conan recipe. Make sure the installed version matches exactly with the Zenoh-CPP version you wish to install. Finally, update the `ZENOH_LIB` option in the `requirements` function of your package's recipe (default value is `zenohc`).

```python
    def requirements(self):
        self.requires("zenohcpp/1.10.1", options={"ZENOH_LIB":"zenohpico"})
```
