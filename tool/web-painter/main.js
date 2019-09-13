// HTML5 Painter
/*

タブメニューの実装
http://fukafuka295.jp/hp/hp_no8.html

代表的なお絵かきソフト

フォーム部品一覧
http://write-remember.com/program/html/formparts/

筆圧感知用
<!--[if IE]>
<object id='wtPlugin' classid='CLSID:092dfa86-5807-5a94-bf3b-5a53ba9e5308'>
</object>
<![endif]--><!--[if !IE]> <-->
<object id="wtPlugin" type="application/x-wacomtabletplugin">
	<param name="onload" value="pluginLoaded" />
</object>
<!--> <![endif]-->

function hitText(rect){
	return tapX>=rect.x&&tapX<rect.x+rect.w&&tapY>=rect.y&&tapY<rect.y+rect.h;
}

*/

// キャンバスサイズ
var canvasWidth=1000;
var canvasHeight=1000;

var USE_UNDO_REDO=false; // undo/redo（注意：重い）

var selectTool="brush";

// ブラシの設定情報
var brushOption={
	size:1.5, // ブラシサイズ
	blur:10,
	hardness:0.9 // ブラシの硬さ(0〜1.0)
};

var preX=0,preY=0;


// --------------------
// エントリーポイント
app.main=function(){
	canvasArea=document.getElementById('canvasArea');
	canvasArea.style.width=canvasWidth+"px";
	canvasArea.style.height=canvasHeight+"px";
	addLayer();
	canvas=layer[selectLayer];
	ctx=canvas.getContext('2d');
	// ctx.clearRect(0,0,canvasWidth,canvasHeight);

	undoredoInit();
	uiInit();
	zoomInit();
	colorInit();
};

// --------------------
// UIのイベント処理
function uiInit(){
	document.getElementById('text-brush-size').value=brushOption.size;
	document.getElementById('text-brush-size').onchange=function(){
		brushOption.size=parseFloat(this.value);
		document.getElementById('slider-brush-size').value=brushOption.size;
	};

	document.getElementById('slider-brush-size').value=brushOption.size;
	document.getElementById('slider-brush-size').oninput=function(){
		brushOption.size=parseFloat(this.value);
		document.getElementById('text-brush-size').value=brushOption.size;
	};

	document.getElementById('text-blur-size').value=(brushOption.hardness*100).toFixed(1);
	document.getElementById('text-blur-size').onchange=function(){
		brushOption.hardness=parseFloat(this.value)/100;
		document.getElementById('slider-blur-size').value=(brushOption.hardness*100).toFixed(1);
	};

	document.getElementById('slider-blur-size').value=(brushOption.hardness*100).toFixed(1);
	document.getElementById('slider-blur-size').oninput=function(){
		brushOption.hardness=parseFloat(this.value)/100;
		document.getElementById('text-blur-size').value=(brushOption.hardness*100).toFixed(1);
	};
}
function setTool(name){
	selectTool=name;
	switch(name){
	case "brush":
		ctx.globalCompositeOperation="source-over";
		break;
	case "eraser":
		ctx.globalCompositeOperation="destination-out";
		break;
	}
}

