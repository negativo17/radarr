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

Name:           radarr
Version:        4.0.5.5981
Release:        2%{?dist}
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

* Sun Jan 23 2022 Simone Caronni <negativo17@gmail.com> - 4.0.3.5879-1
- Update to 4.0.3.5879.

* Thu Jan 20 2022 Simone Caronni <negativo17@gmail.com> - 4.0.2.5836-1
- Update to 4.0.2.5836.

* Thu Jan 13 2022 Simone Caronni <negativo17@gmail.com> - 4.0.1.5813-1
- Update to 4.0.1.5813.

* Tue Jan 04 2022 Simone Caronni <negativo17@gmail.com> - 4.0.0.5745-1
- Update to 4.0.0.5745.

* Thu Jun 03 2021 Simone Caronni <negativo17@gmail.com> - 3.2.2.5080-1
- Update to 3.2.2.5080.

* Fri May 28 2021 Simone Caronni <negativo17@gmail.com> - 3.2.1.5070-1
- Update to 3.2.1.5070.

* Sun May 23 2021 Simone Caronni <negativo17@gmail.com> - 3.2.0.5048-1
- Update to 3.2.0.5048.

* Wed May 05 2021 Simone Caronni <negativo17@gmail.com> - 3.1.1.4954-1
- Update to 3.1.1.4954.

* Fri Apr 23 2021 Simone Caronni <negativo17@gmail.com> - 3.1.0.4893-2
- Do not create build-id links if no debug package is generated.

* Wed Apr 21 2021 Simone Caronni <negativo17@gmail.com> - 3.1.0.4893-1
- Update to 3.1.0.4893.
- Build binaries from source.

* Mon Apr 19 2021 Simone Caronni <negativo17@gmail.com> - 3.1.0.4887-1
- Update to 3.1.0.4887.

* Fri Mar 12 2021 Simone Caronni <negativo17@gmail.com> - 3.1.0.4735-1
- Update to 3.1.0.4735.
- Add SELinux requirements.

* Sun Mar 07 2021 Simone Caronni <negativo17@gmail.com> - 3.1.0.4690-1
- Update to 3.1.0.4690.
- Move installation to libdir.

* Thu Feb 11 2021 Simone Caronni <negativo17@gmail.com> - 3.1.0.4624-1
- Update to 3.1.0.4624.

* Tue Feb 02 2021 Simone Caronni <negativo17@gmail.com> - 3.1.0.4529-1
- Update to 3.1.0.4529.

* Thu Jan 21 2021 Simone Caronni <negativo17@gmail.com> - 3.0.2.4446-1
- Update to 3.0.2.4446.

* Thu Jan  7 2021 Simone Caronni <negativo17@gmail.com> - 3.0.1.4359-1
- Update to 3.0.1.4359.

* Sat Dec 26 2020 Simone Caronni <negativo17@gmail.com> - 3.0.1.4326-1
- Update to 3.0.1.4326.

* Tue Dec 08 2020 Simone Caronni <negativo17@gmail.com> - 3.0.0.4235-1
- Update to 3.0.0.4235.

* Sat Nov 21 2020 Simone Caronni <negativo17@gmail.com> - 3.0.0.4107-1
- Update to 3.0.0.4107.

* Tue Nov 17 2020 Simone Caronni <negativo17@gmail.com> - 3.0.0.4092-1
- Update to 3.0.0.4092.

* Thu Nov 05 2020 Simone Caronni <negativo17@gmail.com> - 3.0.0.3987-1
- Update to 3.0.0.3987.

* Fri Oct 16 2020 Simone Caronni <negativo17@gmail.com> - 3.0.0.3943-1
- Update to 3.0.0.3943.

* Thu Jul 09 2020 Simone Caronni <negativo17@gmail.com> - 0.2.0.1504-1
- Update to version 0.2.0.1504.

* Thu Feb 20 2020 Simone Caronni <negativo17@gmail.com> - 0.2.0.1480-1
- Update to 0.2.0.1480.

* Sat Dec 21 2019 Simone Caronni <negativo17@gmail.com> - 0.2.0.1450-1
- Update to 0.2.0.1450.

* Tue Jul 09 2019 Simone Caronni <negativo17@gmail.com> - 0.2.0.1358-1
- Update to 0.2.0.1358.

* Mon May 06 2019 Simone Caronni <negativo17@gmail.com> - 0.2.0.1344-1
- Update to 0.2.0.1344.

* Fri Feb 08 2019 Simone Caronni <negativo17@gmail.com> - 0.2.0.1293-1
- Update to v0.2.0.1293.

* Mon Dec 03 2018 Simone Caronni <negativo17@gmail.com> - 0.2.0.1217-2
- Add missing mono-locale-extras dependency.

* Sun Nov 25 2018 Simone Caronni <negativo17@gmail.com> - 0.2.0.1217-1
- Update to 0.2.0.1217.

* Fri Jul 20 2018 Simone Caronni <negativo17@gmail.com> - 0.2.0.1120-1
- First build.
