<?php
// キーワード検索の定義
$searchRegular = array(
	'Google' => array(
		'BaseURL' => 'www.google.co.jp/search',
		'Keyword' => '/[?&]q=([^&]+)/',
		'Encoding' => '',
	),
	'Yahoo' => array(
		'BaseURL' => 'search.yahoo.co.jp',
		'Keyword' => '/[?&]p=([^&]+)/',
		'Encoding' => '/[?&]ei=([^&]+)/',
	),
	'MSN' => array(
		'BaseURL' => 'www.bing.com/search',
		'Keyword' => '/[?&]q=([^&]+)/',
		'Encoding' => '',
	),
);

function getsearchword($referer) {
	global $searchRegular;
	$words = array();
	
	foreach ($searchRegular as $reg) {
		if (!strpos($referer, $reg['BaseURL'])) {
			continue;
		}
		preg_match_all($reg['Keyword'], $referer, $match_all, PREG_SET_ORDER);
		
		foreach ($match_all as $match) {
			$match[1] = urldecode($match[1]);
			if ($reg['Encoding']) {
				preg_match($reg['Encoding'], $referer, $match_enc);
				$match[1] = mb_convert_encoding($match[1], "UTF-8", $match_enc[1]);
				//$match[1] = urlencode($tmp);
			}
			
			array_push($words, $match[1]);
		}
	}
	return $words;
}
?>
