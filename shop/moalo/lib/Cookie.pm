package Cookie;
#
# クッキー モジュール
#

use strict;
use Date;
use Jcode;


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
# クッキーの取得
sub get
{
	my $self  = shift;
	my $data  = $ENV{'HTTP_COOKIE'};
	my $jcode = new Jcode();
	my %cook;

	my @pair = split( '; ', $data );
	foreach ( @pair )
	{
		my ( $key, $val ) = split( '=' );

		$cook{ $key } = $jcode->form_decode( $val );
	}

	return \%cook;
}


#-------------------------------------------------
# クッキーの保存
sub set
{
	my $self  = shift;
	my $name  = shift;
	my $data  = shift;
	my $life  = shift || 60;
	my $date  = new Date();
	my $jcode = new Jcode();

	# エンコード
	$data = $jcode->form_encode( $data );

	# クッキーの期限を設定
	my( $sec, $min, $hour, $day, $mon, $year, $week )
		= gmtime( time + $life * 24 * 60 * 60 );

	$week = $date->week_name( $week );
	$mon  = $date->month_name( $mon );

	my $exp = sprintf( "%s, %02d-%s-%04d %02d:%02d:%02d GMT",
		$week, $day, $mon, $year+1900, $hour, $min, $sec );

	# クッキー情報の送信
	print "Set-Cookie: $name=$data; expires=$exp\n";
}


1;
