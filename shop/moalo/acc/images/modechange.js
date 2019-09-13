if( typeof futomi == 'undefined' ) { futomi = {}; }
if( typeof futomi.accs == 'undefined' ) { futomi.accs = {}; }
futomi.accs.modechange = {
	formInit: function() {
		var mode = document.getElementById("MODE");
		var month = document.getElementById("MONTH");
		var day = document.getElementById("DAY");
		var idx = mode.selectedIndex;
		if(idx == 0) {
			month.disabled = true;
			day.disabled = true;
		} else if(idx == 1) {
			month.disabled = false;
			day.disabled = true;
		} else if(idx == 2) {
			month.disabled = false;
			day.disabled = false;
		}
	},
	initDocument: function() {
		var mode = document.getElementById("MODE");
		dom.event.addEventListener(mode, 'change', futomi.accs.modechange.formInit);
		futomi.accs.modechange.formInit();
	}
};
dom.event.addEventListener(window, 'load', futomi.accs.modechange.initDocument);
