var CHUNK_SIZE = 200; // number of frames per chunk
var MAX_FRAME = BATTLE_LENGTH - 1; // total number of frames to load - 1
var LAST_FRAME_REQUESTED = 0; // current highest frame with request sent out
var chunks_loaded = 0;

var ctx;
var CTX_WIDTH;
var CTX_HEIGHT;
var frames = [];
var current_frame = 0;
var PLAY_SPEED = 30;

var COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF"]

var interval_id = null;

$(document).ready(function() {
	load_chunk(LAST_FRAME_REQUESTED, CHUNK_SIZE);
	ctx = $("#battlefield").get(0).getContext('2d');
	CTX_WIDTH = $("#battlefield").width();
	CTX_HEIGHT = $("#battlefield").height();

	$("#nextbutton").click(function() {
		stop_playback();
		next_frame();
	});
	$("#backbutton").click(function() {
		stop_playback();
		previous_frame();
	});
	$("#skipbutton").click(100, skip);
	$("#playbutton").click(play);
	$("#rewindbutton").click(rewind);
	$("#resetbutton").click(reset);
	$("#stopbutton").click(stop_playback);

	for (var i = 0; i < critter_names.length; i++) {
		$('#critterlabel' + i).css('color', COLORS[i]);
		if (i == winner_index) {
			$('#critterlabel' + i).addClass('winner');
		}
		// $('#counter' + i).css('background', COLORS[i]);
	}	
});

function load_complete() {
	if (interval_id == null) {
		// play();
	}
}

function load_chunk(start, end) {
	end = Math.min(end, MAX_FRAME);
	LAST_FRAME_REQUESTED = Math.max(LAST_FRAME_REQUESTED, end);
	$.get(FRAME_URL, {
			start: start,
			end: end
		},
		function(data) {
			chunks_loaded++;
			console.log(data);
			parse_frame_data(data);
			if (chunks_loaded == 1) {
				render_frame();
			}
			if (LAST_FRAME_REQUESTED < MAX_FRAME) {
				load_chunk(LAST_FRAME_REQUESTED + 1, Math.min(LAST_FRAME_REQUESTED + CHUNK_SIZE, MAX_FRAME));
			} else {
				load_complete();
			}
		});
}

function parse_frame_data(data) {
	var new_frames = data.split(/\n\n/);
	for (var i = 0; i < new_frames.length; i++) {
		var new_frame = new_frames[i].split("\n");
		var index = parseInt(new_frame.shift().match(/\d+/));
		for (var j = 0; j < new_frame.length; j++) {
			new_frame[j] = new_frame[j].split(" ");
		}
		frames[index] = new_frame;
	}

	$('#loadcounter').html("Frames Loaded:" + frames.length + "/" + (MAX_FRAME + 1) + " in " + chunks_loaded + " chunks");
}

function render_frame() {
	$('#framecounter').html(current_frame);
	frame = frames[current_frame];
	ctx.clearRect(0, 0, CTX_WIDTH, CTX_HEIGHT);
	critter_counts = [0, 0, 0, 0, 0];
	for (var i = 0; i < frame.length; i++) {
		var critter_type = frame[i][0];
		critter_counts[critter_type]++;
		ctx.fillStyle = COLORS[critter_type];
		var x = frame[i][1] * 5;
		var y = frame[i][2] * 5;
		var direction = frame[i][3];
		ctx.fillRect(x, y, 5, 5);
	}
	for (var i = 0; i < critter_counts.length; i++) {
		$('#crittercounter' + i).html(critter_counts[i]);
	}
}

function next_frame() {
	if (current_frame >= frames.length - 1) {
		stop_playback();
	} else {
		current_frame++;
		render_frame();
	}
}

function previous_frame() {
	if (current_frame <= 0) {
		stop_playback();
	} else {
		current_frame--;
		render_frame();
	}
}

function play() {
	stop_playback();
	interval_id = window.setInterval(next_frame, PLAY_SPEED);
}

function skip() {
	n = 100;
	stop_playback();
	current_frame = Math.min(frames.length - 1, current_frame + n);
	render_frame();
}

function rewind() {
	stop_playback();
	interval_id = window.setInterval(previous_frame, PLAY_SPEED);
}

function stop_playback() {
	if (interval_id) {
		window.clearInterval(interval_id);
	}
	interval_id = null;
}

function reset() {
	stop_playback();
	current_frame = 0;
	render_frame();
}