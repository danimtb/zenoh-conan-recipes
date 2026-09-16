from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.0"


class ZenohPicoPackageConan(ConanFile):
    name = "zenohpico"
    description = "Eclipse zenoh for pico devices: Zero Overhead Pub/sub, Store/Query and Compute protocol"
    topics = ("iot", "networking", "robotics", "messaging", "ros2", "edge-computing", "micro-controller")
    license = "EPL-2.0 OR Apache-2.0"
    author = "ZettaScale Zenoh Team <zenoh@zettascale.tech>"

    url = "https://github.com/zettascalelabs/conan-recipes"
    homepage = "https://github.com/eclipse-zenoh/zenoh-pico"

    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PACKAGING"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TOOLS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_INTEGRATION"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["zenohpico"]
        self.cpp_info.set_property("cmake_file_name", "zenohpico")
        self.cpp_info.set_property("cmake_target_name", "zenohpico::lib")
        self.cpp_info.set_property("cmake_target_aliases", [f"zenohpico::{'shared' if self.options.shared else 'static'}"])

        if self.settings.os == "Windows":
            self.cpp_info.defines.extend(["ZENOH_WINDOWS", "_CRT_SECURE_NO_WARNINGS"])
            self.cpp_info.system_libs = ["ws2_32", "iphlpapi"]
        elif self.settings.os == "Linux":
            self.cpp_info.defines.append("ZENOH_LINUX")
            self.cpp_info.system_libs = ["pthread", "m"]
        elif self.settings.os == "Macos":
            self.cpp_info.defines.append("ZENOH_MACOS")
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "FreeBSD":
            self.cpp_info.defines.append("ZENOH_BSD")
            self.cpp_info.system_libs = ["pthread"]
