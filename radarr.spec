# mock configuration:
# - Requires network for running yarn/dotnet build

%global debug_package %{nil}
%define _build_id_links none

%global user %{name}
%global group %{name}

%global dotnet 6.0

%ifarch x86_64
%global rid x64
%endif

%ifarch aarch64
%global rid arm64
%endif

%ifarch armv7hl
%global rid arm
%endif

%if 0%{?fedora} >= 36
%global __requires_exclude ^liblttng-ust\\.so\\.0.*$
%endif

Name:           radarr
Version:        5.2.4.8328
Release:        1%{?dist}
Summary:        Automated manager and downloader for Movies
License:        GPLv3
URL:            https://radarr.video/

BuildArch:      x86_64 aarch64 armv7hl

Source0:        https://github.com/Radarr/Radarr/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source10:       %{name}.service
Source11:       %{name}.xml

BuildRequires:  dotnet-sdk-%{dotnet}
BuildRequires:  firewalld-filesystem
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  nodejs
BuildRequires:  systemd
BuildRequires:  tar
BuildRequires:  yarnpkg

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       libmediainfo
Requires:       sqlite
Requires(pre):  shadow-utils

%if 0%{?rhel} >= 8 || 0%{?fedora}
Requires:       (%{name}-selinux if selinux-policy)
%endif

%description
Radarr is a PVR for Usenet and BitTorrent users. It can monitor multiple RSS
feeds for new movies and will grab, sort and rename them. It can also be
configured to automatically upgrade the quality of files already downloaded when
a better quality format becomes available.

%prep
%autosetup -n Radarr-%{version}

# Remove test coverage and Windows specific stuff from project file
pushd src
dotnet sln Radarr.sln remove \
  NzbDrone.Api.Test \
  NzbDrone.Automation.Test \
  NzbDrone.Common.Test \
  NzbDrone.Core.Test \
  NzbDrone.Host.Test \
  NzbDrone.Integration.Test \
  NzbDrone.Libraries.Test \
  NzbDrone.Mono.Test \
  NzbDrone.Test.Common \
  NzbDrone.Test.Dummy \
  NzbDrone.Update.Test \
  NzbDrone.Windows.Test \
  NzbDrone.Windows \
  ServiceHelpers/ServiceInstall \
  ServiceHelpers/ServiceUninstall
popd

%build
export DOTNET_CLI_TELEMETRY_OPTOUT=1
dotnet msbuild -restore src/Radarr.sln \
    -p:RuntimeIdentifiers=linux-%{rid} \
    -p:Configuration=Release \
    -p:Platform=Posix \
    -v:normal

# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
yarn run build --mode production

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a _output/net%{dotnet}/* _output/UI %{buildroot}%{_libdir}/%{name}/

install -D -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 -p %{SOURCE11} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

find %{buildroot} -name "*.pdb" -delete
find %{buildroot} -name "ffprobe" -exec chmod 0755 {} \;

%pre
getent group %{group} >/dev/null || groupadd -r %{group}
getent passwd %{user} >/dev/null || \
    useradd -r -g %{group} -d %{_sharedstatedir}/%{name} -s /sbin/nologin \
    -c "%{name}" %{user}
exit 0

%post
%systemd_post %{name}.service
%firewalld_reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%attr(750,%{user},%{group}) %{_sharedstatedir}/%{name}
%{_libdir}/%{name}
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
* Tue Dec 12 2023 Simone Caronni <negativo17@gmail.com> - 5.2.4.8328-1
- Update to 5.2.4.8328.

* Sun Nov 26 2023 Simone Caronni <negativo17@gmail.com> - 5.2.3.8303-1
- Update to 5.2.3.8303.

* Wed Nov 15 2023 Simone Caronni <negativo17@gmail.com> - 5.2.0.8250-1
- Update to 5.2.0.8250.

* Mon Oct 30 2023 Simone Caronni <negativo17@gmail.com> - 5.1.2.8207-1
- Update to 5.1.2.8207.

* Tue Oct 17 2023 Simone Caronni <negativo17@gmail.com> - 5.1.0.8172-1
- Update to 5.1.0.8172.

* Tue Oct 03 2023 Simone Caronni <negativo17@gmail.com> - 5.0.3.8107-1
- Update to 5.0.3.8107.

* Wed Sep 27 2023 Simone Caronni <negativo17@gmail.com> - 5.0.2.8103-1
- Update to 5.0.2.8103.

* Mon Sep 11 2023 Simone Caronni <negativo17@gmail.com> - 5.0.1.7993-2
- Change build to more closely match upstream.

* Mon Sep 04 2023 Simone Caronni <negativo17@gmail.com> - 5.0.1.7993-1
- Update to 5.0.1.7993.

* Sun Aug 27 2023 Simone Caronni <negativo17@gmail.com> - 5.0.0.7952-1
- Update to 5.0.0.7952.

* Sun Aug 20 2023 Simone Caronni <negativo17@gmail.com> - 4.7.5.7809-1
- Update to 4.7.5.7809.

* Mon Aug 07 2023 Simone Caronni <negativo17@gmail.com> - 4.7.4.7758-1
- Update to 4.7.4.7758.

* Mon Jul 17 2023 Simone Caronni <negativo17@gmail.com> - 4.7.1.7640-1
- Update to 4.7.1.7640.

* Tue Jul 11 2023 Simone Caronni <negativo17@gmail.com> - 4.7.0.7588-1
- Update to 4.7.0.7588.

* Tue Jul 04 2023 Simone Caronni <negativo17@gmail.com> - 4.6.4.7568-1
- Update to 4.6.4.7568.

* Sat Jul 01 2023 Simone Caronni <negativo17@gmail.com> - 4.6.3.7516-1
- Update to 4.6.3.7516.

* Thu Jun 22 2023 Simone Caronni <negativo17@gmail.com> - 4.6.2.7490-1
- Update to 4.6.2.7490.

* Mon Jun 12 2023 Simone Caronni <negativo17@gmail.com> - 4.6.1.7456-1
- Update to 4.6.1.7456.

* Tue Jun 06 2023 Simone Caronni <negativo17@gmail.com> - 4.6.0.7439-1
- Update to 4.6.0.7439.

* Tue May 23 2023 Simone Caronni <negativo17@gmail.com> - 4.5.2.7318-1
- Update to 4.5.2.7318.

* Tue May 16 2023 Simone Caronni <negativo17@gmail.com> - 4.5.1.7282-1
- Update to 4.5.1.7282.

* Thu Apr 27 2023 Simone Caronni <negativo17@gmail.com> - 4.5.0.7106-1
- Update to 4.5.0.7106.

* Mon Apr 10 2023 Simone Caronni <negativo17@gmail.com> - 4.4.3.7030-1
- Update to 4.4.3.7030.

* Fri Feb 24 2023 Simone Caronni <negativo17@gmail.com> - 4.4.2.6956-1
- Update to 4.4.2.6956.

* Mon Feb 06 2023 Simone Caronni <negativo17@gmail.com> - 4.4.1.6926-1
- Update to 4.4.1.6926.

* Sun Jan 22 2023 Simone Caronni <negativo17@gmail.com> - 4.4.0.6882-1
- Update to 4.4.0.6882.

* Mon Jan 09 2023 Simone Caronni <negativo17@gmail.com> - 4.3.2.6857-1
- Update to 4.3.2.6857.

* Mon Dec 12 2022 Simone Caronni <negativo17@gmail.com> - 4.3.1.6822-1
- Update to 4.3.1.6822.

* Fri Oct 28 2022 Simone Caronni <negativo17@gmail.com> - 4.3.0.6671-3
- Add note about mock configuration.
- Trim changelog.

* Wed Oct 26 2022 Simone Caronni <negativo17@gmail.com> - 4.3.0.6671-2
- Drop OpenSSL workaround.

* Tue Oct 25 2022 Simone Caronni <negativo17@gmail.com> - 4.3.0.6671-1
- Update to 4.3.0.6671.

* Mon Sep 26 2022 Simone Caronni <negativo17@gmail.com> - 4.2.3.6575-2
- Update to 4.2.4.6635.

* Sun Sep 11 2022 Simone Caronni <negativo17@gmail.com> - 4.2.3.6575-1
- Update to 4.2.3.6575.

* Sun Sep 04 2022 Simone Caronni <negativo17@gmail.com> - 4.2.2.6503-2
- Fix ffprobe permissions (thanks GarryPlotter).

* Tue Aug 23 2022 Simone Caronni <negativo17@gmail.com> - 4.2.2.6503-1
- Update to 4.2.2.6503.

* Mon Aug 15 2022 Simone Caronni <negativo17@gmail.com> - 4.2.1.6478-1
- Update to 4.2.1.6478.

* Thu Jun 16 2022 Simone Caronni <negativo17@gmail.com> - 4.1.0.6175-3
- Fix issues with LTTng Userspace Tracer library 2.13+.

* Sun May 15 2022 Simone Caronni <negativo17@gmail.com> - 4.1.0.6175-2
- Adjust build for OpenSSL 3.0 based distributions.

* Wed Apr 20 2022 Simone Caronni <negativo17@gmail.com> - 4.1.0.6175-1
- Update to 4.1.0.6175.

* Mon Mar 14 2022 Simone Caronni <negativo17@gmail.com> - 4.0.5.5981-2
- Fix typo that actually let the Windows service executables to be built.

* Sun Mar 06 2022 Simone Caronni <negativo17@gmail.com> - 4.0.5.5981-1
- Update to 4.0.5.5981.

* Mon Feb 28 2022 Simone Caronni <negativo17@gmail.com> - 4.0.5.5977-1
- Update to 4.0.5.5977.

* Fri Feb 25 2022 Simone Caronni <negativo17@gmail.com> - 4.0.4.5922-3
- Remove test coverage stuff.

* Sat Feb 12 2022 Simone Caronni <negativo17@gmail.com> - 4.0.4.5922-2
- Clean up SPEC file and fix build on aarch64.

* Fri Feb 04 2022 Simone Caronni <negativo17@gmail.com> - 4.0.4.5922-1
- Update to 4.0.4.5922.
