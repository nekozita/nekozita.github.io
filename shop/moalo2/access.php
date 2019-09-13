<?php
if (empty($_COOKIE['acsess'])){

	// 日付
	$logs[] = date("Y/m/d H:i:s");
	// URL
	$logs[] = $_SERVER['REQUEST_URI'];
	// ブラウザ
	$logs[] = $_SERVER['HTTP_USER_AGENT'];
	// IPアドレス
	$logs[] = $_SERVER['REMOTE_ADDR'];
	// ホスト名
	$logs[] = @gethostbyaddr($_SERVER['REMOTE_ADDR']);
	// リファラ
	$logs[] = $_SERVER['HTTP_REFERER'];
	
	// タブ区切りで文字列結合
	$acsessLog = implode("\t", $logs)."\n";

	// ログファイルの内容を取得
	$lines = file('log/acc.dat');

	$fp = @fopen('log/acc.dat', 'w') or die("ファイルを取得できません！");

	if (flock($fp, LOCK_EX)) {
		// 書き込み
		fwrite($fp, $acsessLog);
		// 50行まで登録
		if (count($lines) > 50) {
			$max_i = 50;
		} else {
			$max_i = count($lines);
		}
		for ($i = 0; $i < $max_i; $i++) {
			fwrite($fp, $lines[$i]);
		}
	}
	flock($fp, LOCK_UN);

	// 有効時間（1800）30分
	setcookie("acsess", 1, time() + 1800);
}
?>
