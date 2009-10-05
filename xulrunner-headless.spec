%define nspr_version 4.8
%define nss_version 3.12.1.1
%define cairo_version 0.6
%define lcms_version 1.17
%define freetype_version 2.1.9
%define sqlite_version 3.5
%define source_name xulrunner

%define build_langpacks      1

%define version 1.9.2
%define snapshot 20090731
%define sversion 0.0~%{snapshot}
%define rel 1
%define release %mkrel 0.%{snapshot}.%{rel}

%define version_internal %{version}a1pre-headless
%define mozappdir         %{_libdir}/%{source_name}-%{version_internal}
%define mozdevdir         %{_libdir}/%{source_name}-devel-%{version_internal}

Summary:        XUL Runtime for Gecko Applications
Name:           xulrunner-headless
Version:        %{version}
Release:        %{release}
URL:            http://developer.mozilla.org/En/XULRunner
License:        MPLv1.1 or GPLv2+ or LGPLv2+
Group:          System/Libraries
Source0:        xulrunner-%{sversion}.tar.bz2
%if %{build_langpacks}
Source2:        xulrunner-langpacks.tar.bz2
%endif
Source10:       %{source_name}-mozconfig


# build patches
Patch0:         mozilla-jemalloc.patch
Patch1:         xulrunner-pkgconfig.patch
Patch2:         moblin-repack.patch
Patch3:         plugin-focus.patch

Patch10:	xulrunner-1.9.0.5-fix-string-format.patch

# ---------------------------------------------------

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

Autoreq: 0
Autoprov: 0

BuildRequires:  nspr-devel >= %{nspr_version}
BuildRequires:  nss-static-devel >= %{nss_version}
#BuildRequires:  cairo-devel >= %{cairo_version}
#BuildRequires:  libpng-devel
#BuildRequires:  libjpeg-devel
BuildRequires:  zip
#BuildRequires:  bzip2-devel
#BuildRequires:  zlib-devel
#BuildRequires:  lcms-devel >= %{lcms_version}
BuildRequires:  libIDL-devel
BuildRequires:  gtk2-devel
BuildRequires:  gnome-vfs2-devel
BuildRequires:  libgnome-devel
BuildRequires:  gnomeui2-devel
BuildRequires:  krb5-devel
BuildRequires:  pango-devel
BuildRequires:  freetype2-devel >= %{freetype_version}
BuildRequires:  libxt-devel
BuildRequires:  libxrender-devel
#BuildRequires:  hunspell-devel
BuildRequires:  sqlite-devel >= %{sqlite_version}
BuildRequires:  startup-notification-devel
BuildRequires:  alsa-lib-devel
# For -sqlite.patch
BuildRequires:  autoconf2.1
BuildRequires:  openssl-devel

Requires:       mozilla-filesystem
Requires:       nspr >= %{nspr_version}
Requires:       nss >= %{nss_version}

Provides:       gecko-libs-headless = %{version}

%description
XULRunner provides the XUL Runtime environment for Gecko applications.

%package devel
Summary: Development files for Gecko
Group: Development/Other

Provides: gecko-headless-devel = %{version}
Requires: %{name} = %{version}-%{release}

%description devel
Gecko development files.

%package python
Summary: Files needed to run Gecko applications written in python
Group: Development/Python
BuildRequires: python-devel
Requires: gecko-libs-headless = %{version}-%{release}
Provides: pyxpcom = %{version}-%{release}
Provides: gecko-python = %{version}-%{release}

%description python
Files needed to run Gecko applications written in python.

%package python-devel
Summary: Development files for building Gecko applications written in python
Group: Development/Python
Requires: gecko-headless-devel = %{version}-%{release}
Provides: pyxpcom-devel = %{version}-%{release}
Provides: gecko-python-devel = %{version}-%{release}

%description python-devel
Development files for building Gecko applications written in python.

#---------------------------------------------------------------------

%prep
%setup -q -c
#cd mozilla-central
cd %{source_name}-%{sversion}

#sed -e 's/__RPM_VERSION_INTERNAL__/%{version_internal}/' %{P:%%PATCH0} \
#    > version.patch
#%{__patch} -p1 -b --suffix .version --fuzz=0 < version.patch

