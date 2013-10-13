// SETTINGS //
AUTOSAVE = true; // bool if editor should automatically save
AUTOSAVE_WAIT = 500; // milliseconds idle before autosaving.
EDITOR_ID = '#editor'; // id of the text area

// KEYS //
$(document).bind('keydown', function(e) {
	if (e.ctrlKey && (e.which == 83)) {
		e.preventDefault();
		return false;
	}
});

// Globals to declare
edits = 0;
saving = false;
compiling = false;
saved = true;

/**
 * Return a string containing the time, ready for insertion into HTML
 */
function time() {
	var date = new Date();
	return '<span id="time">' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds() + '</span>';
}

$(document).ready(function() {
	$("#errordisplay").hide();

	$("#errordisplay").click(function() {
		$(this).slideUp(100)
	});

	if (AUTOSAVE)
		$("#autosavebutton").html("Disable Autosave");
	else 
		$("#autosavebutton").html("Enable Autosave");
	$("#autosavebutton").click(function() {
		AUTOSAVE = !AUTOSAVE;
		if (AUTOSAVE)
			$("#autosavebutton").html("Disable Autosave");
		else 
			$("#autosavebutton").html("Enable Autosave");
	});

	$("#savestatus").html("Opened at " + time());

	$("#savebutton").click(save);
	$("#compilebutton").click(compile);

	var keymap = {
		"Ctrl-S": function(instance) {
			save();
			return false;
		},
		"Cmd-S": function(instance) {
			save();
			return false;
		},
		"Ctrl-B": function(instance) {
			compile();
			return false;
		},
		"Cmd-B": function(instance) {
			compile();
			return false;
		}
	}

	editor = CodeMirror.fromTextArea($(EDITOR_ID).get(0), {
		mode: 'text/x-java',
		lineNumbers: true,
		indentWithTabs: true,
		smartIndent: true,
		indentUnit: 4,
		undoDepth: 100,
		extraKeys: keymap,
		theme: "custom_theme",
	});
	editor.on("change", function() {
		$('#savestatus').html("You have unsaved changes");
		$('#compilestatus').html("uncompiled");
		$('#statusbar').addClass('unsaved');
		$('#statusbar').removeClass('error');
		saved = false;

		if (AUTOSAVE) {
			edits += 1;
			setTimeout(autosave, AUTOSAVE_WAIT);
		}
	});

	/**
	 * Saves the current file to the server.
	 */
	function save(callback) {
		if (!saving && !saved) {
			console.log("saving to " + SAVEPATH)
			$('#savestatus').html("Saving...");
			saving = true;
			$.post(SAVEPATH, {
				content: editor.getValue()
			}, function(data) {
				saving = false;
				if (data != "success") {
					console.log("Save Error: " + data);
					$("#errordisplay").html(data);
					$("#errordisplay").slideDown(150);
					$('#savestatus').html("Error Saving");
					$('#statusbar').addClass('error');
				} else {
					saved = true;
					$('#savestatus').html("Last saved: " + time());
					$('#statusbar').removeClass("unsaved");
				}
				if (callback != undefined) {
					callback(data);
				}
			});
		}
	}

	/**
	 * Compile the current file.
	 */
	function compile() {
		if (!compiling) {
			compiling = true;
			editor.setOption("readOnly", true);
			f = function(savedata) {
				console.log("compiling " + COMPILEPATH);
				$('#compilestatus').html("Compiling...");
				$('#statusbar').addClass('compiling');
				$('#statusbar').removeClass('error');
				$.post(COMPILEPATH, {}, function(data) {
					compiling = false;
					editor.setOption("readOnly", false);
					$('#statusbar').removeClass('compiling');
					if (data != "success") {
						console.log("Compile Error: " + data);
						$("#errordisplay").html(data);
						$("#errordisplay").slideDown(150);
						$('#compilestatus').html("Compilation Error");
						$('#statusbar').addClass('error');

					} else {
						$('#compilestatus').html("Compiled Successfully");
						$('#statusbar').addClass('compiled');
						$('#statusbar').removeClass('error');
						$("#errordisplay").html("");
						$("#errordisplay").slideDown(150);
					}
				});
			}
			if (saved)
				f(null);
			else
				save(f);
		}
	}

	/**
	 * Called for automatic saving.
	 */
	function autosave() {
		edits -= 1;
		if (edits === 0) {
			save();
		}
	}

});