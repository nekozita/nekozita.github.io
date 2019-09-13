// requestAnimationFrame対応ゲームエンジン

// グローバル変数
var WIDTH=320;
var HEIGHT=400;

// ストレージ
function loadStorage(key){
	return JSON.parse(localStorage.getItem(key));
}
function saveStorage(key,value){
	localStorage.setItem(key,JSON.stringify(value));
}

// システム

app={
	scale:1,
	main:function(){},
	onTouch:function(event){updateInput(event);},
	onMove:function(event){updateInput(event);},
	onUp:function(event){updateInput(event);}
};

window.onload=function(){
	canvas=document.getElementById("mainCanvas");
	canvas.width=WIDTH;
	canvas.height=HEIGHT;
	ctx=canvas.getContext('2d');
	ctx.save();
	setTimeout(function(){window.scrollTo(0,1)},100);
	if(hasTouchEvent=('ontouchstart' in window)){
		canvas.addEventListener('touchstart',app.onTouch,true);
		canvas.addEventListener('touchmove',app.onMove,true);
		canvas.addEventListener('touchend',app.onUp,true);
	}else{
		canvas.addEventListener('mousedown',app.onTouch,true);
		canvas.addEventListener('mousemove',app.onMove,true);
		canvas.addEventListener('mouseup',app.onUp,true);
	}
	window.onresize();
	try{
		actx=new AudioContext();
		actx.createGain=actx.createGain||actx.createGainNode;
	}catch(e){
	}
	app.main();
};

window.onresize=function(){
	var scale=window.innerHeight/HEIGHT;
	var w=WIDTH*scale;
	// キャンバスの横幅がはみ出たら
	if(w>window.innerWidth){
		// 横幅を基準に
		scale=window.innerWidth/WIDTH;
	}
	canvas.width=WIDTH*scale;
	canvas.height=HEIGHT*scale;
	app.scale=scale;
	// 以降のキャンバス描画をこのスケール値で行う
	ctx.setTransform(scale,0,0,scale,0,0);
};

// 入力

var touchX=0,moveX=0,tapX=0;
var touchY=0,moveY=0,tapY=0;
var scrollLock=false;
var isTouching=false;
function updateInput(event){
	if(event==null)return;
	if(scrollLock)event.preventDefault();
	var rect=event.target.getBoundingClientRect();

	if(event.type=="touchstart"||event.type=="mousedown"){
		if(hasTouchEvent){
			var touch=event.targetTouches[0];
			touchX=Math.round((touch.clientX-rect.left)/app.scale);
			touchY=Math.round((touch.clientY-rect.top)/app.scale);
		}else{
			touchX=Math.round((event.clientX-rect.left)/app.scale);
			touchY=Math.round((event.clientY-rect.top)/app.scale);
		}
		isTouching=true;
	}
	if(event.type=="touchmove"||event.type=="mousemove"){
		if(hasTouchEvent){
			var touch=event.targetTouches[0];
			moveX=Math.round((touch.clientX-rect.left)/app.scale);
			moveY=Math.round((touch.clientY-rect.top)/app.scale);
		}else{
			moveX=Math.round((event.clientX-rect.left)/app.scale);
			moveY=Math.round((event.clientY-rect.top)/app.scale);
		}
	}
	if(event.type=="touchend"||event.type=="mouseup"){
		if(hasTouchEvent){
			var touch=event.changedTouches[0];
			tapX=Math.round((touch.clientX-rect.left)/app.scale);
			tapY=Math.round((touch.clientY-rect.top)/app.scale);
		}else{
			tapX=Math.round((event.clientX-rect.left)/app.scale);
			tapY=Math.round((event.clientY-rect.top)/app.scale);
		}
		isTouching=false;
	}
}

// サウンド

