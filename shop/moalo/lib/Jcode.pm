package Jcode;
#
# エンコード／デコード モジュール
#

use strict;
#use Encode 'from_to';


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
# FORM デコード
sub form_decode
{
	my $self = shift;
	local $_ = shift;

	tr/+/ /;
	s/%([\da-fA-F]{2})/chr(hex $1)/eg;

	return $_;
}


#-------------------------------------------------
# FORM エンコード
sub form_encode
{
	my $self = shift;
	local $_ = shift;

#	from_to( $_, 'shift-jis', 'utf8' );

	s/([^\w\*\-\. ])/sprintf("%%%02X",ord $1)/eg;
	tr/ /+/;

	return $_;
}


1;
