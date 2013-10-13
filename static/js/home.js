/**
 * [delete_file description]
 * @param  {[type]} filename [description]
 * @return {[type]}          [description]
 */
function delete_file(filename) {
	$.ajax({
		type: "DELETE",
		url: DELETE_FILE_URL.replace('insertfilenamehere', filename),
	}).done(function(data) {
		if (data != 'success') {
			alert(data);
		} else {
			load_critter_list();
		}
	});
}

/**
 * [load_critter_list description]
 * @return {[type]} [description]
 */
function load_critter_list() {
	$.get(CRITTER_LIST_URL, {
		username: USERNAME,
		delete_buttons: true
	}, function(data) {
		console.log(data);
		$('#critterlist').html(data);
	});
}

// 
$(document).ready(function() {
	load_critter_list();
	$("#newfilebutton").click(function() {
		filename = prompt("Enter a name for your new critter:");
		if (filename) {
			if (/[A-Z|a-z][\w]*/.test(filename)) {
				path = NEW_FILE_URL.replace('insertfilenamehere', filename);
				$.post(path, {}, function(data) {
					if (data != 'success') {
						alert(data);
					} else {
						load_critter_list();
					}
				});
			} else {
				alert("Invalid Filename: " + filename);
			}
		}
	});
});