<?php
include('./template.php');

/**************************************/
// 初期化
/**************************************/
$contents = '';

/**************************************/
// Amazon API
/**************************************/
$xmlURL = $api->ItemLookup(array(
	'ResponseGroup' => 'Large,Reviews',
	'ItemId' => $_GET['item'],
));
$amazon_xml = $api->request($xmlURL);

/**************************************/
// コンテンツ
/**************************************/
// エラーメッセージ
$contents .= ErrorMessageHTML($amazon_xml->Items->Request->Errors);
$contents .= "<hr>\n";

// ItemLookup
foreach ($amazon_xml->Items->Item as $item) {
	$asin = $item->ASIN; // ASIN
	$detail = $item->DetailPageURL; // 商品のURL
	$image = $item->MediumImage->URL; // 画像のURL
	$image_large = $item->LargeImage->URL; // 画像のURL
	$author = $item->ItemAttributes->Author;
	$creater = $item->ItemAttributes->Creator;
	$title = $item->ItemAttributes->Title; // 商品名
	$binding = $item->ItemAttributes->Binding;
	$price = $item->ItemAttributes->ListPrice->FormattedPrice; // 価格
	$total_new = $item->OfferSummary->TotalNew; // 新品
	$total_used = $item->OfferSummary->TotalUsed; // 中古
	$avail = $item->Offers->Offer->OfferListing->Availability; // 在庫
	$offer = $item->Offers->Offer->OfferListing->OfferListingId; //出品ID
	
	$cartHTML = CartInHTML($item);
	
	$authors = array();
	if (!empty($author)) $authors[] = "{$author} (著)";
	if (!empty($creater)) $authors[] = "{$creater} ({$creater->attributes()->Role})";
	$author_html = implode(', ', $authors);
	
	$contents .= <<< TAGSET
<a href="{$image_large}"><img src="{$image}" style="float:left;"></a>
<div>
	<h2>{$title} [{$binding}]</h2>
	<div>{$author_html}</div>
	<div><span class="price">{$price}</span></div>
	<div class="item-info-sub">{$avail}</div>
	<div class="item-info-sub">新品：{$total_new} / 中古：{$total_used}</div>
	{$cartHTML}
</div>
<br clear="all">
<div>リンク：<input type="text" value="&lt;a href=&quot;{$domain}?m=lookup&item={$asin}&quot;&gt;{$title}&lt;/a&gt;" size="100" onclick="this.select();" readonly></div>
<hr>
<h2>商品の説明</h2>
<h3>{$item->EditorialReviews->EditorialReview->Source}</h3>
<div>{$item->EditorialReviews->EditorialReview->Content}</div>
<hr>
<h2>登録情報 </h2>
<dl>
<dt>EAN：</dt><dd>{$item->ItemAttributes->EAN}</dd>
<dt>ISBN：</dt><dd>{$item->ItemAttributes->ISBN}</dd>
<dt>Label：</dt><dd>{$item->ItemAttributes->Label}</dd>
<dt>Manufacturer：</dt><dd>{$item->ItemAttributes->Manufacturer}</dd>
<dt>ページ数：</dt><dd>{$item->ItemAttributes->NumberOfPages}ページ</dd>
<dt>サイズ(HLWW)：</dt><dd>{$item->ItemAttributes->PackageDimensions->Height}×{$item->ItemAttributes->PackageDimensions->Length}×{$item->ItemAttributes->PackageDimensions->Weight}×{$item->ItemAttributes->PackageDimensions->Width}</dd>
<dt>ジャンル：</dt><dd>{$item->ItemAttributes->ProductGroup}</dd>
<dt>発売日：</dt><dd>{$item->ItemAttributes->PublicationDate}</dd>
<dt>Publisher：</dt><dd>{$item->ItemAttributes->Publisher}</dd>
<dt>SKU：</dt><dd>{$item->ItemAttributes->SKU}</dd>
<dt>Studio：</dt><dd>{$item->ItemAttributes->Studio}</dd>
</dl>
<br clear="all">


TAGSET;

	if (isset($item->SimilarProducts)) {
		$similarList = <<< TAGSET
<hr>
<h2>この商品を買った人はこんな商品も買っています</h2>
<ul>


TAGSET;
		foreach ($item->SimilarProducts->SimilarProduct as $similar) {
			$title = $similar->Title;
			$asin = $similar->ASIN;
			
			$similarList .= "<li><a href=\"?m=lookup&item={$asin}\">{$title}</a></li>\n";
			unset($similar);
		}

		$contents .= <<< TAGSET
$similarList
</ul>
<hr>
<iframe src="{$item->CustomerReviews->IFrameURL}" width="100%" height="400"></iframe>


TAGSET;
	}
	unset($item);
}


echo $header;
//echo DebugHTML($xmlURL);
echo $contents;
echo $footer;
?>
