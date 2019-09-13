package PC;
#
# ＨＴＭＬページ作成処理（ＰＣ版）
#

use strict;
use Cookie;
use File;
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
# 配列を一つの文字列に連結する
sub _arraycat
{
	my $sep   = shift;
	my $array = shift || return;
	my $max   = shift;

	my $ref = ref $array;

	if ( 'ARRAY' eq $ref )
	{
		$max or $max = @{ $array };
		splice( @{ $array }, $max );
		return join( $sep, @{ $array } );
	}
	elsif ( '' eq $ref )
	{
		return $array;
	}
}


#---------------------------------------
# カートの中身を表示
sub _cart
{
	my $cart = shift;
	my $item = $cart->{'CartItems'}->{'CartItem'};
	my $item_num = 1;
	my $h_cart;

	my $ref = ref $item;

	if ( 'ARRAY' eq $ref )
	{
		foreach ( @{ $item } )
		{
			$h_cart .= _cart_fmt( $_, $item_num );
			$item_num++;
		}
	}
	elsif ( 'HASH' eq $ref )
	{
		$h_cart .= _cart_fmt( $item, $item_num );
	}
	else
	{
		if ( $cart->{'Request'}->{'Errors'} )
		{
			return "\t<a href=\"?m=cart\">カート表示へ戻る</a><br>";
		}
		else
		{
			return "\t現在ショッピングカートに商品はありません。<br>";
		}
	}
	chomp $h_cart;

	return <<_END_HTML;
	<form action="./" method="post">
		<input type="hidden" name="m" value="modify">
		<div align="right"><input type="image" src="skin/img/modify.png" width="52" height="17" alt="更新"></div>
		<br>
		<table class="cart_list" width="570" cellspacing="1" border="0">
		<tr>
			<th width="69%">商品名</th>
			<th width="8%">数量</th>
			<th width="8%">削除</th>
			<th width="15%">価格</th>
		</tr>
$h_cart
		<tr>
			<td colspan="3" align="right"><b>小　計</b></td>
			<td align="right"><span class="price">$cart->{'SubTotal'}->{'FormattedPrice'}</span></td>
		</tr>
		</table>
		<br>
		<table width="570" cellspacing="0" border="0">
		<tr>
			<td><a href="?m=clear"><img src="skin/img/clear.png" width="102" height="17" alt="カートのクリア"></a></td>
			<td align="right"><a href="?m=purch"><img src="skin/img/buy.png" width="70" height="20" alt="お買い上げ"></a></td>
		</tr>
		</table>
	</form>
_END_HTML
}

# カートエラー処理
sub _cart_error
{
	my $errors = shift || return;
	my $num    = 1;
	my $h_atten;

	my %E = (
		'AWS.ParameterOutOfRange' => '数量には、0～999までの数値を入力してください。',
		'AWS.ECommerceService.ExceededMaximumCartItems' => 'カートには、50点を超える商品の追加はできません。'
	);

	my @err = _err_to_array( $errors );

	foreach ( @err )
	{
		$h_atten .= $num.'.&nbsp;'.( $E{$_} || $_ ).'<br>';
		$num++;
	}

	return <<_END_HTML;
	<div class="warning">
		$h_atten
	</div>
	<br>
_END_HTML
}

# カート一覧のフォーマット
sub _cart_fmt
{
	my $item = shift;
	my $num  = shift;

	return <<_END_HTML;
		<tr>
			<td><a href="?m=lookup&amp;id=$item->{'ASIN'}">$item->{'Title'}</a></td>
			<td align="right"><input type="hidden" name="Item.$num.CartItemId" value="$item->{'CartItemId'}"><input type="text" name="Item.$num.Quantity" value="$item->{'Quantity'}" size="4" maxlength="3"></td>
			<td align="center"><input type="checkbox" name="delete.$num" value="1"></td>
			<td align="right"><span class="price">$item->{'Price'}->{'FormattedPrice'}</span></td>
		</tr>
		<tr><td colspan="4"><img src="skin/img/hr_solid.png" width="570" height="1" alt=""></td></tr>
_END_HTML
}


#-------------------------------------------------
# コンテンツを生成
sub _cont
{
	my $xml   = shift;
	my $cd    = shift;
	my $index = shift || 'Etc';
	my $f     = new File();

	my %fn = (
		'Books'      => 'con_books',
		'DVD'        => 'con_dvd',
		'Music'      => 'con_music',
		'VideoGames' => 'con_game',
		'Toys'       => 'con_toys',
		'Etc'        => 'con_top'
	);

	my %h;
	foreach ( keys %$cd )
	{
		my @asin = split( ',', $cd->{$_} );
		my $item;
		for ( my $i=0; $i < @asin; $i++ )
		{
			$item = _get_asin_item( $xml->{'Items'}, $asin[$i] );

			my $no  = $i + 1;
			my $img = _get_image( $item->{'MediumImage'} );
			my $url = '?m=lookup&amp;id='.$item->{'ASIN'};
			my $price = $item->{Offers}->{Offer}->{OfferListing}->{Price}->{FormattedPrice};
			my $release = _get_release( 'ymd', $item->{'ItemAttributes'} );

			$h{"$_$no\.ASIN"} = $item->{'ASIN'};
			$h{"$_$no\.IMAGE"} = "<a href=\"$url\">$img</a>";
			$h{"$_$no\.TITLE"} = "<a href=\"$url\">$item->{ItemAttributes}->{Title}</a>";
			$h{"$_$no\.PRICE"} = $price ? "<span class=\"price\">$price</span>" : '品切れ中';
			$h{"$_$no\.RELEASE"} = $release;
			$h{"$_$no\.MANUFACTURER"} = $item->{'ItemAttributes'}->{'Manufacturer'};
		}
	}

	my $html;
	$html =  $f->readtxt( "skin/$fn{$index}.html" );
	$html =~ s/\${([\w\.]*)}/$h{$1}/eg;

	return $html;
}


