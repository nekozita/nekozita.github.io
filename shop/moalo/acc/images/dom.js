var dom = new Object();
dom.core = new Object();
dom.event = new Object();
dom.ajax = new Object();
dom.misc = new Object();

/* ==================================================================
■コア
=====================================================================*/

/* ------------------------------------------------------------------
[文法]
  dom.core.removeChildNodes(node)
[説明]
  node配下の子要素すべてを削除する。
[引数]
  ・node
      要素ノードオブジェクト
[戻値]
  なし
------------------------------------------------------------------- */
dom.core.removeChildNodes = function(node) {
  while( node.hasChildNodes() ) {
    node.removeChild(node.lastChild);
  }
}

dom.core.getTextContent = function(node) {
  var text = "";
  if(! node) { return text; }
  if(typeof node.textContent != "undefined") {
    text = node.textContent;
  } else if(typeof node.innerText != "undefined") {
    text = node.innerText;
  } else if( node.hasChildNodes() ) {
    for (var i = node.childNodes.length; i--;) {
      var o = node.childNodes.item(i);
      if(o.nodeType == 3) {
        text = o.nodeValue + text;
      } else {
        text = dom.core.getTextContent(o) + text;
      }
    }
  }
  return text;
}

/* ------------------------------------------------------------------
[文法]
  dom.core.childNodes(node)
[説明]
  node配下の子要素のうち、ホワイトスペースノードを除外した要素リストを
  取り出す。
[引数]
  ・node
      要素ノードオブジェクト
[戻値]
  ホワイトスペースノードを除く子要素の配列。nodeListインタフェースを
  エミュレートし、itemメソッドを実装。
------------------------------------------------------------------- */
dom.core.childNodes = function(node) {
  /* ノードオブジェクトを格納する配列を初期化 */
  var array = new Array();
  /* nodeが与えられていなければ終了 */
  if( ! node ) { return array; }
  /* 子要素が存在していなければ終了 */
  if( ! node.hasChildNodes() ) { return array; };
  /* 子要素を取得 */
  var children = node.childNodes;
  /* 子要素をチェックし、配列に格納 */
  for( var i=0; i<children.length; i++ ) {
    /* 子要素のノードオブジェクト */
    var c = children.item(i);
    /* テキストノードかをチェック */
    if(c.nodeType == 3) {
      /* テキストを取り出す */
      var text = c.nodeValue;
      /* テキストがホワイトスペースだけから構成されていれば除外 */
      if( ! text.match("/[^\s\t\n\r]/") ) {
        continue;
      }
    }
    /* 配列に要素ノードオブジェクトを格納 */
    array.push(c);
  }
  /* nodeListのitemメソッドをエミュレート */
  array.item = function(n) {
    if(array[n]) {
      return array[n];
    } else {
      return null;
    }
  }
  /* 配列を返す */
  return array;
}

/* ------------------------------------------------------------------
[文法]
  dom.core.previousSibling(node)
[説明]
  nodeの、ホワイトスペースノードを除外した前の要素ノードを特定する。
[引数]
  ・node
      要素ノードオブジェクト
[戻値]
  ホワイトスペースノードを除く前の要素ノードオブジェクト
------------------------------------------------------------------- */
dom.core.previousSibling = function(node) {
  /* nodeが与えられていなければ終了 */
  if( ! node ) { return null; }
  /* 順次、直前のノードをチェック */
  var o = node;
  var p;
  while( p = o.previousSibling ) {
    if(p.nodeType == 3) {
      /* テキストを取り出す */
      var text = p.nodeValue;
      /* テキストがホワイトスペースだけから構成されていれば除外 */
      if( ! text.match("/[^\s\t\n\r]/") ) {
        o = p;
        continue;
      }
    }
    /* 要素ノードオブジェクトを返す */
    return p;
  }
  /* nullを返す */
  return null;
}

