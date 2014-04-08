// SETTINGS //
AUTOSAVE = true; // bool if editor should automatically save
AUTOSAVE_WAIT = 500; // milliseconds idle before autosaving.
EDITOR_ID = '#editor'; // id of the text area

// SETUP KEYS //
var BLOCK_KEYS = "S"
$(document).bind('keydown', function(e) {
	var k = e.which;
	for (var i = 0; i < BLOCK_KEYS.length; i++) {
		if (e.ctrlKey && (k == BLOCK_KEYS.charCodeAt(i))) {
			e.preventDefault();
			return false;
		}
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
	var errors = [];

	$("#errordisplay").hide();

	// This should probably be designed a little better.
	$("#errordisplay").click(function() {
		clearErrors();
		$(this).slideUp(100, function() {
			resetHeight();
		});
	});

	if (AUTOSAVE) {
		$("#autosavebutton").html("Disable Autosave");
	}
	else {
		$("#autosavebutton").html("Enable Autosave");
	}
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
		lineWrapping: true,
		indentWithTabs: true,
		smartIndent: true,
		indentUnit: 4,
		undoDepth: 100,
		keyMap: "sublime",
		extraKeys: keymap,
		theme: "custom_theme",
		matchBrackets: true,
		styleActiveLine: true,
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
			// console.log("saving to " + SAVEPATH)
			$('#savestatus').html("Saving...");
			saving = true;
			$.post(SAVEPATH, {
				content: editor.getValue()
			}, function(data) {
				saving = false;
				if (data != "success") {
					console.log("Save Error: " + data);
					$("#errordisplay").html(data);
					$("#errordisplay").slideDown(150, function() {
						resetHeight();
					});
					$('#savestatus').html("Error Saving");
					$('#statusbar').addClass('error');
				} else {
					saved = true;
					$('#savestatus').html("Last saved: " + time());
					$('#statusbar').removeClass("unsaved");
					resetHeight();
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
				// console.log("compiling " + COMPILEPATH);
				$('#compilestatus').html("Compiling...");
				$('#statusbar').addClass('compiling');
				$('#statusbar').removeClass('error');
				$.post(COMPILEPATH, {}, function(data) {
					compiling = false;
					editor.setOption("readOnly", false);
					$('#statusbar').removeClass('compiling');
					if (data != "success") {
						// console.log("Compile Error: " + data);
						$("#errordisplay").html(data);
						$("#errordisplay").slideDown(150, function() {
							resetHeight();
						});
						$('#compilestatus').html("Compilation Error");
						$('#statusbar').addClass('error');
						processCompilerOutput(data);
					} else {
						$('#compilestatus').html("Compiled Successfully");
						$('#statusbar').addClass('compiled');
						$('#statusbar').removeClass('error');
						$("#errordisplay").html("");
						$("#errordisplay").slideUp(100, function() {
							resetHeight();
						});
						clearErrors();
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

	/**
	 * Sets the maximum height so the editor doesn't go off the page.
	 */
	function resetHeight(stop) {
		var maxHeight = $(window).height() - $("#editor").offset().top - $('#statusbar').height() - $('#toolbar').height() - 120;
		$('.CodeMirror-scroll').css('max-height', '' + maxHeight + 'px');
		$('#editorbox #helpbox').css('max-height', '' + maxHeight + 'px');
		var minHeight = $('#editorbox #helpbox').height() + 50;
		$('.CodeMirror-scroll').css('min-height', '' + minHeight + 'px');
		editor.refresh();

		// This is needed because it seems this function needs to be called once the DOM rebuilds itself or something
		if (!stop) {
			setTimeout(function(){
				resetHeight(true);
			}, 20);
		}
	}

	/**
	 * Parses the compiler output and marks line errors.
	 */
	function processCompilerOutput(output) {
		var re = /.java:(\d+)/g;
		var matches;
		while ((matches = re.exec(output)) !== null) {
			markLineError(parseInt(matches[1]) - 1);
		}
	}

	/**
	 * Highlights a line for error
	 */
	function markLineError(n) {
		editor.addLineClass(n, 'background', 'compile-error');
		errors.push(n);
	}

	/**
	 * Removes all compile error marks
	 */
	function clearErrors() {
		for (var i = 0; i < errors.length; i++) {
			editor.removeLineClass(errors[i], 'background', 'compile-error');
		}
		errors = [];
	}

	/**
	 * Set the active help tab.
	 */
	function helpTab(i) {
		$('#helpbox .tab').hide();
		$('#helpbox .tabbutton').removeClass('active');
		$('#helpbox .tab:eq(' + i + ')').show();
		$('#helpbox .tabbutton:eq(' + i + ')').addClass('active');
		resetHeight();
	}

	// there should be a better way to do this...
	$('#helpbox #tabbuttonbar .tabbutton:eq(' + 0 + ')').click(function() {
		helpTab(0);
	});
	$('#helpbox #tabbuttonbar .tabbutton:eq(' + 1 + ')').click(function() {
		helpTab(1);
	});
	$('#helpbox #tabbuttonbar .tabbutton:eq(' + 2 + ')').click(function() {
		helpTab(2);
	});
	helpTab(0);

	resetHeight();
	$(window).resize(resetHeight);

	resetHeight();

});