#---------------------------------------
# エラー情報の配列化
sub _err_to_array
{
	my $errors = shift;
	my $type   = shift || 'Code';
	my $error  = $errors->{'Error'};
	my @msg;

	my $ref = ref $error;

	if ( 'ARRAY' eq $ref )
	{
		foreach ( @{ $error } )
		{
			push @msg, $_->{ $type };
		}
	}
	elsif ( 'HASH' eq $ref )
	{
		push @msg, $error->{ $type };
	}

	return @msg;
}


#-------------------------------------------------
# エクスプローラ部分のメニュー作成
sub _explorer
{
	my $exp_kw = shift;
	my $exp_gp = shift;
	my $f      = new File();
	my $jc     = new Jcode();
	my %hash;

	# グループ検索データのファイル名を取得
	my %gp_file = (
		'Books'      => 'exp_books',
		'DVD'        => 'exp_dvd',
		'Music'      => 'exp_music',
		'VideoGames' => 'exp_game',
		'Toys'       => 'exp_toys'
	);
	my $fname = $gp_file{ $exp_gp->{'index'} } || 'exp_top';

	# キーワード検索
	$hash{'VAL_KEYWORDS'} = $exp_kw->{'Keywords'};
	$hash{'HTML_SELECT'}  = _form_search( $exp_kw->{'SearchIndex'} );

	# パラメータの連結
	my $url = '?m=search&amp;sub=exp';
	my @d   = $f->readlog( "data/$fname.dat" );
	foreach ( @d )
	{
		chomp;
		my( $key, $gp, $t, $w, $n ) = split("\t");

		my $p;
		$gp and $p .= "&amp;i=$gp";
		$w  and $p .= "&amp;w=".$jc->form_encode($w);
		$n  and $p .= "&amp;n=$n";

		$key =~ /([\w]+)\./;
		$hash{ "HTML_$1" } .= "\t\t<li><a href=\"$url$p\">$t</a></li>\n";
	}

	# グループリストの埋め込み
	my $html = $f->readtxt( "skin/$fname.html" );
	$html =~ s/\${([\w]*)}/$hash{$1}/eg;

	return $html;
}


#-------------------------------------------------
# ジャンル選択の生成
sub _form_search
{
	my $index = shift;
	my $h_select;

	my @group_key = qw(Books DVD Music VideoGames Software Toys Electronics);
	my %group_name = (
		'Books'       => '本',
		'DVD'         => 'DVD',
		'Music'       => 'ミュージック',
		'VideoGames'  => 'ゲーム',
		'Software'    => 'ソフトウェア',
		'Toys'        => 'おもちゃ＆ホビー',
		'Electronics' => '家電'
	);

	$h_select = "\t\t\t".'<option value="">ジャンル選択</option>'."\n";
	foreach ( @group_key )
	{
		$h_select .= "\t\t\t<option value=\"$_\"";
		$_ eq $index and $h_select .= ' selected="selected"';
		$h_select .= ">$group_name{$_}</option>\n";
	}
	chomp $h_select;

	return $h_select;
}


