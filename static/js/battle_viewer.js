battleViewerModule = new(function() {
	var CHUNK_SIZE = 200; // number of frames per chunk
	var COLORS = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF"]
	var CTX_HEIGHT;
	var CTX_WIDTH;
	var LAST_FRAME_REQUESTED = 0; // current highest frame with request sent out
	var MAX_FRAME = BATTLE_LENGTH - 1; // total number of frames to load - 1
	var PLAY_SPEED = 30;

	var chunks_loaded = 0;
	var ctx;
	var current_frame = 0;
	var frames = [];
	var interval_id = null;

	$(document).ready(function() {
		loadChunk(LAST_FRAME_REQUESTED, CHUNK_SIZE);
		ctx = $("#battlefield").get(0).getContext('2d');
		CTX_WIDTH = $("#battlefield").width();
		CTX_HEIGHT = $("#battlefield").height();

		$("#nextbutton").click(function() {
			stopPlayback();
			nextFrame();
		});
		$("#backbutton").click(function() {
			stopPlayback();
			previous_frame();
		});
		$("#skipbutton").click(100, skip);
		$("#playbutton").click(play);
		$("#rewindbutton").click(rewind);
		$("#resetbutton").click(reset);
		$("#stopbutton").click(stopPlayback);

		for (var i = 0; i < critter_names.length; i++) {
			$('#critterlabel' + i).css('color', COLORS[i]);
			if (i == winner_index) {
				$('#critterlabel' + i).addClass('winner');
			}
			// $('#counter' + i).css('background', COLORS[i]);
		}
	});

	/**
	 * Called when the battle is completely loaded
	 */
	function loadComplete() {
		if (interval_id == null) {
			play();
		}
	}

	/**
	 * Load a chunk of frames.
	 * @param  {int} start
	 * @param  {int} end
	 */
	function loadChunk(start, end) {
		end = Math.min(end, MAX_FRAME);
		LAST_FRAME_REQUESTED = Math.max(LAST_FRAME_REQUESTED, end);
		$.get(FRAME_URL, {
				start: start,
				end: end
			},
			function(data) {
				chunks_loaded++;
				parseFrameData(data);
				if (chunks_loaded == 1) {
					renderFrame();
				}
				if (LAST_FRAME_REQUESTED < MAX_FRAME) {
					loadChunk(LAST_FRAME_REQUESTED + 1, Math.min(LAST_FRAME_REQUESTED + CHUNK_SIZE, MAX_FRAME));
				} else {
					loadComplete();
				}
			});
	}

	/**
	 * Proccess the raw frame data.
	 * @param  {str} data
	 */
	function parseFrameData(data) {
		var new_frames = data.split(/\n\n/);
		for (var i = 0; i < new_frames.length; i++) {
			var new_frame = new_frames[i].split("\n");
			var index = parseInt(new_frame.shift().match(/\d+/));
			for (var j = 0; j < new_frame.length; j++) {
				new_frame[j] = new_frame[j].split(" ");
			}
			frames[index] = new_frame;
		}

		$('#loadcounter').html("Frames Loaded: " + frames.length + "/" + (MAX_FRAME + 1) + " in " + chunks_loaded + " chunks");
	}

	/**
	 * Render the current frame on the canvas.
	 */
	function renderFrame() {
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

	/**
	 * Advance to the next frame.
	 */
	function nextFrame() {
		if (current_frame >= frames.length - 1) {
			stopPlayback();
		} else {
			current_frame++;
			renderFrame();
		}
	}

	/**
	 * Go back to the previous frame.
	 */
	function previous_frame() {
		if (current_frame <= 0) {
			stopPlayback();
		} else {
			current_frame--;
			renderFrame();
		}
	}

	function play() {
		stopPlayback();
		interval_id = window.setInterval(nextFrame, PLAY_SPEED);
	}

	function skip() {
		n = 100;
		stopPlayback();
		current_frame = Math.min(frames.length - 1, current_frame + n);
		renderFrame();
	}

	function rewind() {
		stopPlayback();
		interval_id = window.setInterval(previous_frame, PLAY_SPEED);
	}

	function stopPlayback() {
		if (interval_id) {
			window.clearInterval(interval_id);
		}
		interval_id = null;
	}

	function reset() {
		stopPlayback();
		current_frame = 0;
		renderFrame();
	}
})();