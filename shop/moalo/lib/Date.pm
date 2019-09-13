package Date;
#
# 日時変換 モジュール
#

use strict;


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
# 閏年の判定
sub leap
{
	my $self = shift;
	my $y    = shift;

	return $y % 4 == 0 && ( $y % 100 || $y % 400 == 0 );
}


#-------------------------------------------------
# 月日数を取得
sub month_days
{
	my $self  = shift;
	my $year  = shift;
	my $mon   = shift;
	my @mdays = (31,28,31,30,31,30,31,31,30,31,30,31);

	# 閏年の判定
	$mdays[1]=29 if $self->leap($year);

	return $mdays[ $mon - 1 ];
}


#-------------------------------------------------
# 月名を取得
sub month_name
{
	my $self = shift;
	my $mon  = shift;
	my $type = shift || 'Eng';

	if ( 'Eng' eq $type )
	{
		return qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)[$mon];
	}
	elsif ( 'Jpn' eq $type )
	{
		return qw(睦月 如月 弥生 卯月 皐月 水無月 文月 葉月 長月 神無月 霜月 師走)[$mon];
	}
}


#-------------------------------------------------
# 実日数を取得
sub total_days
{
	my $self = shift;
	my $year = shift;
	my $mon  = shift;
	my $day  = shift;

	# 年日数を加算
	my $oy   = $year - 1;
	my $days = $oy * 365 + int( $oy / 4 ) - int( $oy / 100 ) + int( $oy / 400 );

	# 月日数を加算
	for ( my $i=1; $i < $mon; $i++ )
	{
		$days += $self->month_days($year,$i);
	}

	# 残りの日数を加算
	$days += $day;

	return $days;
}


#-------------------------------------------------
# 曜日名を取得
sub week_name
{
	my $self = shift;
	my $wday = shift;
	my $type = shift || 'Eng';

	if ( 'Eng' eq $type )
	{
		return qw(Sun Mon Tue Wed Thu Fri Sat)[$wday];
	}
	elsif ( 'Jpn' eq $type )
	{
		return qw(日 月 火 水 木 金 土)[$wday];
	}
}


#-------------------------------------------------
# 曜日の取得
sub weekday
{
	my $self = shift;
	my $year = shift;
	my $mon  = shift;
	my $day  = shift;

	return $self->total_days( $year, $mon, $day ) % 7;
}


1;
