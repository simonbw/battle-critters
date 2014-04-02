var owners = [];
var critters = [];

$(document).ready(function() {
	$("#createbutton").click(function() {

		$(this).prop('disabled', true);

		var request_data = {
			critters: critters,
			owners: owners,
			height: $("#height").val(),
			width: $("#width").val(),
			length: $("#length").val()
		};
		console.log(request_data);
		$.post(NEW_BATTLE_URL, request_data, function(data) {
			alert(data);
			var battle_id = parseInt(data);
			window.location.href = VIEW_BATTLE_URL.replace('999999999', battle_id);
		});
	});

	$("#newcritterbutton").click(function() {
		var owner = prompt("owner");
		if (owner) {
			var name = prompt("critter name");
			if (name) {
				add_critter(owner, name);
			} 
		}
	});

	function add_critter(owner, name) {
		critters.push(name);
		owners.push(owner);
		var url = CRITTER_LINK.replace('insertownerhere', owner).replace('insertfilenamehere', name);
		var delete_button = '<button onclick="remove_critter(\'' + owner + "', '" + name +'\')">Delete</button>';
		var item = '<li id="'+owner+'_'+name+'"><a href="' + url + '">' + owner + "." + name + "</a>" + delete_button + "</li>";
		$('#critterlist').append(item);
	}

	function remove_critter(owner, name) {
		$("#" + owner + '_' + name).remove();
		critters.splice(critters.indexOf(name));
		owners.splice(owners.indexOf(owner));
	}
});