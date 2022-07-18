#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import glob
from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanException
from conans.tools import SystemPackageTool

# python 2 / 3 StringIO import
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from conans.errors import ConanInvalidConfiguration


class LapackConan(ConanFile):
    name = "lapack"
    version = "3.7.1"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Reference-LAPACK/lapack"
    description = "Fortran subroutines for solving problems in numerical linear algebra"
    url = "https://github.com/conan-community/conan-lapack"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports = "LICENSE"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    requires = "zlib/1.2.11"
    deprecated = True
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    exports_sources = ["lapack/*"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        if self.settings.os == "Windows":
            return

        sha256 = "4e710786b887210cd3e0f1c8222e53c17f74bddc95d02c6afc20b18d6c136790"
        tools.get("{}/archive/v{}.zip".format(self.homepage, self.version), sha256=sha256)
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self.settings.os == 'Windows':
            return

        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["LAPACKE"] = True
        cmake.definitions["CBLAS"] = True
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        if self.settings.os == "Windows":
            return

        cmake = self._configure_cmake()
        for target in ["blas", "cblas", "lapack", "lapacke"]:
            cmake.build(target=target)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == "Linux":
            cmake = self._configure_cmake()
            cmake.install()
        else:
            self.copy("*.h", dst="include", src="lapack/include", keep_path=False)
            self.copy("*.lib", dst="lib", src="lapack/lib", keep_path=False)
            self.copy("*.dll", dst="bin", src="lapack/lib", keep_path=False)

    def package_info(self):
        # the order is important for static builds
        self.cpp_info.libs = ["lapacke", "lapack", "blas", "cblas", "gfortran", "quadmath"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("m")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.libs = ["lapacke", "lapack", "blas"]
        self.cpp_info.libdirs = ["lib"]