/* ------------------------------------------------------------------
[文法]
  dom.core.nextSibling(node)
[説明]
  nodeの、ホワイトスペースノードを除外した次の要素ノードを特定する。
[引数]
  ・node
      要素ノードオブジェクト
[戻値]
  ホワイトスペースノードを除く次の要素ノードオブジェクト
------------------------------------------------------------------- */
dom.core.nextSibling = function(node) {
  /* nodeが与えられていなければ終了 */
  if( ! node ) { return null; }
  /* 順次、直後のノードをチェック */
  var o = node;
  var p;
  while( p = o.nextSibling ) {
    if(p.nodeType == 3) {
      /* テキストを取り出す */
      var text = p.nodeValue;
      /* テキストがホワイトスペースだけから構成されていれば除外 */
      if( ! text.match("/[^\s\t\n\r]/") ) {
        o = p;
        continue;
      }
    }
    /* 要素ノードオブジェクトを返す */
    return p;
  }
  /* nullを返す */
  return null;
}

/* ==================================================================
■イベント
=====================================================================*/

/* ------------------------------------------------------------------
[文法]
  dom.event.addEventListener(elm, type, func, useCapture)
[説明]
  イベント・リスナーをセットする。
[引数]
  ・elm
      要素ノードオブジェクト
  ・type
      イベント・タイプ
  ・func
      イベント・リスナー関数（コールバック関数）の関数オブジェクト
  ・useCapture
      trueが指定されればキャプチャー・フェーズを有効にする。
      ただし、Internet Explorerでは、trueを指定しても、有効にならず、
      バブリング・フェーズとしてセットされるので、注意すること。
[戻値]
  成功すればtrueを、失敗すればfalseを返す。
------------------------------------------------------------------- */
dom.event.addEventListener = function(elm, type, func, useCapture) {
  if(! elm) { return false; }
  if(! useCapture) {
    useCapture = false;
  }
  if(elm.addEventListener) {
    elm.addEventListener(type, func, false);
  } else if(elm.attachEvent) {
    elm.attachEvent('on'+type, func);
  } else {
    return false;
  }
  return true;
};

/* ------------------------------------------------------------------
[文法]
  dom.event.removeEventListener(elm, type, func, useCapture)
[説明]
  イベント・リスナーを解除する。引数には、リスナーをセットした際に指
  定したものと、すべて同じにすること。
[引数]
  ・elm
      要素ノードオブジェクト
  ・type
      イベント・タイプ
  ・func
      イベント・リスナー関数（コールバック関数）の関数オブジェクト
  ・useCapture
      キャプチャー・フェーズ（trueもしくはfalse）
[戻値]
  成功すればtrueを、失敗すればfalseを返す。
------------------------------------------------------------------- */
dom.event.removeEventListener = function(elm, type, func, useCapture) {
  if(! elm) { return false; }
  if(! useCapture) {
    useCapture = false;
  }
  if(elm.removeEventListener) {
    elm.removeEventListener(type, func, false);
  } else if(elm.detachEvent) {
    elm.detachEvent('on'+type, func);
  } else {
    return false;
  }
  return true;
};

/* ------------------------------------------------------------------
[文法]
  dom.event.target(evt)
[説明]
  evtにセットされているイベントのイベント・ターゲットを特定する。
[引数]
  ・evt
      Eventインタフェース・オブジェクト
[戻値]
  イベント・ターゲットの要素ノードオブジェクト。イベント・ターゲット
  が判別できなかった場合はnullを返す。
------------------------------------------------------------------- */
dom.event.target = function(evt) {
  /* W3C DOM準拠ブラウザー */
  if(evt && evt.target) {
    /* Safari 1.3対策 */
    if(evt.target.nodeType == 3) {
      return evt.target.parentNode;
    } else {
      return evt.target;
    }
  /* Internet Explorer */
  } else if(window.event && window.event.srcElement) {
    return window.event.srcElement;
  /* それ以外 */
  } else {
    return null;
  }
};

