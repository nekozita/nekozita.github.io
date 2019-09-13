#!/usr/bin/perl
################################################################################
# 高機能アクセス解析CGI Standard版（解析結果表示用）
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
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Jcode;
use Time::Local;
use HTML::Template;
use FCC::Apache::Session;
$| = 1;

&main;

sub main {
	#設定情報取得
	unless(-e './conf/config.cgi') {
		&ErrorPrint('./conf/config.cgiがありません。');
	}
	require './conf/config.cgi';
	my $c = &config::get;

	$c->{VERSION} = "4.0.2";
	$c->{COPYRIGHT1} = "futomi\'s CGI Cafe 高機能アクセス解析CGI Standard版 Ver $c->{VERSION}";
	$c->{COPYRIGHT2} = "<a href=\"http://www.futomi.com/\" target=\"_blank\">$c->{COPYRIGHT1}</a>";
	$c->{COPYRIGHT3} = "<a href=\"http://www.futomi.com/\" target=\"_blank\">$c->{COPYRIGHT1}</a>";
	#
	$c->{COOKIE_NAME} = "accs_sid";
	#フリーサーバのドメインリスト（正規表現）
	$c->{FREE_SERVER_NAME} = '\.tok2\.com|\.infoseek\.co\.jp|\.xrea\.com';
	#
	my $q = new CGI;
	$c->{q} = $q;
	# このCGIのURLを特定する。
	if($c->{MANUAL_CGIURL}) {
		$c->{CGI_URL} = $c->{MANUAL_CGIURL};
	} else {
		$c->{CGI_URL} = "acc.cgi";
	}
	# パスワード認証
	my $action = $q->param("action");
	if($c->{AUTHFLAG}) {
		my %cookies = &GetCookie;
		my $sid = $cookies{$c->{COOKIE_NAME}};
		if($sid =~ /[^a-zA-Z0-9]/) {
			&ErrorPrint('不正なアクセスです。');
		}
		my %session_data;
		my $session;
		if($action eq 'logon') {
			&logon($c);
		} elsif($action eq 'logoff') {
			&logoff($c, $sid);
		} elsif($sid) {
			&session_auth($c, $sid, \%session_data);
		} else {
			&PrintAuthForm($c);
		}
	}
	#
	my $mode = $q->param('MODE');
	my $ana_month = $q->param('MONTH');
	my $ana_day = $q->param('DAY');
	$ana_day =~ s/^0*//;

	# 入力値チェック
	&InputCheck($mode, $ana_month, $ana_day);


	#リダイレクト
	my $redirect_url = $q->param("redirect");
	if( $redirect_url ) {
		&redirect($c, $redirect_url);
	}
	# 定義ファイルを読み取る
	my %langcode_list = &ReadDef('./conf/language.dat');

	# 過去ログリストを取得する
	my %LogList = &GetPastLogList($c);

	# 解析対象のログディレクトリ、ログファイルを特定
	my($SelectedLogFile, $SelectedLogFileName) = &GetSelectedLogFile($c);

	# ログファイルを読み取る
	if(-e $SelectedLogFile) {
		open(LOGFILE, "$SelectedLogFile") || &ErrorPrint("アクセスログ「$SelectedLogFile」をオープンできませんでした");
	} else {
		&ErrorPrint("アクセスログ（$SelectedLogFile）がありません。");
	}

	my($date_check, $RemoteHostBuff, $CookieBuff, $RequestBuff, $RefererBuff, $UserAgentBuff, $AcceptLangBuff, $ScreenBuff);
	my(%all_date, %date, %remote_host, %request, %referer, %user_agent, %accept_language, %screen);
	my($date_check_mon, $date_check_day);
	my $i = 0;
	while(<LOGFILE>) {
		chop;
		next if($_ eq '');
		if(/^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\"([^\"]+)\"\s+\"([^\"]+)\"\s+\"([^\"]+)\"/) {
			$date_check = $1;
			$RemoteHostBuff = $2;
			$CookieBuff = $3;
			$RequestBuff = $5;
			$RefererBuff = $6;
			$UserAgentBuff = $7;
			$AcceptLangBuff = $8;
			$ScreenBuff = $9;
		} else {
			next;
		}
		next if($date_check eq '');
		$all_date{$i} = $date_check;
		$date_check_mon = substr($date_check, 0, 6);
		$date_check_day = substr($date_check, 6, 2);
		$date_check_day =~ s/^0//;
		if($mode eq 'MONTHLY' || $mode eq 'DAILY') {
			next unless($date_check_mon eq $ana_month);
			if($mode eq 'DAILY') {
				next unless($date_check_day eq $ana_day);
			}
		}
		$date{$i} = $date_check;
		$remote_host{$i} = lc $RemoteHostBuff;
		$request{$i} = $RequestBuff;
		$referer{$i} = $RefererBuff;
		$user_agent{$i} = $UserAgentBuff;
		$accept_language{$i} = lc $AcceptLangBuff;
		$screen{$i} = $ScreenBuff;
		$i ++;
	}
	close(LOGFILE);
	my $loglines = $i;


	# 対象ログ数のチェック
	unless($loglines >= 1) {
		&ErrorPrint('対象のログが一件もありません。');
	}

	# 対象ログの調査開始時と調査終了時を調べる
	my($min_date, $max_date) = &AnalyzeDateRange(\%date);

	# ログファイルのサイズを調べる(バイト)
	my $log_size = -s $SelectedLogFile;

	#テンプレートをロード
	my $t = &load_template("./template/result.tmpl");

	# 解析概要を出力
	my $summary_data = {
		LogList => \%LogList,
		loglines => $loglines,
		min_date => $min_date,
		max_date => $max_date,
		SelectedLogFileName => $SelectedLogFileName,
		SelectedLogFile => $SelectedLogFile,
		log_size => $log_size,
		mode => $mode,
		ana_month => $ana_month,
		ana_day => $ana_day,
		langcode_list => \%langcode_list,
		all_date => \%all_date
	};
	&print_summary($t, $c, $summary_data);

	# アクセス元HOST名、国名ランキングを調べる
	if($c->{ANA_TARGETS}->{ANA_REMOTETLD} || $c->{ANA_TARGETS}->{ANA_REMOTEDOMAIN} || $c->{ANA_TARGETS}->{ANA_REMOTEHOST}) {
		my($country_list_ref, $domain_list_ref, $host_list_ref) = &AnalyzeRemoteHost(\%remote_host);
		if($c->{ANA_TARGETS}->{ANA_REMOTETLD}) {	# アクセス元トップレベルドメイン（TLD）を出力
			&print_remote_tld($t, $c, $summary_data, $country_list_ref);
		}
		if($c->{ANA_TARGETS}->{ANA_REMOTEDOMAIN}) {	# アクセス元ドメイン名を出力
			&print_remote_domain($t, $c, $summary_data, $domain_list_ref);
		}
		if($c->{ANA_TARGETS}->{ANA_REMOTEHOST}) {	# アクセス元ホスト名を出力
			&print_remote_host($t, $c, $summary_data, $host_list_ref);
		}
	}

	# ブラウザー表示可能言語一覧を調べる
	if($c->{ANA_TARGETS}->{ANA_HTTPLANG}) {
		my $language_list_ref = &AnalyzeAcceptLang(\%accept_language);
		# ブラウザー表示可能言語レポートを出力
		&print_http_lang($t, $c, $summary_data, $language_list_ref);
	}

	# OS, ブラウザーを調べる
	if($c->{ANA_TARGETS}->{ANA_BROWSER} || $c->{ANA_TARGETS}->{ANA_PLATFORM}) {
		my($browser_list_ref, $browser_v_list_ref, $platform_list_ref, $platform_v_list_ref) = &AnalyzeUserAgent(\%user_agent);
		if($c->{ANA_TARGETS}->{ANA_BROWSER}) {	# ブラウザーレポートを出力
			&print_browser($t, $c, $summary_data, $browser_list_ref, $browser_v_list_ref);
		}
		if($c->{ANA_TARGETS}->{ANA_PLATFORM}) {	# プラットフォームレポートを出力
			&print_platform($t, $c, $summary_data, $platform_list_ref, $platform_v_list_ref);
		}
	}

	# 時間別、曜日別、日付別、月別リクエスト数を調べる
	if($c->{ANA_TARGETS}->{ANA_REQUESTMONTHLY} || $c->{ANA_TARGETS}->{ANA_REQUESTDAILY} || $c->{ANA_TARGETS}->{ANA_REQUESTHOURLY} || $c->{ANA_TARGETS}->{ANA_REQUESTWEEKLY}) {
		my($hourly_list_ref, $date_list_ref, $monthly_list_ref, $daily_list_ref) = &AnalyzeRequestDate(\%date);
		if($c->{ANA_TARGETS}->{ANA_REQUESTMONTHLY}) {
			# 月別リクエスト数レポート
			# 全指定解析モードの場合にのみ出力する。
			if($mode eq '') {
				&print_request_monthly($t, $c, $summary_data, $monthly_list_ref);
			} else {
				$t->param("ANA_REQUESTMONTHLY" => 0);
			}
		}
		if($c->{ANA_TARGETS}->{ANA_REQUESTDAILY}) {
			# 日付別リクエスト数レポート
			# 月指定解析モードの場合にのみ出力する。
			if($mode eq 'MONTHLY') {
				&print_request_daily($t, $c, $summary_data, $date_list_ref, $ana_month);
			} else {
				$t->param("ANA_REQUESTDAILY" => 0);
			}
		}
		if($c->{ANA_TARGETS}->{ANA_REQUESTHOURLY}) {
			# 時間別アクセス数レポート
			print_request_hourly($t, $c, $summary_data, $hourly_list_ref);
		}
		if($c->{ANA_TARGETS}->{ANA_REQUESTWEEKLY}) {
			# 曜日別アクセス数レポート
			unless($mode eq 'DAILY') {
				&print_request_weekly($t, $c, $summary_data, $daily_list_ref);
			} else {
				$t->param("ANA_REQUESTWEEKLY" => 0);
			}
		}
	}

	# Request Report を調べる
	if($c->{ANA_TARGETS}->{ANA_REQUESTFILE}) {
		my $request_list_ref = &AnalyzeRequestResource($c, \%request);
		# Request Report を出力
		&print_request_file($t, $c, $summary_data, $request_list_ref);
	}

	# リンク元URL、検索エンジンの検索キーワードを調べる
	if($c->{ANA_TARGETS}->{ANA_REFERERSITE} || $c->{ANA_TARGETS}->{ANA_REFERERURL} || $c->{ANA_TARGETS}->{ANA_KEYWORD}) {
		my($referer_list_ref, $search_word_list_ref) = &AnalyzeReferer($c, \%referer);
		if($c->{ANA_TARGETS}->{ANA_REFERERSITE}) {
			# リンク元サイトレポート
			&print_referer_site($t, $c, $summary_data, $referer_list_ref);
		}
		if($c->{ANA_TARGETS}->{ANA_REFERERURL}) {
			# リンク元URLを出力
			&print_referer_url($t, $c, $summary_data, $referer_list_ref);
		}
		if($c->{ANA_TARGETS}->{ANA_KEYWORD}) {
			# 検索エンジンの検索キーワードを出力
			&print_keyword($t, $c, $summary_data, $search_word_list_ref);
		}
	}

	# スクリーン情報を調べる
	if($c->{ANA_TARGETS}->{ANA_RESOLUTION} || $c->{ANA_TARGETS}->{ANA_COLORDEPTH}) {
		my($resolution_ref, $color_depth_ref) = &AnalyzeScreen(\%screen);
		if($c->{ANA_TARGETS}->{ANA_RESOLUTION}) {
			# 画面解像度を出力
			&print_resolution($t, $c, $summary_data, $resolution_ref);
		}
		if($c->{ANA_TARGETS}->{ANA_COLORDEPTH}) {
			# 画面色深度を出力
			&print_color_depth($t, $c, $summary_data, $color_depth_ref);
		}
	}
	#画面出力
	&print_result($t, $c);
}
exit;

#####################################################################

