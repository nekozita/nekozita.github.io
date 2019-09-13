/* グローバル変数の初期化 */
var inputlimit = new Object;
inputlimit.params = new Object;
/* ------------------------------------------------------------ */
/* 入力開始処理 */
/* ------------------------------------------------------------ */
inputlimit.textInputStart = function(evt) {
	var target = dom.event.target(evt);
	dom.event.addEventListener(target, 'keydown', inputlimit.textInputCheck);
	dom.event.addEventListener(target, 'keyup', inputlimit.textInputCheck);
	inputlimit.params['target'] = target;
	inputlimit.textInputCheck();
};

/* ------------------------------------------------------------ */
/* 入力終了処理
/* ------------------------------------------------------------ */
inputlimit.textInputEnd = function(evt) {
	var target = dom.event.target(evt);
	dom.event.removeEventListener(target, 'keydown', inputlimit.textInputCheck);
	dom.event.removeEventListener(target, 'keyup', inputlimit.textInputCheck);
	inputlimit.textInputCheck();
	inputlimit.params['target'] = null;
};

/* ------------------------------------------------------------ */
/* 入力文字のチェック */
/* ------------------------------------------------------------ */
inputlimit.textInputCheck = function(evt) {
	var elm = inputlimit.params['target'];
	var mt = elm.className.match(/^inputlimit_([a-z]+)$/);
	var re;
	var re_g;
	if(mt[1] == 'datetime') {
		re = /[^\d\:\/\s]/;
		re_g = /[^\d\:\/\s]/g;
	} else if(mt[1] == 'dateiso') {
		re = /[^\d\-\s]/;
		re_g = /[^\d\-\s]/g;
	} else if(mt[1] == 'date') {
		re = /[^\d\/]/;
		re_g = /[^\d\/]/g;
	} else if(mt[1] == 'time') {
		re = /[^\d\:]/;
		re_g = /[^\d\:]/g;
	} else if(mt[1] == 'num') {
		re = /[^\d]/;
		re_g = /[^\d]/g;
	} else if(mt[1] == 'alpha') {
		re = /[^a-zA-Z\-\_]/;
		re_g = /[^a-zA-Z\-\_]/g;
	} else if(mt[1] == 'alphanum') {
		re = /[^\da-zA-Z\-\_]/;
		re_g = /[^\da-zA-Z\-\_]/g;
	} else if(mt[1] == 'url') {
		re = /[^\da-zA-Z\-\_\.\&\?\%\;]/;
		re_g = /[^\da-zA-Z\-\_\.\&\?\%\;\:\/]/g;
	} else if(mt[1] == 'host') {
		re = /[^\da-zA-Z\-\_\.]/;
		re_g = /[^\da-zA-Z\-\_\.]/g;
	}
	if(! re) { return false; }
	/* 半角英数以外の文字を除外 */
	if( elm && elm.value && elm.value.match(re) ) {
		/* 数字以外の文字の位置を特定 */
		var pos = elm.value.search(re);
		/* 数字以外の文字を削除 */
		elm.value = elm.value.replace(re_g, '');
		/* カーソルの位置を変更 */
		if(elm.setSelectionRange) {
			/* Firefox,Opera,Safariの場合 */
			elm.setSelectionRange(pos,pos); 
		} else if(elm.createTextRange) {
			/* Internet Explorerの場合 */
			var range = elm.createTextRange();
			range.move('character', pos);
			range.select();
		}
	}
};

/* ------------------------------------------------------------ */
/* デフォルトアクションの抑止 */
/* ------------------------------------------------------------ */
inputlimit.forbidAction = function(evt) {
	dom.event.preventDefault(evt);
};

/* ------------------------------------------------------------ */
/* HTML文書が読み込まれたときに実行させる処理 */
/* ------------------------------------------------------------ */
inputlimit.initDocument = function() {
	/* テキストボックスのリストを取得 */
	var inputs = document.getElementsByTagName('INPUT');
	/* class属性値に'inputlimit'がセットされたテキストボックスに */
	/* イベントリスナーをセット */
	for( var i=0; i<inputs.length; i++ ) {
		var elm = inputs.item(i);
		if(elm.className.match(/^inputlimit_([a-z]+)$/)) {
			/* 入力開始時の処理 */
			dom.event.addEventListener(elm, 'focus', inputlimit.textInputStart);
			/* 入力終了時の処理 */
			dom.event.addEventListener(elm, 'blur', inputlimit.textInputEnd);
			/* 右クリックによるコンテキストメニュー表示を禁止 */
			/* （ペーストを禁止するため） */
			/* dom.event.addEventListener(elm, 'contextmenu', inputlimit.forbidAction); */
			/* ペーストの禁止（Internet Explorerのみ有効） */
			/* dom.event.addEventListener(elm, 'paste', inputlimit.forbidAction); */
			/* IME起動を禁止（Internet Explorerのみ有効） */
			elm.style.imeMode = 'disabled';
		}
	}
};

dom.event.addEventListener(window, 'load', inputlimit.initDocument);