/* ------------------------------------------------------------------
[文法]
  dom.event.preventDefault(evt)
[説明]
  evtにセットされているイベントのデフォルト・アクションを抑止する。
[引数]
  ・evt
      Eventインタフェース・オブジェクト
[戻値]
  なし
------------------------------------------------------------------- */
dom.event.preventDefault = function(evt) {
  /* W3C DOM準拠ブラウザー */
  if(evt && evt.preventDefault) {
    evt.preventDefault();
    /* Safari 1.3対策 */
    evt.currentTarget['on'+evt.type] = function() {return false;};
  /* Internet Explorer */
  } else if(window.event) {
    window.event.returnValue = false;
  }
};

/* ------------------------------------------------------------------
[文法]
  dom.event.stopPropagation(evt)
[説明]
  evtにセットされているイベントの伝播を抑止する。
[引数]
  ・evt
      Eventインタフェース・オブジェクト
[戻値]
  なし
------------------------------------------------------------------- */
dom.event.stopPropagation = function(evt) {
  /* W3C DOM準拠ブラウザー */
  if(evt && evt.stopPropagation) {
    evt.stopPropagation();
  /* Internet Explorer */
  } else if(window.event) {
    window.event.cancelBubble = true;
  }
};

/* ------------------------------------------------------------------
[文法]
  dom.event.drag(targetElm, dragableElm)
[説明]
  targetElmをドラッグ可能にする。dragableElmが指定されれば、その領域
  をドラッグ可能領域としてセットする。指定されなければ、targetElm全体
  がドラッグ可能領域としてセットする。
[引数]
  ・targetElm
      ドラッグの際に動かしたい領域の要素のノードオブジェクト
  ・dragableElm
      ドラッグ可能な領域の要素ノードオブジェクト（省略可）
[戻値]
  なし
------------------------------------------------------------------- */
dom.event.drag = function(targetElm, dragableElm) {
  if( ! targetElm ) { return; }
  if( ! dragableElm ) {
    dragableElm = targetElm;
  }
  /* 変数の初期化 */
  var mouseX, mouseY, targetX, targetY;
  /* ブラウザーウィンドウサイズ */
  var winSize = dom.misc.getWindowSize();
  /* -----------------------------------*/
  /* ドラッグ終了時のコールバック関数   */
  /* -----------------------------------*/
  var dragEnd = function(evt) {
    /* documentのmousemoveイベントリスナーを解除 */
    dom.event.removeEventListener(document, 'mousemove', dragMove, false);
    /* documentのmouseupイベントリスナーを解除 */
    dom.event.removeEventListener(document, 'mouseup', dragEnd, false);
    /* イベント伝播の抑止 */
    dom.event.stopPropagation(evt);
    /* デフォルト・アクションの抑止 */
    dom.event.preventDefault(evt);
  };
  /* -----------------------------------*/
  /* ドラッグ中のコールバック関数       */
  /* -----------------------------------*/
  var dragMove = function(evt) {
    /* 移動先の座標を計算 */
    var left = targetX - mouseX + evt.clientX;
    var top = targetY - mouseY + evt.clientY;
    var right = left + targetElm.offsetWidth;
    var bottom = top + targetElm.offsetHeight;
    /* 要素がブラウザー内であれば要素を移動 */
    if(
      left > 0 &&  right < winSize.width &&
      top > 0 && bottom < winSize.height
    ) {
      targetElm.style.left = left + 'px';
      targetElm.style.top  = top + 'px';
    /* 要素がブラウザーからはみ出すようであればドラッグ終了 */
    } else {
      dragEnd();
    }
    /* イベント伝播の抑止 */
    dom.event.stopPropagation(evt);
    /* デフォルト・アクションの抑止 */
    dom.event.preventDefault(evt);
  };
  /* -----------------------------------*/
  /* ドラッグ開始時のコールバック関数   */
  /* -----------------------------------*/
  var dragStart = function(evt) {
    /* ブラウザーウィンドウサイズ */
    winSize = dom.misc.getWindowSize();
    /* ドラッグ開始時のマウスの座標 */
    mouseX = evt.clientX;
    mouseY = evt.clientY;
    /* ドラッグ開始時の要素の座標 */
    targetX = targetElm.offsetLeft;
    targetY = targetElm.offsetTop;
    /* documentにmousemoveイベントリスナーをセット */
    dom.event.addEventListener(document, 'mousemove', dragMove, false);
    /* documentにmouseupイベントリスナーをセット */
    dom.event.addEventListener(document, 'mouseup', dragEnd, false);
    /* イベント伝播の抑止 */
    dom.event.stopPropagation(evt);
    /* デフォルト・アクションの抑止 */
    dom.event.preventDefault(evt);
  };
  /* -----------------------------------*/
  /* mousedownイベントリスナーをセット  */
  /* -----------------------------------*/
  dom.event.addEventListener(dragableElm, 'mousedown', dragStart, false);
}

