/*
	レガシーシステム向けに互換プロパティを再定義
*/
// Array.prototype.forEach=Array.prototype.forEach||function(func){
// 	for(var i=0;i<this.length;i++){
// 		func(this[i],i,this);
// 	}
// };
window.performance=window.performance||window.Date;
window.requestAnimationFrame=window.requestAnimationFrame
	||window.webkitRequestAnimationFrame
	||function(callback){window.setTimeout(function(){callback(performance.now())},1000/60)};
