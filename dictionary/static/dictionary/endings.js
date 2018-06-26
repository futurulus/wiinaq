endings = {};
endings.state = {};

var escape_id = function(id) {
    return "#" + id.replace(/(:|\.|\[|\]|,)/g, "\\$1");
}
endings.escape_id = escape_id;

var PopoutState = function($popout) {
    this.popout_id = $popout.attr("id");
    this.active = {};
    this.row_span = {};
    this.col_span = {};
    this.collapse = {};

    this.remove_ids = function(id) {
        var pieces = id.split(":");
        for (var i = 0; i < pieces.length; i++) {
            var id_part = pieces[i];
            if (id_part.indexOf("-") > -1) {
                id_part = id_part.split("-")[0];
            }

            delete this.active[id_part];
        }
    }

    this.add_ids = function(id) {
        var pieces = id.split(":");
        for (var i = 0; i < pieces.length; i++) {
            var id_part = pieces[i];
            if (id_part.indexOf("-") > -1) {
                id_part = id_part.split("-")[0];
            }

            this.active[id_part] = true;
        }
    }

    this.is_active = function(id) {
        if (id == "")
            return true;
        var pieces = id.split(":");
        for (var i = 0; i < pieces.length; i++) {
            var id_part = pieces[i];
            if (id_part.indexOf("-") > -1) {
                id_part = id_part.split("-")[0];
            }

            if (!(id_part in this.active)) {
                return false;
            }
        }
        return true;
    }

    this.activate_cell = function(id) {
        var state = this;

        console.debug("activating " + escape_id(this.popout_id) + " " + escape_id(id));
        var table_id = $(escape_id(this.popout_id) + " " +
                         escape_id(id) + ".ientry").closest('table').attr("id");
        console.debug("table_id: " + table_id);

        $(escape_id(table_id) + " .ientry").map(function() {
            state.remove_ids($(this).attr("id"));
        });

        state.add_ids(id);

        state.refresh_visible();

        return "Active: " + JSON.stringify(this.active);
    }

    this.refresh_visible = function() {
        var state = this;

        $popout.find(".iopt").map(function() {
            var id = $(this).attr("id");
            if (state.is_active(id)) {
                $(this).addClass("show");
            } else {
                $(this).removeClass("show");
            }
        });

        $popout.find(".ientry").map(function() {
            var id = $(this).attr("id");
            var table = $(escape_id(id) + ".ientry").closest('table');
            var table_id = table.attr("id");

            if (id in state.collapse[table_id] &&
                    (state.collapse[table_id][id] === "*" ||
                     state.is_active(state.collapse[table_id][id]))) {
                $(this).addClass("hide");
                $(this).removeClass("active");
            } else {
                $(this).removeClass("hide");

                if (state.is_active(id)) {
                    $(this).addClass("active");
                } else {
                    $(this).removeClass("active");
                }
            }

            if (id in state.row_span[table_id] &&
                    (state.row_span[table_id][id] === "*" ||
                     state.is_active(state.row_span[table_id][id]))) {
                var num_rows = table.find("tr").length - 1;
                $(this).attr("rowspan", num_rows);
            } else {
                $(this).removeAttr("rowspan");
            }

            if (id in state.col_span[table_id] &&
                    (state.col_span[table_id][id] === "*" ||
                     state.is_active(state.col_span[table_id][id]))) {
                var num_cols = table.find("tr:first th").length - 1;
                $(this).attr("colspan", num_cols);
            } else {
                $(this).removeAttr("colspan");
            }
        });
    };

};

$(document).ready(function() {
    $(".ientry").click(function(event) {
        var popout_id = $(this).closest(".popout").attr("id");
        var id = $(this).attr("id");
        endings.state[popout_id].activate_cell(id);
    });

    if($(".popout-content").length > 1) {
        $(".popout-content").css({display: "none"});
        $(".popout-header").addClass("collapsed").text(function () {
            return "Show " + $(this).text();
        });
    }

    $(".popout-header").click(function () {
        // Make ending tables collapse and expand
        // http://jsfiddle.net/hungerpain/eK8X5/7/
        $header = $(this);
        //getting the next element
        $content = $header.next();
        //change text and appearance of header based on visibility of content div
        $header.toggleClass("collapsed");
        var text = $header.text();
        if ($header.hasClass("collapsed")) {
            $header.text(function () {
                return "Show " + text;
            });
        } else {
            $header.text(function () {
                return text.substring(5);
            });
        }
        //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
        $content.slideToggle(200);
    });

    for (var id in endings.state) {
        if (endings.state.hasOwnProperty(id)) {
            endings.state[id].refresh_visible();
        }
    }

});
