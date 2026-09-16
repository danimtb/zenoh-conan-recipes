from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rm
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.microsoft import VCVars, is_msvc
import os

required_conan_version = ">=2.0"


class ZenohCPackageConan(ConanFile):
    name = "zenohc"
    description = "C-API for Eclipse Zenoh: Zero Overhead Pub/sub, Store/Query and Compute protocol"
    topics = ("iot", "networking", "robotics", "messaging", "ros2", "edge-computing", "micro-controller")
    license = "EPL-2.0 OR Apache-2.0"
    author = "ZettaScale Zenoh Team <zenoh@zettascale.tech>"

    url = "https://github.com/zettascalelabs/conan-recipes"
    homepage = "https://github.com/eclipse-zenoh/zenoh-c"

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

    @property
    def _supported_platforms(self):
        return [
            ("Windows", "x86_64"),
            ("Linux", "x86_64"),
            ("Linux", "armv6"),
            ("Linux", "armv7hf"),
            ("Linux", "armv8"),
            ("Macos", "x86_64"),
            ("Macos", "armv8"),
        ]

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

    def validate(self):
        if (self.settings.os, self.settings.arch) not in self._supported_platforms:
            raise ConanInvalidConfiguration("{}/{} combination is not supported".format(self.settings.os, self.settings.arch))

    def build_requirements(self):
        self.tool_requires("rust/1.97.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        if is_msvc(self):
            VCVars(self).generate()
        CMakeToolchain(self).generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Upstream install always ships static and shared; keep only the selected linkage.
        libdir = os.path.join(self.package_folder, "lib")
        bindir = os.path.join(self.package_folder, "bin")
        if self.options.shared:
            rm(self, "libzenohc.a", libdir)
            rm(self, "libzenohcd.a", libdir)
            rm(self, "zenohc.lib", libdir)
            rm(self, "zenohcd.lib", libdir)
        else:
            rm(self, "*.dll", bindir)
            rm(self, "*.dylib", libdir)
            rm(self, "*.so", libdir)
            rm(self, "*.so.*", libdir)
            rm(self, "*.dll.lib", libdir)
            rm(self, "*.dll.a", libdir)

    def package_info(self):
        self.cpp_info.libs = ["zenohc"]
        self.cpp_info.set_property("cmake_file_name", "zenohc")
        self.cpp_info.set_property("cmake_target_name", "zenohc::lib")
        self.cpp_info.set_property("cmake_target_aliases", [f"zenohc::{'shared' if self.options.shared else 'static'}"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32", "crypt32", "secur32", "bcrypt", "ncrypt", "userenv", "ntdll", "iphlpapi", "runtimeobject"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["rt", "pthread", "m", "dl"]
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ["Foundation", "Security"]
