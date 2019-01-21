// Tooltip that is accessible on mobile browsers
// Credit to StackOverflow user flavaflo: http://stackoverflow.com/a/12538532/4481448

$(document).ready(function() {
    $(".source, .variety").click(function() {
        var $title = $(this).find(".title");
        var add = !$title.length;
        $(".title").remove();
        if (add) {
            $(this).append('<span class="title">' +
                           $(this).attr("title") +
                           '</span>');
        }
    });
});
