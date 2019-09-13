<?php
// URL短縮スクリプト
// 動作条件：
// ・PDO_SQLITEが動作するPHP環境
// ・.htaccessのRewriteRuleが動作すること
include "hash62.php";
include "db.php";

if (isset($_POST['url']) && strlen($url = trim($_POST['url']))){
	try{
		$stmt = $db->prepare("SELECT * FROM $TABLE_NAME WHERE url=:url");
		$stmt->bindParam(":url", $url, PDO::PARAM_STR);
		$stmt->execute();
		$shortURL="";
		if ($row = $stmt->fetchAll()){
			$shortURL = $BASE_URL.$row[0]['hash'];
		}
		if(strlen($shortURL)==0){
			$seq=getSQLiteSequence($db);
			$hash = encode_hash62($seq + 1);
			$stmt = $db->prepare("INSERT INTO $TABLE_NAME(url,hash) VALUES(:url,:hash)");
			$stmt->bindParam(":url", $url, PDO::PARAM_STR);
			$stmt->bindParam(":hash", $hash, PDO::PARAM_STR);
			$stmt->execute();
			$shortURL = $BASE_URL.$hash;
		}
	}catch (PDOException $e){
	}
}
?>
<!DOCTYPE html>
<html lang="jp">
<head>
	<meta charset="UTF-8">
	<title>URL短縮</title>
	<style>
	/*リセッター*/
	body{margin:0;padding:0;}

	/*フォントサイズ*/
	body           {font-size: medium;}
	input          {font-size: x-large;}
	button         {font-size: x-large;}
	#header        {font-size: small;}
	#footer        {font-size: small;}
	.attention     {font-size: small;}

	body{
		background-color: #008000;
		color: #fff;
	}
	form{
		border: solid 1px #90ee90;
		margin: 50px 0 20px 0;
		padding: 80px 20px;
	}
	button{
		padding: 5px 20px;
		/*background-color: #006400; color:#fff; border-style:none;*/
	}
	#header{
		background-color: #006400;
		padding: 0 5px;
	}
	#contents{
		padding: 20px 50px;
	}
	#footer{
		border-top: solid 2px #006400;
		margin: 0;
		padding: 20px;
		text-align: center;
	}
	#copy{
		background-color: #fff;
		color: #006400;
		border: none;
	}
	.url{
		width: 80%;
	}
	.copyArea{
		padding: 0 20px 50px 20px;
	}
	.message{
		color: #ffff00;
		padding: 5px 0;
	}
	.description{
	}
	.attention{
		background-color: #006400;
		color: #00cc00;
		text-align: center;
	}
	</style>
	<script>
	window.onload = function(){
		var d = document.getElementById("copy");
		d.focus();
		d.select();
	}
	</script>
</head>
<body>
	<div id="header">
		<div>URL短縮サービス <?php echo $_SERVER["HTTP_HOST"];?></div>
	</div>
	<div id="contents">
		<div class="description">
			長いURLを短く変換することができます。<br>
			文字数制限があって、URLを貼り付けられないような場面でお役立てください。
		</div>
		<form action="" method="post">
			<div>短縮したいURLを入力してね！</div>
			<div>
				<input type="text" class="url" name="url" placeholder="http://">
				<button type="submit">短縮</button>
			</div>
		</form>
		<div class="copyArea">
<?php
if (isset($shortURL)){
	echo '<div class="message">短縮URLの作成に成功しました！</div>';
}
?>
		短縮URL : 
<?php
if (isset($shortURL)){
	echo <<<TAGSET
<input type="text" id="copy" size="30" value="$shortURL"
	readonly="readonly" onclick="this.select()">　←コピーして使ってね
TAGSET;
}
?>
		</div>
		<div class="attention">
			この短縮サービスは実験中のため、予告なく変更を加えることがあります。<br>
			短縮URLの保存期間は今のところ未定です。
		</div>
	</div>
	<div id="footer">
		<p>VERSION 1.0</p>

	</div>
</body>
</html>
<?php unset($db);?>