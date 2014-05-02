// map critter ids to critter datas
var critters_loaded = [];

/**
 * [delete_file description]
 * @param  {[type]} filename [description]
 * @return {[type]}          [description]
 */
function delete_file(filename) {
	$.ajax({
		'type': "DELETE",
		'dataType': 'json',
		'url': DELETE_FILE_URL.replace('insertfilenamehere', filename),
		'complete': function(data, status) {
			if (data.success) {
				load_critter_list();
			} else {
				alert(data.error);
			}
		},
	});
}

/**
 * [load_critter_list description]
 * @return {[type]} [description]
 */
function load_critter_list() {
	$.getJSON(CRITTER_JSON_USER_URL, {}, function(response_data) {
		$("#critterlist").empty();
		for (var i = 0; i < response_data.critters.length; i++) {
			var critter = response_data.critters[i];
			var li = $("<li></li>");
			var a = $("<a></a>", {
				'text': critter['name'],
				'href': critter['url']
			});
			li.append(a);
			$("#critterlist").append(li);
		}
	});
}


$(document).ready(function() {
	load_critter_list();
	$("#newfilebutton").click(function() {
		filename = prompt("Enter a name for your new critter:");
		if (filename) {
			if (/[A-Z|a-z][\w]*/.test(filename)) {
				path = NEW_FILE_URL.replace('insertfilenamehere', filename);
				$.post(path, {}, function(data) {
					if (data.success) {
						load_critter_list();
					} else {
						alert(data.error);
					}
				}, 'json');
			} else {
				alert("Invalid Filename: " + filename);
			}
		}
	});
});