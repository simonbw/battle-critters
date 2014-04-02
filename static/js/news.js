NEWS_PAGE = 0;

function reload_news() {
	console.log("loading news page " + NEWS_PAGE + " from " + NEWS_URL);
	$.get(NEWS_URL, {page: NEWS_PAGE}, function(data) {
		$("#newsbox").html(data);
	});

	$.get(NEWS_URL, {max: true}, function(data) {
		MAX_NEWS = parseInt(data);
	});

	if (NEWS_PAGE + 1 >= MAX_NEWS) {
		$("button#nextnews").prop("disabled", true);;
	} else {
		$("button#nextnews").prop("disabled", false);;
	}
	if (NEWS_PAGE == 0) {
		$("button#previousnews").prop("disabled", true);;
	} else {
		$("button#previousnews").prop("disabled", false);;
	}
}
$(document).ready(function() {
	reload_news();
	$("button#nextnews").click(function(event) {
		NEWS_PAGE = Math.min(NEWS_PAGE + 1, MAX_NEWS - 1);
		reload_news();
	});
	$("button#previousnews").click(function(event) {
		NEWS_PAGE = Math.max(NEWS_PAGE - 1, 0);
		reload_news();
	});
	$("#postnewsbutton").click(function() {
		var title = $("#newsformtitle").val();
		var content = $("#newsformcontent").val();

		console.log("Posting News: " + title + "\n" + content);
		$.post(NEWS_URL, {title: title, content: content}, function(data) {
			if (data != 'success') {
				alert(data);
			} else {
				reload_news();
			}
		});
	});
});