// --------------------
// ドローイング処理
var drawing=false;
app.onTouch=function(event){
	updateInput(event);
	if(!isTouching)return;
	// ゲームの入力処理
	ctx.shadowBlur=brushOption.blur*(1-brushOption.hardness);
	startBrush();
	drawing=true;
};
app.onMove=function(event){
	updateInput(event);


	// var plugin = document.getElementById('wtPlugin');
	// var pressure = plugin.penAPI.pressure;
	// var penX=plugin.penAPI.posX;
	// var penY=plugin.penAPI.posY;

	// ドローイング処理
	if(isTouching){
		drawingBrush();
	}
	drawStatus(event);
};
app.onUp=function(event){
	updateInput(event);
	if(drawing){
		if(USE_UNDO_REDO)saveImageData();
		drawing=false;
	}
};
function startBrush(){
	var px=touchX/cvScale;
	var py=touchY/cvScale;
	var drawX=Math.round(px);
	var drawY=Math.round(py);
	ctx.beginPath();
	ctx.arc(drawX,drawY,brushOption.size,0,2*Math.PI,true);
	ctx.fill();
	preX=px;
	preY=py;
}
function drawingBrush(){
	// 補正あり
	var px=moveX/cvScale;
	var py=moveY/cvScale;
	var distance=Math.sqrt(Math.abs(px-preX)+Math.abs(py-preY));
	for(var step=0;step<distance;step+=0.1){
		var dt=step/distance;
		var drawX=Math.round((1-dt)*preX+dt*px);
		var drawY=Math.round((1-dt)*preY+dt*py);
		ctx.beginPath();
		ctx.arc(drawX,drawY,brushOption.size,0,2*Math.PI,true);
		ctx.fill();
	}
	preX=px;
	preY=py;
}
function drawStatus(event){
	var html="X:%{drawX},Y:%{drawY}";
	html=html.replace("%{drawX}",moveX);
	html=html.replace("%{drawY}",moveY);
	document.getElementById('status').innerHTML=html;
}

// --------------------
// undo/redo機能
var maxRedo=0;
var undoBuffer=[];
var undoRedoPoint=-1;
function undoredoInit(){
	if(USE_UNDO_REDO){
		saveImageData();
	}else{
		document.getElementById('undoButton').style.display="none";
		document.getElementById('redoButton').style.display="none";
	}
}
function saveImageData(){
	var imgData=ctx.getImageData(0,0,canvas.width,canvas.height);
	undoRedoPoint++;
	undoBuffer[undoRedoPoint]=imgData;
	if(maxRedo>0&&undoBuffer.length>maxRedo+1){
		undoBuffer.shift();
		undoRedoPoint--;
	}
}
function undo(){
	if(undoRedoPoint>0){
		undoRedoPoint--;
	}
	ctx.putImageData(undoBuffer[undoRedoPoint],0,0);
}
function redo(){
	if(undoRedoPoint<undoBuffer.length-1){
		undoRedoPoint++;
		ctx.putImageData(undoBuffer[undoRedoPoint],0,0);
	}
}

// --------------------
// zoomin/zoomout
var cvScale=1.0;
function zoomInit(){
	canvasScale(cvScale);
	document.getElementById('button-zoom-in').onclick=function(){
		cvScale+=0.1;
		canvasScale(cvScale);
	};
	document.getElementById('button-zoom-out').onclick=function(){
		if(cvScale>0)cvScale-=0.1;
		canvasScale(cvScale);
	};
}
function canvasScale(scale){
	var tx=canvas.width*scale/2;
	var ty=canvas.height*scale/2;
	// var prop="scale(%{scale}) translate(%{tx}px,%{ty}px)";
	var prop="scale(%{scale})";
	prop=prop.replace("%{scale}",scale);
	prop=prop.replace("%{tx}",-tx);
	prop=prop.replace("%{ty}",-ty);
	canvasArea.style.transform=prop;
	document.getElementsByName('zoom')[0].value=(scale*100).toFixed(1);
}
function changeZoom(){
	var cvScale=parseFloat((document.getElementsByName('zoom')[0].value))/100;
	canvasScale(cvScale);
}

// --------------------
// レイヤー機能
var layer=[];
var selectLayer=-1;
function addLayer(){
	var newCanvas=createCanvas(canvasHeight,canvasHeight);
	selectLayer++;
	layer.splice(selectLayer,0,newCanvas);
	canvasArea.appendChild(newCanvas);
}
function removeLayer(){
	if(layer.length>2){
		layer.splice(selectLayer,1);
		if(selectLayer==layer.length){
			selectLayer--;
		}
	}
}