/* ==================================================================
■Ajax
=====================================================================*/

/* ------------------------------------------------------------------
[文法]
  dom.ajax.httpGetRequest(url, callback)
[説明]
  urlにHTTP GETリクエストを送り、通信が完了したらcallback関数を実行
[引数]
  ・url
      リクエスト先URL
  ・callback
      通信が完了した時点で実行したい関数のオブジェクト。
      通信が完了すると、第一引数にXMLHttpRequestオブジェクトをセット
      します。
[戻値]
  リクエスト送信に成功すればXMLHttpRequestオブジェクトを返します。
  失敗すれば、nullを返します。
------------------------------------------------------------------- */
dom.ajax.httpGetRequest = function(url, callback, headers) {
  /* XMLHttpRequestオブジェクトを生成 */
  var oHttp = null;
  if(window.XMLHttpRequest) {
    oHttp = new XMLHttpRequest();
  } else if(window.ActiveXObject) {
    try {
      oHttp = new window.ActiveXObject("Msxml2.XMLHTTP.3.0");
    } catch(e) {
      return null;
    }
  }
  if( oHttp != null ) {
    /* HTTP GETリクエスト */
    oHttp.open('GET', url, true);
    /* リクエストヘッダーをセット */
    if( typeof(headers) == 'object' ) {
      for(var name in headers) {
        oHttp.setRequestHeader(name, headers[name]);
      }
    }
    /* 状態変化イベントのコールバック関数を定義 */
    oHttp.onreadystatechange = function() {
      if (oHttp.readyState == 4) {
        callback(oHttp);
      }
    };
    /* HTTP GETリクエスト送出 */
    oHttp.send(null);
  }
  /* oHttpを返す */
  return oHttp;
}


/* ==================================================================
■その他
=====================================================================*/

/* ------------------------------------------------------------------
[文法]
  dom.misc.getElementAbsPos(elm)
[説明]
  ブラウザー表示領域左上端を基点とした座標系としたelmの左上端の座標を、
  オブジェクトで返す。
[引数]
  ・elm
      要素ノードオブジェクト
[戻値]
  座標を格納したオブジェクト。xプロパティにX座標の値が、yプロパティに
  Y座標の値がセットされる。
------------------------------------------------------------------- */
dom.misc.getElementAbsPos = function(elm) {
    var obj = new Object();
    obj.x = elm.offsetLeft;
    obj.y = elm.offsetTop;
    while(elm.offsetParent) {
       elm = elm.offsetParent;
       obj.x += elm.offsetLeft;
       obj.y += elm.offsetTop;
    }
    return obj;
}

/* ------------------------------------------------------------------
[文法]
  dom.misc.getWindowSize()
[説明]
  ブラウザーのHTML表示領域のサイズをオブジェクトで返す。
[引数]
  なし
[戻値]
  サイズを格納したオブジェクト。widthプロパティに縦長の値が、yプロパ
  ティに横長の値がセットされる。
------------------------------------------------------------------- */
dom.misc.getWindowSize = function() {
  /* サイズを格納するオブジェクトを生成 */
  var obj = new Object();
  /* Internet Explorerの場合 */
  if( document.uniqueID ) {
    obj.width = document.documentElement.clientWidth;
    obj.height = document.documentElement.clientHeight;
  /* それ以外の場合 */
  } else {
    obj.width = window.innerWidth;
    obj.height = window.innerHeight;
  }
  /* サイズオブジェクトを返す */
  return obj;
};
