// map critter ids to critter datas
var critters_loaded = [];

function deleteCritter(critter_name) {
	console.log('deleting ' + critter_name);
	$.ajax({
		'type': "DELETE",
		'dataType': 'json',
		'url': DELETE_FILE_URL.replace('insertfilenamehere', critter_name),
		'complete': function(data, status) {
			if (data.success) {
				loadCritterList();
			} else {
				alert(data.error);
			}
		},
	});
}

function loadCritterList() {
	$.getJSON(CRITTER_JSON_USER_URL, {}, function(response_data) {
		$("#critterlist>li.critter").remove();
		for (var i = 0; i < response_data.critters.length; i++) {
			var critter = response_data.critters[i];
			var li = $("<li>", {
				'class': 'critter'
			});
			$(li).data('critter_name', critter['name']);
			$(li).data('critter_id', critter['id']);
			var top = $("<div>", {
				'class': 'top'
			});
			li.append(top);
			top.append($("<span>", {
				'text': critter['name'],
				'class': 'name item'
			}));
			top.append($("<span>", {
				'text': critter['score'],
				'class': 'score item'
			}));
			top.append($("<span>", {
				'text': critter['wins'],
				'class': 'wins item'
			}));
			top.append($("<span>", {
				'text': critter['losses'],
				'class': 'losses item'
			}));

			var actionlist = $("<ul>", {
				'class': 'actionlist',
			});
			actionlist.hide();
			li.append(actionlist);

			actionlist.append($('<li>', {
				'html': $('<a>', {
					'text': 'Edit',
					'class': 'edit',
					'href': critter['url']
				})
			}));

			actionlist.append($('<li>', {
				'html': $('<a>', {
					'text': 'Delete',
					'class': 'delete'
				})
			}));

			actionlist.append($('<li>', {
				'html': $('<a>', {
					'text': 'Ranked Battle',
					'class': 'rankedbattle',
					'href': RANKED_BATTLE_URL + '?' + $.param({
						'critters': [critter['id']]
					})
				})
			}));

			actionlist.append($('<li>', {
				'html': $('<a>', {
					'text': 'Custom Battle',
					'class': 'custombattle',
					'href': CUSTOM_BATTLE_URL + '?' + $.param({
						'critters': [critter['id']]
					})
				})
			}));

			var battlelist = $("<ul>", {
				'class': 'battlelist',
			});
			battlelist.hide();
			li.append(battlelist);

			//load battles
			(function(battlelist, critter) {
				var request_data = {
					'critter_id': critter['id']
				};
				$.getJSON(CRITTER_RECENT_BATTLES_URL, request_data, function(response_data2) {
					if (response_data2.success) {
						for (var j = 0; j < response_data2.battles.length; j++) {
							var battle = response_data2.battles[j];
							var text = (battle['winner_id'] == critter['id']) ? 'victory' : 'loss';
							text += ' at ' + battle['pretty_time'];
							battlelist.append($("<li>", {
								'html': $("<a>", {
									'text': text,
									'href': battle['url']
								})
							}));
						}
					} else {
						console.log(response_data2.error);
					}
				});
			})(battlelist, critter);
			$("#critterlist>li:last-child").before(li);
		}
	});
}

/**
 * Selects the nth critter in the list. Selects no critter if n = 0.
 */
function selectCritter(n) {
	$('#critterlist>li.critter').removeClass('selected');
	if (n > 0) {
		$('#critterlist>li.critter:nth-of-type(' + (n + 1) + ')').addClass('selected');
	}
	$('#critterlist>li.selected .battlelist').slideDown('fast');
	$('#critterlist>li:not(.selected) .battlelist').slideUp('fast');
	$('#critterlist>li.selected .actionlist').slideDown('fast');
	$('#critterlist>li:not(.selected) .actionlist').slideUp('fast');
}

$(document).ready(function() {
	loadCritterList();

	$("#critterlist").on('click', '.critter .top', function(event) {
		if ($(this).parent().hasClass('selected')) {
			selectCritter(0);
		} else {
			selectCritter($(this).parent().index());
		}
	});

	$("#critterlist").on('click', '.critter .actionlist .delete', function(event) {
		var old = $(this);
		var realdelete = $('<a>', {
			'text': 'Confirm Delete',
			'class': 'realdelete'
		});
		old.before(realdelete);
		realdelete.hide();

		old.slideUp(100);
		realdelete.slideDown(100);

		realdelete.mouseleave(function(event) {
			realdelete.slideUp(100, function() {
				$(this).remove();
			});
			old.slideDown(100);
		});

	});

	$("#critterlist").on('click', '.critter .actionlist .realdelete', function(event) {
		deleteCritter($(this).parents('.critter').data('critter_name'));
	});

	$('#critterlist').on('click', '.newcritterbutton', function(event) {
		var input = $('<input>', {
			'type': 'text',
			'placeholder': 'Critter Name',
			'class': 'nameinput'
		})
		var old = $(this).replaceWith(input);
		input.focus();
		input.focusout(function() {
			$(input).replaceWith(old);
		});
		input.keyup(function(event) {
			var critter_name = input.val();
			// check if name is valid
			if (/^[A-Z|a-z][\w]*$/.test(critter_name)) {
				input.removeClass('invalid');
				input.addClass('valid');
			} else {
				input.removeClass('valid');
				input.addClass('invalid');
			}
		});
		input.keypress(function(event) {
			if (event.which == K_ENTER) {
				var critter_name = input.val();
				// check if name is valid
				if (/^[A-Z|a-z][\w]*$/.test(critter_name)) {
					$.post(NEW_FILE_URL, {
						'name': critter_name
					}, function(response_data) {
						if (response_data.success) {
							loadCritterList();
						} else {
							alert(response_data.error);
						}
					}, 'json');
					$(input).replaceWith(old);
				}
			}
		});
	});
});