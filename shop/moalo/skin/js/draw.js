/* JavaScript
  ■■■■■■■■■■■■■■■■■■■■■■■■
   「コンテンツ共用描画クラス」
    Version：1.0.0

    (C) ねこめいし.
  ■■■■■■■■■■■■■■■■■■■■■■■■
*/

// 相対パス
dir="./";


/* ■■■ 画像の先読み関数 ■■■■■■■■■■ */

function preloadImages()
{
	pImg=new Array();

	a=preloadImages.arguments;
	for (i=0;i<a.length;i++)
	{
		pImg[i]=new Image();
		pImg[i].src=a[i];
	}
}


/* ■■■ ＳＲＣ属性設定 ■■■■■■■■■■■ */

function setSRC(obj,url)
{
	if (document.getElementById(obj))
	{
		document.getElementById(obj).src=url;
	}
}
