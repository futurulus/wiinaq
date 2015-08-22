endings = {};
endings.active = {};
endings.row_span = {};
endings.col_span = {};
endings.collapse = {};

(function () {

    function escape_id(id) {
        return "#" + id.replace(/(:|\.|\[|\]|,)/g, "\\$1");
    }

    function remove_ids(id) {
        var pieces = id.split(":");
        for (var i = 0; i < pieces.length; i++) {
            var id_part = pieces[i];
            if (id_part.indexOf("-") > -1) {
                id_part = id_part.split("-")[0];
            }

            delete endings.active[id_part];
        }
    }

    function add_ids(id) {
        var pieces = id.split(":");
        for (var i = 0; i < pieces.length; i++) {
            var id_part = pieces[i];
            if (id_part.indexOf("-") > -1) {
                id_part = id_part.split("-")[0];
            }

            endings.active[id_part] = true;
        }
    }

    endings.activate_cell = function(id) {
        console.debug("escape_id(id): " + escape_id(id));
        var table_id = $(escape_id(id) + ".inflection-entry").closest('table').attr("id");
        console.debug("table_id: " + table_id);

        $(escape_id(table_id) + " .inflection-entry").map(function() {
            remove_ids($(this).attr("id"));
        });

        add_ids(id);

        endings.refresh_visible();

        return "Active: " + JSON.stringify(endings.active);
    }

    function is_active(id) {
        var pieces = id.split(":");
        for (var i = 0; i < pieces.length; i++) {
            var id_part = pieces[i];
            if (id_part.indexOf("-") > -1) {
                id_part = id_part.split("-")[0];
            }

            if (!(id_part in endings.active)) {
                return false;
            }
        }
        return true;
    }

    endings.refresh_visible = function() {
        $(".inflection-option").map(function() {
            var id = $(this).attr("id");
            if (is_active(id)) {
                $(this).removeClass("hide");
            } else {
                $(this).addClass("hide");
            }
        });

        $(".inflection-entry").map(function() {
            var id = $(this).attr("id");
            var table = $(escape_id(id) + ".inflection-entry").closest('table');
            var table_id = table.attr("id");

            if (id in endings.collapse[table_id] &&
                    (endings.collapse[table_id][id] === "*" ||
                     is_active(endings.collapse[table_id][id]))) {
                $(this).addClass("hide");
                $(this).removeClass("active");
            } else {
                $(this).removeClass("hide");

                if (is_active(id)) {
                    $(this).addClass("active");
                } else {
                    $(this).removeClass("active");
                }
            }

            if (id in endings.row_span[table_id] &&
                    (endings.row_span[table_id][id] === "*" ||
                     is_active(endings.row_span[table_id][id]))) {
                var num_rows = table.find("tr").length - 1;
                $(this).attr("rowspan", num_rows);
            } else {
                $(this).removeAttr("rowspan");
            }

            if (id in endings.col_span[table_id] &&
                    (endings.col_span[table_id][id] === "*" ||
                     is_active(endings.col_span[table_id][id]))) {
                var num_cols = table.find("tr:first th").length - 1;
                $(this).attr("colspan", num_cols);
            } else {
                $(this).removeAttr("colspan");
            }
        });
    }

})();

$(document).ready(function() {

    $(".inflection-entry").click(function(event) {
        var id = $(this).attr("id");
        endings.activate_cell(id);
    });

    endings.refresh_visible();

});
