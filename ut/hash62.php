<?php
$char_hash62 = array(
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
	'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
	'u', 'v', 'w', 'x', 'y', 'z',
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
	'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
	'U', 'V', 'W', 'X', 'Y', 'Z',
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
	);

// 数値から62進数ハッシュの生成
function encode_hash62($number, $char = NULL){
	global $char_hash62;
	if ($char == NULL) $char = $char_hash62;
	$hash = "";
	while ($number > 0){
		$mod = $number % 62;
		$hash = $char[$mod].$hash;
		$number = (int)($number / 62);
	}
	return $hash;
}

// 62進数ハッシュを10進数へ復元
function decode_hash62($hash, $char = NULL){
	global $char_hash62;
	if ($char == NULL) $char = $char_hash62;
	$number = 0;
	$hash_map = array_combine($char, range(0,count($char)-1));
	for ($i = 0; $i < strlen($hash); $i++){
		$digit = $hash_map[substr($hash, strlen($hash)-1-$i, 1)];
		$number += pow(62, $i) * $digit;
	}
	return $number;
}
?>