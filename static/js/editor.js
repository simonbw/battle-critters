/**
 * This module deals with the text editor.
 */
editorModule = (function() {
	// SETTINGS //
	var AUTOSAVE = true; // if editor should automatically save
	var AUTOCOMPILE = false; // if editor should automatically compile
	var AUTOSAVE_WAIT = 2000; // milliseconds idle before autosaving.
	var BOTTOM_PADDING = 100; // attempted padding at the bottom of the screen
	var FOLD_ERRORS = true; // whether or not to move the gutter for error markers

	// variables 
	var compiling = false;
	var editor = null;
	var edits = 0;
	var errors = []; //{'lineNumber': 1, 'message': 'a message'}
	var saved = true;
	var saving = false;

	/**
	 * Saves the current file to the server.
	 */
	function save(callback) {
		if (!saving && !saved) {
			// console.log("saving to " + SAVE_URL)
			$('#savestatus').html("Saving...");
			saving = true;
			$.post(SAVE_URL, {
				content: editor.getValue()
			}, function(data) {
				saving = false;
				if (data.success) {
					saved = true;
					$('#savestatus').html("Last saved: " + util.time());
					$('#statusbar').removeClass("unsaved");
					resetHeight();
				} else {
					console.log(data.error);
					$("#errordisplay").html(data);
					$("#errordisplay").slideDown(150, function() {
						resetHeight();
					});
					$('#savestatus').html("Error Saving");
					$('#statusbar').addClass('error');
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
			// Is this needed?
			editor.setOption("readOnly", true);
			f = function(savedata) {
				// console.log("compiling " + COMPILE_URL);
				$('#compilestatus').html("Compiling...");
				$('#statusbar').addClass('compiling');
				$('#statusbar').removeClass('error');
				$.post(COMPILE_URL, {}, function(data) {
					console.log(data);
					compiling = false;
					editor.setOption("readOnly", false);
					$('#statusbar').removeClass('compiling');
					if (data.success) {
						$('#compilestatus').html("Compiled Successfully");
						$('#statusbar').addClass('compiled');
						$('#statusbar').removeClass('error');
						$("#errordisplay").html("");
						$("#errordisplay").slideUp(100, function() {
							resetHeight();
						});
						clearErrors();
					} else {
						// console.log("Compile Error: " + data);
						$("#errordisplay").html(data.error);
						$("#errordisplay").slideDown(150, function() {
							resetHeight();
						});
						$('#compilestatus').html("Compilation Error");
						$('#statusbar').addClass('error');
						processCompilerOutput(data.errors);
					}
				}, 'json');
			}
			// save if needed, else compile
			if (saved)
				f(null);
			else
				save(f);
		}
	}

	/**
	 * Revert the file to it's last successful compile.
	 */
	function revert() {
		$.getJSON(REVERT_URL, function(data) {
			if (data.success) {
				editor.setValue(data['content']);
				$('#compilestatus').html("Reverted to successful compile");
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

	/**
	 * Called for automatic saving.
	 */
	function autosave() {
		edits -= 1;
		if (edits === 0) {
			if (AUTOCOMPILE) {
				compile();
			} else {
				save();
			}
		}

		// TODO: autocompile?
	}

	/**
	 * Sets the maximum height so the editor doesn't go off the page.
	 */
	function resetHeight(stop) {
		var maxHeight = $(window).height() - $("#editor").offset().top - $('#statusbar').height() - $('#toolbar').height() - BOTTOM_PADDING;
		$('.CodeMirror-scroll').css('max-height', '' + maxHeight + 'px');
		$('#editorbox #helpbox').css('max-height', '' + maxHeight + 'px');
		var minHeight = $('#editorbox #helpbox').height() + 50;
		$('.CodeMirror-scroll').css('min-height', '' + minHeight + 'px');
		editor.refresh();

		// This is needed because it seems this function needs to be called once the DOM rebuilds itself or something
		if (!stop) {
			setTimeout(function() {
				resetHeight(true);
			}, 20);
		}
	}

	/**
	 * Parses the compiler output and marks line errors.
	 */
	function processCompilerOutput(output) {
		clearErrors();
		for (var n in output) {
			if (n != 'full') {
				console.log(n, output[n]);
				markLineError(parseInt(n - 1), output[n]);
			}
		}
	}

	/**
	 * Marks a line with an error
	 */
	function markLineError(n, message) {
		editor.addLineClass(n, 'background', 'compile-error');
		var marker = document.createElement("div");
		marker.innerHTML = '●';
		marker.title = message;
		marker.classList.add("errormark")
		editor.setGutterMarker(n, "errormarks", marker);
		errors.push({
			'lineNumber': n,
			'message': message
		});
		if (FOLD_ERRORS) {
			$('.errormarks').css('width', '10px');
		}
	}

	/**
	 * Removes all compile error marks
	 */
	function clearErrors() {
		for (var i = 0; i < errors.length; i++) {
			editor.removeLineClass(errors[i].lineNumber, 'background', 'compile-error');
			editor.setGutterMarker(errors[i].lineNumber, "errormarks", null);
		}
		errors = [];
		if (FOLD_ERRORS) {
			$('.errormarks').css('width', '0px');
		}
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

	// init
	$(document).ready(function() {

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
		} else {
			$("#autosavebutton").html("Enable Autosave");
		}
		$("#autosavebutton").click(function() {
			AUTOSAVE = !AUTOSAVE;
			if (AUTOSAVE) {
				$("#autosavebutton").html("Disable Autosave");
			} else {
				$("#autosavebutton").html("Enable Autosave");
			}
		});

		$("#savestatus").html("Opened at " + util.time());
		$("#savebutton").click(save);
		$("#compilebutton").click(compile);
		$("#revertbutton").click(revert);

		// Extra key bindings
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

		editor = CodeMirror.fromTextArea($("#editor").get(0), {
			continueComments: true,
			extraKeys: keymap,
			gutters: ["CodeMirror-linenumbers", "errormarks"],
			indentUnit: 4,
			indentWithTabs: true,
			keyMap: "sublime",
			lineNumbers: true,
			lineWrapping: true,
			matchBrackets: true,
			mode: 'text/x-java',
			smartIndent: true,
			styleActiveLine: true,
			theme: "custom_theme",
			undoDepth: 100,
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


		$('#helpbox #tabbuttonbar').on('click', '.tabbutton', function(event) {
			event.preventDefault();
			helpTab($(this).index());
		});
		helpTab(0);

		if (FOLD_ERRORS) {
			$('.errormarks').css('width', '0px');
		}

		// I'm not quite sure why I call resize so many times...
		resetHeight();
		$(window).resize(resetHeight);
		resetHeight();

	});
})();