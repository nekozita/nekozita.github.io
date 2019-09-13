#!/usr/bin/perl
################################################################################
# 高機能アクセス解析CGI Standard版（アクセスログ ロギング用）
# Ver 4.0.2
# Copyright(C) futomi 2001 - 2008
# http://www.futomi.com/
###############################################################################
use strict;
BEGIN {
	use FindBin;
	if($FindBin::Bin && $FindBin::Bin ne "/") {
		push(@INC, "$FindBin::Bin/lib");
		chdir $FindBin::Bin;
	} else {
		push(@INC, "./lib");
	}
}
use Time::Local;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
$| = 1;
&main;

sub main {
	require './conf/config.cgi';
	my $c = &config::get;
	#フリーサーバのドメインリスト（正規表現）
	$c->{FREE_SERVER_NAME} = '\.tok2\.com|\.infoseek\.co\.jp|\.xrea\.com';
	#
	my $q = new CGI;
	# Remote host
	my $remote_host = &get_remote_host;
	# 指定ホストからのアクセスを除外する
	if(@{$c->{REJECT_HOSTS}}) {
		my $reject_flag = 0;
		for my $reject (@{$c->{REJECT_HOSTS}}) {
			if($reject =~ /[^0-9\.]/) {	# ホスト名指定の場合
				if($remote_host =~ /\Q${reject}\E$/) {
					$reject_flag = 1;
					last;
				}
			} else {	# IPアドレス指定の場合
				if($ENV{'REMOTE_ADDR'} =~ /^\Q${reject}\E/) {
					$reject_flag = 1;
					last;
				}
			}
		}
		if($reject_flag) {
			&print_image;
			exit;
		}
	}
	#
	my $now = time + $c->{TIMEDIFF}*3600;
	my $timestamp = &get_timestamp($now);
	my $ymd = substr($timestamp, 0, 8);
	my $logfile = $c->{LOG};
	if($c->{LOTATION} == 2) {
		$logfile .= "\.${ymd}\.cgi";
	} elsif($c->{LOTATION} == 3) {
		my $mon = substr($timestamp, 0, 6);
		$logfile .= "\.${mon}".'00.cgi';
	} else {
		$logfile .= "\.cgi";
	}
	# Access Log Lotation
	if($c->{LOTATION}) {
		&log_lotation($c, $ymd, $logfile);
	}
	#
	my %logdata;
	$logdata{remote_host} = $remote_host;
	# Remote user
	$logdata{remote_user} = &get_remote_user;
	# The date and time of the request
	$logdata{date} = $timestamp;
	# Requested URI
	$logdata{request} = &get_request($q);
	# HTTP_REFERER
	$logdata{referrer} = &get_referrer;
	# Screen
	($logdata{screen_width}, $logdata{screen_height}, $logdata{color_depth}) = &get_screen_info($q);
	# Make Log String
	my $log_string = &get_log_string(\%logdata);
	# Loging
	&loging($logfile, $log_string);
	# Print Image to the Client
	&print_image($c);
}
exit;



######################################################################
#  Subroutine
######################################################################

# Print Image to the Client
sub print_image {
	my($c) = @_;
	my $ua = $ENV{'HTTP_USER_AGENT'};
	my $mime_type = 'image/gif';
	my $image_file = "./conf/acclogo.gif";
	if($ua =~ /^(J\-PHONE|Vodafone|Softbank)/i) {
		$mime_type = 'image/png';
		$image_file = "./conf/acclogo.png";
	} elsif($ua =~ /UP\.Browser/) {
		$mime_type = 'image/jpeg';
		$image_file = "./conf/acclogo.jpg";
	}
	my $logo_size = -s $image_file;
	open(IMAGE, "<${image_file}") or &error("${image_file}をオープンできませんでした。: $!");
	binmode(IMAGE);
	my $data;
	sysread IMAGE, $data, $logo_size;
	close IMAGE;
	print "Pragma: no-cache\n";
	print "Cache-Control: no-cache\n";
	print "Content-Type: ${mime_type}\n";
	if($ENV{SERVER_NAME} !~ /($c->{FREE_SERVER_NAME})/) {
		print "Content-Length: ${logo_size}\n";
	}
	print "\n";
	print $data;
	exit;
}

