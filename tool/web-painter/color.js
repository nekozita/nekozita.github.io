// --------------------
// カラーピッカー
var rgb=[0,0,0];
var hsv=[0,0,0];
var rgb_slider=[],rgb_text=[];
var hsv_slider=[],hsv_text=[];

function colorInit(){
	setRGB(0,0,0);

	rgb_slider=document.getElementsByName('slider-rgb');
	rgb_text=document.getElementsByName('text-rgb');
	for(var i=0;i<3;i++){
		// rgb_slider[i]=document.getElementById('slider-rgb['+i+']');
		// rgb_text[i]=document.getElementById('text-rgb['+i+']')[i].value=this.value;
		rgb_slider[i].value=0;
		rgb_slider[i].min=0;
		rgb_slider[i].max=255;
		rgb_slider[i].oninput=function(index){
			return function(){
				rgb_text[index].value=this.value;
				rgb[index]=this.value;
				setRGB(rgb[0],rgb[1],rgb[2]);
			};
		}(i);

		rgb_text[i].value=0;
		rgb_text[i].onchange=function(index){
			return function(){
				rgb_slider[index].value=this.value;
				rgb[index]=this.value;
				setRGB(rgb[0],rgb[1],rgb[2]);
			};
		}(i);
	}

	hsv_slider=document.getElementsByName('slider-hsb');
	hsv_text=document.getElementsByName('text-hsb');
	hsv_slider[0].value=0;hsv_slider[0].min=0;hsv_slider[0].max=360;
	hsv_slider[1].value=0;hsv_slider[1].min=0;hsv_slider[1].max=100;
	hsv_slider[2].value=0;hsv_slider[2].min=0;hsv_slider[2].max=100;
	hsv_text[0].value=0;
	hsv_text[1].value=0;
	hsv_text[2].value=0;
	for(var i=0;i<3;i++){
		hsv_slider[i].oninput=function(index){
			return function(){
				hsv_text[index].value=this.value;
				hsv[index]=this.value;
				setHSV(hsv[0]/360,hsv[1]/100,hsv[2]/100);
			};
		}(i);
		hsv_text[i].onchange=function(index){
			return function(){
				hsv_slider[index].value=this.value;
				hsv[index]=this.value;
				setHSV(hsv[0]/360,hsv[1]/100,hsv[2]/100);
			};
		}(i);
	}
}

function changeTab(name){
	document.getElementById('tab1').style.display="none";
	document.getElementById('tab2').style.display="none";
	document.getElementById('tab3').style.display="none";
	document.getElementById(name).style.display="block";

	// RGBタブの更新
	for(var i=0;i<3;i++){
		rgb_slider[i].value=rgb[i];
		rgb_text[i].value=rgb[i];
	}
	// HSBタブの更新
	hsv=rgb_to_hsv(rgb[0]/255,rgb[1]/255,rgb[2]/255);
	hsv[0]=~~(hsv[0]*360);
	hsv[1]=~~(hsv[1]*100);
	hsv[2]=~~(hsv[2]*100);
	for(var i=0;i<3;i++){
		hsv_slider[i].value=hsv[i];
		hsv_text[i].value=hsv[i];
	}
}

function setRGB(r,g,b){
	var c="rgb("+[r,g,b].join(",")+")";
	ctx.fillStyle=c;
	ctx.shadowColor=c;
}

function setHSV(h,s,v){
	rgb=hsv_to_rgb(h,s,v);
	rgb[0]=~~(rgb[0]*255);
	rgb[1]=~~(rgb[1]*255);
	rgb[2]=~~(rgb[2]*255);
	setRGB(rgb[0],rgb[1],rgb[2]);
}


function hsv_to_rgb(h,s,v){
	var r=v;
	var g=v;
	var b=v;
	if(s>0){
		h*=6;
		var i=Math.floor(h);
		var f=h-i;
		switch(i){
			default:
			case 0:
				g*=1-s*(1-f);
				b*=1-s;
				break;
			case 1:
				r*=1-s*f;
				b*=1-s;
				break;
			case 2:
				r*=1-s;
				b*=1-s*(1-f);
				break;
			case 3:
				r*=1-s;
				g*=1-s*f;
				break;
			case 4:
				r*=1-s*(1-f);
				g*=1-s;
				break;
			case 5:
				g*=1-s;
				b*=1-s*f;
				break;
		}
	}
	return [r,g,b];
}

function rgb_to_hsv(r,g,b){
	var max=r>g?r:g;
	max=max>b?max:b;
	var min=r<g?r:g;
	min=min<b?min:b;
	var h=max-min;
	if(h>0){
		if(max==r){
			h=(g-b)/h;
			if(h<0){
				h+=6;
			}
		}else if(max==g){
			h=2+(b-r)/h;
		}else{
			h=4+(r-g)/h;
		}
	}
	h/=6;
	var s=max-min;
	if(max!=0){
		s/=max;
	}
	var v=max;
	return [h,s,v];
}
