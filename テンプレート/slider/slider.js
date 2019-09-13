function Swipe(){}

var supportTouch='ontouchend' in window;
Swipe.START=supportTouch?'touchstart':'mousedown';
Swipe.MOVE=supportTouch?'touchmove':'mousemove';
Swipe.END=supportTouch?'touchend':'mouseup';

Swipe.startEvent=function(event){
	if(event.touches){
		Swipe.startX=event.touches[0].pageX;
	}else{
		Swipe.startX=event.pageX;
	}
};
Swipe.moveEvent=function(event){
	if(event.changedTouches){
		Swipe.endX=event.changedTouches[0].pageX;
	}else{
		Swipe.endX=event.pageX;
	}
	if(Swipe.getDirection()!==''){
		event.preventDefault();
	}
};
Swipe.getDirection=function(){
	if(Swipe.endX-Swipe.startX<-20){
		return 'left';
	}else if(Swipe.endX-Swipe.startX>20){
		return 'right';
	}
	return '';
}

function Slider(className){
	var sliders=document.querySelectorAll(className);

	Array.prototype.forEach.call(sliders,function(slider){
		var slideSet=slider.firstElementChild
		var slides=slideSet.children;

		var currentLeft=slideSet.style.left=0;
		var currentSlide=0;

		for(var i=0;i<slides.length;i++){
			slides[i].style.width=parseInt(100/slides.length)+'%';
		}
		slideSet.style.width=slides.length*100+'%';

		function slideAnim(){
			var slideWidth=slides[0].offsetWidth;
			var toLeft=(currentSlide*-slideWidth);

			animate(slideSet,{left:[currentLeft+'px',toLeft+'px']},{duration:500,easing:'ease',fill:'forwards'});

			currentLeft=toLeft;
		}
		var prev=slider.parentNode.querySelector(className+'-prev');
		prev.addEventListener('click',function(){
			currentSlide--;
			if(currentSlide<0){
				currentSlide=slides.length-1;
			}
			slideAnim();
		});
		var next=slider.parentNode.querySelector(className+'-next');
		next.addEventListener('click',function(){
			currentSlide++;
			if(currentSlide>slides.length-1){
				currentSlide=0;
			}
			slideAnim();
		});
		slider.addEventListener(Swipe.START,Swipe.startEvent,false);
		slider.addEventListener(Swipe.MOVE,Swipe.moveEvent,false);
		slider.addEventListener(Swipe.END,function(event){
			Swipe.moveEvent(event);
			var direction=Swipe.getDirection();
			if(direction==='left'){
				currentSlide++;
				if(currentSlide>slides.length-1){
					currentSlide=0;
				}
				slideAnim();
			}else if(direction==='right'){
				currentSlide--;
				if(currentSlide<0){
					currentSlide=slides.length-1;
				}
				slideAnim();
			}
		},false);
	});
}

function getUnit(property){
	return property.match(/\D*$/)[0];
}

function animate(element,keyframes,options){
	var begin=Date.now();
	var id=setInterval(function(){
		var current=Date.now()-begin;
		if(current>options.duration){
			clearInterval(id);
			current=options.duration;
		}
		for(var key in keyframes){
			var unit=getUnit(keyframes[key][0]);
			var v0=parseFloat(keyframes[key][0]);
			var v1=parseFloat(keyframes[key][1]);
			var t=current/options.duration;

			var EffectTiming_easing={
				'linear':Ease.linear,
				'ease':Ease.inOutCubic,
				'ease-in':Ease.inQuad,
				'ease-out':Ease.outQuad,
				'ease-in-out':Ease.inOutQuad
			};
			var f=EffectTiming_easing[options.easing];
			var value=f(current/options.duration)*(v1-v0)+v0;
			element.style[key]=value+unit;
		}
	},16);
}