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
  rm -f ../openrtm*.deb
  rm -f ../openrtm*.dsc
  rm -f ../openrtm*.changes
  rm -f ../openrtm*.tar.gz
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
    VERSION=`dpkg-parsechangelog --show-field Version | cut -b 1-5`
    SHORT_VERSION=`echo $VERSION | sed 's/\.[0-9]*$//'`
    BUILD_ROOT="buildroot"
}

extract_source()
{
  mkdir ${BUILD_ROOT}
  cp -r ../../examples ${BUILD_ROOT}/
  cp -r ../../OpenRTM_aist* ${BUILD_ROOT}/
  cp ../../OpenRTM-aist.pth ${BUILD_ROOT}/
  find ${BUILD_ROOT}/examples | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
  find ${BUILD_ROOT}/examples -name "*.bat" | xargs rm -f
  rm ${BUILD_ROOT}/examples/rtc.conf.sample
  rm ${BUILD_ROOT}/OpenRTM_aist/RTM_IDL/*.pth
  rm -rf ${BUILD_ROOT}/OpenRTM_aist/RTM_IDL/ext
  rm -rf ${BUILD_ROOT}/OpenRTM_aist/docs
  rm -rf ${BUILD_ROOT}/OpenRTM_aist/ext/sdo/observer/test
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/extended_fsm/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/fsm4rtc_observer/*.idl
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/fsm4rtc_observer/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/fsm4rtc_observer/setup.*
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/http/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/logger/fluentlogger/*.conf
  rm -rf ${BUILD_ROOT}/OpenRTM_aist/ext/ssl/test
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/ssl/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/transport/OpenSplice/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/transport/ROS2Transport/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/ext/transport/ROSTransport/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/utils/rtcd/README
  rm ${BUILD_ROOT}/OpenRTM_aist/utils/rtcd/*.conf
  rm ${BUILD_ROOT}/OpenRTM_aist/utils/rtcd/*.bat
  rm ${BUILD_ROOT}/OpenRTM_aist/utils/rtcd/rtcd2_python
  rm ${BUILD_ROOT}/OpenRTM_aist/utils/rtcprof/*.bat
  rm ${BUILD_ROOT}/OpenRTM_aist/utils/rtcprof/rtcprof2_python
  cp -r ../../local/bin ${BUILD_ROOT}/
}

create_files()
{
  eval `dpkg-architecture`
  ARCH=$DEB_HOST_ARCH
  PKG_VERSION=`dpkg-parsechangelog | sed -n 's/^Version: //p'`
cat << EOF >> debian/files
openrtm2-python3_${PKG_VERSION}_${ARCH}.deb main extra
openrtm2-python3-example_${PKG_VERSION}_${ARCH}.deb main extra
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
  mv ./openrtm2*.deb ..
  mv ./openrtm2*.dsc ..
  mv ./openrtm2*.changes ..
  mv ./openrtm2*.tar.gz ..
}

#==============================
# main
#==============================
get_opt $*

check_distribution
get_version_info

cleanup_files
extract_source
create_files
copy_control_files

build_package
copy_debfiles
