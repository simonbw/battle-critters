NEWS_PAGE = 0;

function reload_news() {
	console.log("loading news");
	$.get(NEWS_URL, {page: NEWS_PAGE}, function(data) {
		$("#newsbox").html(data);
	});

	$.get(NEWS_URL, {max: true}, function(data) {
		MAX_NEWS = parseInt(data);
	});
}
$(document).ready(function() {
	reload_news();
	$("button#nextnews").click(function(event) {
		Math.min(NEWS_PAGE + 1, MAX_NEWS);
		reload_news();
	});
	$("button#previousnews").click(function(event) {
		NEWS_PAGE = Math.max(NEWS_PAGE - 1, 0);
		reload_news();
	});
	$("#postnewsbutton").click(function() {
		var title = $("#newsformtitle").val();
		var content = $("#newsformcontent").val();
		$.post(NEWS_URL, {title: title, content: content}, function(data) {
			if ('data' != 'success') {
				alert(data);
			} else {
				reload_news();
			}
		});
	});
});