from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=2.0"


class ZenohCppPackageConan(ConanFile):
    name = "zenohcpp"
    description = "C++ API for Eclipse Zenoh: Zero Overhead Pub/sub, Store/Query and Compute protocol"
    topics = ("iot", "networking", "robotics", "messaging", "ros2", "edge-computing", "micro-controller", "header-only")
    license = "EPL-2.0 OR Apache-2.0"
    author = "ZettaScale Zenoh Team <zenoh@zettascale.tech>"

    url = "https://github.com/zettascalelabs/conan-recipes"
    homepage = "https://github.com/eclipse-zenoh/zenoh-cpp"

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    options = {
        "ZENOH_LIB": ["zenohc", "zenohpico"],
    }
    default_options = {
        "ZENOH_LIB": "zenohc",
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _cmake_target_name(self):
        if self.options.ZENOH_LIB == "zenohc":
            return "zenohcxx::zenohc"
        return "zenohcxx::zenohpico"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("{}/{}".format(self.options.ZENOH_LIB, self.version), transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(
            self,
            "*.h*",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "zenohcpp")
        self.cpp_info.set_property("cmake_target_name", self._cmake_target_name)
        if self.options.ZENOH_LIB == "zenohc":
            self.cpp_info.defines.append("ZENOHCXX_ZENOHC")
        else:
            self.cpp_info.defines.append("ZENOHCXX_ZENOHPICO")
