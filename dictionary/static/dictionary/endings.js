alutiiq = {}
alutiiq.active = {}

alutiiq.remove_ids = function(id) {
    var id_parts = id.split("+");
    for (var i = 0; i < id_parts.length; i++) {
        delete alutiiq.active[id_parts[i]];
    }
}

alutiiq.add_ids = function(id) {
    var id_parts = id.split("+");
    for (var i = 0; i < id_parts.length; i++) {
        alutiiq.active[id_parts[i]] = true;
    }
}


$(document).ready(function() {

    function is_active(id) {
        var id_parts = id.split("+");
        for (var i = 0; i < id_parts.length; i++) {
            if (!(id_parts[i] in alutiiq.active)) {
                return false;
            }
        }
        return true;
    }

    function refresh_visible() {
        $(".inflection-option").map(function() {
            var id = $(this).attr("id");
            if (is_active(id)) {
                $(this).removeClass("hide");
            } else {
                $(this).addClass("hide");
            }
        });
    }

    function on_cell_click(id, table_id) {
        $("#" + table_id + " .inflection-entry").map(function() {
            alutiiq.remove_ids($(this).attr("id"));
        });

        alutiiq.add_ids(id);

        refresh_visible();

        return "Active: " + JSON.stringify(alutiiq.active);
    }

    $(".inflection-entry").click(function(event) {
        var table_id = $(this).closest('table').attr("id");
        var id = $(this).attr("id");
        //$(event.target).text(on_cell_click(id, table_id));
        on_cell_click(id, table_id);
    });

    refresh_visible();

});
