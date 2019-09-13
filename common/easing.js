// イージング関数
function Ease(){}
Ease.in=function(f){
	return f;
};
Ease.out=function(f){
	return function(t){
		return 1-f(1-t);
	};
};
Ease.inOut=function(f){
	return function(t){
		if(t<0.5)
			return f(2*t)/2;
		else
			return 1-f(2-2*t)/2;
	};
};
// 1次: p(t)=t
Ease.linear=function(t){
	return t;
};
// 2次: p(t)=t^2
Ease.quad=function(t){
	return t*t;
};
Ease.inQuad=Ease.in(Ease.quad);
Ease.outQuad=Ease.out(Ease.quad);
Ease.inOutQuad=Ease.inOut(Ease.quad);
// 3次: p(t)=t^3
Ease.cubic=function(t){
	return t*t*t;
};
Ease.inCubic=Ease.in(Ease.cubic);
Ease.outCubic=Ease.out(Ease.cubic);
Ease.inOutCubic=Ease.inOut(Ease.cubic);
// 4次: p(t)=t^4
Ease.quart=function(t){
	return t*t*t*t;
};
Ease.inQuart=Ease.in(Ease.quart);
Ease.outQuart=Ease.out(Ease.quart);
Ease.inOutQuart=Ease.inOut(Ease.quart);
// 5次: p(t)=t^5
Ease.quint=function(t){
	return t*t*t*t*t;
};
Ease.inQuint=Ease.in(Ease.quint);
Ease.outQuint=Ease.out(Ease.quint);
Ease.inOutQuint=Ease.inOut(Ease.quint);
// 正弦波: p(t)=sin(t×π/2)
Ease.sine=function(t){
	return 1-Math.cos(t*Math.PI/2);
};
Ease.inSine=Ease.in(Ease.sine);
Ease.outSine=Ease.out(Ease.sine);
Ease.inOutSine=Ease.inOut(Ease.sine);
// 指数: p(t)=2^10(t-1)
Ease.exp=function(t){
	return Math.pow(2,10*(t-1));
};
Ease.inExp=Ease.in(Ease.exp);
Ease.outExp=Ease.out(Ease.exp);
Ease.inOutExp=Ease.inOut(Ease.exp);
// 円形: p(t)=1-sqrt(1-t^2)
Ease.circ=function(t){
	return 1-Math.sqrt(1-t*t);
};
Ease.inCirc=Ease.in(Ease.circ);
Ease.outCirc=Ease.out(Ease.circ);
Ease.inOutCirc=Ease.inOut(Ease.circ);
// Back: p(t)=t^2×((s+1)t-s), s=1.70158
Ease.back=function(t){
	return t*t*((1.70158+1)*t-1.70158);
};
Ease.inBack=Ease.in(Ease.back);
Ease.outBack=Ease.out(Ease.back);
Ease.inOutBack=Ease.inOut(Ease.back);
// SoftBack: p(t)=t^2×(2t-1)
Ease.softBack=function(t){
	return t*t*(2*t-1);
};
Ease.inSoftBack=Ease.in(Ease.softBack);
Ease.outSoftBack=Ease.out(Ease.softBack);
Ease.inOutSoftBack=Ease.inOut(Ease.softBack);
// Elastic: p(t)=56t^5-105t^4+60t^3-10t^2
Ease.elastic=function(t){
	return 56*t*t*t*t*t-105*t*t*t*t+60*t*t*t-10*t*t;
};
Ease.inElastic=Ease.in(Ease.elastic);
Ease.outElastic=Ease.out(Ease.elastic);
Ease.inOutElastic=Ease.inOut(Ease.elastic);
// Bounce:
Ease.bounce=function(t){
	var pow2,bounce=4;
	while(t<((pow2=Math.pow(2,--bounce))-1)/11){
	}
	return 1/Math.pow(4,3-bounce)-7.5625*Math.pow((pow2*3-2)/22-t,2);
};
Ease.inBounce=Ease.in(Ease.bounce);
Ease.outBounce=Ease.out(Ease.bounce);
Ease.inOutBounce=Ease.inOut(Ease.bounce);
// Smooth: p(t)=t^2×(3-t)/2
Ease.smooth=function(t){
	return t*t*(3-t)/2
};
Ease.inSmooth=Ease.in(Ease.smooth);
Ease.outSmooth=Ease.out(Ease.smooth);
Ease.inOutSmooth=Ease.inOut(Ease.smooth);

/*
鼻ブログ
http://noze.space/archives/432
*/
