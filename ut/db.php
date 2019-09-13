<?php
date_default_timezone_set('Asia/Tokyo');

// ベースURLの取得
$BASE_URL = (empty($_SERVER["HTTPS"])?"http://":"https://").$_SERVER["HTTP_HOST"].$_SERVER["REQUEST_URI"];

// データベースのファイル名
$DB_FILE='t.db';
// テーブル名
$TABLE_NAME='tansyuku';
// カラム定義
$COLUMNS = array(
	"id INTEGER PRIMARY KEY AUTOINCREMENT",
	"url UNIQUE",
	"hash UNIQUE",
	"created_at default CURRENT_TIMESTAMP"
	);
// idの開始番号(START_ID=開始番号-1)
$START_ID = 99;

try{
	$db = new PDO("sqlite:$DB_FILE");
	$db->query("CREATE TABLE IF NOT EXISTS $TABLE_NAME(".implode(",",$COLUMNS).")");
	initSQLiteSequence($db);
}catch (PDOException $e){
	// PDO_SQLite
	// echo $e->getMessage();
// }catch (Exception $e){
	// SQLite3
	// echo $e->getTraceAsString();
}

// シーケンス番号の取得
function getSQLiteSequence($db){
	$result = $db->query("SELECT * FROM sqlite_sequence WHERE name='$GLOBALS[TABLE_NAME]'");
	$row = $result->fetchAll();
	if (empty($row)){
		$db->query("INSERT INTO sqlite_sequence VALUES('$GLOBALS[TABLE_NAME]',$GLOBALS[START_ID])");
		$seq = $GLOBALS['START_ID'];
	}else{
		$seq = $row[0]['seq'];
	}
	return $seq;
}
// シーケンス番号の初期設定
function initSQLiteSequence($db){
	return getSQLiteSequence($db);
}
?>