#-------------------------------------------------
# 広告データの取得
sub _get_ads
{
	my $h = shift;
	my $exp_gp = shift;

	# 上部広告の出力
	my $f = new File();
	$h->{'HTML_ADS1'} = $f->readtxt('skin/ads1.html');

	#コンテンツ内の広告を出力
#	$h->{'HTML_ADS2'} = $exp_gp->{'index'};
	$h->{'HTML_ADS2'} = '		<div align="center">' . "\n";
	$h->{'HTML_ADS2'} .= '				こちらは商品画像をクリックするだけでアマゾンの商品ページへ飛べます。<br>' . "\n";
	$h->{'HTML_ADS2'} .= "\t\t\t";

	if ( $exp_gp->{'index'} eq 'Books' )
	{
		$h->{'HTML_ADS2'} .= '<OBJECT classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab" id="Player_38249016-58e6-49cc-8276-121b9d213315"  WIDTH="600px" HEIGHT="200px"> <PARAM NAME="movie" VALUE="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F38249016-58e6-49cc-8276-121b9d213315&Operation=GetDisplayTemplate"><PARAM NAME="quality" VALUE="high"><PARAM NAME="bgcolor" VALUE="#FFFFFF"><PARAM NAME="allowscriptaccess" VALUE="always"><embed src="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F38249016-58e6-49cc-8276-121b9d213315&Operation=GetDisplayTemplate" id="Player_38249016-58e6-49cc-8276-121b9d213315" quality="high" bgcolor="#ffffff" name="Player_38249016-58e6-49cc-8276-121b9d213315" allowscriptaccess="always"  type="application/x-shockwave-flash" align="middle" height="200px" width="600px"></embed></OBJECT> <NOSCRIPT><A HREF="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F38249016-58e6-49cc-8276-121b9d213315&Operation=NoScript">Amazon.co.jp ウィジェット</A></NOSCRIPT>';
	}
	elsif ( $exp_gp->{'index'} eq 'DVD' )
	{
		$h->{'HTML_ADS2'} .= '<OBJECT classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab" id="Player_bd3f9126-270c-4044-b09c-9031f79a1d49"  WIDTH="600px" HEIGHT="200px"> <PARAM NAME="movie" VALUE="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2Fbd3f9126-270c-4044-b09c-9031f79a1d49&Operation=GetDisplayTemplate"><PARAM NAME="quality" VALUE="high"><PARAM NAME="bgcolor" VALUE="#FFFFFF"><PARAM NAME="allowscriptaccess" VALUE="always"><embed src="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2Fbd3f9126-270c-4044-b09c-9031f79a1d49&Operation=GetDisplayTemplate" id="Player_bd3f9126-270c-4044-b09c-9031f79a1d49" quality="high" bgcolor="#ffffff" name="Player_bd3f9126-270c-4044-b09c-9031f79a1d49" allowscriptaccess="always"  type="application/x-shockwave-flash" align="middle" height="200px" width="600px"></embed></OBJECT> <NOSCRIPT><A HREF="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2Fbd3f9126-270c-4044-b09c-9031f79a1d49&Operation=NoScript">Amazon.co.jp ウィジェット</A></NOSCRIPT>';
	}
	elsif ( $exp_gp->{'index'} eq 'Music' )
	{
		$h->{'HTML_ADS2'} .= '<OBJECT classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab" id="Player_265c0885-0b20-411b-af4d-3f634be835da"  WIDTH="600px" HEIGHT="200px"> <PARAM NAME="movie" VALUE="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F265c0885-0b20-411b-af4d-3f634be835da&Operation=GetDisplayTemplate"><PARAM NAME="quality" VALUE="high"><PARAM NAME="bgcolor" VALUE="#FFFFFF"><PARAM NAME="allowscriptaccess" VALUE="always"><embed src="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F265c0885-0b20-411b-af4d-3f634be835da&Operation=GetDisplayTemplate" id="Player_265c0885-0b20-411b-af4d-3f634be835da" quality="high" bgcolor="#ffffff" name="Player_265c0885-0b20-411b-af4d-3f634be835da" allowscriptaccess="always"  type="application/x-shockwave-flash" align="middle" height="200px" width="600px"></embed></OBJECT> <NOSCRIPT><A HREF="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F265c0885-0b20-411b-af4d-3f634be835da&Operation=NoScript">Amazon.co.jp ウィジェット</A></NOSCRIPT>';
	}
	elsif ( $exp_gp->{'index'} eq 'VideoGames' )
	{
		$h->{'HTML_ADS2'} .= '<OBJECT classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab" id="Player_5c6ea4b5-69c2-4b85-8e59-7847c3ea041c"  WIDTH="600px" HEIGHT="200px"> <PARAM NAME="movie" VALUE="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F5c6ea4b5-69c2-4b85-8e59-7847c3ea041c&Operation=GetDisplayTemplate"><PARAM NAME="quality" VALUE="high"><PARAM NAME="bgcolor" VALUE="#FFFFFF"><PARAM NAME="allowscriptaccess" VALUE="always"><embed src="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F5c6ea4b5-69c2-4b85-8e59-7847c3ea041c&Operation=GetDisplayTemplate" id="Player_5c6ea4b5-69c2-4b85-8e59-7847c3ea041c" quality="high" bgcolor="#ffffff" name="Player_5c6ea4b5-69c2-4b85-8e59-7847c3ea041c" allowscriptaccess="always"  type="application/x-shockwave-flash" align="middle" height="200px" width="600px"></embed></OBJECT> <NOSCRIPT><A HREF="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F5c6ea4b5-69c2-4b85-8e59-7847c3ea041c&Operation=NoScript">Amazon.co.jp ウィジェット</A></NOSCRIPT>';
	}
	elsif ( $exp_gp->{'index'} eq 'Toys' )
	{
		$h->{'HTML_ADS2'} .= '<OBJECT classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://fpdownload.macromedia.com/get/flashplayer/current/swflash.cab" id="Player_4f9a0910-3b05-43fa-95ac-f72597854771"  WIDTH="600px" HEIGHT="200px"> <PARAM NAME="movie" VALUE="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F4f9a0910-3b05-43fa-95ac-f72597854771&Operation=GetDisplayTemplate"><PARAM NAME="quality" VALUE="high"><PARAM NAME="bgcolor" VALUE="#FFFFFF"><PARAM NAME="allowscriptaccess" VALUE="always"><embed src="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F4f9a0910-3b05-43fa-95ac-f72597854771&Operation=GetDisplayTemplate" id="Player_4f9a0910-3b05-43fa-95ac-f72597854771" quality="high" bgcolor="#ffffff" name="Player_4f9a0910-3b05-43fa-95ac-f72597854771" allowscriptaccess="always"  type="application/x-shockwave-flash" align="middle" height="200px" width="600px"></embed></OBJECT> <NOSCRIPT><A HREF="http://ws.amazon.co.jp/widgets/q?ServiceVersion=20070822&MarketPlace=JP&ID=V20070822%2FJP%2Fnekozitacafe-22%2F8010%2F4f9a0910-3b05-43fa-95ac-f72597854771&Operation=NoScript">Amazon.co.jp ウィジェット</A></NOSCRIPT>';
	}
	else
	{
		$h->{'HTML_ADS2'} .= '';
	}

	$h->{'HTML_ADS2'} .= "\n";
	$h->{'HTML_ADS2'} .= '		</div>' . "\n";
}


