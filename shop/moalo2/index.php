<?php
// テスト用パラメータ
if (empty($_SERVER['HTTP_HOST'])) {$_SERVER['HTTP_HOST'] = '';}
if (empty($_SERVER['REQUEST_METHOD'])) {
//	$_GET['m']='lookup';
//	$_GET['i']='Books';
//	$_GET['w']='メイド';
//	$_GET['item']='4829139021';
	$_SERVER['HTTP_REFERER']='https://www.google.co.jp/search?hl=ja&q=%E7%8C%AB%E8%88%8C%E3%80%80%E5%90%8C%E4%BA%BA&lr=lang_ja#hl=ja&lr=lang_ja&q=%E7%8C%AB%E8%88%8C+%E5%90%8C%E4%BA%BA&tbs=lr:lang_1ja';
}

if (!empty($_GET['m'])) {
	if ($_GET['m'] === 'search') {
		if ($_GET['i'] === 'All' && empty($_GET['w'])) {
			include('./top.php');
		} else {
			include('./search.php');
		}
	} elseif ($_GET['m'] === 'lookup')  {
		include('./lookup.php');
	} elseif ($_GET['m'] === 'CartAdd') {
		include('./cart.php');
	} elseif ($_GET['m'] === 'CartGet') {
		include('./cart.php');
	} elseif ($_GET['m'] === 'CartModify') {
		include('./cart.php');
	} else {
		include('./top.php');
	}
} else {
		include('./top.php');
}

//include('./access.php');
?>