sub session_auth {
	my($c, $sid, $session_data_ref) = @_;
	my $session = new FCC::Apache::Session("./session");
	%{$session_data_ref} = $session->sessoin_auth($sid);
	unless($session_data_ref->{_sid}) {
		my $error = $session->error();
		my $t = &load_template("./template/auth_error.tmpl");
		$t->param("error" => $error);
		$t->param("CGI_URL" => $c->{CGI_URL});
		$t->param("COOKIE_NAME" => $c->{COOKIE_NAME});
		my $html = $t->output();
		my $clen = length $html;
		print &ClearCookie($c->{COOKIE_NAME});
		if($ENV{'SERVER_NAME'} !~ /($c->{FREE_SERVER_NAME})/) {
			print "Content-Length: ${clen}\n";
		}
		print "Content-Type: text/html; charset=utf-8\n";
		print "\n";
		print $html;
		exit;
	}
	return $session;
}

sub logoff {
	my($c, $sid) = @_;
	my $session = new FCC::Apache::Session("./session");
	$session->logoff($sid);
	print &ClearCookie($c->{COOKIE_NAME});
	print "Content-Type: text/html; charset=utf-8\n";
	print "\n";
	print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n";
	print "<html lang=\"ja\" xml:lang=\"ja\" xmlns=\"http://www.w3.org/1999/xhtml\">\n";
	print "<head>\n";
	print "<meta http-equiv=\"content-type\" content=\"text/html;charset=utf-8\" />\n";
	if($ENV{SERVER_NAME} =~ /($c->{FREE_SERVER_NAME})/) {
		print "<meta http-equiv=\"Set-Cookie\" content=\"$c->{COOKIE_NAME}=clear; expires=Thu, 01-Jan-1970 00:00:00 GMT;\" />\n";
	}
	print "<meta http-equiv=\"refresh\" content=\"0;URL=$c->{CGI_URL}\" />\n";
	print "<title>ログオフ中...</title>\n";
	print "</head>\n";
	print "<body>\n";
	print "<p style=\"font-size:small\">ログオフ中 ...</p>\n";
	print "</body></html>";
	exit;
}

sub logon {
	my($c) = @_;
	my $in_pass = $c->{q}->param('PASS');
	if($in_pass eq '') {
		&PrintAuthForm($c, 1);
	}
	if($in_pass ne $c->{PASSWORD}) {
		&PrintAuthForm($c, 1);
	}
	my $session = new FCC::Apache::Session("./session");
	unless($session) {
		&ErrorPrint("システムエラー : sessionディレクトリのパーミッションを777にしてください。");
	}
	my %session_data = ${session}->session_create();
	unless($session_data{_sid}) {
		my $err = '認証に失敗しました。:' . $session->error();
		&ErrorPrint($err);
	}
	my $target_url = $c->{CGI_URL} . "?t=" . time;
	print &SetCookie($c->{COOKIE_NAME}, $session_data{_sid}), "\n";
	print "Content-Type: text/html; charset=utf-8\n";
	print "\n";
	print "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n";
	print "<html lang=\"ja\" xml:lang=\"ja\" xmlns=\"http://www.w3.org/1999/xhtml\">\n";
	print "<head>\n";
	print "<meta http-equiv=\"content-type\" content=\"text/html;charset=utf-8\" />\n";
	if($ENV{SERVER_NAME} =~ /($c->{FREE_SERVER_NAME})/) {
		print "<meta http-equiv=\"Set-Cookie\" content=\"$c->{COOKIE_NAME}=$session_data{_sid};\" />\n";
	}
	print "<meta http-equiv=\"refresh\" content=\"0;URL=${target_url}\" />\n";
	print "<title>ログオン中...</title>\n";
	print "</head>\n";
	print "<body>\n";
	print "<p style=\"font-size:small\">ログオン中 ...</p>\n";
	print "</body></html>";
	exit;
}

sub redirect {
	my($c, $url) = @_;
	my $url_disp = &SecureHtml($url);
	my $error = 0;
	if($url =~ /[^a-zA-Z0-9\.\-\_\/\:\?\&\%\=\+\~\,]/) {
		$error = 1;
	}
	my $t = &load_template("./template/redirect.tmpl");
	$t->param("url" => $url);
	$t->param("url_disp" => $url_disp);
	$t->param("error" => $error);
	my $body = $t->output();
	my $clen = length $body;
	print "Content-Type: text/html; charset=utf-8\n";
	if($ENV{SERVER_NAME} !~ /($c->{FREE_SERVER_NAME})/) {
		print "Content-Length: ${clen}\n";
	}
	print "\n";
	print $body;
	exit;
}

sub load_template {
	my($f) = @_;
	my $t = HTML::Template->new(
		filename => $f,
		die_on_bad_params => 0,
		vanguard_compatibility_mode => 1,
		loop_context_vars => 1
	);
	require './conf/config.cgi';
	my $c = &config::get;
	&convert_template_common($t, $c);
	return $t;
}

sub convert_template_common {
	my($t, $c) = @_;
	while( my($k, $v) = each %{$c->{ANA_TARGETS}} ) {
		$t->param($k => $v);
	}
	for(my $i=1; $i<=3; $i++) {
		$t->param("COPYRIGHT${i}" => $c->{"COPYRIGHT${i}"});
	}
	$t->param("IMAGE_URL" => $c->{IMAGE_URL});
	$t->param("CGI_URL" => $c->{CGI_URL});
	$t->param("AUTHFLAG" => $c->{AUTHFLAG});
}

sub print_result {
	my($t, $c) =@_;
	my $body = $t->output();
	my $clen = length $body;
	print "Content-Type: text/html; charset=utf-8\n";
	if($ENV{SERVER_NAME} !~ /($c->{FREE_SERVER_NAME})/) {
		print "Content-Length: ${clen}\n";
	}
	print "\n";
	print $body;
	exit;
}

sub AnalyzeDateRange {
	my($date_ref) = @_;
	# 対象ログの調査開始時と調査終了時を調べる
	my $min_date = 99999999999999;
	my $max_date = 0;
	while( my($i, $d) = each %{$date_ref} ) {
		if($date_ref->{$i} > $max_date) {
			$max_date = $date_ref->{$i};
		}
		if($date_ref->{$i} < $min_date) {
			$min_date = $date_ref->{$i};
		}
	}
	return($min_date, $max_date);
}

# アクセス元ホスト名、ドメイン名、国名ランキングを調べる
sub AnalyzeRemoteHost {
	my($remote_hosts_ref) = @_;
	my %country_list;
	my %domain_list;
	my %host_list;
	while( my($i, $host) = each %{$remote_hosts_ref} ) {
		$host_list{$host} ++;
		my @dom_buff = split(/\./, $host);
		my $tld = pop(@dom_buff);
		if($tld eq '' || $tld =~ /[^a-zA-Z]/) {
			$country_list{'?'} ++;
		} else {
			$country_list{$tld} ++;
		}
		if($tld eq '') {
			$domain_list{'?'} ++;
		} elsif($tld =~ /[^a-zA-Z]/) {
			$domain_list{'?'} ++;
		} else {
			my $domain = &GetDomainByHostname($host);
			$domain_list{$domain} ++;
		}
	}
	return \%country_list, \%domain_list, \%host_list;
}

sub GetDomainByHostname {
	my($host) = @_;
	my %tld_fix = (
		'com' =>'2', 'net'=>'2', 'org'=>'2', 'biz'=>'2', 'info'=>'2', 'name'=>'3',
		'aero'=>'2', 'coop'=>'2', 'museum'=>'2', 'pro'=>'3', 'edu'=>'2', 'gov'=>'2',
		'mil'=>'2', 'int'=>'2', 'arpa'=>'2', 'nato'=>'2', 
		'hk'=>'3', 'sg'=>'3', 'kr'=>'3', 'uk'=>'3', 'au'=>'3', 'mx'=>'3', 'th'=>'3', 'br'=>'3', 'pe'=>'3', 'nz'=>'3'
	);
	my %sld_fix = (
		#日本
		'ac.jp'=>'3', 'ad.jp'=>'3', 'co.jp'=>'3', 'ed.jp'=>'3', 'go.jp'=>'3',
		'gr.jp'=>'3', 'lg.jp'=>'3', 'ne.jp'=>'3', 'or.jp'=>'3',
		'hokkaido.jp'=>'3', 'aomori.jp'=>'3', 'iwate.jp'=>'3', 'miyagi.jp'=>'3',
		'akita.jp'=>'3', 'yamagata.jp'=>'3', 'fukushima.jp'=>'3', 'ibaraki.jp'=>'3',
		'tochigi.jp'=>'3', 'gunma.jp'=>'3', 'saitama.jp'=>'3', 'chiba.jp'=>'3',
		'tokyo.jp'=>'3', 'kanagawa.jp'=>'3', 'niigata.jp'=>'3', 'toyama.jp'=>'3',
		'ishikawa.jp'=>'3', 'fukui.jp'=>'3', 'yamanashi.jp'=>'3', 'nagano.jp'=>'3',
		'gifu.jp'=>'3', 'shizuoka.jp'=>'3', 'aichi.jp'=>'3', 'mie.jp'=>'3',
		'shiga.jp'=>'3', 'kyoto.jp'=>'3', 'osaka.jp'=>'3', 'hyogo.jp'=>'3',
		'nara.jp'=>'3', 'wakayama.jp'=>'3', 'tottori.jp'=>'3', 'shimane.jp'=>'3',
		'okayama.jp'=>'3', 'hiroshima.jp'=>'3', 'yamaguchi.jp'=>'3', 'tokushima.jp'=>'3',
		'kagawa.jp'=>'3', 'ehime.jp'=>'3', 'kochi.jp'=>'3', 'fukuoka.jp'=>'3',
		'saga.jp'=>'3', 'nagasaki.jp'=>'3', 'kumamoto.jp'=>'3', 'oita.jp'=>'3',
		'miyazaki.jp'=>'3', 'kagoshima.jp'=>'3', 'okinawa.jp'=>'3', 'sapporo.jp'=>'3',
		'sendai.jp'=>'3', 'chiba.jp'=>'3', 'yokohama.jp'=>'3', 'kawasaki.jp'=>'3',
		'nagoya.jp'=>'3', 'kyoto.jp'=>'3', 'osaka.jp'=>'3', 'kobe.jp'=>'3',
		'hiroshima.jp'=>'3', 'fukuoka.jp'=>'3', 'kitakyushu.jp'=>'3',
		#台湾
		'com.tw'=>'3', 'net.tw'=>'3', 'org.tw'=>'3', 'idv.tw'=>'3', 'game.tw'=>'3',
		'ebiz.tw'=>'3', 'club.tw'=>'3', 'edu.tw'=>'3',
		#中国
		'com.cn'=>'3', 'net.cn'=>'3', 'org.cn'=>'3', 'gov.cn'=>'3', 'ac.cn'=>'3',
		'edu.cn'=>'3'
	);
	my($level3, $level2, $level1) = $host =~ /([^\.]+)\.([^\.]+)\.([^\.]+)$/;
	my $org_domain;
	if(my $dom_level = $tld_fix{$level1}) {
		if($dom_level eq '2') {
			$org_domain = "${level2}.${level1}";
		} else {
			$org_domain = "${level3}.${level2}.${level1}";
		}
	} elsif($sld_fix{"${level2}.${level1}"}) {
		$org_domain = "${level3}.${level2}.${level1}";
	} else {
		$org_domain = "${level2}.${level1}";
	}
	return $org_domain;
}

# ブラウザー表示可能言語一覧を調べる
sub AnalyzeAcceptLang {
	my($accept_language_ref) = @_;
	my %language_list;
	while( my($i, $v) = each %{$accept_language_ref} ) {
		my @buff = split(/,/, $v);
		my $max = 0;
		my $lang;
		for my $j (@buff) {
			my($lang_tmp, $value_tmp) = split(/\;/, $j);
			$value_tmp =~ s/q=//;
			if($value_tmp eq '') { $value_tmp = 1; }
			if($max < $value_tmp) {
				$lang = $lang_tmp;
				$max = $value_tmp;
			}
		}
		$language_list{"\L$lang"} ++;
	}
	return \%language_list;
}

sub AnalyzeUserAgent {
	# OS, ブラウザーを調べる
	my($user_agent_ref) = @_;
	my %browser_list;
	my %browser_v_list;
	my %platform_list;
	my %platform_v_list;
	while( my($i, $ua) = each %{$user_agent_ref} ) {
		my($platform, $platform_v, $browser, $browser_v) = &User_Agent($ua);
		$browser_list{$browser} ++;
		$browser_v_list{"$browser:$browser_v"} ++;
		$platform_list{"$platform"} ++;
		$platform_v_list{"$platform:$platform_v"} ++;
	}
	return \%browser_list, \%browser_v_list, \%platform_list, \%platform_v_list;
}