#-------------------------------------------------
# ASIN アイテムデータの取得
sub _get_asin_item
{
	my $items = shift;
	my $asin  = shift;
	my $item;

	my $ref = ref $items->{'Item'};

	if ( 'ARRAY' eq $ref )
	{
		foreach ( @{ $items->{'Item'} } )
		{
			if ( $_->{'ASIN'} eq $asin )
			{
				$item = $_;
				last;
			}
		}
	}
	elsif ( 'HASH' eq $ref )
	{
		$item = $items->{'Item'};
	}

	return $item;
}


#-------------------------------------------------
# 画像の取得
sub _get_image
{
	my $img = shift;

	if ( $img )
	{
		return "<img src=\"$img->{URL}\" width=\"$img->{Width}\" height=\"$img->{Height}\" alt=\"\">";
	}
	else
	{
		return '<img src="skin/img/noimage.png" width="60" height="60" alt="no&nbsp;image">';
	}
}


#-------------------------------------------------
# ソート名を共通化
sub _get_sort_comm
{
	my $r = shift;

	my %sort_comm = (
		'salesrank'      => 'sales',
		'pricerank'      => 'price',
		'price'          => 'price',
		'titlerank'      => 'title',
		'daterank'       => 'release',
		'-orig-rel-date' => 'release',
		'-releasedate'   => 'release'
	);

	return $sort_comm{ $r->{'Sort'} };
}


