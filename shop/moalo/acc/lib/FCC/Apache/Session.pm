package FCC::Apache::Session;
################################################################################
# Copyright(C) futomi 2007-2008
# http://www.futomi.com/
###############################################################################
use strict;
use Digest::Perl::MD5;
use Data::Random::String;
$| = 1;
my $ERROR;
sub new {
	my($self, $directory, $session_timeout) = @_;
	#初期値設定
	my $objref = {};
	$objref->{error}  = undef;
	if($directory eq '') {
		$directory = './session';
	}
	#セッションディレクトリのチェック
	unless(-e $directory) {
		#$ERROR = "$directory が見つかりませんでした。: $!";
		return undef;
	}
	unless(-d $directory) {
		#$ERROR = "$directory はディレクトリではありません。: $!";
		return undef;
	}
	my $test_file = "${directory}/test.tmp";
	if(open(TEST, ">${test_file}")) {
		close(TEST);
		unlink $test_file;
	} else {
		#$ERROR = "$directory に書き込み権限がありません。: $!";
		return undef;
	}
	$objref->{'directory'} = $directory;
	#セッションタイムアウト(秒）のチェック
	unless($session_timeout) {
		$session_timeout = 86400;
	}
	if($session_timeout =~ /[^\d]/) {
		$session_timeout = 86400;
	}
	$objref->{'session_timeout'} = $session_timeout;
	#セッションファイルのお掃除
	&_session_sweep($directory, 86400);

	bless $objref, $self;
	return $objref;
}

sub error {
	my($self) = @_;
	return $self->{'error'};
}

sub logoff {
	my($self, $sid) = @_;
	my $dir = $self->{'directory'};
	unlink "${dir}/${sid}.cgi";
	return 1;
}

sub session_update {
	my($self, $sid, $data_ref) = @_;
	my $dir = $self->{'directory'};
	my $session_file = "${dir}/${sid}.cgi";
	unless(-e $session_file) {
		$self->{error} = "You've already logoffed.  : $!";
		return undef;
	}
	my %session;
	unless(open(SESSION, "+<${session_file}")) {
		$self->{error} = "Authentication Fail. System Error. Can't open ${session_file} : $!";
		return undef;
	}
	if(my $err = &_lockfile(*SESSION)) {
		$self->{error} = "Authentication Fail. System Error. Can't lock ${session_file} : $err";
		return undef;
	}
	while(<SESSION>) {
		chomp;
		my($key, $value) = split(/\t/);
		$session{$key} = $value;
	}
	seek SESSION, 0, 0;
	truncate SESSION, 0;
	for my $key (keys %{$data_ref}) {
		$session{$key} = $data_ref->{$key};
	}
	my $epoch = time;
	$session{'_mtime'} = $epoch;
	for my $key (sort keys %session) {
		my $value = $session{$key};
		print SESSION "${key}\t${value}\n";
	}
	close(SESSION);
	return %session;
}

sub session_create {
	my($self, $userid) = @_;
	my $dir = $self->{'directory'};
	my @ip_addrs = split(/\./, $ENV{'REMOTE_ADDR'});
	for(my $i=0;$i<4;$i++) {
		my $num = sprintf("%03d", $ip_addrs[$i]);
		$ip_addrs[$i] = $num;
	}
	my $ipaddress = join("", @ip_addrs);
	my $remote_port = sprintf("%04d", $ENV{'REMOTE_PORT'});
	my $seed = $ipaddress.$remote_port.time.$ENV{'HTTP_USER_AGENT'}.Data::Random::String->create_random_string(length=>'32', contains=>'alphanumeric');
	my $sid = Digest::Perl::MD5::md5_hex(Digest::Perl::MD5::md5_hex($seed));
	my $session_file = "${dir}/${sid}.cgi";
	if(-e $session_file) {
		$self->{error} = "Failed to generate a session id. Try again. : $!";
		return undef;
	}
	my $epoch = time;
	my %session;
	$session{'_mtime'} = $epoch;
	$session{'_ctime'} = $epoch;
	$session{'_userid'} = $userid;
	$session{'_sid'} = $sid;
	unless(open(SESSION, ">$session_file")) {
		$self->{error} = "Failed to generate a session id. Try again. : $!";
		return undef;
	}
	for my $key (sort keys %session) {
		my $value = $session{$key};
		print SESSION "${key}\t${value}\n";
	}
	close(SESSION);
	return %session;
}

sub sessoin_auth {
	my($self, $sid) = @_;
	my $dir = $self->{'directory'};
	my $session_file = "${dir}/${sid}.cgi";
	unless(-e $session_file) {
		$self->{error} = "You've already logoffed.  : $!";
		return undef;
	}
	my %session;
	unless(open(SESSION, "+<${session_file}")) {
		$self->{error} = "Authentication Fail. System Error. Can't open ${session_file} : $!";
		return undef;
	}
	if(my $err = &_lockfile(*SESSION)) {
		$self->{error} = "Authentication Fail. System Error. Can't lock ${session_file} : $err";
		return undef;
	}
	while(<SESSION>) {
		chomp;
		my($key, $value) = split(/\t/);
		$session{$key} = $value;
	}
	my $epoch = time;
	if($epoch - $session{'_mtime'} > $self->{'session_timeout'}) {
		unlink "${dir}/${sid}.cgi";
		$self->{error} = "Session Timeout. Logon again.";
		return undef;
	}
	seek SESSION, 0, 0;
	truncate SESSION, 0;
	$session{'_mtime'} = $epoch;
	for my $key (sort keys %session) {
		my $value = $session{$key};
		print SESSION "${key}\t${value}\n";
	}
	close(SESSION);
	return %session;
}

sub _lockfile {
	local(*FILE) = @_;
	eval{flock(FILE, 2)};
	if($@) {
		return $!;
	} else {
		return '';
	}
}

sub _session_sweep {
	my($dir, $delete_time) = @_;
	opendir(DIR, "${dir}");
	my @files = readdir(DIR);
	closedir(DIR);
	my $now = time;
	for my $file (@files) {
		unless($file =~ /\.cgi$/) {next;}
		my $session_file = "${dir}/$file";
		my $mtime = (stat($session_file))[9];
		if($now - $mtime > $delete_time) {
			unlink $session_file;
		}
	}
	return 1;
}

1;