sub AnalyzeRequestDate {
	# 時間別、曜日別、日付別、月別リクエスト数を調べる
	my($date_ref) = @_;
	my %hourly_list;
	my %date_list;
	my %monthly_list;
	my %daily_list;
	while( my($key, $v) = each %{$date_ref} ) {
	#for my $key (keys(%date)) {
		my $hourly = substr($v, 8, 2);
		$hourly_list{$hourly} ++;
		my $daily_y = substr($v, 0, 4);
		my $daily_m = substr($v, 4, 2);
		my $daily_d = substr($v, 6, 2);
		my @daily_array = localtime(timelocal(0, 0, 0, $daily_d, $daily_m - 1, $daily_y));
		$daily_list{$daily_array[6]} ++;
		$date_list{"$daily_y$daily_m$daily_d"} ++;
		$monthly_list{"$daily_y$daily_m"} ++;
	}
	return \%hourly_list, \%date_list, \%monthly_list, \%daily_list;
}

sub AnalyzeRequestResource {
	# Directory Report, Request Report を調べる
	my($c, $request_ref) = @_;
	my %request_list;
	while( my($key, $v) = each %{$request_ref} ) {
		if($v =~ /^http:\/\/[^\/]+$/) {
			$v .= '/';
		}
		my $uri = $v;
		if($v =~ /\/$/) {
			$_ = $v;
			m|^https*://[^\/]+/(.*)$|;
			my $RequestUri = "/$1";
			my $HtmlFilePath = $ENV{'DOCUMENT_ROOT'}.$RequestUri;
			my $HitFlag = 0;
			for my $Index (@{$c->{DIRECTORYINDEX}}) {
				my $FileTest = $HtmlFilePath.$Index;
				if(-e $FileTest) {
					$uri = $v.$Index;
					$HitFlag = 1;
					last;
				}
			}
			unless($HitFlag) {$uri = $v;}
		}
		$request_list{$uri} ++;
	}
	return \%request_list;
}

# リンク元URL、検索エンジンの検索キーワードを調べる
sub AnalyzeReferer {
	my($c, $referer_ref) = @_;
	my %referer_list;
	my %search_word_list;
	while( my($key, $v) = each %{$referer_ref} ) {
		next if($v eq '' || $v eq '-');
		next unless($v =~ /^http/);
		my $flag = 0;
		if(scalar @{$c->{MY_SITE_URLs}}) {
			for my $myurl (@{$c->{MY_SITE_URLs}}) {
				if($v =~ /^\Q${myurl}\E/) {
					$flag = 1;
					last;
				}
			}
		}
		if($flag) {next;}
		$referer_list{$v} ++;
		my($word) = &GetSearchKeyword($v);
		next if($word eq '');
		$search_word_list{$word} ++;
	}
	return \%referer_list, \%search_word_list;
}

sub GetSearchKeyword {
	my($requested_url) = @_;
	my ($url, $getstr) = split(/\?/, $requested_url);
	if($getstr eq '' && $url !~ /(a9\.com|\.excite\.com|technorati\.jp)/) {
		return '';
	}
	my @parts = split(/\&/, $getstr);
	my %variables;
	for my $part (@parts) {
		my ($name, $value) = split(/=/, $part);
		if($value ne '') {
			$variables{$name} = $value;
		}
	}
	my @url_parts = split(/\//, $url);
	my @url_parts2 = split(/\./, $url_parts[2]);
	my $tld = pop @url_parts2;
	my $word = '';
	my $engine_name = '';
	my $engine_url = '';
	if($url =~ /\.google\./) {
		if($url =~ /images\.google\./) {
			my $prev = $variables{'prev'};
			$prev = &URL_Decode($prev);
			if($prev =~ /q=([^&]+)&/) {
				$word = $1;
			}
		} elsif($variables{'q'} ne '') {
			$word = $variables{'q'};
		} elsif($variables{'as_q'} ne '') {
			$word = $variables{'as_q'};
		}
		$engine_name = "Google($tld)";
		my @tmp = split(/\.google\./, $url);
		my $suffix = pop @tmp;
		$engine_url = 'http://www.google.' . $suffix;
	} elsif($url =~ /\.yahoo\./) {
		if($variables{'p'} ne '') {
			$word = $variables{'p'};
		} elsif($variables{'key'} ne '') {
			$word = $variables{'key'};
		}
		$engine_name = "Yahoo!($tld)";
		my @tmp = split(/\.yahoo\./, $url);
		my $suffix = pop @tmp;
		$engine_url = 'http://www.yahoo.' . $suffix;
	} elsif($url =~ /\.excite\./) {
		if($url =~ /odn\.excite\.co\.jp/) {
			$word = $variables{'search'};
			$engine_name = "ODN Search";
			$engine_url = 'http://www.odn.ne.jp/';
		} elsif($url =~ /dion\.excite\.co\.jp/) {
			$word = $variables{'search'};
			$engine_name = "DION Search";
			$engine_url = 'http://www.dion.ne.jp/';
		} else {
			if($variables{'search'}) {
				$word = $variables{'search'};
			} elsif($variables{'s'}) {
				$word = $variables{'s'};
			}
			$engine_name = "excite($tld)";
			my @tmp = split(/\.excite\./, $url);
			my $suffix = pop @tmp;
			$engine_url = 'http://www.excite.' . $suffix;
		}
	} elsif($url =~ /\.msn\./) {
		$word = $variables{'q'};
		$engine_name = "MSN($tld)";
		my @tmp = split(/\.msn\./, $url);
		my $suffix = pop @tmp;
		$engine_url = 'http://www.msn.' . $suffix;
	} elsif($url =~ /\.live\.com/) {
		$word = $variables{'q'};
		$engine_name = 'Live Search';
		$engine_url = 'http://www.live.com/';
	} elsif($url =~ /\.infoseek\./) {
		$word = $variables{'qt'};
		$engine_name = 'infoseek';
		$engine_url = 'http://www.infoseek.co.jp/';
	} elsif($url =~ /\.goo\.ne\.jp/) {
		$word = $variables{'MT'};
		$engine_name = 'goo';
		$engine_url = 'http://www.goo.ne.jp/';
	} elsif($url =~ /search\.livedoor\.com/) {
		$word = $variables{'q'};
		$engine_name = 'livedoor';
		$engine_url = 'http://www.livedoor.com/';
	} elsif($url =~ /ask\.[a-z]+\//) {
		$word = $variables{'q'};
		$engine_name = "Ask($tld)";
		$engine_url = 'http://ask.' . $tld;
	} elsif($url =~ /lycos/) {
		if($url =~ /wisenut/) {
			$word = $variables{'q'};
		} else {
			$word = $variables{'query'};
		}
		$engine_name = "Lycos($tld)";
		my @tmp = split(/\.lycos\./, $url);
		my $suffix = pop @tmp;
		$engine_url = 'http://www.lycos.' . $suffix;
	} elsif($url =~ /\.fresheye\.com/) {
		$word = $variables{'kw'};
		$engine_name = 'フレッシュアイ';
		$engine_url = 'http://www.fresheye.com/';
	} elsif($url =~ /search\.biglobe\.ne\.jp/) {
		$word = $variables{'q'};
		$engine_name = 'BIGLOBEサーチ attayo';
		$engine_url = 'http://search.biglobe.ne.jp/';
	} elsif($url =~ /\.netscape\.com/) {
		$word = $variables{'s'};
		$engine_name = 'Netscape Search';
		$engine_url = 'http://www.netscape.com/';
	} elsif($url =~ /www\.overture\.com/) {
		$word = $variables{'Keywords'};
		$engine_name = 'overture';
		$engine_url = 'http://www.overture.com/';
	} elsif($url =~ /\.altavista\.com/) {
		$word = $variables{'q'};
		$engine_name = 'altavista';
		$engine_url = 'http://www.altavista.com/';
	} elsif($url =~ /search\.aol\.com/) {
		$word = $variables{'query'};
		$engine_name = 'AOL Search(com)';
		$engine_url = 'http://search.aol.com/aolcom/webhome';
	} elsif($url =~ /search\.jp\.aol\.com/) {
		$word = $variables{'query'};
		$engine_name = 'AOL Search(jp)';
		$engine_url = 'http://search.jp.aol.com/index';
	} elsif($url =~ /\.looksmart\.com/) {
		$word = $variables{'qt'};
		$engine_name = 'looksmart';
		$engine_url = 'http://search.looksmart.com/';
	} elsif($url =~ /bach\.istc\.kobe\-u\.ac\.jp\/cgi\-bin\/metcha\.cgi/) {
		$word = $variables{'q'};
		$engine_name = 'Metcha Seearch';
		$engine_url = 'http://bach.cs.kobe-u.ac.jp/metcha/';
	} elsif($url =~ /\.alltheweb\.com/) {
		$word = $variables{'q'};
		$engine_name = 'alltheweb';
		$engine_url = 'http://www.alltheweb.com/';
	} elsif($url =~ /\.alexa\.com\/search/) {
		$word = $variables{'q'};
		$engine_name = 'Alexa';
		$engine_url = 'http://www.alexa.com/';
	} elsif($url =~ /search\.naver\.com/) {
		$word = $variables{'query'};
		$engine_name = 'NEVER';
		$engine_url = 'http://www.naver.com/';
	} elsif($url =~ /\.baidu\.com/) {
		$word = $variables{'wd'};
		$engine_name = '百度';
		$engine_url = 'http://www.baidu.com/';
	} elsif($url =~ /\.mooter\.co\.jp/) {
		$word = $variables{'keywords'};
		$engine_name = 'Mooter';
		$engine_url = 'http://www.mooter.co.jp/';
	} elsif($url =~ /\.marsflag\.com/) {
		$word = $variables{'phrase'};
		$engine_name = 'MARS FLAG';
		$engine_url = 'http://www.marsflag.com/';
	} elsif($url =~ /clusty\.jp/) {
		$word = $variables{'query'};
		$engine_name = 'Clusty';
		$engine_url = 'http://clusty.jp/';
	} elsif($url =~ /(search|newsflash)\.nifty\.com/) {
		if($variables{'Text'} ne '') {
			$word = $variables{'Text'};
		} elsif($variables{'q'} ne '') {
			$word = $variables{'q'};
		} elsif($variables{'key'} ne '') {
			$word = $variables{'key'};
		}
		$engine_name = '@nifty アット・サーチ';
		$engine_url = 'http://www.nifty.com/search/';
	} elsif($url =~ /\.technorati\.jp\/search\/(.+)$/) {
		$word = $1;
		$engine_name = 'テクノラティ';
		$engine_url = 'http://www.technorati.jp/';
	} else {
		return '';
	}
	if($word eq '') {
		return '';
	}
	$word = &URL_Decode($word);
	if($requested_url =~ /\&(ei|ie)\=utf\-8/i) {
		#何もしない
	} elsif($requested_url =~ /\&(ei|ie)\=euc\-jp/i) {
		&Jcode::convert(\$word, "utf8", "euc");
	} else {
		&Jcode::convert(\$word, "utf8");
	}
	$word =~ s/　/ /g;
	$word =~ s/\s+/ /g;
	$word =~ s/^\s//;
	$word =~ s/\s$//;
	return $word, $engine_name, $engine_url;
}

sub AnalyzeScreen {
	my($screen_ref) = @_;
	my %ScreenResolution;
	my %ScreenColorDepth;
	while( my($key, $v) = each %{$screen_ref} ) {
		if($v eq '-' || $v eq '') {
			next;
		}
		my($w, $h, $c) = split(/\s/, $v);
		$ScreenResolution{"$w×$h"} ++;
		$ScreenColorDepth{$c} ++;
	}
	return \%ScreenResolution, \%ScreenColorDepth;
}

sub print_summary {
	my ($t, $c, $summary) = @_;
	my($min_year, $min_mon, $min_mday, $min_hour, $min_min, $min_sec) = $summary->{min_date} =~ /^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/;
	my($max_year, $max_mon, $max_mday, $max_hour, $max_min, $max_sec) = $summary->{max_date} =~ /^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/;
	#対象ログ内の対象月のリストを作成する
	my %year_mon_list;
	while( my($i, $v) = each %{$summary->{all_date}} ) {
		my $ym = substr($v, 0, 6);
		$year_mon_list{$ym} ++;
	}
	#ページビュー
	$t->param("loglines" => &CommaFormat($summary->{loglines}));
	#ログファイル欄出力
	my @log_list_array;
	for my $key (sort keys %{$summary->{LogList}}) {
		my %hash;
		$hash{logfilename} = $key;
		if($key eq $summary->{SelectedLogFileName}) {
			$hash{selected} = 'selected="selected"';
		}
		push(@log_list_array, \%hash);
	}
	$t->param("LOG_LIST" => \@log_list_array);
	# ログファイルサイズ欄出力
	$t->param("log_size" => &CommaFormat($summary->{log_size}));

	# ログローテーション欄出力
	my $LogSizeRate = int(($summary->{log_size} * 100 / $c->{LOTATION_SIZE}) * 10) / 10;
	if($LogSizeRate > 100) {$LogSizeRate = 100;}
	my $LogSizeGraphMaxLen = 150;	#ピクセル
	my $LogSizeGraphLen = int($LogSizeGraphMaxLen * $LogSizeRate / 100);	#ピクセル
 	if($c->{LOTATION} eq '0') {
		$t->param("LOTATION_0" => 1);
 	} elsif($c->{LOTATION} eq '1') {
		$t->param("LOTATION_1" => 1);
		$t->param("lotation_size" => &CommaFormat($c->{LOTATION_SIZE}));
		$t->param("LogSizeRate" => $LogSizeRate);
	} elsif($c->{LOTATION} eq '2') {
		$t->param("LOTATION_2" => 1);
	} elsif($c->{LOTATION} eq '3') {
		$t->param("LOTATION_3" => 1);
	}
	# 解析モード欄出力
	my($ana_mode_year, $ana_mode_mon) = $summary->{ana_month} =~ /^(\d{4})(\d{2})/;
	$t->param("ana_mode_year" => $ana_mode_year);
	$t->param("ana_mode_mon" => $ana_mode_mon);
	$t->param("ana_mode_day" => $summary->{ana_day});
	if($summary->{mode} eq 'DAILY') {
		$t->param("ANA_MODE_DAILY" => 1);
	} elsif($summary->{mode} eq 'MONTHLY') {
		$t->param("ANA_MODE_MONTHLY" => 1);
	} else {
		$t->param("ANA_MODE_ALL" => 1);
	}
 	# 解析モード指定欄出力
	$t->param("SelectedLogFileName" => $summary->{SelectedLogFileName});
	if($summary->{mode} eq 'MONTHLY') {
		$t->param("mode_selected_monthly" => 'selected="selected"');
	} elsif($summary->{mode} eq 'DAILY') {
		$t->param("mode_selected_daily" => 'selected="selected"');
		$t->param("ana_day" => $summary->{ana_day});
	} else {
		$t->param("mode_selected_all" => 'selected="selected"');
	}
	my @year_mon_list_array;
	for my $key (sort {$a <=> $b} keys(%year_mon_list)) {
		my($y, $m) = $key =~ /^(\d{4})(\d{2})/;
		my %hash;
		$hash{y} = $y;
		$hash{m} = $m;
		if($summary->{mode} eq 'MONTHLY' && $key eq $summary->{ana_month}) {
			$hash{selected} = 'selected="selected"';
		}
		push(@year_mon_list_array, \%hash);
	}
	$t->param("YEAR_MON_LIST" => \@year_mon_list_array);
	# 解析対象期間欄出力
	$t->param("min_year" => $min_year);
	$t->param("min_mon" => $min_mon);
	$t->param("min_mday" => $min_mday);
	$t->param("min_hour" => $min_hour);
	$t->param("min_min" => $min_min);
	$t->param("min_sec" => $min_sec);
	$t->param("max_year" => $max_year);
	$t->param("max_mon" => $max_mon);
	$t->param("max_mday" => $max_mday);
	$t->param("max_hour" => $max_hour);
	$t->param("max_min" => $max_min);
	$t->param("max_sec" => $max_sec);
}

# 国別ドメイン名レポート
sub print_remote_tld {
	my($t, $c, $summary, $country_list_ref) = @_;
	my %tld_list = &ReadDef('./conf/country_code.dat');
	my @ana_remotetld_list_array;
	my $order = 1; 
	for my $tld ( sort { $country_list_ref->{$b} <=> $country_list_ref->{$a} } keys %{$country_list_ref} ) {
		my $rate = int($country_list_ref->{$tld} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{order} = $order;
		$hash{tld} = $tld;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $country_list_ref->{$tld};
		$hash{country} = $tld_list{$tld};
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_remotetld_list_array, \%hash);
		$order ++;
	}
	$t->param("ANA_REMOTETLD_LIST" => \@ana_remotetld_list_array);
}

# アクセス元ドメイン名レポート
sub print_remote_domain {
	my($t, $c, $summary, $domain_list_ref) = @_;
	my @ana_remotedomain_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $domain ( sort { $domain_list_ref->{$b} <=> $domain_list_ref->{$a} } keys %{$domain_list_ref} ) {
		unless($domain_list_ref->{$domain} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $rate = int($domain_list_ref->{$domain} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{order} = $dsp_order;
		$hash{domain} = $domain;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $domain_list_ref->{$domain};
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_remotedomain_list_array, \%hash);
		$pre_velue = $domain_list_ref->{$domain};
		$order ++;
	}
	$t->param("ANA_REMOTEDOMAIN_LIST" => \@ana_remotedomain_list_array);
}

# アクセス元ホスト名レポート
sub print_remote_host {
	my($t, $c, $summary, $host_list_ref) = @_;
	my @ana_remotehost_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $host_list_ref->{$b} <=> $host_list_ref->{$a} } keys %{$host_list_ref} ) {
		unless($host_list_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $rate = int($host_list_ref->{$key} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{order} = $dsp_order;
		$hash{host} = $key;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $host_list_ref->{$key};
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_remotehost_list_array, \%hash);
		$pre_velue = $host_list_ref->{$key};
		$order ++;
	}
	$t->param("ANA_REMOTEHOST_LIST" => \@ana_remotehost_list_array);
}

# ブラウザー表示可能言語レポート
sub print_http_lang {
	my($t, $c, $summary, $language_list_ref) = @_;
	my @ana_httplang_list_array;
	my $order = 1; 
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $language_list_ref->{$b} <=> $language_list_ref->{$a} } keys %{$language_list_ref} ) {
		unless($language_list_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $rate = int($language_list_ref->{$key} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{order} = $dsp_order;
		$hash{lang} = $key;
		if($key eq '' || $key eq '-') {
			$hash{lang} = "";
		} else {
			$hash{lang_caption} = $summary->{langcode_list}->{$key};
		}
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $language_list_ref->{$key};
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_httplang_list_array, \%hash);
		$pre_velue = $language_list_ref->{$key};
		$order ++;
	}
	$t->param("ANA_HTTPLANG_LIST" => \@ana_httplang_list_array);
}

