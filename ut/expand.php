<?php
include "db.php";

if (isset($_GET['hash'])){
	try{
		$stmt = $db->prepare("SELECT * FROM $TABLE_NAME WHERE hash=:hash");
		$stmt->bindParam(":hash", $_GET['hash'], PDO::PARAM_STR);
		$stmt->execute();
		$row = $stmt->fetchAll();
		$url = $row[0]['url'];
		if (!preg_match("#^(http|https)://#",$url)){
			$url = "http://$url";
		}
		header("Location: $url");
	}catch (PDOException $e){
	}
}else{
	echo "ページに遷移できませんでした";
}
unset($db);
?>