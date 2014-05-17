/**
 * This file contains things common to different files. It declares constants and provides useful functions.
 */

// Key bindings
var K_ALT = 18
var K_CAPS = 20
var K_CTRL = 17
var K_ENTER = 13
var K_ESC = 27
var K_SHIFT = 16
var K_SPACE = 32

// The module for doing nice things
util = new (function() {

	/**
	 * Return a string containing the time, ready for insertion into HTML
	 */
	this.time = function() {
		var date = new Date();
		return '<span id="time">' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds() + '</span>';
	}

	console.log("util loaded");

})();