# ブラウザーレポート
sub print_browser {
	my($t, $c, $summary, $browser_list_ref, $browser_v_list_ref) = @_;
	my @ana_browser_list_array;
	my $order = 1; 
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $browser_list_ref->{$b} <=> $browser_list_ref->{$a} } keys %{$browser_list_ref} ) {
		unless($browser_list_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $rate = int($browser_list_ref->{$key} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{order} = $dsp_order;
		$hash{browser} = $key;
		if($key eq '' || $key eq '-') {
			$hash{browser} = "";
		}
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $browser_list_ref->{$key};
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		$pre_velue = $browser_list_ref->{$key};
		$order ++;
		#
		my @version_list_array;
		for my $key1 (sort keys %{$browser_v_list_ref}) {
			if($key1 =~ /^$key:/) {
				my $vrate = int($browser_v_list_ref->{$key1} * 10000 / $summary->{loglines}) / 100;
				my $GraphLength2 = int($c->{GRAPHMAXLENGTH} * $vrate / 100);
				my $v = $key1;
				$v =~ s/^$key://;
				my %vhash;
				$vhash{version} = $v;
				$vhash{rate} = $vrate;
				$vhash{num} = $browser_v_list_ref->{$key1};
				$vhash{GraphLength} = $GraphLength2;
				$vhash{IMAGE_URL} = $c->{IMAGE_URL};
				push(@version_list_array, \%vhash);
			}
		}
		$hash{VERSION_LIST} = \@version_list_array;
		push(@ana_browser_list_array, \%hash);
	}
	$t->param("ANA_BROWSER_LIST" => \@ana_browser_list_array);
}

#プラットフォームレポート
sub print_platform {
	my($t, $c, $summary, $platform_list_ref, $platform_v_list_ref) = @_;
	my @ana_platform_list_array;
	my $order = 1; 
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $platform_list_ref->{$b} <=> $platform_list_ref->{$a} } keys %{$platform_list_ref} ) {
		unless($platform_list_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $rate = int($platform_list_ref->{$key} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{order} = $dsp_order;
		$hash{platform} = $key;
		if($key eq '' || $key eq '-') {
			$hash{platform} = "";
		}
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $platform_list_ref->{$key};
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		$pre_velue = $platform_list_ref->{$key};
		$order ++;
		#
		my @version_list_array;
		for my $key1 (sort keys %{$platform_v_list_ref}) {
			if($key1 =~ /^$key:/) {
				my $vrate = int($platform_v_list_ref->{$key1} * 10000 / $summary->{loglines}) / 100;
				my $GraphLength2 = int($c->{GRAPHMAXLENGTH} * $vrate / 100);
				my $v = $key1;
				$v =~ s/^$key://;
				my %vhash;
				$vhash{version} = $v;
				$vhash{rate} = $vrate;
				$vhash{num} = $platform_v_list_ref->{$key1};
				$vhash{GraphLength} = $GraphLength2;
				$vhash{IMAGE_URL} = $c->{IMAGE_URL};
				push(@version_list_array, \%vhash);
			}
		}
		$hash{VERSION_LIST} = \@version_list_array;
		push(@ana_platform_list_array, \%hash);
	}
	$t->param("ANA_PLATFORM_LIST" => \@ana_platform_list_array);
}

#月別アクセス数レポート
sub print_request_monthly {
	my($t, $c, $summary, $monthly_list_ref) = @_;
	my @ana_monthly_list_array;
	for my $key (sort keys %{$monthly_list_ref}) {
		my($year, $month) = $key =~ /^(\d{4})(\d{2})/;
		my $rate = int($monthly_list_ref->{$key} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{year} = $year;
		$hash{month} = $month;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $monthly_list_ref->{$key};
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_monthly_list_array, \%hash);
	}
	$t->param("ANA_REQUESTMONTHLY_LIST" => \@ana_monthly_list_array);
}

#日付別アクセス数レポート
sub print_request_daily {
	my($t, $c, $summary, $date_list_ref, $ana_month) = @_;
	my($year, $month) = $ana_month =~ /^(\d{4})(\d{2})/;
	my $last_day = &LastDay($year, $month);
	my @ana_daily_list_array;
	my @week_map = ('日', '月', '火', '水', '木', '金', '土');
	for( my $key=1; $key<=$last_day; $key++ ) {
		my $day = sprintf("%02d", $key);
		my $num = $date_list_ref->{"${year}${month}${day}"} + 0;
		my $rate = int($num * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my $w = &Youbi($year, $month, $key);
		my %hash;
		$hash{year} = $year;
		$hash{month} = $month;
		$hash{day} = $day;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{w} = $w;
		$hash{week} = $week_map[$w];
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_daily_list_array, \%hash);
	}
	$t->param("ANA_REQUESTDAILY_LIST" => \@ana_daily_list_array);
}

#時間別アクセス数レポート
sub print_request_hourly {
	my($t, $c, $summary, $hourly_list_ref) = @_;
	my @ana_hourly_list_array;
	for( my $key=0; $key<24; $key++ ) {
		my $hour = sprintf("%02d", $key);
		my $num = $hourly_list_ref->{$hour} + 0;
		my $rate = int($num * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{hour} = $hour;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_hourly_list_array, \%hash);
	}
	$t->param("ANA_REQUESTHOURLY_LIST" => \@ana_hourly_list_array);
}

# 曜日別アクセス数レポート
sub print_request_weekly {
	my($t, $c, $summary, $daily_list_ref) = @_;
	my @ana_weekly_list_array;
	my @week_map = ('日', '月', '火', '水', '木', '金', '土');
	for( my $key=0; $key<=6; $key++ ) {
		my $num = $daily_list_ref->{$key} + 0;
		my $rate = int($num * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{w} = $key;
		$hash{week} = $week_map[$key];
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_weekly_list_array, \%hash);
	}
	$t->param("ANA_REQUESTWEEKLY_LIST" => \@ana_weekly_list_array);
}

#リクエストレポート
sub print_request_file {
	my($t, $c, $summary, $request_list_ref) = @_;
	my @ana_requestfile_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $request_list_ref->{$b} <=> $request_list_ref->{$a} } keys %{$request_list_ref} ) {
		unless($request_list_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $num = $request_list_ref->{$key} + 0;
		my $rate = int($request_list_ref->{$key} * 10000 / $summary->{loglines}) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my $title = &GetHtmlTitle($c, $key);
		my %hash;
		$hash{title} = $title;
		$hash{url} = $key;
		# 表示するURLを、50文字に縮める
		my $dsp_url = $key;
		if(length($key) > 50) {
			$dsp_url = substr($key, 0, 50);
			$dsp_url .= '...';
		}
		$hash{url_disp} = &SecureHtml($dsp_url);
		$hash{url_encoded} = &UrlEncode($key);
		$hash{order} = $dsp_order;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		$hash{CGI_URL} = $c->{CGI_URL};
		push(@ana_requestfile_list_array, \%hash);
		$pre_velue = $request_list_ref->{$key};
		$order ++;
	}
	$t->param("ANA_REQUESTFILE_LIST" => \@ana_requestfile_list_array);
}