#autoconf-2.13
%patch0 -p1 -b .jemalloc
%patch1 -p1 -b .pc
%patch2 -p1 -b .moblin-repack
%patch3 -p1 -b .plugin-focus

%patch10 -p0 -b .string-format

%{__rm} -f .mozconfig
%{__cp} %{SOURCE10} .mozconfig

#---------------------------------------------------------------------

%build
#cd mozilla-central
cd %{source_name}-%{sversion}

INTERNAL_GECKO=%{version_internal}
MOZ_APP_DIR=%{_libdir}/%{name}-${INTERNAL_GECKO}

# Mozilla builds with -Wall with exception of a few warnings which show up
# everywhere in the code; so, don't override that.
MOZ_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | %{__sed} -e 's/-Wall//')
export CFLAGS=$MOZ_OPT_FLAGS
export CXXFLAGS=$MOZ_OPT_FLAGS

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

MOZ_SMP_FLAGS=-j1
%ifnarch ppc ppc64 s390 s390x
[ -z "$RPM_BUILD_NCPUS" ] && \
     RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"
[ "$RPM_BUILD_NCPUS" -gt 1 ] && MOZ_SMP_FLAGS=-j2
%endif

export LDFLAGS="-Wl,-rpath,${MOZ_APP_DIR}"
make -f client.mk build STRIP="/bin/true" MOZ_MAKE_FLAGS="$MOZ_SMP_FLAGS"

#---------------------------------------------------------------------

%install
#cd mozilla-central
cd %{source_name}-%{sversion}
%{__rm} -rf $RPM_BUILD_ROOT

INTERNAL_GECKO=%{version_internal}

INTERNAL_APP_NAME=%{source_name}-${INTERNAL_GECKO}
MOZ_APP_DIR=%{_libdir}/${INTERNAL_APP_NAME}

INTERNAL_APP_SDK_NAME=%{source_name}-devel-${INTERNAL_GECKO}
MOZ_APP_SDK_DIR=%{_libdir}/${INTERNAL_APP_SDK_NAME}

DESTDIR=$RPM_BUILD_ROOT make install

%{__mkdir_p} $RPM_BUILD_ROOT/${MOZ_APP_DIR} \
             $RPM_BUILD_ROOT%{_datadir}/idl/${INTERNAL_APP_SDK_NAME} \
             $RPM_BUILD_ROOT%{_includedir}/${INTERNAL_APP_SDK_NAME}
%{__install} -p dist/sdk/bin/regxpcom $RPM_BUILD_ROOT/$MOZ_APP_DIR

%{__mkdir_p} $RPM_BUILD_ROOT{%{_libdir},%{_bindir},%{_datadir}/applications}

# set up our default preferences
#%{__cat} %{SOURCE12} | %{__sed} -e 's,RPM_VERREL,%{version}-%{release},g' > rh-default-prefs
#%{__install} -p -D -m 644 rh-default-prefs $RPM_BUILD_ROOT/${MOZ_APP_DIR}/defaults/pref/all-redhat.js
#%{__rm} rh-default-prefs

# Start script install
#%{__rm} -rf $RPM_BUILD_ROOT%{_bindir}/%{name}
#%{__cat} %{SOURCE21} | %{__sed} -e 's,XULRUNNER_VERSION,%{version_internal},g' > \
#  $RPM_BUILD_ROOT%{_bindir}/%{name}
#%{__chmod} 755 $RPM_BUILD_ROOT%{_bindir}/%{name}

%if %{build_langpacks}
# Install langpacks
%{__tar} xjf %{SOURCE2}
sys_chrome=$RPM_BUILD_ROOT/%{mozappdir}/chrome
for langpack in `ls xulrunner-langpacks/*.xpi`; do
  lang=`basename $langpack .xpi`
  unzip $langpack -d $lang
  find $lang -type f | xargs chmod 644
  cat $lang/chrome.manifest | grep 'chrome\/' | sed -e 's/chrome\///'  > ${sys_chrome}/${lang}.manifest
  cp $lang/chrome/${lang}.jar ${sys_chrome}/

  rm -rf $lang
done
%{__rm} -rf xulrunner-langpacks
%endif # build_langpacks

%{__rm} -f $RPM_BUILD_ROOT${MOZ_APP_DIR}/%{name}-config