function playBGM(buffer){
	var source=actx.createBufferSource();
	source.buffer=buffer;
	// source.connect(actx.destination);
	var gain=actx.createGain();
	source.connect(gain);
	gain.connect(actx.destination);
	// レガシーバージョン対策
	source.start=source.start||source.noteOn;
	source.stop=source.stop||source.noteOff;

	source.loop=true;
	source.start(0);
	return {source:source,gainNode:gain};
}
function playSE(buffer){
	var source=actx.createBufferSource();
	source.buffer=buffer;
	// source.connect(actx.destination);
	var gain=actx.createGain();
	source.connect(gain);
	gain.connect(actx.destination);
	// レガシーバージョン対策
	source.start=source.start||source.noteOn;
	source.stop=source.stop||source.noteOff;
	
	source.loop=false;
	source.start(0);
	return {source:source,gainNode:gain};
}
// function stopSound(source){source.stop();}
// function setVolume(gainNode,value){gainNode.gain.value=value;}

// グラフィックス

function shadowText(str,x,y){
	var color=ctx.fillStyle;
	ctx.fillStyle="#000";
	ctx.fillText(str,x+1,y+1);
	ctx.fillStyle=color;
	ctx.fillText(str,x,y);
}
function drawTextWidth(text,x,y,width){
	ctx.font="14px sans-serif";

	var textY=0;
	var tmp="";
	for(var i=0;i<text.length;i++){
		var c=text.charAt(i);
		if(c=="\n"){
			ctx.fillText(tmp,x,y+textY);
			textY+=18;
			tmp="";
			continue;
		}
		if(ctx.measureText(tmp+c).width<=width){
			tmp+=c;
		}else{
			ctx.fillText(tmp,x,y+textY);
			textY+=18;
			tmp=c;
		}
	}
	if(tmp.length>0){
		ctx.fillText(tmp,x,y+textY);
		textY+=18;
	}
}

// トランジション

function TransitionManager(){
	this.scene=transitionEmpty;
	this.isTranslating=false;
}
TransitionManager.prototype.set=function(trans){
	this.scene=trans;
	this.scene.init();
	this.isTranslating=true;
};
TransitionManager.prototype.end=function(){
	this.scene=transitionEmpty;
	this.isTranslating=false;
};

var transitionEmpty={
	init:function(){},
	update:function(timeStamp){}
};

var transition=new TransitionManager();

// フェード
function TransitionFade(duration,scene,color){
	this.duration=duration;
	this.halfDuration=duration/2;
	this.nextScene=scene;
	this.color=color;
}
TransitionFade.prototype.init=function(){
	this.phase=0;
	this.startTime=performance.now();
};
TransitionFade.prototype.update=function(timeStamp){
	var dt=(timeStamp-this.startTime)/1000;
	if(this.phase==0){
		ctx.globalAlpha=dt/this.halfDuration;
		if(dt>=this.halfDuration){
			ctx.globalAlpha=1;
			this.phase=5;
			app.scene=this.nextScene;
			this.nextScene.init();
			this.startTime=performance.now();
		}
	}else if(this.phase==5){
		ctx.globalAlpha=(this.halfDuration-dt)/this.halfDuration;
		if(dt>=this.halfDuration){
			ctx.globalAlpha=0;
			this.pase=10;
			transition.end();
		}
	}
	ctx.fillStyle=this.color;
	ctx.fillRect(0,0,WIDTH,HEIGHT);
};

// フェード(フレーム数指定版)
// function TransitionFade(duration,scene,color){
// 	this.duration=duration;
// 	this.halfDuration=duration/2|0;
// 	this.nextScene=scene;
// 	this.color=color;
// }
// TransitionFade.prototype.init=function(){
// 	this.phase=0;
// 	this.fadeCount=0;
// };
// TransitionFade.prototype.update=function(timeStamp){
// 	this.fadeCount++;
// 	if(this.fadeCount==this.halfDuration){
// 		app.scene=this.nextScene;
// 		this.nextScene.init();
// 	}
// 	if(this.fadeCount==this.duration){
// 		transition.end();
// 	}
// 	if(this.fadeCount<this.halfDuration){
// 		ctx.globalAlpha=this.fadeCount/this.halfDuration;
// 		ctx.fillStyle=this.color;
// 		ctx.fillRect(0,0,WIDTH,HEIGHT);
// 	}else if(this.fadeCount<this.duration){
// 		ctx.globalAlpha=(this.duration-this.fadeCount)/this.halfDuration;
// 		ctx.fillStyle=this.color;
// 		ctx.fillRect(0,0,WIDTH,HEIGHT);
// 	}
// };
