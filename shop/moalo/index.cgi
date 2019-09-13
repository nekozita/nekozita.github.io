#!/usr/bin/perl
# ◆■■■■■■■■■■■■■■■■■■■■■■◆
#
# ＭＯＡＬＯ メイン処理
#
# 作成者：ねこめいし
# メール：info@nekozita.com
# ＵＲＬ：http://nekozita.com/
#
# ◆■■■■■■■■■■■■■■■■■■■■■■◆

use lib './lib';
use Cookie;
use Jcode;
use HTTP;
use XML;
use File;
use SignatureHelper;

#-------------------------------------------------

# 必須パラメータ
$AWSAccessKeyId = '0BADXS9AY5JNB6MZT682';
$AssociateTag   = 'nekozitacafe-22';
$Version        = '2009-07-01';

# ノード番号
%CATEGORY = (
'Books'      => '46413011',
'DVD'        => '562020',
'Music'      => '562060',
'VideoGames' => '637874',
'Toys'       => '13366991'
);

# ソート・パラメータ
%SORT_TYPE1 = (
'sales'   => 'salesrank',
'price'   => 'pricerank',
'title'   => 'titlerank',
'release' => 'daterank'
);
%SORT_TYPE2 = (
'sales'   => 'salesrank',
'price'   => 'pricerank',
'title'   => 'titlerank',
'release' => '-orig-rel-date'
);
%SORT_TYPE3 = (
'sales'   => 'salesrank',
'price'   => 'pricerank',
'title'   => 'titlerank',
'release' => '-releasedate'
);
%SORT_TYPE4 = (
'sales'   => 'salesrank',
'price'   => 'price',
'title'   => 'titlerank',
'release' => '-release-date'
);
%SORT = (
'Books'       => \%SORT_TYPE1,
'DVD'         => \%SORT_TYPE2,
'Music'       => \%SORT_TYPE2,
'Electronics' => \%SORT_TYPE3,
'Software'    => \%SORT_TYPE4,
'Toys'        => \%SORT_TYPE4,
'Hobbies'     => \%SORT_TYPE4,
'VideoGames'  => \%SORT_TYPE4
);

#-------------------------------------------------


# 初期化
&decode( &get_env );
$CXML = new XML();

# 端末判別
$_ = $ENV{'HTTP_USER_AGENT'};
if ( /^(DoCoMo|KDDI|Vodafone)[\/\-]/ )
{
	require Mobile;
	$PUTH = new Mobile();
	$PUTH->error();
}
else
{
	require PC;
	$PUTH = new PC();
}

# クッキー情報の取得
$cookie = new Cookie();
$COOK = $cookie->get();

# ベストセラーの取得
%ECS         = &new_bestseller( %FORM );
$XML_TOPS    = &get_amazon( %ECS );
$XML{'tops'} = $CXML->convert( \$XML_TOPS );