#cd $RPM_BUILD_ROOT${MOZ_APP_DIR}/chrome
#find . -name "*" -type d -maxdepth 1 -exec %{__rm} -rf {} \;
#cd -

# Prepare our devel package
%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_SDK_NAME}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig

%{__cp} -rL dist/include/* \
  $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}

## Copy mozilla-config to stable include dir
#%{__cp} dist/include/mozilla-config.h \
#  $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}/stable

# Fix multilib devel conflicts...
%ifarch x86_64 ia64 s390x ppc64
%define mozbits 64
%else
%define mozbits 32
%endif

function install_file() {
genheader=$*
mv ${genheader}.h ${genheader}%{mozbits}.h
cat > ${genheader}.h << EOF
// This file exists to fix multilib conflicts
#if defined(__x86_64__) || defined(__ia64__) || defined(__s390x__) || defined(__powerpc64__)
#include "${genheader}64.h"
#else
#include "${genheader}32.h"
#endif
EOF
}

pushd $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}
install_file "mozilla-config"
popd

#pushd $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}/stable
#install_file "mozilla-config"
#popd

#pushd $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}/unstable
#install_file "mozilla-config"
#popd

pushd $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}
install_file "jsautocfg"
popd

#pushd $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}/unstable
#install_file "jsautocfg"
#popd

%{__install} -p -c -m 755 dist/bin/xpcshell \
  dist/bin/xpidl \
  dist/bin/xpt_dump \
  dist/bin/xpt_link \
  $RPM_BUILD_ROOT/${MOZ_APP_DIR}

#%{__rm} -rf $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_NAME}
#%{__rm} -rf $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_NAME}

#%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/include
#ln -s  %{_includedir}/${INTERNAL_APP_SDK_NAME}/unstable \
#       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/include
#%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/idl
#ln -s  %{_datadir}/idl/${INTERNAL_APP_SDK_NAME}/unstable \
#       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/idl

#%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/include
#ln -s  %{_includedir}/${INTERNAL_APP_SDK_NAME}/stable \
#       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/include
#%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/idl
#ln -s  %{_datadir}/idl/${INTERNAL_APP_SDK_NAME}/stable \
#       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/idl

find $RPM_BUILD_ROOT/%{_includedir} -type f -name "*.h" | xargs chmod 644
find $RPM_BUILD_ROOT/%{_datadir}/idl -type f -name "*.idl" | xargs chmod 644

%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/lib/*.so
pushd $RPM_BUILD_ROOT${MOZ_APP_DIR}
for i in *.so; do
    ln -s ${MOZ_APP_DIR}/$i $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/lib/$i
done
popd

# GRE stuff
%ifarch x86_64 ia64 ppc64 s390x
%define gre_conf_file gre64-headless.conf
%else
%define gre_conf_file gre-headless.conf
%endif

MOZILLA_GECKO_VERSION=`./config/milestone.pl --topsrcdir=.`
%{__mv} $RPM_BUILD_ROOT/etc/gre.d/$MOZILLA_GECKO_VERSION".system.conf" \
        $RPM_BUILD_ROOT/etc/gre.d/%{gre_conf_file}
chmod 644 $RPM_BUILD_ROOT/etc/gre.d/%{gre_conf_file}

# Library path
%ifarch x86_64 ia64 ppc64 s390x
%define ld_conf_file xulrunner-headless-64.conf
%else
%define ld_conf_file xulrunner-headless-32.conf
%endif

%{__mkdir_p} $RPM_BUILD_ROOT/etc/ld.so.conf.d
%{__cat} > $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{ld_conf_file} << EOF
${MOZ_APP_DIR}
${MOZ_APP_SDK_DIR}/sdk/lib
EOF

# Copy over the LICENSE
%{__install} -p -c -m 644 LICENSE $RPM_BUILD_ROOT${MOZ_APP_DIR}

# Use the system hunspell dictionaries
#%{__rm} -rf ${RPM_BUILD_ROOT}${MOZ_APP_DIR}/dictionaries
#ln -s %{_datadir}/myspell ${RPM_BUILD_ROOT}${MOZ_APP_DIR}/dictionaries

# ghost files
%{__mkdir_p} $RPM_BUILD_ROOT${MOZ_APP_DIR}/components
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/compreg.dat
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/xpti.dat

# remove /usr/bin/xulrunner
%{__rm} -f $RPM_BUILD_ROOT%{_bindir}/xulrunner


%clean
%{__rm} -rf $RPM_BUILD_ROOT

#---------------------------------------------------------------------

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%preun
# is it a final removal?
if [ $1 -eq 0 ]; then
  %{__rm} -rf ${MOZ_APP_DIR}/components
fi

%files
%defattr(-,root,root,-)
#%{_bindir}/xulrunner
%dir /etc/gre.d
/etc/gre.d/%{gre_conf_file}
#%dir %{mozappdir}
%doc %attr(644, root, root) %{mozappdir}/LICENSE
%doc %attr(644, root, root) %{mozappdir}/README.txt
%{mozappdir}/chrome
#%{mozappdir}/dictionaries
%dir %{mozappdir}/components
%ghost %{mozappdir}/components/compreg.dat
%ghost %{mozappdir}/components/xpti.dat
#%{mozappdir}/components/*.so
%{mozappdir}/*.so
%{mozappdir}/plugins/*.so
%{mozappdir}/components/*.xpt
#%exclude %{mozappdir}/components/libpyloader.so
%attr(644, root, root) %{mozappdir}/components/*.js
%{mozappdir}/defaults
%{mozappdir}/dictionaries
%{mozappdir}/greprefs
#%dir %{mozappdir}/icons
#%attr(644, root, root) %{mozappdir}/icons/*
#%{mozappdir}/js
%{mozappdir}/modules
#%{mozappdir}/plugins
%{mozappdir}/res
#%{mozappdir}/*.so
#%{mozappdir}/mozilla-xremote-client
%{mozappdir}/run-mozilla.sh
%{mozappdir}/regxpcom
%{mozappdir}/xulrunner
%{mozappdir}/xulrunner-bin
%{mozappdir}/xulrunner-stub
%{mozappdir}/platform.ini
%{mozappdir}/dependentlibs.list
%{_sysconfdir}/ld.so.conf.d/xulrunner*.conf

# XXX See if these are needed still
#%{mozappdir}/updater*
%{mozappdir}/updater
%{mozappdir}/update.locale

# what are these?
#%{mozappdir}/*.chk

# we don't want these
%exclude %{mozdevdir}/bin
%exclude %{mozdevdir}/idl
%exclude %{mozdevdir}/include
%exclude %{mozdevdir}/lib

%files devel
%defattr(-,root,root,-)
#%dir %{_datadir}/idl/%{name}*%{version_internal}
%{_datadir}/idl/%{source_name}-%{version_internal}
%{_includedir}/%{source_name}*%{version_internal}
#%exclude %{_includedir}/%{name}*%{version_internal}/unstable
#%exclude %{_includedir}/%{name}*%{version_internal}/pyxpcom
#%dir %{_libdir}/%{name}-sdk-*
#%dir %{_libdir}/%{name}-sdk-*/sdk
%dir %{mozdevdir}/sdk
%{mozappdir}/xpcshell
%{mozappdir}/xpidl
%{mozappdir}/xpt_dump
%{mozappdir}/xpt_link
#%{_libdir}/%{name}-sdk-*/*.h
#%{_libdir}/%{name}-sdk-*/sdk/*
%{mozdevdir}/*.h
%{mozdevdir}/sdk/*
#%exclude %{_libdir}/%{name}-sdk-%{version_internal}/sdk/lib/libpyxpcom.so
#%exclude %{_libdir}/pkgconfig/*gtkmozembed*.pc
%{_libdir}/pkgconfig/*.pc

# we don't want these
%exclude %{mozdevdir}/bin
%exclude %{mozdevdir}/idl
%exclude %{mozdevdir}/include
%exclude %{mozdevdir}/lib

%files python
#%{mozappdir}/components/pyabout.py*
#%{mozappdir}/components/libpyloader.so
#%{mozappdir}/python

%files python-devel
#%{_includedir}/%{name}*%{version_internal}/pyxpcom
#%{_libdir}/%{name}-sdk-%{version_internal}/sdk/lib/libpyxpcom.so

#---------------------------------------------------------------------
