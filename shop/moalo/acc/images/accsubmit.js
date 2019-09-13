if( typeof futomi == 'undefined' ) { futomi = {}; }
if( typeof futomi.accs == 'undefined' ) { futomi.accs = {}; }
futomi.accs.accsubmit = {
	formSubmit: function(evt) {
		if(evt) {
			dom.event.preventDefault(evt);
		}
		var frm = dom.event.target(evt);
		var ctrls_num = frm.elements.length;
		for( var i=0; i<ctrls_num; i++ ) {
			var ctrl = frm.elements.item(i);
			if(ctrl.type == "submit") {
				ctrl.disabled = true;
				ctrl.value = "解析中...";
			}
		}
		frm.submit();
	},
	initDocument: function() {
		var abtn = document.getElementById("abtn");
		dom.event.addEventListener(abtn.form, 'submit', futomi.accs.accsubmit.formSubmit);
		abtn.disabled = false;
		abtn.value = "解析開始";
		var cbtn = document.getElementById("cbtn");
		dom.event.addEventListener(cbtn.form, 'submit', futomi.accs.accsubmit.formSubmit);
		cbtn.disabled = false;
		cbtn.value = "ログ切替";
	}
};
dom.event.addEventListener(window, 'load', futomi.accs.accsubmit.initDocument);
