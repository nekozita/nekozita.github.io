<?php
include('./MyAmazon.php');

/**************************************/
// Amazon API
/**************************************/
$api = new MyAmazon(array(
	'accessKeyId'     => '0BADXS9AY5JNB6MZT682',
	'associateTag'    => 'nekozitacafe-22',
	'secretAccessKey' => 'MLZ8T+LiPEuFRXVAneZeIH/wIJv0uUO7wOoovonF',
));

if (isset($_COOKIE['cartId'])) {
	$api->setCartId($_COOKIE['cartId']);
	$api->setCartHmac($_COOKIE['cartHmac']);
}

/**************************************/
// 共通部品
/**************************************/
// トップページ用ドメイン
$domain = "http://".$_SERVER['HTTP_HOST']."/shop/moalo2/";

// ページのタイトル
$title = "MOALO 2";

// SearchIndex
$indexMenu = array(
	'All' => 'すべて',
	'Apparel' => '服&ファッション小物',
	'Appliances' => '大型家電',
	'Automotive' => '車・バイク用品',
	'Baby' => 'ベビー&マタニティ',
	'Beauty' => 'コスメ',
//	'Blended' => 'すべて',
	'Books' => '本',
	'Classical' => 'クラシック',
	'DVD' => 'DVD',
	'Electronics' => '家電&カメラ',
	'ForeignBooks' => '洋書',
	'Grocery' => '食品&飲料',
	'HealthPersonalCare' => 'ヘルス&ビューティ',
	'Hobbies' => 'ホビー',
	'HomeImprovement' => 'DIY・工具',
	'Jewelry' => 'ジュエリー',
	'KindleStore' => 'Kindleストア',
	'Kitchen' => 'ホーム&キッチン',
//	'Marketplace' => 'Amazonマーケットプレイス',
	'MobileApps' => 'モバイルアプリ',
	'MP3Downloads' => 'MP3ミュージック',
	'Music' => 'ミュージック',
	'MusicalInstruments' => '楽器',
//	'MusicTracks' => '曲名',
	'OfficeProducts' => '文房具・オフィス用品',
	'Shoes' => 'シューズ&バッグ',
	'Software' => 'PCソフト',
	'SportingGoods' => 'スポーツ&アウトドア',
	'Toys' => 'おもちゃ',
//	'VHS' => 'VHS',
//	'Video' => 'Amazonインスタント・ビデオ',
	'VideoGames' => 'TVゲーム',
	'Watches' => '腕時計',
);

// 最上位のブラウズノードID
$topBrowseNode = array(
	'Apparel'=>'361299011',
	'Appliances'=>'2277724051',
	'Automotive'=>'2017304051',
	'Baby'=>'170303011',
	'Beauty'=>'52391051',
	'Books'=>'465610',
	'Classical'=>'562032',
	'DVD'=>'562002',
	'Electronics'=>'3210991',
	'ForeignBooks'=>'52033011',
	'Grocery'=>'57239051',
	'HealthPersonalCare'=>'161669011',
	'Hobbies'=>'2277721051',
	'HomeImprovement'=>'2016930051',
	'Jewelry'=>'85896051',
	'KindleStore'=>'2250738051',
	'Kitchen'=>'3839151',
	'MobileApps'=>'2381130051',
	'MP3Downloads'=>'2128134051',
	'Music'=>'562032',
	'MusicalInstruments'=>'2123629051',
	'OfficeProducts'=>'86731051',
	'Shoes'=>'2016926051',
	'Software'=>'637630',
	'SportingGoods'=>'14304371',
	'Toys'=>'13299531',
//	'VHS'=>'2130989051 ',
//	'Video'=>'561972',
	'VideoGames'=>'637872',
	'Watches'=>'324025011',
);

/**************************************/
// ジャンル選択
/**************************************/
$optIndex = isset($_GET['i']) ? $_GET['i'] : 'All';

$indexOptions = "\n";
foreach ($indexMenu as $k=>$v) {
	if ($k === $optIndex) {
		$sel = " selected";
	} else {
		$sel = "";
	}
	$indexOptions .= "<option value=\"{$k}\"{$sel}>{$v}</option>\n";
}

/**************************************/
// ヘッダー定義
/**************************************/
$inputWord = isset($_GET['w']) ? $_GET['w'] : '';

$header = <<< TAGSET
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{$title}</title>
<link rel="stylesheet" href="base.css">
</head>
<body>
<div class="wrap">

<!--=== HEADER ===-->

<h1><a href="{$domain}"><img src="img/logo.png"></a></h1>
<div>HTML5専用で見やすくなりました！</div>

<div class="search-area">

<!--=== SEARCH INDEX ===-->
<form class="searchIndex-area" action="./" method="get">
<div>
<input type="hidden" name="m" value="search">
<select name="i">{$indexOptions}</select>
<img src="img/search.png">
<input class="keyword" type="text" name="w" value="{$inputWord}">
<input type="submit" value="検索">
</div>
</form>

<!--=== CART ===-->
<form class="cart-area" action="?" method="get">
<div>
	<input type="hidden" name="m" value="CartGet">
	<input type="submit" value="カートを見る">
