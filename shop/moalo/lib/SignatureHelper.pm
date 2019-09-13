package SignatureHelper;
#
# 署名認証ヘルパーモジュール
#

use strict;

use Digest::SHA::PurePerl qw(hmac_sha256_base64);
use URI::Escape;

use constant DEBUG => '0';

use constant AWS_ACCESS_KEY => '0BADXS9AY5JNB6MZT682';
use constant AWS_SECRET_KEY => 'MLZ8T+LiPEuFRXVAneZeIH/wIJv0uUO7wOoovonF';
use constant END_POINT => 'webservices.amazon.co.jp';
use constant REQUEST_METHOD => 'GET';
use constant REQUEST_URI => '/onca/xml';

use constant URI_ESCAPE_REGEX => '^A-Za-z0-9\-_.~';


#-------------------------------------------------
# コンストラクタ
sub new
{
	my ($class, %args) = @_;

	my $self  = {};
	bless $self, $class;

	return $self;
}


#-------------------------------------------------
# カノニカライズ
sub canonicalize {
	my ($self, $params) = @_;

	my @parts=();
	while (my ($k, $v) = each %$params) {
		my $x = $self->escape($k) . '=' . $self->escape($v);
		push @parts, $x;
	}

	my $out = join('&', sort @parts);
	return $out;
}


#-------------------------------------------------
# 暗号化
sub digest {
	my ($self, $x) = @_;
	my $digest = hmac_sha256_base64($x, AWS_SECRET_KEY);

	while (length($digest) % 4) {
		$digest .= '=';
	}
	return $digest;
}


#-------------------------------------------------
# URLエンコーディング
sub escape {
	my ($self, $x) = @_;
	return uri_escape($x, URI_ESCAPE_REGEX);
}


#-------------------------------------------------
# タイムスタンプの取得。
# フォーマット：GMT "YYYY-MM-DDThh:mm:ssZ" 形式。
sub getTimestamp {
	return sprintf("%04d-%02d-%02dT%02d:%02d:%02d.000Z",
		sub {
			($_[5]+1900,
			$_[4]+1,
			$_[3],
			$_[2],
			$_[1],
			$_[0])
		}->(gmtime(time)));
}


#-------------------------------------------------
# 署名認証パラメータの追加
sub sign {
	my ($self, $params) = @_;

	# AccessKey
	$params->{'AWSAccessKeyId'} = AWS_ACCESS_KEY;

	# Timestamp
	$params->{'Timestamp'} = $self->getTimestamp() unless exists $params->{'Timestamp'};

	# canonical
	my $canonical = $self->canonicalize($params);
	debug("[canonical]\n $canonical\n");

	# signed
	my $signed =
		REQUEST_METHOD . "\n" .
		END_POINT . "\n" .
		REQUEST_URI . "\n" .
		$canonical;
	debug("[signed]\n $signed\n");

	# signature
	my $signature = $self->digest($signed);
	$params->{'Signature'} = $signature;
	debug("[signature]\n $signature\n");

	return $params;
}


#-------------------------------------------------
# デバッグ出力
sub debug {
	if (DEBUG) { print shift; }
}


1;
