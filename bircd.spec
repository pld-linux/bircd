#
# Conditional build
%bcond_with	smode	# build with /smode command support
%bcond_with	crypt	# build with crypted passwords support
#
Summary:	Internet Relay Chat Server
Summary(pl.UTF-8):	Serwer IRC (Internet Relay Chat)
Name:		bircd
%define		_rc	rc2
%define		_rel	1
Version:	2.1.0
Release:	0.%{_rc}.%{_rel}
Epoch:		1
License:	GPL
Group:		Daemons
Source0:	ftp://ftp.benet.uu3.net/pub/irc/%{name}-%{version}%{_rc}.tgz
# Source0-md5:	03ba33362b131fc0441d9f1724207bf7
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.logrotate
Source4:	%{name}.motd
Patch0:		%{name}-makefile.patch
Patch1:		%{name}-config.patch
Patch2:		%{name}-smode.patch
Patch3:		%{name}-crypt.patch
URL:		http://www.benet.uu3.net/~borg/
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(ircd)
Provides:	user(ircd)
Obsoletes:	ircd
Obsoletes:	ircd-hybrid
Obsoletes:	ircd-ptlink
Obsoletes:	ircd6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/ircd
%define		_localstatedir	/var/lib/ircd

%description
bIRCd is a small, simple and very fast IRC server. It is easy to
configure and use. It also has support for IPv6.

%description -l pl.UTF-8
bIRCd jest małym, prostym i bardzo szybkim serwerem IRC. Jest bardzo
prosty w konfiguracji i użytkowaniu. Posiada również wsparcie dla
IPv6.

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1
%{?with_smode:%patch2 -p1}
%{?with_crypt:%patch3 -p1}

%build
./Config
%{__make} \
	LIBDIR=%{_libdir}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_var}/log/{,archiv/}ircd,%{_sbindir}} \
	$RPM_BUILD_ROOT{%{_sysconfdir},/etc/{rc.d/init.d,sysconfig,logrotate.d}} \
	$RPM_BUILD_ROOT%{_localstatedir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ircd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/ircd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/logrotate.d/ircd
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/ircd.motd

touch $RPM_BUILD_ROOT%{_localstatedir}/ircd.pid

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -f -g 75 ircd
%useradd -g ircd -d /etc/ircd -u 75 -s /bin/true -c "IRC Service account" ircd

%post
/sbin/chkconfig --add ircd
%service ircd restart "IRC daemon"
touch /var/log/ircd/{opers.log,rejects.log,users.log}
chmod 640 /var/log/ircd/*
chown ircd:ircd /var/log/ircd/*

%preun
if [ "$1" = "0" ]; then
	%service ircd stop
	/sbin/chkconfig --del ircd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove ircd
	%groupremove ircd
fi

%files
%defattr(644,root,root,755)
%doc README CHANGES
%doc doc/{Advertisement,Authors,Etiquette,Manual,Operators,README.patches}
%doc doc/{conf.doc,example.conf,tao.of.irc,whatsnew}
%attr(755,root,root) %{_sbindir}/*
%attr(770,root,ircd) %dir %{_var}/log/ircd
%attr(770,root,ircd) %dir %{_var}/log/archive/ircd
%attr(770,root,ircd) %dir %{_localstatedir}
%attr(640,ircd,ircd) %ghost %{_localstatedir}/ircd.pid
%attr(750,root,ircd) %dir %{_sysconfdir}
%attr(660,root,ircd) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ircd.conf
%attr(660,root,ircd) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ircd.motd
%attr(754,root,root) /etc/rc.d/init.d/ircd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/ircd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ircd