# イベント処理
if ( 'contents' eq $FORM{'m'} )
{
	%ECS         = &contents_load( %FORM );
	$XML_LOOK    = &get_amazon( %ECS );
	$XML{'look'} = $CXML->convert( \$XML_LOOK );

	$PUTH->contents( \%XML, \%CD, $FORM{'i'} );
}
elsif ( 'search' eq $FORM{'m'} )
{
	%ECS          = &new_param_search( %FORM );
	$XML_ITEMS    = &get_amazon( %ECS );
	$XML{'items'} = $CXML->convert( \$XML_ITEMS );

	$PUTH->search( \%XML );
}
elsif ( 'lookup' eq $FORM{'m'} )
{
	%ECS         = &new_param_lookup( %FORM );
	$XML_ITEM    = &get_amazon( %ECS );
	$XML{'look'} = $CXML->convert( \$XML_ITEM );

	$PUTH->lookup( \%XML );
}
elsif ( 'cart' eq $FORM{'m'} )
{
	if ( $COOK->{'cart_id'} )
	{
		%ECS         = &new_param_cart( 'CartGet' );
		$XML_CART    = &get_amazon( %ECS );
		$XML{'cart'} = $CXML->convert( \$XML_CART );

		$PUTH->cart( \%XML );
	}
	else
	{
		$PUTH->empty( \%XML );
	}
}
elsif ( 'add' eq $FORM{'m'} )
{
	if ( $COOK->{'cart_id'} )
	{
		%ECS = &new_param_cart( 'CartAdd' );
	}
	else
	{
		%ECS = &new_param_cart( 'CartCreate' );
	}
	$XML_CART    = &get_amazon( %ECS );
	$XML{'cart'} = $CXML->convert( \$XML_CART );

	$PUTH->cart( \%XML );
}
elsif ( 'modify' eq $FORM{'m'} )
{
	if ( $COOK->{'cart_id'} )
	{
		%ECS         = &new_param_cart( 'CartModify' );
		$XML_CART    = &get_amazon( %ECS );
		$XML{'cart'} = $CXML->convert( \$XML_CART );

		$PUTH->cart( \%XML );
	}
	else
	{
		$PUTH->empty( \%XML );
	}
}
elsif ( 'clear' eq $FORM{'m'} )
{
	if ( $COOK->{'cart_id'} )
	{
		%ECS         = &new_param_cart( 'CartClear' );
		$XML_CART    = &get_amazon( %ECS );
		$XML{'cart'} = $CXML->convert( \$XML_CART );

		$PUTH->cart( \%XML );
	}
	else
	{
		$PUTH->empty( \%XML );
	}
}
elsif ( 'purch' eq $FORM{'m'} )
{
	%ECS         = &new_param_cart( 'CartGet' );
	$XML_CART    = &get_amazon( %ECS );
	$XML{'cart'} = $CXML->convert( \$XML_CART );

	print "Location: $XML{cart}->{CartGetResponse}->{Cart}->{PurchaseURL}\n";
	$cookie->set( 'cart_id', '', '-1' );
	$cookie->set( 'hmac',    '', '-1' );
	print "\n";
}
elsif ( 'help' eq $FORM{'m'} )
{
	$PUTH->help( \%XML, $FORM{'f'} );
}
else
{
	%ECS         = &contents_load( %FORM );
	$XML_LOOK    = &get_amazon( %ECS );
	$XML{'look'} = $CXML->convert( \$XML_LOOK );

	$PUTH->contents( \%XML, \%CD );
}

exit;


#---------------------------------------
# 全角→半角数字変換
sub ascii_number
{
	local $_  = shift;
	my %ascii = qw(０ 0 １ 1 ２ 2 ３ 3 ４ 4 ５ 5 ６ 6 ７ 7 ８ 8 ９ 9);
	my $match = '０|１|２|３|４|５|６|７|８|９';

	s/($match)/$ascii{$1}/eg;

	return $_;
}


#---------------------------------------
# コンテンツデータの読み込み
sub contents_load
{
	my %F = @_;
	my $f = new File();
	my @asin;

	$F{'i'} or $F{'i'} = 'Etc';

	my %fn = (
		'Books'      => 'con_books',
		'DVD'        => 'con_dvd',
		'Music'      => 'con_music',
		'VideoGames' => 'con_game',
		'Toys'       => 'con_toys',
		'Etc'        => 'con_top'
	);

	my @d = $f->readlog( "data/$fn{$F{i}}.dat" );
	foreach ( @d )
	{
		chomp;
		my( $key, $val ) = split("\t");

		push @asin, $val;
		$CD{ $key } = $val;
	}
	$F{'id'} = join( ',', @asin );

	return &new_param_lookup(%F);
}


#-------------------------------------------------
# デコード処理
sub decode
{
	my $buf   = shift;
	my $jcode = new Jcode();
	my @pair;

	undef %FORM;

	@pair = split( '&', $buf );
	foreach ( @pair )
	{
		my( $key, $val ) = split('=');

		$FORM{$key} = $jcode->form_decode( $val );
	}
}


#-------------------------------------------------
# エンコード処理
sub encode
{
	my %args  = @_;
	my $jcode = new Jcode();
	my @pair;

	foreach ( sort keys %args )
	{
		$args{$_} = $jcode->form_encode( $args{$_} );
		push( @pair, "$_=$args{$_}" );
	}
	return join( '&', @pair );
}


#-------------------------------------------------
# エラー処理
sub err
{
	print "Content-Type: text/html\n\n";
	print "<html><body>\n";
	print "<pre>\n";
	print "@_\n";
	print "</pre>\n";
	print "</body></html>\n";

	exit;
}


