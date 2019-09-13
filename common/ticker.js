/*
	ニュースティッカー
*/
var tickerSpeed='1s'; // ティッカーのアニメーション速度
var tickerDelay=6000; // ティッカーの更新間隔
var tickerEasing='ease';

function NewsTicker(){
	var tickers=document.querySelectorAll('.ticker');

	Array.prototype.forEach.call(tickers,function(ticker){
		var effectFilter=ticker.getAttribute('rel');
		var targetUL=ticker.querySelector('ul');
		var targetLI=targetUL.querySelectorAll('li');
		var setList=targetUL.firstElementChild;

		var ulWidth=targetUL.clientWidth;
		setList.style.display='block';
		var listHeight=setList.clientHeight;
		setList.style.display='none';
		ticker.style.height=listHeight+"px";

		for(var i=0;i<targetLI.length;i++){
			targetLI[i].style.top=0;
			targetLI[i].style.left=0;
			targetLI[i].style.position='absolute';
		}

		if(effectFilter==='fade'){
			// 最初の表示用
			setList.style.display='block';
			setList.style.opacity=0;
			setList.style.zIndex=99;
			setList.style.webkitAnimation=setList.style.animation=[
				'ticker-fadein',
				tickerSpeed,
				tickerEasing,
				'forwards'
			].join(' ');
			setList.classList.add('showlist');

			if(targetLI.length>1){
				setInterval(function(){
					var showList=ticker.querySelector('.showlist');
					// フェードアウト
					showList.style.webkitAnimation=showList.style.animation=[
						'ticker-fadeout',
						tickerSpeed,
						tickerEasing,
						'forwards'
					].join(' ');
					// アニメーション終了後の処理
					function fadeEnd(){
						var showList=ticker.querySelector('.showlist');
						// 次のリストノードを表示に加える
						var next=showList.nextElementSibling;
						next.style.display='block';
						next.style.opacity=0;
						next.style.zIndex=99;
						next.style.webkitAnimation=next.style.animation=[
							'ticker-fadein',
							tickerSpeed,
							tickerEasing,
							'forwards'
						].join(' ');
						next.classList.add('showlist');
						// アニメーションが終わったリストノードの処理
						showList.style.display='none';
						showList.style.zIndex=98;
						showList.style.webkitAnimation='';
						showList.style.animation='';
						showList.removeEventListener('webkitAnimationEnd',fadeEnd);
						showList.removeEventListener('animationend',fadeEnd);
						showList.classList.remove('showlist');
						targetUL.appendChild(showList);
					}
					showList.addEventListener('webkitAnimationEnd',fadeEnd);
					showList.addEventListener('animationend',fadeEnd);
				},tickerDelay);
			}
		}else if(effectFilter==='roll'){
			// 最初の表示用
			setList.style.display='block';
			setList.style.top='3em';
			setList.style.opacity=0;
			setList.style.zIndex=99;
			setList.style.webkitAnimation=setList.style.animation=[
				'ticker-rollin',
				tickerSpeed,
				tickerEasing,
				'forwards'
			].join(' ');
			setList.classList.add('showlist');

			if(targetLI.length>1){
				setInterval(function(){
					var showList=ticker.querySelector('.showlist');
					// ロールアウト
					showList.style.webkitAnimation=showList.style.animation=[
						'ticker-rollout',
						tickerSpeed,
						tickerEasing,
						'forwards'
					].join(' ');
					// アニメーション終了後の処理
					function rollEnd(){
						var showList=ticker.querySelector('.showlist');
						// 次のリストノードを表示に加える
						var next=showList.nextElementSibling;
						next.style.display='block';
						next.style.top='3em';
						next.style.opacity=0;
						next.style.zIndex=99;
						next.style.webkitAnimation=next.style.animation=[
							'ticker-rollin',
							tickerSpeed,
							tickerEasing,
							'forwards'
						].join(' ');
						next.classList.add('showlist');
						// アニメーションが終わったリストノードの処理
						showList.style.display='none';
						showList.style.zIndex=98;
						showList.style.webkitAnimation='';
						showList.style.animation='';
						showList.removeEventListener('webkitAnimationEnd',rollEnd);
						showList.removeEventListener('animationend',rollEnd);
						showList.classList.remove('showlist');
						targetUL.appendChild(showList);
					}
					showList.addEventListener('webkitAnimationEnd',rollEnd);
					showList.addEventListener('animationend',rollEnd);
				},tickerDelay);
			}
		}else if(effectFilter==='slide'){
			// 最初の表示用
			setList.style.display='block';
			setList.style.left='100%';
			setList.style.opacity=0;
			setList.style.zIndex=99;
			setList.style.webkitAnimation=setList.style.animation=[
				'ticker-slidein',
				tickerSpeed,
				tickerEasing,
				'forwards'
			].join(' ');
			setList.classList.add('showlist');

			if(targetLI.length>1){
				setInterval(function(){
					var showList=ticker.querySelector('.showlist');
					// スライドアウト
					showList.style.webkitAnimation=showList.style.animation=[
						'ticker-slideout',
						tickerSpeed,
						tickerEasing,
						'forwards'
					].join(' ');
					// アニメーション終了後の処理
					function slideEnd(){
						var showList=ticker.querySelector('.showlist');
						// 次のリストノードを表示に加える
						var next=showList.nextElementSibling;
						next.style.display='block';
						next.style.left='100%';
						next.style.opacity=0;
						next.style.zIndex=99;
						next.style.webkitAnimation=next.style.animation=[
							'ticker-slidein',
							tickerSpeed,
							tickerEasing,
							'forwards'
						].join(' ');
						next.classList.add('showlist');
						// アニメーションが終わったリストノードの処理
						showList.style.display='none';
						showList.style.zIndex=98;
						showList.style.webkitAnimation='';
						showList.style.animation='';
						showList.removeEventListener('webkitAnimationEnd',slideEnd);
						showList.removeEventListener('animationend',slideEnd);
						showList.classList.remove('showlist');
						targetUL.appendChild(showList);
					}
					showList.addEventListener('webkitAnimationEnd',slideEnd);
					showList.addEventListener('animationend',slideEnd);
				},tickerDelay);
			}
		}
	});
}