sub UrlEncode {
	my($string) = @_;
	#半角英数字および半角スペースでない文字をエンコード
	$string =~ s/([^A-Za-z0-9\s])/'%'.unpack("H2", $1)/ego;
	#半角スペースを"+"に変換
	$string =~ s/\s/+/g;
	return $string;
}

#リンク元サイトレポート
sub print_referer_site {
	my($t, $c, $summary, $referer_list_ref) = @_;
	my %referer_site_list;
	my $total = 0;
	for my $url (keys %{$referer_list_ref}) {
		my @url_parts = split(/\//, $url);
		my $site = "$url_parts[0]//$url_parts[2]/";
		$referer_site_list{$site} += $referer_list_ref->{$url};
		$total += $referer_list_ref->{$url};
	}
	my @ana_referersite_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $referer_site_list{$b} <=> $referer_site_list{$a} } keys %referer_site_list ) {
		unless($referer_site_list{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $num = $referer_site_list{$key} + 0;
		my $rate = int($num * 10000 / $total) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my $dsp_url = $key;
		if(length($key) > 50) {
			$dsp_url = substr($key, 0, 50);
			$dsp_url .= '...';
		}
		$dsp_url = &SecureHtml($dsp_url);
		my %hash;
		$hash{url_disp} = $dsp_url;
		$hash{url_encoded} = &UrlEncode($key);
		$hash{order} = $dsp_order;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		$hash{CGI_URL} = $c->{CGI_URL};
		push(@ana_referersite_list_array, \%hash);
		$pre_velue = $referer_site_list{$key};
		$order ++;
	}
	$t->param("ANA_REFERERSITE_LIST" => \@ana_referersite_list_array);
}

#リンク元URLレポート
sub print_referer_url {
	my($t, $c, $summary, $referer_list_ref) = @_;
	my $total = 0;
	while( my($url, $n) = each %{$referer_list_ref} ) {
		$total += $n;
	}
	my @ana_refererurl_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $referer_list_ref->{$b} <=> $referer_list_ref->{$a} } keys %{$referer_list_ref} ) {
		unless($referer_list_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $num = $referer_list_ref->{$key} + 0;
		my $rate = int($num * 10000 / $total) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		# 表示するURLを、50文字に縮める
		my $dsp_url = $key;
		if(length($key) > 50) {
			$dsp_url = substr($key, 0, 50);
			$dsp_url .= '...';
		}
		$dsp_url = &SecureHtml($dsp_url);
		my %hash;
		$hash{url_disp} = $dsp_url;
		$hash{url_encoded} = &UrlEncode($key);
		$hash{order} = $dsp_order;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		$hash{CGI_URL} = $c->{CGI_URL};
		push(@ana_refererurl_list_array, \%hash);
		$pre_velue = $referer_list_ref->{$key};
		$order ++;
	}
	$t->param("ANA_REFERERURL_LIST" => \@ana_refererurl_list_array);
}

#検索エンジンの検索キーワード レポート
sub print_keyword {
	my($t, $c, $summary, $search_word_list_ref) = @_;
	my $cnt = 0;
	while( my($w, $n) = each %{$search_word_list_ref} ) {
		$cnt += $n;
	}
	my @ana_keyword_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $search_word_list_ref->{$b} <=> $search_word_list_ref->{$a} } keys %{$search_word_list_ref} ) {
		unless($search_word_list_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $num = $search_word_list_ref->{$key} + 0;
		my $rate = int($num * 10000 / $cnt) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my $disp_word = &SecureHtml($key);
		my %hash;
		$hash{keyword} = $disp_word;
		$hash{order} = $dsp_order;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_keyword_list_array, \%hash);
		$pre_velue = $search_word_list_ref->{$key};
		$order ++;
	}
	$t->param("ANA_KEYWORD_LIST" => \@ana_keyword_list_array);
}

sub SecureHtml {
	my($html) = @_;
	$html =~ s/\&amp;/\&/g;
	$html =~ s/\&/&amp;/g;
	$html =~ s/\"/&quot;/g;
	$html =~ s/</&lt;/g;
	$html =~ s/>/&gt;/g;
	return $html;
}

#画面解像度レポート
sub print_resolution {
	my($t, $c, $summary, $resolution_ref) = @_;
	my $cnt = 0;
	while( my($key, $n) = each %{$resolution_ref} ) {
		$cnt += $n;
	}
	my @ana_resolution_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $resolution_ref->{$b} <=> $resolution_ref->{$a} } keys %{$resolution_ref} ) {
		unless($resolution_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $num = $resolution_ref->{$key} + 0;
		my $rate = int($num * 10000 / $cnt) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{resolution} = $key;
		$hash{order} = $dsp_order;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_resolution_list_array, \%hash);
		$pre_velue = $resolution_ref->{$key};
		$order ++;
	}
	$t->param("ANA_RESOLUTION_LIST" => \@ana_resolution_list_array);
}

#画面色深度レポート
sub print_color_depth {
	my($t, $c, $summary, $color_depth_ref) = @_;
	my $cnt = 0;
	while( my($key, $n) = each %{$color_depth_ref} ) {
		$cnt += $n;
	}
	my @ana_list_array;
	my $order = 1;
	my $dsp_order = 1;
	my $pre_velue = "";
	for my $key ( sort { $color_depth_ref->{$b} <=> $color_depth_ref->{$a} } keys %{$color_depth_ref} ) {
		unless($color_depth_ref->{$key} == $pre_velue) {
			$dsp_order = $order;
			last if($dsp_order > $c->{ROW});
		}
		my $num = $color_depth_ref->{$key} + 0;
		my $rate = int($num * 10000 / $cnt) / 100;
		my $GraphLength = int($c->{GRAPHMAXLENGTH} * $rate / 100);
		my %hash;
		$hash{color} = &CommaFormat(2 ** $key);
		$hash{bit} = $key;
		$hash{order} = $dsp_order;
		$hash{rate} = $rate;
		$hash{GraphLength} = $GraphLength;
		$hash{num} = $num;
		$hash{IMAGE_URL} = $c->{IMAGE_URL};
		push(@ana_list_array, \%hash);
		$pre_velue = $color_depth_ref->{$key};
		$order ++;
	}
	$t->param("ANA_COLORDEPTH_LIST" => \@ana_list_array);
}

# URLエンコードされた文字列を、デコードして返す
sub URL_Decode {
	my($str) = @_;
	$str =~ s/\+/ /g;
	$str =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C",hex($1))/eg;
	return $str;
}

# 西暦、月、日を引数に取り、曜日コードを返す。
# 日:0, 月:1, 火:2, 水:3, 木:4, 金:5, 土:6
sub Youbi {
	my($year, $month, $day) = @_;
	my $time = timelocal(0, 0, 0, $day, $month - 1, $year);
	my @date_array = localtime($time);
	return $date_array[6];
}

# 西暦と月を引数に取り、該当月の最終日を返す
sub LastDay {
	my($year, $month) = @_;
	$month =~ s/^0//;
	if($month =~ /[^0-9]/ || $year =~ /[^0-9]/) {
		return '';
	}
	if($month < 1 && $month > 12) {
		return '';
	}
	if($year > 2037 || $year < 1900) {
		return '';
	}
	my($lastday) = 1;
	my($time) = timelocal(0, 0, 0, 1, $month-1, $year-1900);
	my(@date_array) = localtime($time);
	my($mon) = $date_array[4];
	my($flag) = 1;
	my($count) = 0;
	while($flag) {
		if($mon ne $date_array[4]) {
			return $lastday;
			$flag = 0;
		}
		$lastday = $date_array[3];
		$time = $time + (60 * 60 * 24);
		@date_array = localtime($time);
		$count ++;
		last if($count > 40);
	}
}