#-------------------------------------------------
# 発売日の取得
sub _get_release
{
	my $fmt  = shift;
	my $attr = shift;

	my $date = $attr->{'ReleaseDate'} || $attr->{'PublicationDate'};

	if    ( 'ymd' eq $fmt ) { $date =~ tr/\-/\//;  return $date; }
	elsif ( 'y'   eq $fmt ) { $date =~ /(^[\d]+)/; return $1; }
}


#-------------------------------------------------
# 商品リストを生成
sub _search
{
	my $xml   = shift;
	my $items = $xml->{'ItemSearchResponse'}->{'Items'};
	my $h_list;

	# ソート・インデックスの作成
	my $h_sort = _sort( $items->{'Request'}->{'ItemSearchRequest'} );

	# 商品リストの作成
	my $item = $items->{'Item'};
	if ( 'ARRAY' eq ref $item )
	{
		foreach ( @{ $item } )
		{
			$h_list .= __search_fmt( $_ );
		}
	}
	elsif ( 'HASH' eq ref $item )
	{
		$h_list .= __search_fmt( $item );
	}
	else
	{
		$h_list .= _search_error( $items->{'Request'}->{'Errors'} );
	}

	# ページ・インデックスの作成
	my $h_pindex = _page_index( $items );

	return <<_END_HTML;
	<h2>
		<img src="skin/img/search.png" width="14" height="14" alt="search">
		&quot;$items->{Request}->{ItemSearchRequest}->{Keywords}&quot;
	</h2>
$h_sort
	<br>
	<table width="100%" cellspacing="0" border="0">
$h_list
	</table>
	<br>
$h_pindex
_END_HTML
}

# 検索エラー処理
sub _search_error
{
	my $errors   = shift || return;
	my $num      = 1;
	my $h_atten;

	my %E = (
		'AWS.ECommerceService.NoExactMatches' => '検索結果：&nbsp;&quot;該当する商品がありませんでした。'
	);

	my @err = _err_to_array( $errors );

	foreach ( @err )
	{
		$h_atten .= $num.'.&nbsp;'.( $E{$_} || $_ ).'<br>';
		$num++;
	}

	return <<_END_HTML;
	<div class="warning">
		$h_atten
	</div>
	<br>
_END_HTML
}

# 商品リストページのフォーマット
sub __search_fmt
{
	my $item    = shift;

	my $img     = _get_image( $item->{'SmallImage'} );
	my $creator = _arraycat( '、', $item->{'ItemAttributes'}->{'Creator'}, 4 );
	my $addr    = '?m=lookup&amp;id='.$item->{'ASIN'};

	# クリエイタ情報が無ければ、発売元を表示
	$creator or $creator = $item->{'ItemAttributes'}->{'Manufacturer'};

	# 発売日の取得
	my $release = _get_release( 'ymd', $item->{'ItemAttributes'} );

	# 価格情報
	my $price;
	if ( $_ = $item->{'Offers'}->{'Offer'}->{'OfferListing'} )
	{
		$price = '価格：&nbsp;<span class="price">'.$_->{Price}->{FormattedPrice}.'</span>&nbsp;(税込み)';
	}
	else
	{
		$price = '品切れ中です';
	}

	return <<_END_HTML;
	<tr>
		<td width="100" valign="top">
			<a href="$addr">$img</a>
		</td>
		<td width="470" valign="top">
			<table width="100%" cellspacing="0" border="0">
			<tr>
				<td>
					<a href="$addr"><span class="list_title">$item->{ItemAttributes}->{Title}</span></a>&nbsp;
					(<span class="group">$item->{ItemAttributes}->{Binding}</span>)<br>
					<span class="creator">$creator</span><br>
				</td>
			</tr>
			<tr><td><img src="skin/img/hr_solid.png" width="470" height="1" alt=""></td></tr>
			<tr>
				<td>
					$price&nbsp;&nbsp;｜&nbsp;&nbsp;発売日：&nbsp;$release<br>
				</td>
			</tr>
			</table>
		</td>
	</tr>
	<tr><td colspan="2"><img class="hr" src="skin/img/hr_l.png" width="570" height="1" alt=""></td></tr>
_END_HTML
}


#-------------------------------------------------
# 商品詳細ページを生成
sub _lookup
{
	my $xml  = shift;
	my $item = $xml->{'ItemLookupResponse'}->{'Items'}->{'Item'};
	my $html;

	$html  = _lookup_summary( $item );
	$html .= _lookup_ditail( $item );
	$html .= _lookup_review( $item->{'EditorialReviews'}->{'EditorialReview'} );
	$html .= _lookup_tracks( $item->{'Tracks'} );
	$html .= _lookup_similar( $item->{'SimilarProducts'}->{'SimilarProduct'} );
	chomp $html;

	return $html;
}

# 商品の詳細
sub _lookup_ditail
{
	my $item = shift;
	my $attr = $item->{'ItemAttributes'};
	my $gr   = $attr->{'ProductGroup'};
	my $h_ditail;

	# 発売日の取得
	my $release = _get_release( 'ymd', $attr );

	# フォーマットの取得
	my $format = _arraycat( ',', $attr->{'Format'} );

	# ジャンル別詳細
	if ( 'Books' eq $gr )
	{
		$h_ditail .= "\t<tr><th>$attr->{Binding}</th><td>$attr->{NumberOfPages}ページ</td></tr>\n";
		$h_ditail .= "\t<tr><th>出版社</th><td>$attr->{Publisher}</td></tr>\n";
	}
	elsif ( 'DVD' eq $gr )
	{
		$h_ditail .= "\t<tr><th>メディア</th><td>$attr->{Binding}</td></tr>\n";
		$h_ditail .= "\t<tr><th>ディスク枚数</th><td>$attr->{NumberOfDiscs}枚</td></tr>\n";
		$h_ditail .= "\t<tr><th>リージョンコード</th><td>$attr->{RegionCode}</td></tr>\n";
		$h_ditail .= "\t<tr><th>発売元</th><td>$attr->{Manufacturer}</td></tr>\n";
	}
	elsif ( 'Music' eq $gr )
	{
		$h_ditail .= "\t<tr><th>$attr->{Binding}</th><td>$format</td></tr>\n";
		$h_ditail .= "\t<tr><th>ディスク枚数</th><td>$attr->{NumberOfDiscs}枚</td></tr>\n";
		$h_ditail .= "\t<tr><th>レーベル</th><td>$attr->{Label}</td></tr>\n";
	}
	elsif ( 'VideoGames' eq $gr )
	{
		$h_ditail .= "\t<tr><th>プラットフォーム</th><td>$attr->{Platform}</td></tr>\n";
		$h_ditail .= "\t<tr><th>メーカー</th><td>$attr->{Brand}</td></tr>\n";
	}
	elsif ( 'Software' eq $gr )
	{
		$h_ditail .= "\t<tr><th>OS</th><td>$attr->{Platform}</td></tr>\n";
		$h_ditail .= "\t<tr><th>メディア</th><td>$attr->{Binding}</td></tr>\n";
		$h_ditail .= "\t<tr><th>対象</th><td>$format</td></tr>\n";
		$h_ditail .= "\t<tr><th>メーカー</th><td>$attr->{Brand}</td></tr>\n";
	}
	elsif ( 'Toys' eq $gr or 'Hobbies' eq $gr )
	{
		$h_ditail .= "\t<tr><th>分類</th><td>$attr->{Binding}</td></tr>\n";
		$h_ditail .= "\t<tr><th>製造元</th><td>$attr->{Manufacturer}</td></tr>\n";
		$h_ditail .= "\t<tr><th>モデル</th><td>$attr->{Model}</td></tr>\n";
	}
	elsif ( 'Electronics' eq $gr )
	{
		$h_ditail .= "\t<tr><th>メディア</th><td>$attr->{Binding}</td></tr>\n";
		$h_ditail .= "\t<tr><th>メーカー</th><td>$attr->{Brand}</td></tr>\n";
	}
	chomp $h_ditail;

	return <<_END_HTML;
	<hr noshade="noshade" size="1">
	<h2>商品の詳細</h2>
	<br>
	<table class="ditail" cellspacing="2" border="0">
$h_ditail
	<tr><th>発売日</th><td>$release</td></tr>
	<tr><th>ASIN</th><td>$item->{ASIN}</td></tr>
	<tr><th>売上ランキング</th><td>$item->{SalesRank}位</td></tr>
	</table>
	<br>
_END_HTML
}

# 商品の紹介文
sub _lookup_review
{
	my $review = shift || return;
	my $h_rev;

	my $ref = ref $review;

	if ( 'ARRAY' eq $ref )
	{
		foreach ( @{ $review } )
		{
			$_->{'Content'} =~ s/\&lt\;br\&gt\;/<br>/g;

			$h_rev .= "\t\t<b>$_->{Source}</b><br>\n";
			$h_rev .= "\t\t$_->{Content}\n";
		}
	}
	elsif ( 'HASH' eq $ref )
	{
			$review->{'Content'} =~ s/\&lt\;br\&gt\;/<br>/g;

			$h_rev .= "\t\t<b>$review->{Source}</b><br>\n";
			$h_rev .= "\t\t$review->{Content}\n";
	}
	chomp $h_rev;

	return <<_END_HTML;
	<hr noshade="noshade" size="1">
	<h2>商品の紹介文</h2>
	<div>
$h_rev
	</div>
	<br>
_END_HTML
}

# 類似商品
sub _lookup_similar
{
	my $similar = shift || return;
	my $list;

	my $ref = ref $similar;

	if ( 'ARRAY' eq $ref )
	{
		foreach ( @{ $similar } )
		{
			$list .= "\t\t<li><a href=\"?m=lookup&amp;id=$_->{ASIN}\">$_->{Title}</a></li>\n";
		}
	}
	elsif ( 'HASH' eq $ref )
	{
		$list = "\t\t<li><a href=\"?m=lookup&amp;id=$similar->{ASIN}\">$similar->{Title}</a></li>\n";
	}
	chomp $list;

	return <<_END_HTML;
	<hr noshade="noshade" size="1">
	<h2>この商品を買った人はこんな商品も買っています</h2>
	<br>
	<ul>
$list
	</ul>
	<br>
_END_HTML
}

# 商品の概要
sub _lookup_summary
{
	my $item = shift;
	my $attr = $item->{'ItemAttributes'};

	# クリエイタ情報
	my $creator = _arraycat( '', $attr->{'Creator'}, 1 );

	# 商品画像
	my $url   = $item->{'LargeImage'}->{'URL'};
	my $h_img = _get_image( $item->{'MediumImage'} );
	if ( $item->{'MediumImage'} )
	{
		$h_img = "<a href=\"$url\">$h_img</a><br><a href=\"$url\">イメージを拡大</a>";
	}

	# 商品情報
	my $info;
	if ( $_ = $item->{'Offers'}->{'Offer'}->{'OfferListing'} )
	{
		$info  = "$attr->{Manufacturer}<br>";
		$info .= "<b>価格</b>：&nbsp;<span class=\"price\">$_->{Price}->{FormattedPrice}</span><br>";
		$info .= "<br>";
		$info .= "<b>発送可能時期</b>：&nbsp;$_->{Availability}<br>";
		$info .= "<br>";
		$info .= '<a href="?m=add&amp;Item.1.ASIN='.$item->{'ASIN'}.'&amp;Item.1.Quantity=1"><img src="skin/img/cartin.png" width="100" height="20" alt="カゴに入れる"></a>';
	}
	else
	{
		$info = '品切れ中です。';
	}

	return <<_END_HTML;
	<span class="look_title">$attr->{Title}&nbsp;[$attr->{Binding}]</span><br>
	<span class="creator">$creator</span><br>
	<br>
	<table cellspacing="5" border="0">
	<tr>
		<td align="center">$h_img</td>
		<td valign="top">$info</td>
	</tr>
	</table>
	<br>
_END_HTML
}

# 曲目リスト
sub _lookup_tracks
{
	my $tracks = shift || return;
	my $track  = 1;
	my $h_tracks;

	my $ref = ref $tracks->{'Disc'};

	if ( 'ARRAY' eq $ref )
	{
		my $disc = 1;

		foreach ( @{ $tracks->{'Disc'} } )
		{
			$ref = ref $_->{'Track'};

			$h_tracks .= "\t<tr><td class=\"disc\" colspan=\"2\">ディスク$disc</td></tr>\n";

			if ( 'ARRAY' eq $ref )
			{
				foreach ( @{ $_->{'Track'} } )
				{
					$h_tracks .= &_lookup_track_fmt( $track, $_ );
					$track++;
				}
			}
			elsif ( '' eq $ref )
			{
				$h_tracks .= &_lookup_track_fmt( $track, $_->{'Track'} );
			}
			$h_tracks .= "\t<tr><td colspan=\"2\">&nbsp;</td></tr>\n";

			$disc++;
		}
	}
	if ( 'HASH' eq $ref )
	{
		$ref = ref $tracks->{'Disc'}->{'Track'};

		if ( 'ARRAY' eq $ref )
		{
			foreach ( @{ $tracks->{'Disc'}->{'Track'} } )
			{
				$h_tracks .= &_lookup_track_fmt( $track, $_ );
				$track++;
			}
		}
		elsif ( '' eq $ref )
		{
			$h_tracks .= &_lookup_track_fmt( $track, $tracks->{'Disc'}->{'Track'} );
		}
	}
	chomp $h_tracks;

	return <<_END_HTML;
	<hr noshade="noshade" size="1">
	<h2>収録曲</h2>
	<br>
	<table class="tracks" width="400" cellspacing="0" border="0">
$h_tracks
	</table>
	<br>
_END_HTML
}

# トラック情報のフォーマット化
sub _lookup_track_fmt
{
	my $track = shift;
	my $title = shift;
	my $color = ( $track % 2 ) ? '1' : '2';

	return <<_END_HTML;
	<tr class="track_color$color">
		<td width="30">$track\.</td><td width="370">$title</td>
	</tr>
_END_HTML
}


#-------------------------------------------------
# ページ・インデックスの出力
sub _page_index
{
	my $items = shift || return;
	my $r     = $items->{'Request'}->{'ItemSearchRequest'};
	my $jcode = new Jcode();
	my $h_pindex;
	my $h_prev;
	my $h_next;
	my $h_prev_to;
	my $h_next_to;

	# 検索パラメータの設定
	my %param = (
		'w' => $r->{'Keywords'},
		'i' => $r->{'SearchIndex'},
		'n' => $r->{'BrowseNode'},
		's' => _get_sort_comm( $r )
	);
	my $this = $r->{'ItemPage'} || 1;

	# エンコード処理
	$param{'w'} = $jcode->form_encode( $param{'w'} );

	# パラメータの連結
	my $url = '?m=search';
	foreach ( sort keys %param )
	{
		$param{$_} ne '' and $url .= "&amp;$_=$param{$_}";
	}

	# 最大ページ数の算出
	my $pages;
	my $smap = $items->{'SearchResultsMap'}->{'SearchIndex'};
	if ( 'ARRAY' eq ref $smap )
	{
		foreach ( @{ $smap } )
		{
			$_->{'Pages'} > $pages and $pages = $_->{'Pages'};
		}
	}
	else
	{
		$pages = $items->{'TotalPages'};
	}

	# インデックス範囲の制限
	my $view = 10;
	my $top;
	my $bot;
	if ( $this < $view or $view == $pages )
	{
		$top = 1;
		$bot = ( $pages < $view ) ? $pages : $view;
	}
	else
	{
		my $side = $view >> 1;
		$top = $this - $side; $top < 1      and $top = 1;
		$bot = $this + $side; $bot > $pages and $bot = $pages;
	}

	# インデックスの作成
	for ( my $i=$top; $i <= $bot; $i++ )
	{
		if ( $i == $this )
		{
			$h_pindex .= "\t\t\t<td class=\"this\">$i</td>\n";
		}
		else
		{
			$h_pindex .= "\t\t\t<td class=\"page_no\"><a href=\"$url&amp;pg=$i\">$i</a></td>\n";
		}
	}

	# prev , next リンクの付加
	$this > 1      and $h_prev = "<a href=\"$url&amp;pg=".( $this - 1 ).'">&lt;&nbsp;前へ</a>';
	$this < $pages and $h_next = "<a href=\"$url&amp;pg=".( $this + 1 ).'">次へ&nbsp;&gt;</a>';

	# 範囲外ページの有無
	$top > 1      and $h_prev_to = "<td class=\"page_no\"><a href=\"$url&amp;pg=1\">1</a></td><td>..</td>";
	$bot < $pages and $h_next_to = '<td>..</td>';

	return <<_END_HTML;
	<div align="center">
		<table class="page_index" cellspacing="5" border="0">
		<tr>
			<td class="move_page">$h_prev</td>
			$h_prev_to
$h_pindex
			$h_next_to
			<td class="move_page">$h_next</td>
		</tr>
		</table>
	</div>
_END_HTML
}


#-------------------------------------------------
# ソートの HTML を生成
sub _sort
{
	my $r     = shift || return;
	my $jcode = new Jcode();
	my $h_sort;

	$r->{'SearchIndex'} eq 'Blended' and return "<br>\n";

	# 検索パラメータの設定
	my %param = (
		'w'  => $r->{'Keywords'},
		'i'  => $r->{'SearchIndex'},
		'n'  => $r->{'BrowseNode'}
	);

	# エンコード処理
	$param{'w'} = $jcode->form_encode( $param{'w'} );

	# パラメータの連結
	my $url = '?m=search';
	foreach ( sort keys %param )
	{
		$param{$_} ne '' and $url .= "&amp;$_=$param{$_}";
	}

	my @sort_key = ( 'sales', 'price', 'title', 'release' );
	my %sort_name = (
		'sales'   => '人気順',
		'price'   => '価格順',
		'title'   => 'タイトル順',
		'release' => '発売順'
	);

	my $sort = _get_sort_comm( $r );

	foreach ( @sort_key )
	{
		if ( $_ eq $sort )
		{
			$h_sort .= "\t\t<span class=\"this\">$sort_name{$_}</span>&nbsp;\n";
		}
		else
		{
			$h_sort .= "\t\t<a href=\"$url&amp;s=$_\">$sort_name{$_}</a>&nbsp;\n";
		}
	}

	return <<_END_HTML;
	<div class="sort" align="center">
$h_sort
	</div>
_END_HTML
}


#-------------------------------------------------
# トップセラーの HTML を生成
sub _tops
{
	my $xml   = shift;
	my $items = $xml->{'ItemSearchResponse'}->{'Items'};
	my $rank  = 1;
	my $h_list;

	# 商品リストの作成
	my $item = $items->{'Item'};
	if ( 'ARRAY' eq ref $item )
	{
		foreach ( @{ $item } )
		{
			$h_list .= __tops_fmt( $_, $rank++ );
		}
	}
	elsif ( 'HASH' eq ref $item )
	{
		$h_list .= __tops_fmt( $item, $rank++ );
	}

	return <<_END_HTML;
		<div id="topseller">
			<h3><img src="skin/img/crown.png" width="11" height="12" alt="crown">$items->{Request}->{ItemSearchRequest}->{SearchIndex} Top 10</h3>
			<br>
$h_list
		</div>
_END_HTML
}

# トップセラーのフォーマット
sub __tops_fmt
{
	my $item = shift;
	my $rank = shift;
	my $img  = _get_image( $item->{'SmallImage'} );
	my $addr = '?m=lookup&amp;id='.$item->{'ASIN'};

	return <<_END_HTML;
			<table style="table-layout: fixed;" width="150" cellspacing="0" border="0">
			<tr>
				<td valign="top"><a href="$addr">$img</a></td>
				<td valign="top">
					<span class="rank">$rank.</span><a href="$addr">$item->{ItemAttributes}->{Title}</a><br>
					<span class="price">$item->{Offers}->{Offer}->{OfferListing}->{Price}->{FormattedPrice}</span><br>
				</td>
			</tr>
			</table>
			<br>
_END_HTML
}


#-------------------------------------------------
# HTML ページの共通処理
sub _html
{
	my $hash   = shift;
	my $exp_kw = shift;
	my $exp_gp = shift;
	my $f      = new File();
	my $html;

	# 広告データの取得
	_get_ads( $hash, $exp_gp );

	# エクスプローラ・ソースの作成
	$hash->{'HTML_EXPLORER'} = _explorer( $exp_kw, $exp_gp );

	$hash->{'VAL_KEYWORDS'} = $exp_kw->{'Keywords'};
	$hash->{'HTML_SELECT'}  = _form_search( $exp_kw->{'SearchIndex'} );

	# オリジナル変数の挿入
	$html =  $f->readtxt('skin/top.html');
	$html =~ s/\${([\w]*)}/$hash->{$1}/eg;

	print "Content-Type: text/html; charset=UTF-8\n";
#	print "Pragma: no-cache\n";
#	print "Cache-Control: no-cache\n";
	print "\n";
	print $html;
}


#-------------------------------------------------
# カートを見るページの出力
sub cart
{
	my $self   = shift;
	my $xml    = shift;
	my $file   = new File();
	my $cookie = new Cookie();
	my $rkey   = (keys %{ $xml->{'cart'} })[0];
	my $cart   = $xml->{'cart'}->{ $rkey }->{'Cart'};

	my $h_atte = _cart_error( $cart->{'Request'}->{'Errors'} );
	my $h_cart = _cart( $cart );
	my $h_tops = _tops( $xml->{'tops'} );

	# カートのHTMLソースを作成
	$_    = $file->readtxt('skin/cart.html');
	my %F = (
		'HTML_ATTENTION' => $h_atte,
		'HTML_CART'      => $h_cart
	 );
	s/\${([\w]*)}/$F{$1}/eg;
	$h_cart = $_;

	# コンテンツの挿入
	undef %F;
	my %F = (
		'HTML_CONTENTS'  => $h_cart,
		'HTML_TOPSELLER' => $h_tops
	);

	# クッキーの保存
	if ( $cart->{'CartId'} )
	{
		$cookie->set( 'cart_id', $cart->{'CartId'}, '90' );
		$cookie->set( 'hmac',    $cart->{'HMAC'},   '90' );
	}

	_html( \%F );
}


#-------------------------------------------------
# コンテンツページの出力
sub contents
{
	my $self  = shift;
	my $xml   = shift;
	my $cd    = shift;
	my $index = shift;

	my $h_look = _cont( $xml->{'look'}->{'ItemLookupResponse'}, $cd, $index );
	my $h_tops = _tops( $xml->{'tops'} );

	my %F = (
		'HTML_CONTENTS'  => $h_look,
		'HTML_TOPSELLER' => $h_tops
	);

	my %exp_gp = ( 'index' => $index );

	_html( \%F, {}, \%exp_gp );
}


#-------------------------------------------------
# カートが空のページを出力
sub empty
{
	my $self = shift;
	my $xml  = shift;
	my $f    = new File();

	my $h_cart = _cart();
	my $h_tops = _tops( $xml->{'tops'} );

	# カートのHTMLソースを作成
	$_    = $f->readtxt('skin/cart.html');
	my %F = ( 'HTML_CART' => $h_cart );
	s/\${([\w]*)}/$F{$1}/eg;
	$h_cart = $_;

	# コンテンツの挿入
	undef %F;
	my %F = (
		'HTML_CONTENTS'  => $h_cart,
		'HTML_TOPSELLER' => $h_tops
	);

	_html( \%F );
}


#-------------------------------------------------
# ヘルプページの出力
sub help
{
	my $self  = shift;
	my $xml   = shift;
	my $fname = shift;
	my $f     = new File();

	my $h_look = $f->readtxt("skin/$fname.html");
	my $h_tops = _tops( $xml->{'tops'} );

	my %F = (
		'HTML_CONTENTS'  => $h_look,
		'HTML_TOPSELLER' => $h_tops
	);

	_html( \%F );
}


#-------------------------------------------------
# 商品詳細ページの出力
sub lookup
{
	my $self = shift;
	my $xml  = shift;

	my $h_look = _lookup( $xml->{'look'} );
	my $h_tops = _tops( $xml->{'tops'} );

	my %F = (
		'HTML_CONTENTS'  => $h_look,
		'HTML_TOPSELLER' => $h_tops
	);

	_html( \%F );
}


#-------------------------------------------------
# 検索ページの出力
sub search
{
	my $self  = shift;
	my $xml   = shift;
	my $r    = $xml->{'items'}->{'ItemSearchResponse'}->{'Items'}->{'Request'}->{'ItemSearchRequest'};

	my $h_items = _search( $xml->{'items'} );
	my $h_tops  = _tops( $xml->{'tops'} );

	my %F = (
		'HTML_CONTENTS'  => $h_items,
		'HTML_TOPSELLER' => $h_tops
	);

	my %exp_gp = ( 'index' => $r->{'SearchIndex'} );

	_html( \%F, $r, \%exp_gp );
}


1;
