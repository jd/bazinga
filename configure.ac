AC_PREREQ(2.61)
AC_INIT([bazinga],
        0.1,
        [bazinga@naquadah.org])
AC_CONFIG_SRCDIR([configure.ac])
AM_INIT_AUTOMAKE([
                  foreign
                  no-dist-gzip
                  dist-bzip2
                  dist-xz
                  subdir-objects
                  color-tests
                  silent-rules
                  parallel-tests
                  ])
                  dnl for future check of --help/--version
                  dnl std-options
AM_SILENT_RULES([yes])

AM_PATH_PYTHON([2.6])

AC_CONFIG_FILES([
                 Makefile
                 tests/Makefile
                 ])

AC_OUTPUT
