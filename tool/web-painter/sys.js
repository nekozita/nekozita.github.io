// HTML5 Painterエンジン

function createCanvas(width,height){
	var newCanvas=document.createElement('canvas');
	newCanvas.width=width;
	newCanvas.height=height;
	return newCanvas;
}

app={
	main:function(){},
	onTouch:function(event){updateInput(event);},
	onMove:function(event){updateInput(event);},
	onUp:function(event){updateInput(event);}
};

window.onload=function(){
	if(hasTouchEvent=('ontouchstart' in window)){
		document.addEventListener('touchstart',app.onTouch,true);
		document.addEventListener('touchmove',app.onMove,true);
		document.addEventListener('touchend',app.onUp,true);
	}else{
		document.addEventListener('mousedown',app.onTouch,true);
		document.addEventListener('mousemove',app.onMove,true);
		document.addEventListener('mouseup',app.onUp,true);
	}
	app.main();
};

// 入力

var touchX=0,moveX=0,tapX=0;
var touchY=0,moveY=0,tapY=0;
var scrollLock=false;
var isTouching=false;
function updateInput(event){
	if(event==null)return;
	if(scrollLock)event.preventDefault();
	var rect=canvas.getBoundingClientRect();

	if(event.type=="touchstart"||event.type=="mousedown"){
		if(hasTouchEvent){
			var touch=event.targetTouches[0];
			touchX=touch.clientX-rect.left;
			touchY=touch.clientY-rect.top;
		}else{
			touchX=event.clientX-rect.left;
			touchY=event.clientY-rect.top;
		}
		if(event.target==canvas||event.target==document.documentElement){
			isTouching=true;
		}
	}
	if(event.type=="touchmove"||event.type=="mousemove"){
		if(hasTouchEvent){
			var touch=event.targetTouches[0];
			moveX=touch.clientX-rect.left;
			moveY=touch.clientY-rect.top;
		}else{
			moveX=event.clientX-rect.left;
			moveY=event.clientY-rect.top;
		}
	}
	if(event.type=="touchend"||event.type=="mouseup"){
		if(hasTouchEvent){
			var touch=event.changedTouches[0];
			tapX=touch.clientX-rect.left;
			tapY=touch.clientY-rect.top;
		}else{
			tapX=event.clientX-rect.left;
			tapY=event.clientY-rect.top;
		}
		isTouching=false;
	}
}

// ストレージ
function loadStorage(key){
	return JSON.parse(localStorage.getItem(key));
}
function saveStorage(key,value){
	localStorage.setItem(key,JSON.stringify(value));
}