sub get_screen_info {
	my($q) = @_;
	my $width = $q->param('width');
	my $height = $q->param('height');
	my $color = $q->param('color');
	my $ua = $ENV{HTTP_USER_AGENT};
	if($ua =~ /(J\-PHONE|Vodafone|Softbank)/i) {
		if($ENV{HTTP_X_JPHONE_DISPLAY} && $ENV{HTTP_X_JPHONE_COLOR}) {
			($width, $height) = split(/\*/, $ENV{HTTP_X_JPHONE_DISPLAY});
			my $jcolor = $ENV{HTTP_X_JPHONE_COLOR};
			$jcolor =~ s/^[^0-9]+//;
			$color = log($jcolor) / log(2);
		}
	} elsif($ua =~ /(KDDI|UP\.Browser)/i) {
		if($ENV{HTTP_X_UP_DEVCAP_SCREENDEPTH} && $ENV{HTTP_X_UP_DEVCAP_SCREENPIXELS}) {
			($width, $height) = split(/,/, $ENV{HTTP_X_UP_DEVCAP_SCREENPIXELS});
			($color) = split(/,/, $ENV{HTTP_X_UP_DEVCAP_SCREENDEPTH});
		}
	} elsif($ua =~ /^PDXGW\/[0-9\.]+\s*\(([^\)]+)\)/) {
		#PDXGW/1.0 (TX=8;TY=7;GX=96;GY=84;C=C256;G=BF;GI=2)
		my $tmp = $1;
		my @devinfos = split(/;/, $tmp);
		for my $key (@devinfos) {
			my($name, $value) = split(/=/, $key);
			if($name eq 'GX') {
				$width = $value;
			} elsif($name eq 'GY') {
				$height = $value;
			} elsif($name eq 'C') {
				if($value eq 'CF') {
					$color = '16';
				} elsif($value eq 'C256') {
					$color = '8';
				} elsif($value eq 'C4') {
					$color = '2';
				} elsif($value eq 'G2') {
					$color = '1';
				} else {
					$color = '';
				}
			}
		}
	}
	return $width, $height, $color;
}

sub loging {
	my($log_file, $string) = @_;
	open(LOGFILE, ">>${log_file}") || &error("ログファイルの書き込みに失敗しました。ディレクトリ「logs」のパーミッションを777にしてください。パーミッションを変更したら、ディレクトリ「logs」内にあるファイルをすべて削除してから、再度ブラウザーで acclog.cgi にアクセスしてみて下さい。: $!");
	if(&lock(*LOGFILE)) {
		&error("ログファイルのロック処理に失敗しました。 : $!");
	}
	print LOGFILE "${string}\n";
	close(LOGFILE);
}

sub get_log_string {
	my($p) = @_;
	my $log;
	$log .= "$p->{date} $p->{remote_host} - $p->{remote_user} $p->{request} $p->{referrer}";
	$log .= " \"$ENV{'HTTP_USER_AGENT'}\"";
	if($ENV{HTTP_ACCEPT_LANGUAGE} eq '') {
		$log .= " \"-\"";
	} else {
		$log .= " \"$ENV{HTTP_ACCEPT_LANGUAGE}\"";
	}
	if($p->{screen_width} && $p->{screen_height} && $p->{color_depth}) {
		$log .= " \"$p->{screen_width} $p->{screen_height} $p->{color_depth}\"";
	} else {
		$log .= " \"-\"";
	}
	return $log;
}

sub get_referrer {
	my @query_parts = split(/&/, $ENV{QUERY_STRING});
	my $referrer;
	my $part;
	my $flag = 0;
	for $part (@query_parts) {
		if($part =~ /^(width|height|color)=/i) {
			$flag = 0;
		}
		if($part =~ /^referrer=/i) {
			$flag = 1;
		}
		if($flag) {
			$part =~ s/^referrer=//;
			$referrer .= "$part&";
		}
	}
	$referrer =~ s/&$//;
	if($referrer eq '') {
		$referrer = '-';
	}
	$referrer =~ s/\%7e/\~/ig;
	return $referrer;
}

