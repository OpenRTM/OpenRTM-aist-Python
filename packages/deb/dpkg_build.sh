#!/bin/sh 
#
# Debian package build script
#
# the following files are constant
# - README.Debian
# - changelog
# - compat
# - control
# - copyright
# - dirs
# - docs
# - rules
#
# the following files shoud be generated at make-dist
# - files
#
# Package build process
#
# 1. edit "changelog" file with appropriate package version number
#    like "1.1.0-2." This version number will be used for actual
#    deb package files.
#
# 2. Check permissions of the parent directory of distribution sourcecode
#    extracted directory. (ex. parent of OpenRTM-aist-1.0.0)
#    Package build script create deb packages there.
#
# 3. Run package build script debpkg_build.sh
#    This script do everithings.
#

export LANG=C
export LC_ALL=C

BUILD_ROOT=""

cleanup_files()
{
  get_version_info
  rm -f ../openrtm-aist*.deb
  rm -f ../openrtm-aist*.dsc
  rm -f ../openrtm-aist*.changes
  rm -f ../openrtm-aist*.tar.gz
  rm -rf ${BUILD_ROOT}
}

get_opt()
{
  if test "x$1" = "xclean"; then
    cleanup_files
    exit 0
  fi
}

check_distribution()
{
  os=`uname -s`
  release=`uname -r`-`uname -p`
  dist_name=""
  dist_key=""
  # Check the lsb distribution name
  if test -f /etc/lsb-release ; then
    . /etc/lsb-release
    if test "x$DISTRIB_DESCRIPTION" != "x" ; then
      dist_name=$DISTRIB_DESCRIPTION-`uname -m`
      dist_key=$DISTRIB_ID
    fi
  fi
  # Check the Fedora version
  if test "x$dist_name" = "x" && test -f /etc/fedora-release ; then
    dist_name=`cat /etc/fedora-release`-`uname -m`
    dist_key=`sed -e 's/.[^0-9]*\([0-9]\).*/fc\1/' /etc/fedora-release`
  fi
  # Check the Debian version
  if test "x$dist_name" = "x" && test -f /etc/debian_version ; then
    dist_name="Debian"`cat /etc/debian_version`-`uname -m`
    dist_key="Debian"
  fi
  # Check the Vine version
  if test "x$dist_name" = "x" && test -f /etc/vine-release ; then
    dist_name=`cat /etc/vine-release`-`uname -m`
    dist_key=`sed -e 's/.*\([0-9]\)\.\([0-9]\).*/vl\1\2/' /etc/vine-release`
  fi
  # Check the TuboLinux version
  if test "x$dist_name" = "x" && test -f /etc/turbolinux-release ; then
    dist_name=`cat /etc/tubolinux-release`-`uname -m`
    dist_key=""
  fi

  if test "x$dist_name" = "x" ; then
    dist_name=$os$release
  fi
  # Check the RedHat/Fedora version
  if test "x$dist_name" = "x" && test -f /etc/redhat-release ; then
    dist_name=`cat /etc/redhat-release`-`uname -m`
  fi

  # only fedora and vine
  if test ! "x$dist_key" = "xDebian" -a ! "x$dist_key" = "xUbuntu" ; then
    echo $dist_key
    echo "This is not debian/ubuntu"
    exit 0
  fi
  DIST_KEY=$dist_key
  DIST_NAME=`echo $dist_name | sed 's/[ |\(|\)]//g'`
}

get_version_info()
{
    VERSION=`python3 ../../setup.py --version`
    SHORT_VERSION=`echo $VERSION | sed 's/\.[0-9]*$//'`
    BUILD_ROOT="buildroot"
    PKG_NAME="OpenRTM-aist-Python-${VERSION}"
}

create_source_package()
{
  cd ../../
  python3 setup.py build
  python3 setup.py sdist
  cd -
}

extract_source()
{
  tar xvzf ../../dist/${PKG_NAME}.tar.gz
  mv ${PKG_NAME} ${BUILD_ROOT}
}

create_files()
{
  eval `dpkg-architecture`
  ARCH=$DEB_HOST_ARCH
  PKG_VERSION=`dpkg-parsechangelog | sed -n 's/^Version: //p'`
cat << EOF >> debian/files
openrtm-aist-python3_${PKG_VERSION}_${ARCH}.deb main extra
openrtm-aist-python3-example_${PKG_VERSION}_${ARCH}.deb main extra
openrtm-aist-python3-doc_${PKG_VERSION}_all.deb main extra
EOF
}

copy_control_files()
{
  chmod 444 debian/files
  chmod 755 debian/rules
  cp -r debian ${BUILD_ROOT}/
}

build_package()
{
  if test ! -d ${BUILD_ROOT} ; then
    echo "${BUILD_ROOT} not found. Aborting."
    exit -1
  fi
  cd $BUILD_ROOT
  dpkg-buildpackage -W -us -uc -rfakeroot
  if test $? -ne 0; then
    echo "dpkg-build failed"
    exit -1
  fi
  cd -
}

copy_debfiles()
{
  mv ./openrtm-aist*.deb ..
  mv ./openrtm-aist*.dsc ..
  mv ./openrtm-aist*.changes ..
  mv ./openrtm-aist*.tar.gz ..
}

#==============================
# main
#==============================
get_opt $*

check_distribution
get_version_info

cleanup_files
create_source_package
extract_source
create_files
copy_control_files

build_package
copy_debfiles
