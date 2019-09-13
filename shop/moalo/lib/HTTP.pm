package HTTP;
#
# ＨＴＴＰ通信 簡易モジュール
#

use strict;
use Socket;


#-------------------------------------------------
# コンストラクタ
sub new
{
	my $class = shift;
	my $self  = {@_};
	bless $self, $class;

	return $self;
}


#-------------------------------------------------
# ＨＴＴＰサーバから受信
sub get
{
	my ( $self, $url ) = @_;
	my $header;
	my $body;

	# ＵＲＬの解析
	$url =~ m|http://([^/]*)(/.*)|;
	my $host = $1;
	my $path = $2;

	my $port = getservbyname( 'http', 'tcp' );
	my $addr = inet_aton( $host );
	my $sock_addr = pack_sockaddr_in( $port, $addr );

	# ソケットの生成
	socket( SOCKET, PF_INET, SOCK_STREAM, 0 ) or
	  die("ソケットを生成できません！\n");

	# 接続
	connect( SOCKET, $sock_addr ) or
	  die("$host に接続できません！\n");

	select(SOCKET); $|=1; select(STDOUT);

	# ＷＷＷサーバにリクエストを送信
	print SOCKET "GET $path HTTP/1.1\n";
	print SOCKET "Host: $host\n";
	print SOCKET "Connection: close\n";
	print SOCKET "\n";

	while ( <SOCKET> )
	{
		/^[\r\n]+$/ and last;
		$header .= $_;
	}

	while ( <SOCKET> )
	{
		$_ = <SOCKET>;
		s/(\r\n|\r|\n)$//g;
		$body .= $_;
	}

	close SOCKET;

	return wantarray ? ($header,$body) : $body;
}


1;
