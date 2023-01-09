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
Version:        4.3.2.6857
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
pushd src
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
dotnet publish \
    --configuration Release \
    --framework net%{dotnet} \
    --output _output \
    --runtime linux-%{rid} \
    --self-contained \
    --verbosity normal \
    Radarr.sln
popd

# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
yarn run build --mode production

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a src/_output/* _output/UI %{buildroot}%{_libdir}/%{name}/

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