#-------------------------------------------------
# Amazon XML サーバからデータを取得
sub get_amazon
{
	my %e    = @_;
	my $base = 'http://webservices.amazon.co.jp/onca/xml?';

	# 共通パラメータ
	$e{'Service'}        = 'AWSECommerceService';
	$e{'AWSAccessKeyId'} = $AWSAccessKeyId;
	$e{'AssociateTag'}   = $AssociateTag;
	$e{'Version'}        = $Version;

	# リクエストURL
	my $sh = new SignatureHelper();
	my $request = $sh->canonicalize( $sh->sign( \%e ) );

	# XMLデータを取得
	my $http = new HTTP();
	my $body = $http->get( $base.$request );

	return $body;
}


#-------------------------------------------------
# 環境変数の取得
sub get_env
{
	my $buf;

	if ( $ENV{'REQUEST_METHOD'} eq 'POST' )
	{
		read( STDIN, $buf, $ENV{'CONTENT_LENGTH'} );
	}
	else
	{
		$buf = $ENV{'QUERY_STRING'};
	}

	return $buf;
}


#-------------------------------------------------
# ローカルからＸＭＬデータの取得（デバッグ用）
sub local_xml
{
	my $path = shift;
	my $file = new File();
	my $src  = $file->readtxt( $path );

	return $src;
}


#-------------------------------------------------
# カートパラメータの生成
sub new_param_cart
{
	my $ope = shift;
	my %P   = (
		'Operation'     => $ope,
		'ResponseGroup' => 'Cart'
	);

	# ID の追加
	if ( $COOK->{'cart_id'} )
	{
		$P{'CartId'} = $COOK->{'cart_id'};
		$P{'HMAC'}   = $COOK->{'hmac'};
	}

	# カート操作の追加
	foreach ( keys %FORM )
	{
		if ( /^Item\.[\d]+\./ )
		{
			if ( /^Item\.[\d]+\.Quantity/ )
			{
				$P{$_} = &ascii_number( $FORM{$_} );
			}
			else
			{
				$P{$_} = $FORM{$_};
			}
		}
	}

	# 削除機能の反映
	foreach ( keys %FORM )
	{
		if ( /^delete\.([\d]+)/ )
		{
			if ( $FORM{$_} )
			{
				$P{"Item\.$1\.Quantity"} = 0;
			}
		}
	}

	return %P;
}


#---------------------------------------
# ItemLookup パラメータの生成
sub new_param_lookup
{
	my %I = @_;
	my %P = (
		'Operation'     => 'ItemLookup',
		'ResponseGroup' => 'Medium,Offers,EditorialReview,Similarities,Tracks'
	);

	# ASIN の取り出し
	my @id = split( ',', $I{'id'} );
	if ( @id > 1 )
	{
		for ( my $i=0; $i < @id; $i++ )
		{
			$P{ 'ItemId.'.($i+1) } = $id[$i];
		}
	}
	else
	{
		$P{'ItemId'} = $id[0];
	}

	return %P;
}


#-------------------------------------------------
# ItemSearch パラメータの生成
sub new_param_search
{
	my %F = @_;
	my %P = (
		'Operation'     => 'ItemSearch',
		'SearchIndex'   => $F{'i'}  || 'Blended',
		'ItemPage'      => $F{'pg'} || '1',
		'ResponseGroup' => 'Medium,Offers'
	);

	# Word or Node 検索パラメータ
	$F{'w'} ne '' and $P{'Keywords'}   = $F{'w'};
	$F{'n'} ne '' and $P{'BrowseNode'} = $F{'n'};

	# ソート
	if ( $P{'SearchIndex'} ne 'Blended' )
	{
		if ( $F{'s'} )
		{
			$P{'Sort'} = $SORT{ $P{'SearchIndex'} }->{ $F{'s'} };
		}
		else
		{
			$P{'Sort'} = $SORT{ $P{'SearchIndex'} }->{'sales'};
		}
	}

	return %P;
}


#-------------------------------------------------
# ベストセラーパラメータの生成
sub new_bestseller
{
	my %F = @_;
	my %P = (
		'i'  => $F{'i'}  || 'Blended'
	);

	if ( $P{'i'} ne 'Blended' )
	{
		# ジャンル・カテゴリの確定
		$P{'n'} = $CATEGORY{ $P{'i'} };
	}
	else
	{
		# ジャンルの自動選択
		my @key  = keys %CATEGORY;
		my $auto = int rand scalar @key;
		$P{'i'} = $key[ $auto ];
		$P{'n'} = $CATEGORY{ $key[ $auto ] };
	}

	return &new_param_search(%P);
}
