#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import shutil


class ELFUtilsConan(ConanFile):
    name = "elfutils"
    version = "0.173"
    description = "A collection of utilities and libraries to read, create and modify ELF binary files"
    url = "https://github.com/bincrafters/conan-elfutils"
    homepage = "https://sourceware.org/elfutils"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = "fPIC=True"
    autotools = None
    source_subfolder = "source_subfolder"
    requires = (
        "bzip2/1.0.6@conan/stable",
        "zlib/1.2.11@conan/stable",
        "lzma/5.2.4@bincrafters/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        tools.get("{}/ftp/{}/{}-{}.tar.bz2".format(self.homepage, self.version, self.name, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def configure_autotools(self):
        if not self.autotools:
            args = ['--enable-silent-rules', '--with-zlib', '--with-bzlib', '--with-lzma']
            self.autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            self.autotools.configure(configure_dir=self.source_subfolder, args=args)
        return self.autotools

    def patch_warnings(self):
        search = "$(if $($(*F)_no_Wunused),,-Wunused -Wextra)"
        replace = "$(if $($(*F)_no_Wunused),,-Wno-unused -Wextra)"
        for path in ["libdwfl", "src"]:
            tools.replace_in_file(os.path.join(self.source_subfolder, path, "Makefile.in"), search=search, replace=replace)

    def build(self):
        self.patch_warnings()
        autotools = self.configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self.source_subfolder)
        autotools = self.configure_autotools()
        autotools.install()
        shutil.rmtree(os.path.join(self.package_folder, "share"))
        shutil.rmtree(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
