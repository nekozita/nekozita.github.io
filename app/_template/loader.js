// ローダー
function Loader(){
	this.count=0;
}
Loader.prototype.download=function(urls,data,callback){
	if(urls.length==0)return callback();
	this.count+=urls.length;

	for(var i=0;i<urls.length;i++){
		var ext=getExtension(urls[i]);
		if(ext==="png"||ext==="gif"){
			var img=new Image();
			img.src=urls[i];
			img.onload=this.dlCheck(this,urls,callback);
			img.onerror=this.dlCheck(this,urls,callback);
			data[urls[i]]=img;
		}else if(ext==="org"||ext==="wav"||ext==="mp3"){
			// Web Audio対応の場合
			var request=new XMLHttpRequest();
			request.open('GET',urls[i],true);
			request.responseType='arraybuffer';
			request.onload=this.loadSound(this,urls[i],data,callback,request);
			request.onerror=this.dlCheck(this,urls,callback);
			request.send();
			// Web Audio非対応の場合
			// var aud=new Audio(urls[i]);
			// aud.load();
			// data[urls[i]]=aud;
			// if(--this.count==0)callback();
		}else{
			data[urls[i]]=null;
			if(--this.count==0)callback();
		}
	}
};
Loader.prototype.dlCheck=function(my,urls,callback){
	return function(){
		my.count--;
		if(my.count==0)callback();
	};
};
Loader.prototype.loadSound=function(my,url,data,callback,request){
	return function(){
		actx.decodeAudioData(request.response,function(buffer){
			data[url]=buffer;
			my.count--;
			if(my.count==0)callback();
		},function(error){});
	};
};
function getExtension(url){
	return url.substring(url.lastIndexOf(".")+1,url.length);
}