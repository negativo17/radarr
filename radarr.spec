# mock configuration:
# - Requires network for running yarn/dotnet build

%global debug_package %{nil}
%define _build_id_links none

%global user %{name}
%global group %{name}

%global dotnet 8.0

%ifarch x86_64
%global rid x64
%endif

%ifarch aarch64
%global rid arm64
%endif

%ifarch armv7hl
%global rid arm
%endif

%if 0%{?fedora}
%global __requires_exclude ^liblttng-ust\\.so\\.0.*$
%endif

Name:           radarr
Version:        5.28.0.10274
Release:        1%{?dist}
Summary:        Automated manager and downloader for Movies
License:        GPLv3
URL:            https://radarr.video/

BuildArch:      x86_64 aarch64 armv7hl

Source0:        https://github.com/Radarr/Radarr/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source10:       %{name}.service
Source11:       %{name}.xml
Source12:       %{name}.sysusers.conf

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
Requires:       %{name}-selinux

%description
Radarr is a PVR for Usenet and BitTorrent users. It can monitor multiple RSS
feeds for new movies and will grab, sort and rename them. It can also be
configured to automatically upgrade the quality of files already downloaded when
a better quality format becomes available.

%prep
%autosetup -p1 -n Radarr-%{version}

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
    -p:SelfContained=true \
    -v:normal

# Use a huge timeout for aarch64 builds
yarn install --frozen-lockfile --network-timeout 1000000
yarn run build --mode production

find . -name libcoreclrtraceptprovider.so -delete

