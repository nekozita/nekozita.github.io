<?php
include('./template.php');
include('./searchword.php');

/**************************************/
// 初期化
/**************************************/
$word_link = '';

$words = getsearchword($_SERVER['HTTP_REFERER']);
foreach ($words as $word) {
	$word_enc = urlencode($word);
	$word_link .= "<a href=\"?m=search&i=All&w={$word_enc}\">{$word}</a>　";
}


/**************************************/
// Amazon API ベストセラー
/**************************************/
$categorys = array_keys($topBrowseNode);
$category = $categorys[rand() % count($categorys)];

$xmlURL = $api->BrowseNodeLookup(array(
	'BrowseNodeId'=>$topBrowseNode[$category],
	'ResponseGroup'=>'TopSellers',
));
$amazon_xml = $api->request($xmlURL);

/**************************************/
// トップページの出力
/**************************************/
$best_list = '';
foreach($amazon_xml->BrowseNodes->BrowseNode->TopSellers->TopSeller as $TopSeller){
	$asin = $TopSeller->ASIN; // ASIN
	$title = $TopSeller->Title; // 品名
	
	$best_list .= "<li><a href=\"?m=lookup&item={$asin}\">{$title}</a></li>\n";
}
$best_html = <<< TAGSET
<div class="bestseller-area">
<h2>{$indexMenu[$category]} のベストセラー</h2>
<ul>
{$best_list}
</ul>
</div>

TAGSET;


echo $header;
if (!empty($word_link)) {
	echo <<< TAGSET
<div class="searchWord-area">
<h2>以下の商品をお探しですか？</h2>
{$word_link}
</div>

TAGSET;
}
echo $best_html;
//echo DebugHTML($xmlURL);
echo $footer;
?>
