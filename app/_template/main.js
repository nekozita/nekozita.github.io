// New Game

// function hitText(rect){
// 	return tapX>=rect.x&&tapX<rect.x+rect.w&&tapY>=rect.y&&tapY<rect.y+rect.h;
// }

// エントリーポイント
app.main=function(){
	init();
	enterFrame(0);
};

// 入力処理
app.onTouch=function(event){
	updateInput(event);
	// ゲームの入力処理
};

// ゲームの初期化処理
function init(){
}

// 毎フレーム呼び出される
function enterFrame(timeStamp){
	timer=requestAnimationFrame(enterFrame);
	// ゲームの演算処理
	
	// ゲームの描画処理
	ctx.clearRect(0,0,WIDTH,HEIGHT);
}
