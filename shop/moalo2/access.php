<?php
if (empty($_COOKIE['acsess'])){

	// ���t
	$logs[] = date("Y/m/d H:i:s");
	// URL
	$logs[] = $_SERVER['REQUEST_URI'];
	// �u���E�U
	$logs[] = $_SERVER['HTTP_USER_AGENT'];
	// IP�A�h���X
	$logs[] = $_SERVER['REMOTE_ADDR'];
	// �z�X�g��
	$logs[] = @gethostbyaddr($_SERVER['REMOTE_ADDR']);
	// ���t�@��
	$logs[] = $_SERVER['HTTP_REFERER'];
	
	// �^�u��؂�ŕ����񌋍�
	$acsessLog = implode("\t", $logs)."\n";

	// ���O�t�@�C���̓��e���擾
	$lines = file('log/acc.dat');

	$fp = @fopen('log/acc.dat', 'w') or die("�t�@�C�����擾�ł��܂���I");

	if (flock($fp, LOCK_EX)) {
		// ��������
		fwrite($fp, $acsessLog);
		// 50�s�܂œo�^
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

	// �L�����ԁi1800�j30��
	setcookie("acsess", 1, time() + 1800);
}
?>
