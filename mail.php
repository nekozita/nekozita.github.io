<!DOCTYPE html>
<html lang="jp">
<head>
	<meta charset="UTF-8">
	<title>送信完了</title>
	<meta name="viewport" content="width=device-width,initial-scale=1,minimum-scale=1">
	<link rel="stylesheet" href="common/style.css">
	<!-- <link rel="stylesheet" href="common/icomoon/style.css"> -->

	<!-- <script src="common/easing.js"></script> -->
	<!-- <script src="common/legacy.js"></script> -->
	<!-- <script src="common/ticker.js"></script> -->
	<!-- <script src="common/slider.js"></script> -->
</head>
<body>
	
<?php
mb_language("Japanese");
mb_internal_encoding("UTF-8");

$action=$_POST['action'];
$name=htmlspecialchars($_POST['name']);
$email=htmlspecialchars(($_POST['email']));
$comment=htmlspecialchars(($_POST['comment']));
$to='info@nekozita.com';
$subject='【猫舌メール】'.htmlspecialchars($_POST['subject']);
$message='[お名前] '.$name."\n";
$message.='[email] '.$email."\n";
$message.='[コメント]'."\n".$comment."\n\n\n";
$header='From: '.$email."\r\n";
// $header.='Reply-To: '.$email."\r\n";

if($_SERVER["REQUEST_METHOD"]=="POST"){
	$status=mb_send_mail($to, $subject, $message, $header);
	if($status){
		echo '<p class="msg">メールは正常に送信されました</p>';
		echo '<button type="button" onclick="history.go(-1)">入力フォームに戻る</button>';
	}else{
		echo '<p class="msg">メールの送信に失敗しました</p>';
	}
}
?>

</body>
</html>