</div>
</form>

<br clear="all">
</div>

<!--=== CONTENTS ===-->

<div class="contents-area">

TAGSET;

/**************************************/
// フッター定義
/**************************************/
$footer = <<< TAGSET
</div>

<!--/=== CONTENTS ===-->

<!--=== FOOTER ===-->

<hr>

<div class="footer-area">
	<div class="help-area">
		<h2>ヘルプ＆ガイド (アマゾンページ)</h2>
		<ul>
		<li><a href="http://www.amazon.co.jp/gp/help/customer/display.html/ref=footer_shiprates?ie=UTF8&nodeId=642982">配送料と配送情報</a></li>
		<li><a href="http://www.amazon.co.jp/gp/subs/primeclub/signup/main.html/ref=footer_prime">Amazonプライム</a></li>
		<li><a href="http://www.amazon.co.jp/gp/css/returns/homepage.html/ref=footer_returns">商品の返品・交換</a></li>
		<li><a href="http://www.amazon.co.jp/gp/help/customer/display.html/ref=footer_contactus?ie=UTF8&nodeId=643018">カスタマーサービスに連絡</a></li>
		</ul>
	</div>
	<address>&copy; MOALO. Affiliates by Amazon.co.jp</address>
</div>

</div>
</body>
</html>
TAGSET;

/**************************************/
// デバッグ用
/**************************************/
function DebugHTML($xmlURL) {
	return <<< TAGSET
<div class="debug"><a href="{$xmlURL}">★</a></div>


TAGSET;
}

/**************************************/
// エラーメッセージの出力
/**************************************/
function ErrorMessageHTML($errs) {
	if (empty($errs)) return '';
	
	$html = '';
	foreach ($errs->Error as $e) {
		$message = $e->Message;
		$html .= "<div>{$message}</div>\n";
	}
	return $html;
}

/**************************************/
// カートに入れるボタンの出力
/**************************************/
function CartInHTML($item) {
	$Availability = $item->Offers->Offer->OfferListing->Availability; // 在庫状況
	$OfferListingId = $item->Offers->Offer->OfferListing->OfferListingId;
	
	if (preg_match("/予約可/", $Availability)) {
		$cartButton = '<div><button class="preorder" type="submit">予約する</button></div>';
	} else if (preg_match("/在庫あり/", $Availability) || isset($OfferListingId)) {
		$cartButton = '<div><button class="cartin" type="submit">カートに入れる</button></div>';
	}else{
		return ''; // 在庫がない
	}
	
	return <<< TAGSET
<form action="?m=CartAdd" method="post">
	<div><input type="hidden" name="offer" value="{$OfferListingId}"></div>
	{$cartButton}
</form>

TAGSET;
}

/**************************************/
// 発売日の取得
/**************************************/
function GetItemReleaseDate($item) {
	if (isset($item->ItemAttributes->ReleaseDate)) {
		return $item->ItemAttributes->ReleaseDate;
	}
	if (isset($item->ItemAttributes->PublicationDate)) {
		return $item->ItemAttributes->PublicationDate;
	}
	return null;
}

/**************************************/
// ブラウズノードの出力
/**************************************/
function StackBrowseNode($node) {
	if(is_array($node)){
		foreach($node as $k=>$v){
			$ret[$k]=StackBrowseNode($v);
		}
	}else{
		if(isset($node->BrowseNode)){
			$ret["BrowseNode"]=StackBrowseNode($node->BrowseNode);
		}
		if(isset($node->Ancestors)){
			$ret["Ancestors"]=StackBrowseNode($node->Ancestors);
		}
		if(isset($node->Name)){
			$ret["$node->Name"]=$node->BrowseNodeId;
		}
	}
	return $ret;
}
function ShowBrowseNode($xml) {
	foreach ($xml->Items->Item as $item) {
		if(isset($item->BrowseNodes)){
			$stack=StackBrowseNode($item->BrowseNodes);
		}
	}
	return $stack;
}
function BrowseNodeHTML($BrowseNodes) {
	if(empty($BrowseNodes)) return '';
	
	$bnlist .= "<div>\n<ul>\n";
	foreach($item->BrowseNodes->BrowseNode as $browse){
		$node=$browse->BrowseNodeId; // ノードID
		$name=$browse->Name; // ジャンル別
		$root=$browse->IsCategoryRoot; // ルート番号
		$children=$browse->Children; // 子ノード
		
		$bnlist .= "<li>{$root}.{$name}</li>\n";
		$bnlist .= "<ul>\n";
		if(isset($children)){
			foreach($children->BrowseNode as $child){
				$node=$child->BrowseNodeId; // ノードID
				$name=$child->Name; // ジャンル別
				
				$bnlist .= "<li>+<a href=\"?m=search&i={$_POST['i']}&node={$node}\">{$name}</a></li>\n";
				unset($child);
			}
		}
		$bnlist .= "</ul>\n";
		unset($browse);
	}
	$bnlist .= "</ul>\n</div>\n";
}
?>