%install
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -a _output/net*/* _output/UI %{buildroot}%{_libdir}/%{name}/

install -D -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 -p %{SOURCE11} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml
install -D -m 0644 -p %{SOURCE12} %{buildroot}%{_sysusersdir}/%{name}.conf

find %{buildroot} -name "*.pdb" -delete
find %{buildroot} -name "ffprobe" -exec chmod 0755 {} \;

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
%{_sysusersdir}/%{name}.conf
%{_unitdir}/%{name}.service

%changelog
* Sun Nov 09 2025 Simone Caronni <negativo17@gmail.com> - 5.28.0.10274-1
- Update to 5.28.0.10274.

* Sat Sep 06 2025 Simone Caronni <negativo17@gmail.com> - 5.27.5.10198-2
- Make sure tracerpt is disabled, it requires an old liblttng-ust.

* Thu Sep 04 2025 Simone Caronni <negativo17@gmail.com> - 5.27.5.10198-1
- Update to 5.27.5.10198.

* Fri Jun 13 2025 Simone Caronni <negativo17@gmail.com> - 5.26.2.10099-1
- Update to 5.26.2.10099.

* Sun May 11 2025 Simone Caronni <negativo17@gmail.com> - 5.22.4.9896-1
- Update to 5.22.4.9896.

* Sun Apr 13 2025 Simone Caronni <negativo17@gmail.com> - 5.21.1.9799-1
- Update to 5.21.1.9799.

* Tue Mar 11 2025 Simone Caronni <negativo17@gmail.com> - 5.19.3.9730-2
- Fix for GHSA-65x7-c272-7g7r.

* Mon Mar 10 2025 Simone Caronni <negativo17@gmail.com> - 5.19.3.9730-1
- Update to 5.19.3.9730.

* Tue Feb 04 2025 Simone Caronni <negativo17@gmail.com> - 5.18.4.9674-1
- Update to 5.18.4.9674.

* Mon Jan 06 2025 Simone Caronni <negativo17@gmail.com> - 5.17.2.9580-1
- Update to 5.17.2.9580.

* Fri Dec 20 2024 Simone Caronni <negativo17@gmail.com> - 5.16.3.9541-1
- Update to 5.16.3.9541.

* Thu Nov 28 2024 Simone Caronni <negativo17@gmail.com> - 5.15.1.9463-1
- Update to 5.15.1.9463.

* Sun Oct 27 2024 Simone Caronni <negativo17@gmail.com> - 5.14.0.9383-1
- Update to 5.14.0.9383.
- Switch to .net 8.0 for building.

* Thu Oct 10 2024 Simone Caronni <negativo17@gmail.com> - 5.11.0.9244-1
- Update to 5.11.0.9244.

* Tue Sep 24 2024 Simone Caronni <negativo17@gmail.com> - 5.10.4.9218-1
- Update to 5.10.4.9218.

* Thu Sep 12 2024 Simone Caronni <negativo17@gmail.com> - 5.10.2.9164-1
- Update to 5.10.2.9164.

* Thu Aug 29 2024 Simone Caronni <negativo17@gmail.com> - 5.10.0.9090-1
- Update to 5.10.0.9090.

* Sun Aug 18 2024 Simone Caronni <negativo17@gmail.com> - 5.9.0.9058-1
- Update to 5.9.0.9058.

* Sun Aug 04 2024 Simone Caronni <negativo17@gmail.com> - 5.8.3.8933-1
- Update to 5.8.3.8933.
- Fix for https://github.com/advisories/GHSA-63p8-c4ww-9cg7.
- Clean up SPEC file.

* Wed Jul 10 2024 Simone Caronni <negativo17@gmail.com> - 5.8.1.8906-1
- Update to 5.8.1.8906.

* Wed Jul 03 2024 Simone Caronni <negativo17@gmail.com> - 5.8.0.8897-1
- Update to 5.8.0.8897.

* Fri Jun 21 2024 Simone Caronni <negativo17@gmail.com> - 5.7.0.8882-1
- Update to 5.7.0.8882.

* Thu May 16 2024 Simone Caronni <negativo17@gmail.com> - 5.6.0.8846-1
- Update to 5.6.0.8846.

* Wed May 08 2024 Simone Caronni <negativo17@gmail.com> - 5.5.2.8781-1
- Update to 5.5.2.8781.

* Wed Apr 24 2024 Simone Caronni <negativo17@gmail.com> - 5.5.0.8730-1
- Update to 5.5.0.8730.

* Tue Apr 16 2024 Simone Caronni <negativo17@gmail.com> - 5.4.6.8723-1
- Update to 5.4.6.8723.

* Tue Apr 02 2024 Simone Caronni <negativo17@gmail.com> - 5.4.4.8688-1
- Update to 5.4.4.8688.

* Wed Mar 20 2024 Simone Caronni <negativo17@gmail.com> - 5.4.3.8677-1
- Update to 5.4.3.8677.

* Tue Mar 12 2024 Simone Caronni <negativo17@gmail.com> - 5.4.2.8667-1
- Update to 5.4.2.8667.

* Sun Mar 03 2024 Simone Caronni <negativo17@gmail.com> - 5.4.1.8654-1
- Update to 5.4.1.8654.

* Tue Feb 20 2024 Simone Caronni <negativo17@gmail.com> - 5.3.6.8612-1
- Update to 5.3.6.8612.

* Mon Feb 12 2024 Simone Caronni <negativo17@gmail.com> - 5.3.5.8592-1
- Update to 5.3.5.8592.

* Mon Feb 05 2024 Simone Caronni <negativo17@gmail.com> - 5.3.4.8567-1
- Update to 5.3.4.8567.

* Wed Jan 31 2024 Simone Caronni <negativo17@gmail.com> - 5.3.3.8535-1
- Update to 5.3.3.8535.

* Thu Jan 25 2024 Simone Caronni <negativo17@gmail.com> - 5.3.2.8504-1
- Update to 5.3.2.8504.

* Wed Jan 17 2024 Simone Caronni <negativo17@gmail.com> - 5.3.1.8438-1
- Update to 5.3.1.8438.

* Mon Jan 08 2024 Simone Caronni <negativo17@gmail.com> - 5.3.0.8410-1
- Update to 5.3.0.8410.

* Thu Dec 28 2023 Simone Caronni <negativo17@gmail.com> - 5.2.6.8376-1
- Update to 5.2.6.8376.

* Thu Dec 21 2023 Simone Caronni <negativo17@gmail.com> - 5.2.5.8361-1
- Update to 5.2.5.8361.

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