sub get_timestamp {
	my($time) = @_;
	my($sec, $min, $hour, $mday, $mon, $year) = localtime($time);
	$year += 1900;
	$mon += 1;
	$mon = sprintf("%02d", $mon);
	$mday = sprintf("%02d", $mday);
	$hour = sprintf("%02d", $hour);
	$min = sprintf("%02d", $min);
	$sec = sprintf("%02d", $sec);
	return "${year}${mon}${mday}${hour}${min}${sec}";
}

sub lock {
	local(*FILE) = @_;
	eval{flock(FILE, 2)};
	if($@) {
		return $!;
	} else {
		return '';
	}
}

sub get_request {
	my($q) = @_;
	my $request = $q->param('url');
	unless($request) {
		if($ENV{HTTP_REFERER} eq '') {
			$request = '-';
		} else {
			$request = $ENV{HTTP_REFERER};
		}
	}
	$request =~ s/\%7e/\~/ig;
	return $request;
}

sub get_remote_user {
	my $remote_user;
	if($ENV{REMOTE_USER} eq '') {
		$remote_user = '-';
	} else {
		$remote_user = $ENV{REMOTE_USER};
	}
	return $remote_user;
}

sub get_remote_host {
	my $remote_host;
	if($ENV{REMOTE_HOST} =~ /[^0-9\.]/) {
		$remote_host = $ENV{REMOTE_HOST};
	} else {
		my(@addr) = split(/\./, $ENV{REMOTE_ADDR});
		my($packed_addr) = pack("C4", $addr[0], $addr[1], $addr[2], $addr[3]);
		my($aliases, $addrtype, $length, @addrs);
		($remote_host, $aliases, $addrtype, $length, @addrs) = gethostbyaddr($packed_addr, 2);
		unless($remote_host) {
			$remote_host = $ENV{REMOTE_ADDR};
		}
	}
	return $remote_host;
}

sub log_lotation {
	my($c, $ymd, $logfile) = @_;
	my $log_size = -s $logfile;
	if($c->{LOTATION} == 1) {
		if($log_size > $c->{LOTATION_SIZE}) {
			if($c->{LOTATION_SAVE}) {
				my $f = $logfile;
				$f =~ s/\.cgi//;
				if(-e "${f}.${ymd}.cgi" || -e "${f}.${ymd}.0.cgi" ) {
					for( my $i=1; $i<=100; $i++ ) {
						my $fpath = "${f}\.${ymd}\.${i}\.cgi";
						unless(-e $fpath) {
							rename($logfile, $fpath);
							if(-e "${f}.${ymd}.cgi") {
								rename("${f}.${ymd}.cgi", "${f}.${ymd}.0.cgi");
							}
							last;
						}
					}
				} else {
					rename($logfile, "${f}\.${ymd}\.cgi");
				}
			} else {
				unlink($logfile);
			}
		}
	} elsif($c->{LOTATION} == 2 || $c->{LOTATION} == 3) {
		unless($c->{LOTATION_SAVE}) {
			my @parts = split(/\//, $logfile);
			my $logname = pop @parts;
			my($logname_key) = split(/\./, $logname);
			my $logdir = join('/', @parts);
			if(opendir(DIR, "$logdir")) {
				my @files = readdir(DIR);
				closedir(DIR);
				my $file;
				for $file (@files) {
					if($file eq $logname) {
						next;
					}
					if($file =~ /^$logname_key/) {
						unlink("$logdir/$file");
					}
				}
			}
		}
	}
}

sub error {
	my($msg) = @_;
	my $html;
	$html .= "<html>\n";
	$html .= "<head>\n";
	$html .= "<meta http-equiv=\"Content-Language\" content=\"ja\" />\n";
	$html .= "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />\n";
	$html .= "<title>エラー</title>\n";
	$html .= "</head><body>\n";
	$html .= "<p>${msg}</p>";
	$html .= "</body></html>";
	print "Content-Type: text/html; charset=utf-8\n";
	print "\n";
	print $html;
	exit;
}

