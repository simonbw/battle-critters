var newBattleModule = (function() {
	var module = {}
		// number of critters to request
	var LOADING_LIMIT = 32;
	// if currently waiting for response
	var request_out = false;
	// The currently chosen tab
	var active_tab;
	// Data for all the tabs
	var tab_info = {};
	tab_info['user'] = {
		'list': [],
		'url': CRITTER_USER_IDS_URL,
		'sorting': null
	}
	tab_info['random'] = {
		'list': [],
		'url': CRITTER_RANDOM_IDS_URL,
		'sorting': null
	}
	// map critter ids to critter datas
	var critters_loaded = [];
	// ids of user's critters
	var user_critters = [];
	// ids of random critters
	var random_critters = [];
	// the critter ids selected for the battle
	var critters_selected = [];

	/**
	 * Request some critters.
	 */
	function loadCritters(ids, callback) {
		// console.log("loading:", ids);
		if (ids.length > 0) {
			var request_data = {
				'ids': ids
			};
			$.getJSON(CRITTER_JSON_URL, request_data, function(response_data) {
				// console.log("loaded: ", response_data);
				$.each(response_data, function(critter_id, critter_info) {
					critters_loaded[critter_id] = critter_info;
					critters_loaded[critter_id].id = parseInt(critter_id);
				});
				callback();
			});
		} else {
			callback();
		}
	}

	/**
	 * Load the ids of the user's critters
	 */
	function requestCritters() {
		var request_data = {
			'limit': LOADING_LIMIT
		};
		$.getJSON(tab_info[active_tab].url, request_data, function(response_data) {
			var critter_list = tab_info[active_tab].list = response_data['ids'];
			var to_load = [];
			for (var i = 0; i < critter_list.length; i++) {
				var id = critter_list[i];
				if (!(id in critters_loaded)) {
					to_load.push(id);
				}
			}
			if (to_load.length) {
				loadCritters(to_load, refreshDisplay);
			}
			refreshDisplay();
		});
	}

	/**
	 * Update the list to display the active tab of critters.
	 */
	function refreshDisplay() {
		// console.log("critters selected", critters_selected);
		var e_list = $('#critterselection .tablebox ul');
		e_list.empty();
		var critter_list = tab_info[active_tab].list;
		for (var i = 0; i < critter_list.length; i++) {
			var id = critter_list[i];
			var li;
			if (critters_loaded[id]) {
				var critter = critters_loaded[id];

				var span1 = $('<span></span>', {
					'text': critter.name,
					'class': 'crittername'
				});
				var span2 = $('<span></span>', {
					'text': critter.owner_name,
					'class': 'critterowner'
				});
				var span3 = $('<span></span>', {
					'text': critter.rank,
					'class': 'critterrank'
				});

				// this lookds sketchy. Its to avoid problems with closures
				li = (function(critter) {
					return $('<li></li>', {
						'click': function() {
							if ($(this).hasClass('selected')) {
								deselectCritter(critter.id);
							} else {
								selectCritter(critter.id);
							}
						}
					})
				})(critter);
			} else {
				li = $('<li></li>', {
					text: "loading...",
					'class': 'loading'
				});
			}
			if (critters_selected.indexOf(id) != -1) {
				li.addClass('selected');
			}
			li.append(span1);
			li.append(span2);
			li.append(span3);
			e_list.append(li);
		}
	}

	/**
	 * Set the active tab
	 */
	function setTab(tab) {
		active_tab = tab;
		requestCritters();
	}

	/**
	 * Add a critter to the selected list.
	 */
	function selectCritter(id) {
		// only add if the critter is not already selected
		if (critters_selected.indexOf(id) == -1) {
			// remove "no critter selected" message		
			if (critters_selected.length == 0) {
				$("#critterlist").html("");
			}

			critters_selected.push(id);
			var critter = critters_loaded[id];
			var li = $('<li></li>');
			li.append('<span class="crittername">' + critter.name + '</span>');
			li.append('<span class="ownername">' + critter.owner_name + '</span>');
			li.append($('<a></a>', {
				'class': 'remove',
				'text': 'X',
				'click': function() {
					deselectCritter(id);
				}
			}));
			$("#critterlist").append(li);

			checkCreateButton();
			var i = tab_info[active_tab].list.indexOf(id);
			if (i != -1) {
				$('#critterselection .tablebox ul>li:nth-of-type(' + (i + 1) + ')').addClass('selected');
			}
		}
	}

	/**
	 * Remove a critter from the selected list.
	 */
	function deselectCritter(id) {
		var i = critters_selected.indexOf(id);
		if (i >= 0) {
			// remove from the list
			critters_selected.splice(i, 1);
			// remove from the dom
			$("#critterlist>li:nth-of-type(" + (i + 1) + ")").remove();

			var j = tab_info[active_tab].list.indexOf(id);
			if (j != -1) {
				$('#critterselection .tablebox ul>li:nth-of-type(' + (j + 1) + ')').removeClass('selected');
			}
		}

		// deselect last critter
		checkCreateButton();
		if (critters_selected.length == 0) {
			$("#critterlist").html("No critters selected");
		}
	}

	/**
	 * Checks if the create button should be disabled and sets it accordingly.
	 * @return {bool} true if button is usable, else false
	 */
	function checkCreateButton() {
		if (critters_selected.length && !request_out) {
			// not disabled
			$("#createbutton").removeClass('disabled');
			return true;
		} else {
			// disabled
			$("#createbutton").addClass('disabled');
			return false;
		}
	}

	// On load
	$(function() {
		setTab('user');
		checkCreateButton();

		$("#selectrandom").click(function() {
			setTab('random');
		});

		$("#selectuser").click(function() {
			setTab('user');
		});

		// Create the battle
		$("#createbutton").click(function() {
			if (checkCreateButton()) {
				request_out = true;
				checkCreateButton();

				var request_data = {
					critters: critters_selected,
					height: $("#battleheight").val(),
					width: $("#battlewidth").val(),
					length: $("#battlelength").val()
				};
				console.log(request_data);
				$.post(NEW_BATTLE_URL, request_data, function(data) {
					request_out = false;
					checkCreateButton();
					if (data.success) {
						window.location.href = data.url;
					} else {
						alert(data.error);
					}
				});
			}
		});
	});

	// add public functions
	module['deselectCritter'] = deselectCritter;
	module['loadCritters'] = loadCritters;
	module['refreshDisplay'] = refreshDisplay;
	module['requestCritters'] = requestCritters;
	module['selectCritter'] = selectCritter;
	module['setTab'] = setTab;
	return module;
})();