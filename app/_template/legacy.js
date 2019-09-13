/*
	下位互換ライブラリ
	ブラウザバージョンで異なるプロパティの違いを吸収する。
*/

window.performance=window.performance||window.Date;

window.requestAnimationFrame=window.requestAnimationFrame||
	function(callback){window.setTimeout(function(){callback(performance.now())},1000/60)};

window.AudioContext=window.AudioContext||window.webkitAudioContext;

// よほど古いブラウザをサポートしない限り定義しなくていい
// Array.prototype.forEach=Array.prototype.forEach||function(func){
// 	for(var i=0;i<this.length;i++){
// 		func(this[i],i,this);
// 	}
// };
