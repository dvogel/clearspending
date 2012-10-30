$(document).ready(function(){

    var itemgetter = function (k) {
        return function (o) {
            return o[k];
        };
    };

    var short_money = function (n) {
        var sizes = [
            ['trillion', Math.pow(10, 12)],
            ['billion', Math.pow(10, 9)],
            ['million', Math.pow(10, 6)],
            ['thousand', Math.pow(10, 3)]
        ];
        for (var ix = 0; ix < sizes.length; ix++) {
            var label = sizes[ix][0];
            var dollars = sizes[ix][1];
            if (n >= dollars) {
                short_n = Math.round(n / dollars, 2);
                return "$" + short_n.toString() + " " + label;
            }
        }
        return "$" + n
    };

    var initials = function (name) {
        var first_clause = function (s) {
            return s.split(',')[0];
        };
        var first_letter = function (s) {
            return s.substr(0, 1);
        };
        var bad_words = function (s) {
            return ["of", "for", "and", "the", "United", "States"].indexOf(s) < 0;
        };

        return first_clause(name).split(/\s+/g)
                                 .filter(bad_words)
                                 .map(first_letter)
                                 .join('');
    };

    var default_chart_year = function () {
        var years = $("span.fiscal_year_chooser").map(function(){ return $(this).text(); });
        var max_year = Math.max.apply(null, years);
        return max_year;
    };


    var consistency_treemap = function (options) {
        var options = options || {};
        var default_to = function (opt, val) { options[opt] = options[opt] || val; };
        default_to("width", 840);
        default_to("height", 520);
        default_to("element", "#chart");

        var cell = function (d, i) {
            this.style("left", function(d){ return d.x + "px"; })
                .style("top", function(d){ return d.y + "px"; })
                .style("width", function(d){ return Math.max(0, d.dx - 1) + "px"; })
                .style("height", function(d){ return Math.max(0, d.dy - 1) + "px"; });
        };

        var show_program_label = function (d) {
            if (d.children) {
                console.log(this);
            } else {
                var ag_prefix = d.number.split('.')[0];
                var ag_name = agencies[ag_prefix];
                var ag_inits = initials(ag_name);
                $("#program-description").text(d.title
                                               + " (CFDA program "
                                               + d.number
                                               + "), "
                                               + ag_name
                                               + ": "
                                               + short_money(d.size)
                                               );
                $("#status, #program-description").toggle();
            }
        };

        var reset_program_label = function (d) {
            if (d.children) {
            } else {
                $("#status, #program-description").toggle();
            }
        };

        var classify_datum = function (d) {
            if (d.non == -100.0) {
                return 'cell blind';
            } else if ((d.over >= 50.0) || (d.under >= 50.0)) {
                return 'cell fail';
            } else if ((d.over >= 0) || (d.under >= 0)) {
                return 'cell pass';
            } else if (d.children == null) {
                return 'cell perfect';
            } else {
                return 'cell category';
            }
        };

        var id_from_program_number = function (d) {
            if (d.children) {
                return "category_" + d.name;
            } else {
                return "program_" + d.number.toString().replace(".", "_");
            }
        };

        var show_consistency_flare = function (fiscal_year) {
            $(options["element"]).css("width", options["width"]).css("height", options["height"]).empty().append('<div class="chart-loading"><div>Loading...</div></div>');
            setTimeout(function(){

                var flare_url = "../static/data/consistency_flare_" + fiscal_year + "_categories.json";
                d3.json(flare_url, function(json){
                    var treemap = d3.layout.treemap()
                                    .size([options["width"], options["height"]])
                                    .sticky(true)
                                    .value(function(d){ return d.size; });

                    $(options["element"]).empty();

                    var chart = d3.select(options['element'])
                                  .append("div")
                                  .style("position", "relative")
                                  .style("width", options["width"] + "px")
                                  .style("height", options["height"] + "px");

                    var map = chart.data([json])
                                   .selectAll("div")
                                   .data(treemap.nodes);

                    map.enter()
                       .append("div")
                       .on("mouseover", show_program_label)
                       .on("mouseout", reset_program_label)
                       .on("click", function(d){
                           window.location.href = "/program/" + d.number + "/pct/";
                       })
                       .attr("class", classify_datum)
                       .attr("id", id_from_program_number)
                       .call(cell);

                    map.exit().remove();

                });
            }, 0);

            $("span.fiscal_year_chooser").each(function(){
                $(this).removeClass("selected");
                var year = parseInt($(this).text());
                if (year == fiscal_year) {
                    $(this).addClass("selected");
                }
            });
        };

        $("span.fiscal_year_chooser").click(function(event){
            show_consistency_flare(parseInt($(this).text()));
        });
        
        show_consistency_flare(default_chart_year());
    };

    var timeliness_chart = function (options) {
        var options = options || {};
        var default_to = function (opt, val) { options[opt] = options[opt] || val; };
        default_to("width", 280);
        default_to("height", 380);
        default_to("element", "#chart");

        var show_timeliness_chart = function (fiscal_year) {
            $(options["element"]).css("width", options["width"]).css("height", options["height"]).empty().append('<div class="chart-loading"></div>');
            setTimeout(function(){
                var flare_url = "" + fiscal_year + "/";
                d3.json(flare_url, function(json){
                    json.forEach(function(d){
                        d['delta_rows'] = d.lag_rows - 30;
                        d['delta_dollars'] = d.lag_dollars - 30;
                    });

                    json.sort(function(a,b){ return a.delta_rows - b.delta_rows; });

                    var chart = d3.select(options['element'])
                                  .append("svg")
                                  .attr("id", "timeliness-art")
                                  .style("width", options["width"] + "px")
                                  .style("height", options["height"] + "px");

                    var x = d3.scale
                              .ordinal()
                              .rangeRoundBands([0, options["width"]], 0.1)
                              .domain(json.map(function(d){ return d.title; }));

                    y_min = d3.min(json.map(function(d){ return d.delta_rows; }));
                    y_max= d3.max(json.map(function(d){ return d.delta_rows; }));
                    y = d3.scale
                              .linear()
                              .range([0, options["width"]])
                              .domain([y_min, y_max]);
                    var on_time_xcoord = y(0);

                    var bars = chart.selectAll("g.bar")
                                    .data(json)
                                    .enter()
                                    .append("g")
                                    .attr("data-agency-code", function(d){ return d.number; })
                                    .attr("data-agency-name", function(d){ return d.title; })
                                    .attr("class", "bar")
                                    .attr("transform", function(d){
                                        return "translate(X, 0)".replace("X", '' + x(d.title));
                                    }).on("mouseover", function(d){
                                        $("#program-description").html(
                                            d.title
                                            + "<br> "
                                            + Math.abs(d.delta_rows)
                                            + " days "
                                            + ((d.delta_rows >= 0) ? "late" : "early")
                                        );
                                        $("#status, #program-description").toggle();
                                    }).on("mouseout", function(d){
                                        $("#status, #program-description").toggle();
                                    });

                    bars.append("rect")
                        .attr("class", function(d){
                            if (d.delta_rows > 0) {
                                return "bar fail";
                            } else {
                                return "bar pass";
                            }
                        })
                        .attr("x", 0)
                        .attr("y", function(d){
                            if (d.delta_rows > 0) {
                                return on_time_xcoord - 1;
                            } else {
                                return y(d.delta_rows) - 1;
                            }
                        })
                        .attr("height", function(d){
                            if (d.delta_rows > 0) {
                                return y(d.delta_rows) - on_time_xcoord + 2;
                            } else {
                                return on_time_xcoord - y(d.delta_rows) + 2;
                            }
                        })
                        .attr("width", x.rangeBand());

/*
                    bars.append("text")
                        .attr("class", "delta-label")
                        .attr("x", 1)
                        .attr("y", y.rangeBand() / 2)
                        .attr("dy", "0.35em")
                        .attr("text-anchor", function(d){ return (d.delta_rows >= 0) ? "end" : "start"; })
                        .text(function(d){ return "" + d.delta_rows + " days"; }) */
                });

            }, 0);

            $("span.fiscal_year_chooser").each(function(){
                $(this).removeClass("selected");
                var year = parseInt($(this).text());
                if (year == fiscal_year) {
                    $(this).addClass("selected");
                }
            });
        };

        $("span.fiscal_year_chooser").click(function(event){
            show_timeliness_chart(parseInt($(this).text()));
        });

        show_timeliness_chart(default_chart_year());
    };


    var completeness_diagram = function (options) {
        var options = options || {};
        var default_to = function (opt, val) { options[opt] = options[opt] || val; };
        default_to("width", 840);
        default_to("height", 380);
        default_to("element", "#chart");

        var chart = d3.select(options['element'])
                      .append("svg")
                      .attr("id", "timeliness-art")
                      .style("width", options["width"] + "px")
                      .style("height", options["height"] + "px");

        var show_completeness_diagram = function (fiscal_year) {
            //$(options["element"]).css("width", options["width"]).css("height", options["height"]).empty().append('<div class="chart-loading"></div>');
            $("svg", options["element"]).empty();
            setTimeout(function(){
                var url = "" + fiscal_year + "/";
                var generic_compare = function (a, b) {
                    if (a == b) { return 0; }
                    else if (a < b) { return -1; }
                    else { return 1; }
                };
                d3.json(url, function(json){
                    json.sort(function(a,b){
                        var a_inits = initials(a.agency__name);
                        var b_inits = initials(b.agency__name);
                        return generic_compare(a_inits, b_inits);
                    });

                    var y = d3.scale
                              .ordinal()
                              .rangeRoundBands([0, options["height"]], 0.3)
                              .domain(json.map(itemgetter('agency__name')));

                    var col_fields = [
                        'principal_place_state', 'record_type',
                        'cfda_program_num', 'recipient_type',
                        'recipient_state', 'principal_place_cc',
                        'principal_place_code', 'recipient_county_code',
                        'assistance_type', 'federal_funding_amount',
                        'federal_agency_code', 'recipient_city_code',
                        'recipient_county_name', 'recipient_name',
                        'obligation_action_date', 'recipient_cong_district',
                        'recipient_city_name', 'federal_award_id',
                        'action_type' ];
                  
                    var x = d3.scale
                              .ordinal()
                              .rangeRoundBands([0, options["width"]], 0.15)
                              .domain(["agency__name"].concat(col_fields));

                    var bars = chart.selectAll("g.bar")
                                    .data(json)
                                    .enter()
                                    .append("g")
                                    .attr("class", "bar")
                                    .attr("transform", function(d){
                                        return "translate(0, Y)".replace("Y", y(d.agency__name));
                                    });

                    bars.append("rect")
                        .attr("class", "agency-name")
                        .attr("x", x("agency__name"))
                        .attr("y", 0)
                        .attr("width", x.rangeBand())
                        .attr("height", y.rangeBand());

                    bars.append("text")
                        .attr("class", "agency-name")
                        .attr("x", 1)
                        .attr("y", y.rangeBand() / 2)
                        .attr("dy", "0.35em")
                        .text(function(d){
                            return initials(d.agency__name);
                        });

                    for (var ix = 0; ix < col_fields.length; ix++) {
                        var col = col_fields[ix];
                        var pct_col = col + "_pct";

                        bars.append("rect")
                            .attr("class", function(d){
                                var val = d[pct_col] || 0;
                                var grade = (val == 0) ? "pass" : "fail";
                                return ["column", col,  grade].join(" ");
                            })
                            .attr("x", x(col))
                            .attr("y", 0)
                            .attr("width", x.rangeBand())
                            .attr("height", y.rangeBand())
                            .attr("opacity", function(d){
                                var val = d[pct_col];
                                if (val == null)
                                    val = 0;
                                if (val == 0)
                                    return 1;
                                return val;
                            });
                    }
                });
            }, 0);

            $("span.fiscal_year_chooser").each(function(){
                $(this).removeClass("selected");
                var year = parseInt($(this).text());
                if (year == fiscal_year) {
                    $(this).addClass("selected");
                }
            });
        };

        $("span.fiscal_year_chooser").click(function(event){
            show_completeness_diagram(parseInt($(this).text()));
        });

        show_completeness_diagram(default_chart_year());
    };

    if ($("body.consistency").length > 0) {
        consistency_treemap();
    };
    if ($("body.timeliness").length > 0) {
        timeliness_chart();
    };
    if ($("body.completeness").length > 0) {
        completeness_diagram();
    };
});
