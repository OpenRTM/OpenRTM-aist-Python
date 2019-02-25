#!/bin/sh
#
# @file rpm_build.sh
# @author Noriaki Ando <n-ando@aist.go.jp>
# @brief rpm package build script
#
# $Id$
#
export LC_ALL=C
arch=`uname -i | sed -s 's/i[3-5]/i6/g'`

clean_dirs()
{
    rm -rf *.log *.bak .rpmrc
    dirs="BUILD RPMS SOURCES SPECS SRPMS BUILDROOT"
    for d in $dirs; do
	rm -rf $d
    done

}
get_opt()
{
    if test "x$1" = "xclean" ; then
	clean_dirs
	exit 0
    fi
}

check_distribution()
{
    dist_name=""
    dist_key=""
    FEDORA_VER=""
    # Check the lsb distribution name
    if test -f /etc/lsb-release ; then
	. /etc/lsb-release
	if test "x$DISTRIB_DESCRIPTION" != "x" ; then
	    dist_name=$DISTRIB_DESCRIPTION-`uname -m`
	fi
    fi
    # Check the Fedora version
    if test "x$dist_name" = "x" && test -f /etc/fedora-release ; then
        dist_name=`cat /etc/fedora-release`-`uname -m`
        dist_key=`sed -e 's/.[^0-9]*\([0-9]\+\).*/\1/' /etc/fedora-release`
        FEDORA_VER=$dist_key
    fi
    #Check the Debian version
    if test "x$dist_name" = "x" && test -f /etc/debian_version ; then
	dist_name="Debian"`cat /etc/debian_version`-`uname -m`
	dist_key=""
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
    if test "x$dist_key" = "x" ; then
	echo "This is not Feodra/Vine/Scientific/RedHat distribution"
	exit 0
    fi
    DIST_KEY=$dist_key
    DIST_NAME=`echo $dist_name | sed 's/[ |\(|\)]//g'`
}

get_version_info()
{
    VERSION=`../../setup.py --version`
    SHORT_VERSION=`echo $VERSION | sed 's/\.[0-9]*$//'`
}

create_rpmbuilddir()
{
    clean_dirs
    mkdir {BUILD,RPMS,SOURCES,SPECS,SRPMS}
    mkdir RPMS/{$arch,noarch}
    export BUILD_DIR=`pwd`
}

rewrite_chebang_to_python3()
{
    if [ $FEDORA_VER -ge 29 ] ; then
        find ../../OpenRTM_aist -name "*.py" | xargs -I {} sh -c "sed -i -e '1 s/env python/python3/g' {}"
        find ../../OpenRTM_aist/utils/rtcd -name "rtcd_python" | xargs -I {} sh -c "sed -i -e '1 s/env python/python3/g' {}"
        find ../../OpenRTM_aist/utils/rtcprof -name "rtcprof_python" | xargs -I {} sh -c "sed -i -e '1 s/env python/python3/g' {}"
    fi
}

create_source_package()
{
    cd ../../
    ./setup.py build
    ./setup.py sdist
    cd -
}

copy_source_package()
{
    cp ../../dist/OpenRTM-aist-Python*.tar.gz ./SOURCES/
}

create_spec_file()
{
    if [ $FEDORA_VER -lt 29 ] ; then
        sed "s/__DISTNAME__/$DIST_KEY/g" openrtm-aist.spec.in > openrtm-aist.spec.1
    else
        sed "s/__DISTNAME__/$DIST_KEY/g" openrtm-aist_py3.spec.in > openrtm-aist.spec.1
    fi
    sed "s/__VERSION__/$VERSION/g" openrtm-aist.spec.1 > openrtm-aist.spec.2
    sed "s/__SHORT_VERSION__/$SHORT_VERSION/g" openrtm-aist.spec.2 > openrtm-aist.spec.3
    cp openrtm-aist.spec.3 SPECS/openrtm-aist.spec
    rm openrtm-aist.spec.[0-9]
    echo "%_topdir $BUILD_DIR" > .rpmrc
}

build_rpm()
{
    cd SPECS
    rpm_def="_topdir $BUILD_DIR"
    if rpmbuild --target "$arch" --define "$rpm_def" -ba openrtm-aist.spec ; then
	echo "Build successful"
    else
	echo "Build failed"
	exit 1
    fi
}

copy_rpm()
{
    find $BUILD_DIR -name '*.rpm' -exec cp {} ${BUILD_DIR}/.. \;
}

#------------------------------
# main
#------------------------------
get_opt $*

check_distribution
get_version_info

create_rpmbuilddir
rewrite_chebang_to_python3
create_source_package
copy_source_package
create_spec_file

build_rpm
copy_rpm
