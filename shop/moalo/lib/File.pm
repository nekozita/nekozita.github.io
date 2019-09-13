package File;
#
# ファイル管理 モジュール
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
# ログ形式のファイルを読み込む
sub readlog
{
	my $self = shift;
	my $path = shift;

	open( IN, "<$path" ) or return;
	@_ = <IN>;
	close IN;

	return @_;
}


#-------------------------------------------------
# テキスト形式のファイルを読み込む
sub readtxt
{
	my $self = shift;
	my $path = shift;
	my $data;

	open( IN, "<$path" ) or return;
	while ( <IN> )
	{
		$data .= $_;
	}
	close IN;

	return $data;
}


1;
