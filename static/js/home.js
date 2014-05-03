// map critter ids to critter datas
var critters_loaded = [];

/**
 * [delete_file description]
 * @param  {[type]} filename [description]
 * @return {[type]}          [description]
 */
function delete_critter(critter_name) {
	$.ajax({
		'type': "DELETE",
		'dataType': 'json',
		'url': DELETE_FILE_URL.replace('insertfilenamehere', critter_name),
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
 */
function load_critter_list() {
	$.getJSON(CRITTER_JSON_USER_URL, {}, function(response_data) {
		$("#critterlist").empty();
		for (var i = 0; i < response_data.critters.length; i++) {
			var critter = response_data.critters[i];
			var li = $("<li></li>");
			li.append($("<a></a>", {
				'text': critter['name'],
			}));
			li.append($("<span>", {
				'text': critter['score'],
				'class': 'score',
			}));
			li.append($("<a>", {
				'text': 'edit',
				'href': critter['url'],
				'class': 'edit'
			}));
			li.append($("<button>", {
				'text': 'show battles',
				'class': 'showbattles'
			}));
			var deletebutton = $("<button>", {
				'text': 'delete',
				'click': (function(critter_name) {
					return (function() {
						delete_critter(critter_name)
					});
				})(critter['name'])
			});
			var ul = $("<ul>", {
				'class': 'battlelist',
			});
			ul.hide();
			li.append(deletebutton);
			li.append(ul);

			(function(ul, id) {
				var request_data = {
					'critter_id': id
				};
				$.getJSON(CRITTER_RECENT_BATTLES_URL, request_data, function(response_data2) {
					if (response_data2.success) {
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

$(document).ready(function() {
	load_critter_list();

	// $("#critterlist").on('click', '.showbattles', function(event) {
	// 	event.preventDefault();
	// 	$(this).text('hide battles');
	// 	$(this).parent().children('.battlelist').slideDown(200);
	// 	$(this).removeClass('showbattles');
	// 	$(this).addClass('hidebattles');
	// });

	// $("#critterlist").on('click', '.hidebattles', function(event) {
	// 	event.preventDefault();
	// 	$(this).text('show battles');
	// 	$(this).parent().children('.battlelist').slideUp(200);
	// 	$(this).removeClass('hidebattles');
	// 	$(this).addClass('showbattles');
	// });

	$('#critterlist>li')

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