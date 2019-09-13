<?php
include('./template.php');

/**************************************/
// 初期化
/**************************************/
$cartID = $api->getCartId();
$cartHMAC = $api->getCartHmac();

$contents = '';

/**************************************/
// Amazon API
//
// カートの有効期限
// カートの中に商品がある場合は90日間。空の場合は7日間。
// カートを変更することで有効期限がリセットされる。
/**************************************/
if (empty($_GET['m'])) {
	echo "不正なパラメータです.\n";
	return;
}
if (empty($cartID)) {
	if ($_GET['m'] === 'CartAdd') {
		$xmlURL = $api->CartCreate(array(
			'Item.1.OfferListingId' => $_POST['offer'],
			'Item.1.Quantity' => '1',
		));
		$amazon_xml = $api->request($xmlURL);
		
		// カート識別情報の保存
		$api->setCartId($amazon_xml->Cart->CartId);
		$api->setCartHmac($amazon_xml->Cart->HMAC);
		setcookie('cartId', $api->getCartId(), time() + 60*60*24*90);
		setcookie('cartHmac', $api->getCartHmac(), time() + 60*60*24*90);
	}
} else {
	if ($_GET['m'] === 'CartAdd') {
		$xmlURL = $api->CartAdd(array(
			'Item.1.OfferListingId' => $_POST['offer'],
			'Item.1.Quantity' => '1',
		));
		$amazon_xml = $api->request($xmlURL);
	} elseif($_GET['m'] === 'CartModify') {
		$xmlURL = $api->CartModify(array(
			'Item.1.CartItemId' => $_POST['cart-item'],
			'Item.1.Quantity' => $_POST['quantity'],
		));
		$amazon_xml = $api->request($xmlURL);
		setcookie('cartId', $api->getCartId(), time() + 60*60*24*90);
		setcookie('cartHmac', $api->getCartHmac(), time() + 60*60*24*90);
	} elseif($_GET['m'] === 'CartGet') {
		$xmlURL = $api->CartGet();
		$amazon_xml = $api->request($xmlURL);
	}
}

/**************************************/
// コンテンツ
// カート内容の出力
/**************************************/
// エラーメッセージ
$contents .= ErrorMessageHTML($amazon_xml->Cart->Request->Errors);
$contents .= "<hr>\n";

$total_price = $amazon_xml->Cart->SubTotal->FormattedPrice; // 合計金額
$purchase = $amazon_xml->Cart->PurchaseURL; // 購入URL

// 商品リスト
foreach ($amazon_xml->Cart->CartItems->CartItem as $item) {
	$asin = $item->ASIN; // ASIN
	$title = $item->Title; // 商品名
	$detail = $item->DetailPageURL; // 商品のURL
	$seller = $item->SellerNickname; // 出品者
	$quantity = $item->Quantity; // 数量
	$price = $item->Price->FormattedPrice; //単価
	$item_total = $item->ItemTotal->FormattedPrice; //価格
	$cart_item_id = $item->CartItemId;
	
	$cart_html = <<< TAGSET
<div>
	<div><a href="?m=lookup&id={$asin}"><span class="item-title">{$title}</span></a></div>
	<div class="item-info-sub">出品者：{$seller}</div>
	<div><span class="price">{$item_total}</span> (<span class="price">{$price}</span>)</div>
	<div>
		<form action="?m=CartModify" method="post">
		<div>
			<input type="hidden" name="cart-item" value="{$cart_item_id}">
			数量：<input class="quantity" type="text" name="quantity" value="{$quantity}" size="2">
			<input type="submit" value="更新">
		</div>
		</form>
	</div>
	
	<form action="?m=CartModify" method="post">
	<div>
		<input type="hidden" name="cart-item" value="{$cart_item_id}">
		<input type="hidden" name="quantity" value="0">
		<input type="submit" value="削除">
	</div>
	</form>
</div>
<hr>
TAGSET;
	$contents .= $cart_html;
	unset($item);
}

$contents .= "<div>合計金額：<span class=\"total-price\">{$total_price}</span></div>\n";
$contents .= '<div><a href="'.$purchase.'">購入ページへ</a></div>'."\n";


echo $header;
//echo DebugHTML($xmlURL);
echo $contents;
echo $footer;
?>
