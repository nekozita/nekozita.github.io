if( typeof futomi == 'undefined' ) { futomi = {}; }
if( typeof futomi.accs == 'undefined' ) { futomi.accs = {}; }
futomi.accs.form = {};
futomi.accs.form.initDocument = function() {
	var frms = document.forms;
	for( var i=0; i<frms.length; i++ ) {
		dom.event.addEventListener(frms.item(i), 'submit', futomi.accs.form.submitForm);
	}
	if(frms.length > 0) {
		var inputs = frms.item(0).getElementsByTagName('INPUT');
		for( var i=0; i<inputs.length; i++ ) {
			var elm = inputs.item(i);
			if(elm.type == 'text' || elm.type == 'password') {
				elm.focus();
				break;
			}
		}
	}
	futomi.accs.form.buttonDisabled(false);
}

futomi.accs.form.submitForm = function(e) {
	dom.event.preventDefault(e)
	futomi.accs.form.buttonDisabled(true);
	var f = dom.event.target(e);
	if(f.nodeName != 'FORM') {
		f = f.form;
	}
	f.submit();
}

futomi.accs.form.buttonDisabled = function(disabled) {
	var inputs = document.getElementsByTagName('INPUT');
	for( var i=0; i<inputs.length; i++ ) {
		var elm = inputs.item(i);
		if(elm.type == 'submit' || elm.type == 'reset') {
			elm.disabled = disabled;
		}
	}
}
dom.event.addEventListener(window, 'load', futomi.accs.form.initDocument);
