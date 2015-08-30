// Tooltip that is accessible on mobile browsers
// Credit to StackOverflow user flavaflo: http://stackoverflow.com/a/12538532/4481448

$(document).ready(function() {
    $(".source").click(function() {
        var $title = $(this).find(".title");
        if (!$title.length) {
            $(this).append('<span class="title">' +
                           $(this).attr("title") +
                           '</span>');
        } else {
            $title.remove();
        }
    });
});
