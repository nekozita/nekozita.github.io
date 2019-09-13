<?php
class MyAmazon {
	public $accessKeyId;
	public $associateTag;
	public $secretAccessKey;
	public $apiVersion;
	public $cartId;
	public $cartHmac;
	
	public function __construct($args) {
		$this->setAccessKeyId($args['accessKeyId']);
		$this->setAssociateTag($args['associateTag']);
		$this->setSecretAccessKey($args['secretAccessKey']);
		$this->baseUrl = 'http://webservices.amazon.co.jp/onca/xml';
		$this->service ='AWSECommerceService';
		$this->apiVersion = '2011-08-01';
		if (isset($args['cartId'])) {
			$this->setCartId($args['cartId']);
		}
		if (isset($args['cartHmac'])) {
			$this->setCartHmac($args['cartHmac']);
		}
	}
	
	public function setAccessKeyId($accessKeyId) {
		$this->accessKeyId = $accessKeyId;
		return $this;
	}
	
	public function getAccessKeyId() {
		return $this->accessKeyId;
	}
	
	public function setAssociateTag($associateTag) {
		$this->associateTag = $associateTag;
		return $this;
	}
	
	public function getAssociateTag() {
		return $this->associateTag;
	}
	
	public function setSecretAccessKey($secretAccessKey) {
		$this->secretAccessKey = $secretAccessKey;
		return $this;
	}
	
	public function getSecretAccessKey() {
		return $this->secretAccessKey;
	}
	
	public function setCartId($cartId) {
		$this->cartId = $cartId;
		return $this;
	}
	
	public function getCartId() {
		return $this->cartId;
	}
	
	public function setCartHmac($hmac) {
		$this->cartHmac = $hmac;
		return $this;
	}
	
	public function getCartHmac() {
		return $this->cartHmac;
	}
	
	public  function getTimeStamp() {
		return gmdate('Y-m-d\TH:i:s\Z');
	}
	
	public  function getMaxPage($pageName) {
		$maxPage = array(
			'VariationPage' => 150,
			'ReviewPage' => 20,
			'OfferPage' => 100,
			'ItemPage' => 400,
			'ProductPage' => 30,
			'ListPage' => 20,
			'ReviewPage' => 10,
			'CustomerPage' => 20,
			);
		return $maxPage[$pageName];
	}
	
	public function urlencode_rfc3986($str) {
		return str_replace('%7E', '~', rawurlencode($str));
	}
	
	public function createUrl($params = array()) {
		$params = array_merge(
			array(
				'Service' => $this->service,
				'AWSAccessKeyId' => $this->getAccessKeyId(),
				'AssociateTag' => $this->getAssociateTag(),
				'Version' => $this->apiVersion,
				'Timestamp' => $this->getTimeStamp(),
			), $params);
	    ksort($params);
	    
	    // canonical string
	    $canonical_string = '';
	    foreach ($params as $k => $v) {
	        $canonical_string .= '&'.$this->urlencode_rfc3986($k).'='.$this->urlencode_rfc3986($v);
	    }
	    $canonical_string = substr($canonical_string, 1);
	    
	    // 署名の作成
	    $parsed_url = parse_url($this->baseUrl);
	    $string_to_sign = "GET\n{$parsed_url['host']}\n{$parsed_url['path']}\n{$canonical_string}";
	    $signature = base64_encode(hash_hmac('sha256', $string_to_sign,  $this->getSecretAccessKey(), true));
	    
	    // リクエストURLの作成、末尾に署名を追加
	    $url = $this->baseUrl.'?'.$canonical_string.'&Signature='.$this->urlencode_rfc3986($signature);
	    
	    return $url;
	}
	
	// APIリクエスト
	public function request($url) {
		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, $url);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($ch, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
		$response = curl_exec($ch);
		curl_close($ch);
		
		return simplexml_load_string($response);
	}
	
	// ブラウズノード
	public function BrowseNodeLookup($params = array()) {
		return $this->createUrl(
			array_merge(
				array('Operation' => 'BrowseNodeLookup'), $params));
	}
	
	// キーワード検索
	public function ItemSearch($params = array()) {
		return $this->createUrl(
			array_merge(
				array('Operation' => 'ItemSearch'), $params));
	}
	
	// 商品閲覧
	public function ItemLookup($params = array()) {
		return $this->createUrl(
			array_merge(
				array('Operation' => 'ItemLookup'), $params));
	}
	
	// カートの作成
	public function CartCreate($params = array()) {
		return $this->createUrl(
			array_merge(
				array(
					'Operation' => 'CartCreate',
				), $params));
	}
	
	// カートに商品を追加
	public function CartAdd($params = array()) {
		return $this->createUrl(
			array_merge(
				array(
					'Operation' => 'CartAdd',
					'CartId' => $this->getCartId(),
					'HMAC' => $this->getCartHmac(),
				), $params));
	}
	
	// カート情報の取得
	public function CartGet($params = array()) {
		return $this->createUrl(
			array_merge(
				array(
					'Operation' => 'CartGet',
					'CartId' => $this->getCartId(),
					'HMAC' => $this->getCartHmac(),
				), $params));
	}
	
	// カートの消去
	public function CartClear($params = array()) {
		return $this->createUrl(
			array_merge(
				array(
					'Operation' => 'CartClear',
					'CartId' => $this->getCartId(),
					'HMAC' => $this->getCartHmac(),
				), $params));
	}
	
	// カート商品の変更
	public function CartModify($params = array()) {
		return $this->createUrl(
			array_merge(
				array(
					'Operation' => 'CartModify',
					'CartId' => $this->getCartId(),
					'HMAC' => $this->getCartHmac(),
				), $params));
	}
	
	public function f($params = array()) {
	}
}
?>
