from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir
import os

required_conan_version = ">=2.0"


class RustConan(ConanFile):
    name = "rust"
    description = "The Rust Programming Language (official pre-built toolchain)"
    license = "MIT OR Apache-2.0"
    author = "ZettaScale Zenoh Team <zenoh@zettascale.tech>"
    url = "https://github.com/zettascalelabs/conan-recipes"
    homepage = "https://www.rust-lang.org"
    topics = ("rust", "language", "toolchain", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.build_type
        if self.info.settings.os != "Windows":
            del self.info.settings.compiler
        else:
            # Official Windows tarballs differ for MSVC vs GNU; keep the family in the package id.
            self.info.settings.rm_safe("compiler.version")
            self.info.settings.rm_safe("compiler.runtime")
            self.info.settings.rm_safe("compiler.runtime_type")
            self.info.settings.rm_safe("compiler.update")
            self.info.settings.rm_safe("compiler.cppstd")
            self.info.settings.rm_safe("compiler.libcxx")
            if self.info.settings.compiler != "gcc":
                self.info.settings.compiler = "msvc"

    @property
    def _rust_download_info(self):
        os_name = str(self.settings.os)
        arch_name = str(self.settings.arch)
        version_info = self.conan_data["sources"][self.version]
        if os_name == "Windows":
            compiler_name = "gcc" if self.settings.compiler == "gcc" else "msvc"
            return version_info.get(os_name, {}).get(compiler_name, {}).get(arch_name)
        return version_info.get(os_name, {}).get(arch_name)

    def validate(self):
        if not self._rust_download_info:
            raise ConanInvalidConfiguration(
                f"Unsupported OS/arch combination for rust: {self.settings.os}/{self.settings.arch}"
            )

    def build(self):
        get(self, **self._rust_download_info, strip_root=True)

    def package(self):
        copy(self, "LICENSE-APACHE", self.build_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-MIT", self.build_folder, os.path.join(self.package_folder, "licenses"))
        for name in os.listdir(self.build_folder):
            path = os.path.join(self.build_folder, name)
            if os.path.isdir(path) and "docs" not in name:
                copy(self, "*", path, self.package_folder)
        rm(self, "manifest.in", self.package_folder)
        rm(self, "*.pdb", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "libexec"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        exe = ".exe" if self.settings.os == "Windows" else ""
        self.buildenv_info.prepend_path("PATH", bindir)
        self.buildenv_info.define_path("CARGO", os.path.join(bindir, f"cargo{exe}"))
        self.buildenv_info.define_path("RUSTC", os.path.join(bindir, f"rustc{exe}"))
        self.buildenv_info.define_path("RUSTDOC", os.path.join(bindir, f"rustdoc{exe}"))
        self.buildenv_info.define_path("RUSTFMT", os.path.join(bindir, f"rustfmt{exe}"))
