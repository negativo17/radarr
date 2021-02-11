%global user %{name}
%global group %{name}

Name:           radarr
Version:        3.1.0.4624
Release:        1%{?dist}
Summary:        Automated manager and downloader for Movies
License:        GPLv3
URL:            https://radarr.video/

Source0:        https://radarr.servarr.com/v1/update/nightly/updatefile?version=%{version}&os=linux&runtime=netcore&arch=x64#/Radarr.nightly.%{version}.linux-core-x64.tar.gz
Source1:        https://radarr.servarr.com/v1/update/nightly/updatefile?version=%{version}&os=linux&runtime=netcore&arch=arm64#/Radarr.nightly.%{version}.linux-core-arm64.tar.gz
Source5:        https://raw.githubusercontent.com/Radarr/Radarr/develop/LICENSE
Source6:        https://raw.githubusercontent.com/Radarr/Radarr/develop/README.md
Source10:       %{name}.service
Source11:       %{name}.xml

BuildRequires:  firewalld-filesystem
BuildRequires:  systemd
BuildRequires:  tar

Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
Requires:       libmediainfo
Requires:       mono-core
Requires:       mono-locale-extras
Requires:       sqlite
Requires(pre):  shadow-utils

%description
Radarr is a PVR for Usenet and BitTorrent users. It can monitor multiple RSS
feeds for new movies and will grab, sort and rename them. It can also be
configured to automatically upgrade the quality of files already downloaded when
a better quality format becomes available.

%prep
%ifarch x86_64
%setup -q -n Radarr
%endif

%ifarch aarch64
%setup -q -T -b 1 -n Radarr
%endif

cp %{SOURCE5} %{SOURCE6} .

%install
mkdir -p %{buildroot}%{_datadir}/%{name}
mkdir -p %{buildroot}%{_prefix}/lib/firewalld/services/
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}

cp -fr * %{buildroot}%{_datadir}/%{name}

install -m 0644 -p %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -m 0644 -p %{SOURCE11} %{buildroot}%{_prefix}/lib/firewalld/services/%{name}.xml

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
%{_datadir}/%{name}
%{_prefix}/lib/firewalld/services/%{name}.xml
%{_unitdir}/%{name}.service

%changelog
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
