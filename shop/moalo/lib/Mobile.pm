package Mobile;
#
# ＨＴＭＬページ作成処理（モバイル版）
#

use strict;
use File;


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
# コンストラクタ
sub error
{
	my $self = shift;
	my $f    = new File();

	my $html = $f->readtxt("skin/mobile/error.html");

	print "Content-Type: text/html\n\n";
	print $html;
	exit;
}


1;