sub DateConv {
	my($day_time) = @_;
	my @temp = split(/ /, $day_time);
	$day_time = $temp[0];
	my($day, $hour, $min, $sec) = split(/:/, $day_time);
	my($mday, $mon, $year) = split(/\//, $day);
	my %month = (
		'Jan'	=>	'01',
		'Feb'	=>	'02',
		'Mar'	=>	'03',
		'Apr'	=>	'04',
		'May'	=>	'05',
		'Jun'	=>	'06',
		'Jul'	=>	'07',
		'Aug'	=>	'08',
		'Sep'	=>	'09',
		'Oct'	=>	'10',
		'Nov'	=>	'11',
		'Dec'	=>	'12'
	);
	$mon = $month{$mon};
	if($mon eq '') {return '';}
	return "$year$mon$mday$hour$min$sec";
}

sub EncryptPasswd {
	my($pass) = @_;
	my @salt_set = ('a'..'z','A'..'Z','0'..'9','.','/');
	srand;
	my $seed1 = int(rand(64));
	my $seed2 = int(rand(64));
	my $salt = $salt_set[$seed1] . $salt_set[$seed2];
	return crypt($pass,$salt);
}

sub InputCheck {
	my($mode, $ana_month, $ana_day) = @_;
	if($ana_month && $ana_month !~ /^\d{6}$/) {
		&ErrorPrint('年月に不正な値が送信されました。');
	}
	if($mode eq 'DAILY') {
		if($ana_month eq '') {
			&ErrorPrint('年月がを指定してください。');
		}
		if($ana_day =~ /[^0-9]/) {
			&ErrorPrint('日付は、半角数字で指定してください。');
		}
		my($y, $m) = $ana_month =~ /^(\d{4})(\d{2})/;
		my $last_day = &LastDay($y, $m);
		if($ana_day > $last_day || $ana_day < 1) {
			&ErrorPrint('日付が正しくありません。');
		}
	}
}

# 指定された定義ファイルを読み取り、連想配列を返す。
sub ReadDef {
	my($file) = @_;
	my %hash;
	open(FILE, "$file") || &ErrorPrint("$file をオープンできませんでした。");
	while(<FILE>) {
		chop;
		my @buff = split(/=/);
		$hash{$buff[0]} = $buff[1];
	}
	close(FILE);
	return %hash;
}

sub PrintAuthForm {
	my($c, $err_flag) = @_;
	my $t = &load_template("./template/logon.tmpl");
	if($err_flag) {
		$t->param("err" => "認証エラー");
	}
	my $body = $t->output();
	my $clen = length $body;
	print "Content-Type: text/html; charset=utf-8\n";
	if($ENV{SERVER_NAME} !~ /($c->{FREE_SERVER_NAME})/) {
		print "Content-Length: ${clen}\n";
	}
	print "\n";
	print $body;
	exit;
}

sub ErrorPrint {
	my($err) = @_;
	my $t = &load_template("./template/error.tmpl");
	$t->param("err" => $err);
	my $body = $t->output();
	my $clen = length $body;
	print "Content-Type: text/html; charset=utf-8\n";
	print "\n";
	print $body;
	exit;
}

sub SetCookie {
	my($CookieName, $CookieValue) = @_;
	# URLエンコード
	$CookieValue =~ s/([^\w\=\& ])/'%' . unpack("H2", $1)/eg;
	$CookieValue =~ tr/ /+/;
	my $CookieHeaderString = "Set-Cookie: $CookieName=$CookieValue\;";
	return $CookieHeaderString;
}

sub GetCookie {
	my(@CookieList) = split(/\; /, $ENV{'HTTP_COOKIE'});
	my(%Cookie) = ();
	my($key, $CookieName, $CookieValue);
	for $key (@CookieList) {
		($CookieName, $CookieValue) = split(/=/, $key);
		$CookieValue =~ s/\+/ /g;
		$CookieValue =~ s/%([0-9a-fA-F][0-9a-fA-F])/pack("C",hex($1))/eg;
		$Cookie{$CookieName} = $CookieValue;
	}
	return %Cookie;
}

sub ClearCookie {
	my($name) = @_;
	my $expire = 'Thu, 01-Jan-1970 00:00:00 GMT';
	my $cookie_header = "Set-Cookie: $name=clear; expires=$expire;";
	$cookie_header .= "\n";
	return $cookie_header;
}

sub GetSelectedLogFile {
	my($c) = @_;
	my $dir = $c->{LOG};
	$dir =~ s/\/([^\/]*)$//;
	my $LogFileName = $1;
	my $SelectedLogFileName = $c->{q}->param('LOG');
	if($SelectedLogFileName) {
		if($SelectedLogFileName =~ /[^a-zA-Z0-9\_\.]/) {
			&ErrorPrint("ログファイル名に不正な値が送信されました。");
		}
	} else {
		if($c->{LOTATION} == 2) {
			my $DateStr = &GetToday($c);
			$SelectedLogFileName = "$LogFileName\.$DateStr\.cgi";
		} elsif($c->{LOTATION} == 3) {
			my $DateStr = &GetToday($c);
			my $MonStr = substr($DateStr, 0, 6);
			$SelectedLogFileName = "$LogFileName\.$MonStr"."00.cgi";
		} else {
			$SelectedLogFileName = "$LogFileName\.cgi";
		}
	}
	my $SelectedLogFile = "${dir}/$SelectedLogFileName";
	unless(-e $SelectedLogFile) {
		opendir(DIR, $dir);
		my @files = readdir(DIR);
		closedir(DIR);
		my @tmp;
		for my $f (@files) {
			if($f !~ /\.cgi$/) { next; }
			push(@tmp, $f);
		}
		my @sorted = sort {$b cmp $a} @tmp;
		$SelectedLogFileName = $sorted[0];
		$SelectedLogFile = "${dir}/$sorted[0]";
	}
	return($SelectedLogFile, $SelectedLogFileName);
}

sub GetPastLogList {
	my($c) = @_;
	my %LogList = ();
	my $LogDir = $c->{LOG};
	$LogDir =~ s/\/([^\/]*)$//;
	my $LogFileName = $1;
	unless($LogDir) {$LogDir = '.';}
	opendir(LOGDIR, "$LogDir") || &ErrorPrint("ログ格納ディレクトリ「$LogDir」をオープンできませんでした。");
	my @FileList = readdir(LOGDIR);
	for my $key (@FileList) {
		if($key =~ /^$LogFileName/) {
			$LogList{$key} = "$LogDir\/$key";
		}
	}
	return %LogList;
}

sub GetToday {
	my($c) = @_;
	my @tm = localtime(time + $c->{TIMEDIFF}*60*60);
	my $y = $tm[5] + 1900;
	my $m = $tm[4] + 1;
	my $d = $tm[3];
	$m = sprintf("%02d", $m);
	$d = sprintf("%02d", $d);
	return $y.$m.$d;
}

#指定したドキュメントルートからのパスから、タイトルを取得する。
sub GetHtmlTitle {
	my($c, $URL) = @_;
	$URL =~ s/\?.*$//;
	$URL =~ s/\#.*$//;
	my($Title, $Path, $HtmlFile);
	if($c->{URL2PATH_FLAG}) {
		for my $key (keys %{$c->{URL2PATH}}) {
			if($URL =~ /^$key/) {
				$HtmlFile = $URL;
				$HtmlFile =~ s/^$key/$c->{URL2PATH}->{$key}/;
			}
		}
		unless($HtmlFile) {
			return '';
		}
	} else {
		$_ = $URL;
		m|https*://[^/]+/(.*)|;
		$Path = '/'.$1;
		$HtmlFile = $ENV{DOCUMENT_ROOT}.$Path;
	}
	unless(-e $HtmlFile) {return ''};
	open(HTML, "$HtmlFile") || return '';
	my $HitFlag  = 0;
	while(my $line = <HTML>) {
		chop $line;
		if( $line =~ /<title>([^<]*)<\/title>/i ) {
			$Title = $1;
			$HitFlag = 1;
			last;
		}
		if( $line =~ /<\/head>/i ) {last;}
	}
	close(HTML);
	if($HitFlag) {
		&Jcode::convert(\$Title, "utf8");
		return $Title;
	} else {
		return '';
	}
}


sub CommaFormat {
	my($num) = @_;
	#数字とドット以外の文字が含まれていたら、引数をそのまま返す。
	if($num =~ /[^0-9\.]/) {return $num;}
	#整数部分と小数点を分離
	my($int, $decimal) = split(/\./, $num);
	#整数部分の桁数を調べる
	my $figure = length $int;
	my $commaformat;
	#整数部分にカンマを挿入
	for(my $i=1;$i<=$figure;$i++) {
		my $n = substr($int, $figure-$i, 1);
		if(($i-1) % 3 == 0 && $i != 1) {
			$commaformat = "$n,$commaformat";
		} else {
			$commaformat = "$n$commaformat";
		}
	}
	#小数点があれば、それを加える
	if($decimal) {
		$commaformat .= "\.$decimal";
	}
	#結果を返す
	return $commaformat;
}

sub User_Agent {
	my($user_agent, $remote_host) = @_;
	my($platform, @agentPart, $browser, $browser_v);
	my($platform_v, @agentPart2, $user_agent2, @buff, @buff2, @buff3);
	my($flag, $key, @version_buff);
	if($user_agent =~ /Trend Micro/) {
		return;
	}
	if($user_agent =~ /DoCoMo/i) {
		$platform = 'DoCoMo';
		@agentPart = split(/\//, $user_agent);
		$browser = 'DoCoMo';
		$browser_v = $agentPart[1];
		$platform_v = $agentPart[2];
		if($platform_v eq '') {
			if($user_agent =~ /DoCoMo\/([0-9\.]+)\s+([0-9a-zA-Z]+)/) {
				$browser_v = $1;
				$platform_v = $2;
			}
		}
	} elsif($user_agent =~ /NetPositive/i) {
		$browser = 'NetPositive';
		if($user_agent =~ /NetPositive\/([0-9\.\-]+)/) {
			$browser_v = $1;
		}
		$platform = 'BeOS';
		$platform_v = '';
	} elsif($user_agent =~ /OmniWeb/) {
		$browser = 'OmniWeb';
		if($user_agent =~ /Mac_PowerPC/i) {
			$platform = 'MacOS';
			$platform_v = '';
		} else {
			$platform = '';
			$platform_v = '';
		}
		if($user_agent =~ /OmniWeb\/([0-9\.]+)/) {
			$browser_v = $1;
		} else {
			$browser_v = '';
		}
	} elsif($user_agent =~ /Cuam/i) {
		$browser = 'Cuam';
		$platform = 'Windows';
		$browser_v = '';
		$platform_v = '';
		if($user_agent =~ /Cuam Ver([0-9\.]+)/i) {
			$platform_v = '';
			$browser_v = $1;
		} else {
			if($user_agent =~ /Windows\s+([^\;\)]+)/) {
				$platform_v = $1;
			}
			if($user_agent =~ /Cuam\s+(0-9a-z\.)/) {
				$browser_v = $1;
			}
		}
	} elsif($user_agent =~ /^JustView\/([0-9\.]+)/) {
		$platform = 'Windows';
		$platform_v = '';
		$browser = 'JustView';
		$browser_v = $1;
	} elsif($user_agent =~ /^sharp pda browser\/([0-9\.]+).*\((.+)\//) {
		$platform = 'ZAURUS';
		$platform_v = $2;
		$browser = 'sharp_pda_browser';
		$browser_v = $1;
	} elsif($user_agent =~ /DreamPassport\/([0-9\.]+)/) {
		$platform = 'Dreamcast';
		$platform_v = '';
		$browser = 'DreamPassport';
		$browser_v = $1;
	} elsif($user_agent =~ /\(PLAYSTATION\s*(\d+)\;\s*([\d\.]+)\)/) {
		$platform = 'PlayStation';
		$platform_v = "PlayStation $1";
		$browser = $platform_v;
		$browser_v = $2;
	} elsif($user_agent =~ /\(PS\d+\s*\(PlayStation\s*(\d+)\)\;\s*([\d\.]+)\)/) {
		$platform = 'PlayStation';
		$platform_v = "PlayStation $1";
		$browser = $platform_v;
		$browser_v = $2;
	} elsif($user_agent =~ /\(PlayStation Portable\)\;\s*([\d\.]+)/) {
		$platform = 'PlayStation';
		$platform_v = "PlayStation Portable";
		$browser = $platform_v;
		$browser_v = $1;
	} elsif($user_agent =~ /^Sonybrowser2 \(.+\/PlayStation2 .+\)/) {
		$platform = 'PlayStation';
		$platform_v = 'PlayStation 2';
		$browser = 'Sonybrowser2';
		$browser_v = '';
	} elsif($user_agent =~ /Opera\/([\d\.]+)\s*\(Nintendo Wii/i) {
		$platform = 'Nintendo';
		$platform_v = 'Wii';
		$browser = 'Opera';
		$browser_v = $1;

	} elsif($user_agent =~ /Nitro/ && $user_agent =~ /Opera\s+([\d\.]+)/) {
		$platform = 'Nintendo';
		$platform_v = 'DS';
		$browser = 'Opera';
		$browser_v = $1;
	} elsif($user_agent =~ /(CBBoard|CBBstandard)\-[0-9\.]+/) {
		$platform = 'DoCoMo';
		$platform_v = 'ColorBrowserBorad';
		$browser = 'DoCoMo';
		$browser_v = 'ColorBrowserBorad';
	} elsif($user_agent =~ /^PDXGW/) {
		$platform = 'DDI POCKET';
		$platform_v = 'H"';
		$browser = 'DDI POCKET';
		$browser_v = 'H"';
	} elsif($user_agent =~ /^Sleipnir Version ([0-9\.]+)/) {
		$browser = 'Sleipnir';
		$browser_v = $1;
		$platform = 'Windows';
		$platform_v = '';
	} elsif($user_agent =~ /AppleWebKit/ && $user_agent =~ / Safari/) {
		if($user_agent =~ /Mobile\/([a-zA-Z0-9\-\.]+)/) {
			$platform_v = $1;
			if($user_agent =~ /\(iPod\;/) {
				$platform = 'iPod touch';
			} elsif($user_agent =~ /\(iPhone[\s\;]/) {
				$platform = 'iPhone';
			}
			$browser = 'Safari Mobile';
			($browser_v) = $user_agent =~ /Version\/(\d+\.\d+)/;
		} else {
			my($build) = $user_agent =~ /Safari\/([\d\.]+)/;
			$platform = 'MacOS';
			$browser = 'Safari';
			if($build eq "523.12") {
				$browser_v = '3.0';
				$platform_v = '10.4';
			} elsif($build >= 523) {
				$browser_v = '3.0';
				$platform_v = '10.5';
			} elsif($build >= 412) {
				$browser_v = '2.0';
				$platform_v = '10.4';
			} elsif($build >= 312) {
				$browser_v = '1.3';
				$platform_v = '10.3';
			} elsif($build >= 125) {
				$browser_v = '1.2';
				$platform_v = '10.3';
			} elsif($build >= 100) {
				$browser_v = '1.1';
				$platform_v = '10.3';
			} elsif($build >= 85) {
				$browser_v = '1.0';
				$platform_v = '10.2';
			}
			if($user_agent =~ /Version\/(\d+\.\d+)/) {
				$browser_v = $1;
			}
			if($user_agent =~ /Windows\s+([^\;]+)/i) {
				$platform = "Windows";
				$platform_v = $1;
				if($platform_v eq 'NT 6.0') {
					$platform_v = 'Vista';
				} elsif($platform_v eq 'NT 5.0') {
					$platform_v = '2000';
				} elsif($platform_v eq 'NT 5.1') {
					$platform_v = 'XP';
				}
			}
			if($user_agent =~ /Chrome\/([\d\.]+)/) {
				$browser_v = $1;
				$browser = 'Chrome';
			}
		}
	} elsif($user_agent =~ /(DIPOCKET|WILLCOM)\;\w+\/([\w\d\-]+)/i) {
		$platform_v = $2;
		$platform = 'WILLCOM';
		if($user_agent =~ /(Opera|NetFront|CNF)[\/\s]([\d\.]+)/) {
			$browser = $1;
			$browser_v = $2;
		}
	} elsif($user_agent =~ /(KYOCERA|SHARP)\/([AW][\w\d\-]+)/) {
		$platform_v = $2;
		$platform = 'WILLCOM';
		if($user_agent =~ /(Opera|NetFront|CNF)[\/\s]([\d\.]+)/) {
			$browser = $1;
			$browser_v = $2;
		}
	} elsif($user_agent =~ /KYOCERAAH\-([\w\d\-]+)/) {
		$platform_v = 'AH-' . $1;
		$platform = 'WILLCOM';
		if($user_agent =~ /(Opera|NetFront|CNF)[\/\s]([\d\.]+)/) {
			$browser = $1;
			$browser_v = $2;
		}
	} elsif($user_agent =~ /SHARP ([AW][\w\d\-]+)\//) {
		$platform_v = $1;
		$platform = 'WILLCOM';
		if($user_agent =~ /(Opera|NetFront|CNF)[\/\s]([\d\.]+)/) {
			$browser = $1;
			$browser_v = $2;
		}
	} elsif($user_agent =~ /^(J\-PHONE|Vodafone|Softbank)/i) {
		$browser = $1;
		$platform = 'SoftBank';
		my @parts = split(/\//, $user_agent);
		$browser_v = $parts[1];
		$platform_v = $parts[2];
		if($user_agent =~ /Browser\/([^\/]+)\/([\d\.]+)/) {
			$browser = $1;
			$browser_v = $2;
		}
	} elsif($user_agent =~ /UP\.\s*Browser/i) {
		$user_agent =~ s/UP\.\s*Browser/UP\.Browser/;
		$browser = 'UP.Browser';
		@agentPart = split(/ /, $user_agent);
		if($agentPart[0] =~ /KDDI/i) {
			my @tmp = split(/\-/, $agentPart[0]);
			$platform_v = $tmp[1];
			my @tmp2 = split(/\//, $agentPart[1]);
			$browser_v = $tmp2[1];
		} else {
			@agentPart2 = split(/\//, $agentPart[0]);
			($browser_v, $platform_v) = split(/\-/, $agentPart2[1]);
		}
		my %devid_list = (
			#http://www.au.kddi.com/ezfactory/tec/spec/4_4.html
			#■CDMA 1X WIN (W03H、W02H、W01を除く)
			'HI3E' => 'au,W63H',
			'SH37' => 'au,W64SH',
			'MA34' => 'au,W62P',
			'SH36' => 'au,URBANO',
			'CA3B' => 'au,W62CA',
			'SN3F' => 'au,re',
			'TS3J' => 'au,W62T',
			'SN3D' => 'au,W61S',
			'TS3I' => 'au,W61T',
			'PT33' => 'au,W61PT',
			'KC3D' => 'au,W61K',
			'SN3C' => 'au,W54S',
			'HI3B' => 'au,W53H',
			'KC3E' => 'au,W44K IIカメラなしモデル',
			'ST32' => 'au,W53SA',
			'CA38' => 'au,W52CA',
			'TS3D' => 'au,W53T',
			'KC3A' => 'au,MEDIA SKIN',
			'TS3C' => 'au,W52T',
			'HI39' => 'au,W51H',
			'KC39' => 'au,W51K',
			'SN38' => 'au,W44S',
			'TS38' => 'au,W45T',
			'SN37' => 'au,W43S',
			'SH31' => 'au,W41SH',
			'TS37' => 'au,W44T/T II/T III',
			'SN36' => 'au,W42S',
			'SA36' => 'au,W41SA',
			'CA33' => 'au,W41CA',
			'SA35' => 'au,W33SA/SA II',
			'KC34' => 'au,W32K',
			'CA32' => 'au,W31CA',
			'KC33' => 'au,W31K/K II',
			'HI33' => 'au,W22H',
			'SA31' => 'au,W21SA',
			'HI32' => 'au,W21H',
			'CA36' => 'au,E03CA',
			'TS3M' => 'au,W65T',
			'KC3I' => 'au,W65K',
			'TS3L' => 'au,W64T',
			'PT34' => 'au,W62PT',
			'HI3D' => 'au,W62H',
			'KC3H' => 'au,W63K',
			'SA3D' => 'au,W63SA',
			'SA3C' => 'au,W61SA',
			'HI3C' => 'au,W61H',
			'MA33' => 'au,W61P',
			'SA3B' => 'au,W54SA',
			'TS3H' => 'au,W56T',
			'KC3B' => 'au,W53K/W64K',
			'SN3B' => 'au,W53S',
			'TS3E' => 'au,W54T',
			'MA32' => 'au,W52P',
			'SA3A' => 'au,W52SA',
			'SH32' => 'au,W51SH',
			'TS3B' => 'au,W51T',
			'CA37' => 'au,W51CA',
			'TS39' => 'au,DRAPE',
			'KC38' => 'au,W44K/K II',
			'CA35' => 'au,W43CA',
			'KC37' => 'au,W43K',
			'CA34' => 'au,W42CA',
			'TS35' => 'au,neon',
			'KC36' => 'au,W42K',
			'TS34' => 'au,W41T',
			'SN34' => 'au,W41S',
			'TS33' => 'au,W32T',
			'HI35' => 'au,W32H',
			'TS32' => 'au,W31T',
			'SA33' => 'au,W31SA/SA II',
			'CA31' => 'au,W21CA/CA II',
			'SN31' => 'au,W21S',
			'KC31' => 'au,W11K',
			'SA37' => 'au,E02SA',
			'CA3C' => 'au,W63CA',
			'SN3G' => 'au,W64S',
			'KC3K' => 'au,W63Kカメラ無し',
			'SA3E' => 'au,W64SA',
			'SH35' => 'au,W62SH',
			'TS3K' => 'au,Sportio',
			'KC3G' => 'au,W62K',
			'SN3E' => 'au,W62S',
			'ST34' => 'au,W62SA',
			'CA3A' => 'au,W61CA',
			'SH34' => 'au,W61SH',
			'TS3G' => 'au,W55T',
			'ST33' => 'au,INFOBAR 2',
			'CA39' => 'au,W53CA',
			'SH33' => 'au,W52SH',
			'SN3A' => 'au,W52S',
			'HI3A' => 'au,W52H',
			'SN39' => 'au,W51S',
			'SA39' => 'au,W51SA',
			'MA31' => 'au,W51P',
			'TS3A' => 'au,W47T',
			'SA38' => 'au,W43SA',
			'HI38' => 'au,W43H/H II',
			'ST31' => 'au,W42SA',
			'HI37' => 'au,W42H',
			'TS36' => 'au,W43T',
			'KC35' => 'au,W41K',
			'HI36' => 'au,W41H',
			'HI34' => 'au,PENCK',
			'SA34' => 'au,W32SA',
			'SN33/SN35' => 'au,W32S',
			'SN32' => 'au,W31S',
			'SA32' => 'au,W22SA',
			'TS31' => 'au,W21T',
			'KC32' => 'au,W21K',
			'HI31' => 'au,W11H',
			#■CDMA 1X
			'ST2C' => 'au,Sweets cute',
			'ST26' => 'au,Sweets',
			'SA2A' => 'au,A5527SA',
			'TS2D' => 'au,A5523T',
			'ST2A' => 'au,A5520SA/SA II',
			'TS2B' => 'au,A5516T',
			'CA27' => 'au,A5512CA',
			'ST24' => 'au,A5507SA',
			'TS27' => 'au,A5504T',
			'TS26' => 'au,A5501T',
			'ST23' => 'au,A5405SA',
			'SN24' => 'au,A5402S',
			'ST21' => 'au,A5306ST',
			'HI24' => 'au,A5303H II',
			'TS23' => 'au,A5301T',
			'PT21' => 'au,A1405PT',
			'SN27' => 'au,A1402S II',
			'KC23' => 'au,A1401K',
			'TS25' => 'au,A1304T',
			'SA24' => 'au,A1302SA',
			'KC15' => 'au,A1013K',
			'ST29' => 'au,Sweets pure',
			'ST25' => 'au,talby',
			'KC29' => 'au,A5526K',
			'SA29' => 'au,A5522SA',
			'ST28' => 'au,A5518SA',
			'KC27' => 'au,A5515K',
			'TS2A' => 'au,A5511T',
			'TS28' => 'au,A5506T',
			'SA26' => 'au,A5503SA',
			'CA26' => 'au,A5407CA',
			'SN25' => 'au,A5404S',
			'CA23' => 'au,A5401CA II',
			'KC22' => 'au,A5305K',
			'HI23' => 'au,A5303H',
			'SA22' => 'au,A3015SA',
			'SN29' => 'au,A1404S/S II',
			'SN28' => 'au,A1402S II カメラ無し',
			'SA28' => 'au,A1305SA',
			'SN23' => 'au,A1301S',
			'KC26' => 'au,B01K',
			'CA28' => 'au,G\'zOne TYPE-R',
			'ST22' => 'au,INFOBAR',
			'ST2D' => 'au,A5525SA',
			'KC28' => 'au,A5521K',
			'TS2C' => 'au,A5517T',
			'ST27' => 'au,A5514SA',
			'TS29' => 'au,A5509T',
			'SA27' => 'au,A5505SA',
			'KC24' => 'au,A5502K',
			'KC25' => 'au,A5502K',
			'CA25' => 'au,A5406CA',
			'CA24' => 'au,A5403CA',
			'CA23' => 'au,A5401CA',
			'TS24' => 'au,A5304T',
			'CA22' => 'au,A5302CA',
			'PT22' => 'au,A1406PT',
			'KC26' => 'au,A1403K',
			'SN26' => 'au,A1402S',
			'SA25' => 'au,A1303SA',
			'ST14' => 'au,A1014ST',
			#■cdmaOne
			'SN21' => 'au,A3014S',
			'SA21' => 'au,A3011SA',
			'KC14' => 'au,A1012K',
			'MA21' => 'au,C3003P',
			'SN17' => 'au,C1002S',
			'HI14' => 'au,C451H',
			'KC13' => 'au,C414K',
			'ST12' => 'au,C411ST',
			'MA13' => 'au,C408P',
			'SY13' => 'au,C405SA',
			'DN11' => 'au,C402DE',
			'TS22' => 'au,A3013T',
			'SN22' => 'au,A1101S',
			'ST13' => 'au,A1011ST',
			'KC21' => 'au,C3002K',
			'SY15' => 'au,C1001SA',
			'TS14' => 'au,C415T',
			'SN15' => 'au,C413S',
			'SN16' => 'au,C413S',
			'TS13' => 'au,C410T',
			'HI13' => 'au,C407H',
			'SN12' => 'au,C404S',
			'SN14' => 'au,C404S',
			'SY12' => 'au,C401SA',
			'CA21' => 'au,A3012CA',
			'KC14' => 'au,A1012K II',
			'TS21' => 'au,C5001T',
			'HI21' => 'au,C3001H',
			'CA14' => 'au,C452CA',
			'KC13' => 'au,C414K II',
			'SY14' => 'au,C412SA',
			'CA13' => 'au,C409CA',
			'SN13' => 'au,C406S',
			'ST11' => 'au,C403ST',
			#■TU-KA
			'KCTE' => 'TU-KA,TK51',
			'SYT5' => 'TU-KA,TS41',
			'TST7' => 'TU-KA,TT31',
			'KCTB' => 'TU-KA,TK23',
			'KCT9' => 'TU-KA,TK21',
			'KCT8' => 'TU-KA,TK12',
			'MIT1' => 'TU-KA,TD11',
			'TST3' => 'TU-KA,TT03',
			'SYT2' => 'TU-KA,TS02',
			'KCT3' => 'TU-KA,TK0K',
			'TST1' => 'TU-KA,TT01',
			'TST9' => 'TU-KA,TT51',
			'KCTD' => 'TU-KA,TK40',
			'KCTC' => 'TU-KA,TK31',
			'KCTA' => 'TU-KA,TK22',
			'TST5' => 'TU-KA,TT21',
			'SYT3' => 'TU-KA,TS11',
			'MAT3' => 'TU-KA,TP11',
			'KCT5' => 'TU-KA,TK04',
			'MAT1' => 'TU-KA,TP01',
			'MAT2' => 'TU-KA,TP01',
			'KCT2' => 'TU-KA,TK02',
			'SYT1' => 'TU-KA,TS01',
			'KCU1' => 'TU-KA,TK41',
			'TST8' => 'TU-KA,TT32',
			'SYT4' => 'TU-KA,TS31',
			'TST6' => 'TU-KA,TT22',
			'TST4' => 'TU-KA,TT11',
			'KCT7' => 'TU-KA,TK11',
			'KCT6' => 'TU-KA,TK05',
			'KCT4' => 'TU-KA,TK03',
			'TST2' => 'TU-KA,TT02',
			'KCT1' => 'TU-KA,TK01',
			#その他
			'NT95'=>'UP.SDK',
			'UPG'=>'UP.SDK',
			'P-PAT'=>'DoCoMo,P-PAT',
			'D2'=>'DoCoMo,D2'
		);
		if($devid_list{$platform_v} eq '') {
			$platform = '';
			$platform_v = '';
		} else {
			($platform, $platform_v) = split(/,/, $devid_list{$platform_v});
		}
	} elsif($user_agent =~ /^ASTEL\/(.+)\/(.+)\/(.+)\//) {
		$platform = 'ASTEL';
		$browser = 'ASTEL';
		$browser_v = '';
		$platform_v = substr($2, 0, 5);
	} elsif($user_agent =~ /^Mozilla\/.+ AVE-Front\/(.+) \(.+\;Product=(.+)\;.+\)/) {
		$browser = 'NetFront';
		$browser_v = $1;
		$platform = $2;
		$platform_v = '';
	} elsif($user_agent =~ /^Mozilla\/.+ Foliage-iBrowser\/([0-9\.]+) \(WinCE\)/) {
		$platform = 'Windows';
		$platform_v = 'CE';
		$browser = 'Foliage-iBrowser';
		$browser_v = $1;		
	} elsif($user_agent =~ /^Mozilla\/.+\(compatible\; MSPIE ([0-9\.]+)\; Windows CE/) {
		$platform = 'Windows';
		$platform_v = 'CE';
		$browser = 'PocketIE';
		$browser_v = $1;
	} elsif($user_agent =~ /Opera/) {
		$browser = "Opera";
		if($user_agent =~ /^Opera\/([0-9\.]+)/) {
			$browser_v = $1;
		} elsif($user_agent =~ /Opera\s+([0-9\.]+)/) {
			$browser_v = $1;
		} else {
			$browser_v = '';
		}
		if($user_agent =~ /Windows\s+([^\;]+)(\;|\))/i) {
			$platform = "Windows";
			$platform_v = $1;
			if($platform_v eq 'NT 6.0') {
				$platform_v = 'Vista';
			} elsif($platform_v eq 'NT 5.0') {
				$platform_v = '2000';
			} elsif($platform_v eq 'NT 5.1') {
				$platform_v = 'XP';
			} elsif($platform_v eq 'NT 5.2') {
				$platform_v = '2003';
			} elsif($platform_v eq 'ME') {
				$platform_v = 'Me';
			}
		} elsif($user_agent =~ /Macintosh/) {
			if($user_agent =~ /Mac OS X/) {
				$platform = "MacOS";
				$platform_v = '';
			}
		} elsif($user_agent =~ /Mac_PowerPC/i) {
			$platform = 'MacOS';
			$platform_v = '';
		} elsif($user_agent =~ /Linux\s+([a-zA-Z0-9\.\-]+)/) {
			$platform = "Linux";
			$platform_v = $1;
		} elsif($user_agent =~ /BeOS ([A-Z0-9\.\-]+)(\;|\))/) {
			$platform = 'BeOS';
			$platform_v = $1;
		} else {
			$platform = '';
			$platform_v = '';
		}
	} elsif($user_agent =~ /^Mozilla\/[^\(]+\(compatible\; MSIE .+\)/) {
		if($user_agent =~ /NetCaptor ([0-9\.]+)/) {
			$browser = 'NetCaptor';
			$browser_v = $1;
		} elsif($user_agent =~ /Sleipnir\/([\d\.]+)/) {
			$browser = 'Sleipnir';
			$browser_v = $1;
		} elsif($user_agent =~ /Lunascape\s+([\d\.]+)/) {
			$browser = 'Lunascape';
			$browser_v = $1;
		} else {
			$browser = 'Internet Explorer';
			$user_agent2 = $user_agent;
			$user_agent2 =~ s/ //g;
			@buff = split(/\;/, $user_agent2);
			@version_buff = grep(/MSIE/i, @buff);
			$browser_v = $version_buff[0];
			$browser_v =~ s/MSIE//g;
			if($browser_v =~ /^([0-9]+)\.([0-9]+)/) {
        			$browser_v = "$1\.$2";
			}
		}

		if($user_agent =~ /Windows 3\.1/i) {
			$platform = 'Windows';
			$platform_v = '3.1';
		} elsif($user_agent =~ /Win32/i) {
			$platform = 'Windows';
			$platform_v = '32';
		} elsif($user_agent =~ /Windows 95/i) {
			$platform = 'Windows';
			$platform_v = '95';
		} elsif($user_agent =~ /Windows 98/i) {
			$platform = 'Windows';
			if($user_agent =~ /Win 9x 4\.90/) {
				$platform_v = 'Me';
			} else {
				$platform_v = '98';
			}
		} elsif($user_agent =~ /Windows NT 6\.0/i) {
			$platform = 'Windows';
			$platform_v = 'Vista';
		} elsif($user_agent =~ /Windows NT 5\.0/i) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows NT 5\.1/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Windows NT 5\.2/i) {
			$platform = 'Windows';
			$platform_v = '2003';
		} elsif($user_agent =~ /Windows NT/i 
				&& $user_agent !~ /Windows NT 5\.0/i) {
			$platform = 'Windows';
			$platform_v = 'NT';
		} elsif($user_agent =~ /Windows 2000/) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows ME/i) {
			$platform = 'Windows';
			$platform_v = 'Me';
		} elsif($user_agent =~ /Windows XP/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Windows CE/i) {
			$platform = 'Windows';
			$platform_v = 'CE';
		} elsif($user_agent =~ /Mac/i) {
			$platform = 'MacOS';
			if($browser_v >= 5.22) {
				$platform_v = '10.x';
			} else {
				$platform_v = '9以下';
			}
		} elsif($user_agent =~ /WebTV/i) {
			$platform = 'WebTV';
			@buff2 = split(/ /, $user_agent);
			@buff3 = split(/\//, $buff2[1]);
			$platform_v = $buff3[1];
		} else {
			$platform = '';
			$platform_v = '';
		}
	} elsif($user_agent =~ /^Mozilla\/([0-9\.]+)/) {
		$browser = 'Netscape';
		$browser_v = $1;
		if($user_agent =~ /Gecko/) {
			if($user_agent =~ /Netscape[0-9]*\/([0-9a-zA-Z\.]+)/) {
				$browser_v = $1;
			} elsif($user_agent =~ /Firefox\/[\d\.]+\s+Navigator\/([\d\.]+)/) {
				$browser_v = $1;
			} elsif($user_agent =~ /(Phoenix|Chimera|Firefox|Camino|Konqueror)\/([0-9a-zA-Z\.]+)/) {
				$browser = $1;
				$browser_v = $2;
			} else {
				$browser = 'Mozilla';
				if($user_agent =~ /rv:([0-9\.]+)/) {
					$browser_v = $1;
				} else {
					$browser_v = '';
				}
			}
		}
		if($user_agent =~ /Win95/) {
			$platform = 'Windows';
			$platform_v = '95';
		} elsif($user_agent =~ /Windows 95/) {
			$platform = 'Windows';
			$platform_v = '95';
		} elsif($user_agent =~ /Win 9x 4\.90/i) {
			$platform = 'Windows';
			$platform_v = 'Me';
		} elsif($user_agent =~ /Windows Me/i) {
			$platform = 'Windows';
			$platform_v = 'Me';
		} elsif($user_agent =~ /Win98/i) {
			$platform = 'Windows';
			$platform_v = '98';
		} elsif($user_agent =~ /WinNT/i) {
			$platform = 'Windows';
			$platform_v = 'NT';
		} elsif($user_agent =~ /Windows NT 6\.0/i) {
			$platform = 'Windows';
			$platform_v = 'Vista';
		} elsif($user_agent =~ /Windows NT 5\.0/i) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows NT 5\.1/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Windows NT 5\.2/i) {
			$platform = 'Windows';
			$platform_v = '2003';
		} elsif($user_agent =~ /Windows 2000/i) {
			$platform = 'Windows';
			$platform_v = '2000';
		} elsif($user_agent =~ /Windows XP/i) {
			$platform = 'Windows';
			$platform_v = 'XP';
		} elsif($user_agent =~ /Macintosh/i) {
			$platform = 'MacOS';
			if($user_agent =~ /Mac OS X/i) {
				if($user_agent =~ /Mac OS X ([\d\.]+)\;/) {
					$platform_v = $1;
				} else {
					$platform_v = '10.x';
				}
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /SunOS/i) {
			$platform = 'Solaris';
			if($user_agent =~ /SunOS\s+([0-9\-\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /Linux/i) {
			$platform = 'Linux';
			if($user_agent =~ /Fedora/) {
				$platform_v = 'Fedora Core';
				if($user_agent =~ /\.fc([\d+\.]+)\s+/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /SUSE/) {
				$platform_v = 'SUSE';
				if($user_agent =~ /SUSE\/([\d\.\-]+)/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /Vine/) {
				$platform_v = 'Vine';
				if($user_agent =~ /Vine\/([\d\.\-\w]+)/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /VineLinux/) {
				$platform_v = 'Vine';
				if($user_agent =~ /VineLinux\/([\d\.\-\w]+)/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /Mandriva/) {
				$platform_v = 'Mandriva';
				if($user_agent =~ /Mandriva\/([\d\.\-\w]+)/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /Red Hat/) {
				$platform_v = 'Red Hat';
				if($user_agent =~ /Red Hat\/([\d\.\-\w]+)/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /Debian/) {
				$platform_v = 'Debian';
				if($user_agent =~ /Debian\-([\d\.\-\w\+]+)/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /Ubuntu/) {
				$platform_v = "Ubuntu";
				if($user_agent =~ /Ubuntu(\/|\-)([\d\.\-\w\+]+)/) {
					$platform_v .= " $2";
				}
			} elsif($user_agent =~ /CentOS/) {
				$platform_v = "CentOS";
				if($user_agent =~ /CentOS\/([\d\.\-\w\+]+)/) {
					$platform_v .= " $1";
				}
			} elsif($user_agent =~ /Linux\s+([0-9\-\.]+)/) {
				$platform_v = $1;
			}
		} elsif($user_agent =~ /FreeBSD/i) {
			$platform = 'FreeBSD';
			if($user_agent =~ /FreeBSD\s+([a-zA-Z0-9\.\-\_]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /NetBSD/i) {
			$platform = 'NetBSD';
			$platform_v = '';
		} elsif($user_agent =~ /AIX/i) {
			$platform = 'AIX';
			if($user_agent =~ /AIX\s+([0-9\.]+)/) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /IRIX/i) {
			$platform = 'IRIX';
			if($user_agent =~ /IRIX\s+([0-9\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /HP-UX/i) {
			$platform = 'HP-UX';
			if($user_agent =~ /HP-UX\s+([a-zA-Z0-9\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /OSF1/i) {
			$platform = 'OSF1';
			if($user_agent =~ /OSF1\s+([a-zA-Z0-9\.]+)/i) {
				$platform_v = $1;
			} else {
				$platform_v = '';
			}
		} elsif($user_agent =~ /BeOS/i) {
			$platform = 'BeOS';
			$platform_v = '';
		} else {
			$platform = '';
			$platform_v = '';
		}
	} else {
		$platform = '';
		$platform_v = '';
		$browser = '';
		$browser_v = '';
	}
	return ($platform, $platform_v, $browser, $browser_v);
}
