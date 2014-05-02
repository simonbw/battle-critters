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
		console.log(response_data);
		for (var i = 0; i < response_data.critters.length; i++) {
			var critter = response_data.critters[i];
			var li = $("<li></li>");
			var a = $("<a></a>", {
				'text': critter['name'],
				'href': critter['url']
			});
			var ul = $("<ul>", {
				'class': 'battlelist',
			})
			li.append(a);
			li.append(ul);

			(function(ul, id) {
				var request_data = {
					'critter_id': id
				};
				console.log('request_data: ', request_data)
				$.getJSON(CRITTER_RECENT_BATTLES_URL, request_data, function(response_data2) {
					if (response_data2.success) {
						console.log(response_data2);
						for (var j = 0; j < response_data2.battles.length; j++) {
							var battle = response_data2.battles[j];
							ul.append($("<li>", {
								'html': $("<a>", {
									'text': battle['pretty_time'],
									'href': battle['url']
								})
							}));
						}
					} else {
						console.log(response_data2.error);
					}
				});
			})(ul, critter['id']);
			$("#critterlist").append(li);
		}
	});
}

function show_recent_battles() {

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