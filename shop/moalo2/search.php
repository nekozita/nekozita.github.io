<?php
include('./template.php');

/**************************************/
// 初期化
/**************************************/
// 検索アイテムの列数
$listCol = 2;

// 初期化
$contents = '';
$searchList = '';
$bnlist = '';

/**************************************/
// Amazonへリクエスト送信
/**************************************/

if (empty($_GET['w']) && empty($_GET['node'])) {
	$params['BrowseNode'] = $topBrowseNode[$_GET['i']];
}
if (isset($_GET['i']))    {$params['SearchIndex'] = $_GET['i'];}
if (isset($_GET['w']))    {$params['Keywords']    = $_GET['w'];}
if (isset($_GET['page'])) {$params['ItemPage']    = $_GET['page'];}
if (isset($_GET['node'])) {$params['BrowseNode']  = $_GET['node'];}
$params['ResponseGroup'] = 'Medium,Offers,BrowseNodes';

$xmlURL = $api->ItemSearch($params);
$amazon_xml = $api->request($xmlURL);

/**************************************/
// コンテンツ
// ItemSearch
// TotalResultsおよびTotalPagesは、ItemPageの値により増減する
/**************************************/
$total_results = $amazon_xml->Items->TotalResults; // 検索ヒット数

$contents .= "<div>検索結果：{$total_results}件</div>\n";

// エラーメッセージ
$contents .= ErrorMessageHTML($amazon_xml->Items->Request->Errors);
$contents .= "<hr>\n";

$i = 0;
foreach ($amazon_xml->Items->Item as $item) {
	$asin = $item->ASIN; // ASIN
	$detail = $item->DetailPageURL; // 商品のURL
	$image = $item->MediumImage->URL; // 画像のURL
	$author = $item->ItemAttributes->Author;
	$binding = $item->ItemAttributes->Binding;
	$release = $item->ItemAttributes->ReleaseDate;
	$title = $item->ItemAttributes->Title; // 商品名
	$price = $item->OfferSummary->LowestNewPrice->FormattedPrice; // 価格
	$total_new = $item->OfferSummary->TotalNew; // 新品
	$total_used = $item->OfferSummary->TotalUsed; // 中古
	$avail = $item->Offers->Offer->OfferListing->Availability; // 在庫
	$offer = $item->Offers->Offer->OfferListing->OfferListingId; //出品ID
	
	$itemdate = GetItemReleaseDate($item);
	$release_html = !empty($itemdate) ? '('.date('Y年n月j日', strtotime($itemdate)).')' : '';
	$cartHTML = CartInHTML($item);
	
	$itemList = <<< TAGSET
<div class="searchItem-area">
	<div style="height:180px;"><a href="?m=lookup&item={$asin}"><img src="{$image}"></a></div>
	<div><a href="?m=lookup&item={$asin}"><span class="item-title">{$title}</span></a> {$author} {$release_html}</div>
	<div><span class="price">{$price}</span></div>
	<div class="item-info-sub">{$avail}</div>
	<div class="item-info-sub">新品：{$total_new} / 中古：{$total_used}</div>
	{$cartHTML}
</div>

TAGSET;
	
	$searchList .= (($i != 0) && ($i % $listCol == 0) ? "<br clear=\"all\">\n<hr>\n" : "");
	$searchList .= $itemList;
	$i++;
	
	unset($item);
}

$page_html = PageIndexHTML($amazon_xml);

$contents .= <<< TAGSET
<!--=== SUB MENU ===-->
<div style="float:left; width:200px;">
&nbsp;
</div>

<!--=== 検索リスト ===-->
<div style="float:left; width:800px;">
{$searchList}
<br clear="all">
</div>

<br clear="all">
<hr>

{$page_html}


TAGSET;


echo $header;
//echo DebugHTML($xmlURL);
echo $contents;
echo $footer;


// ページング
function PageIndexHTML($xml){
	$total = $xml->Items->TotalPages; // ページ数
	$submits = '';
	
	// 開始ページ番号をセット
	$pageNo = isset($_GET['page']) ? $_GET['page'] : 1;
	
	for ($i=0; $i<$total; $i++) {
		if ($i == 10) {
			break;
		}
		$submits .= "<input type=\"submit\" name=\"page\" value=\"{$pageNo}\">\n";
		$pageNo++;
	}
	return <<< TAGSET
<!--=== PAGE INDEX ===-->

<form class="pageIndex-area" action="./" method="get">
<input type="hidden" name="m" value="search">
<input type="hidden" name="i" value="{$_GET['i']}">
<input type="hidden" name="w" value="{$_GET['w']}">
{$submits}
</form>


TAGSET;
}
?>
