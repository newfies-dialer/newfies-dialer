/*calls*/
function call_report(report_type)
{
    // Call report without graph
    $.ajax({
        url: '/admin_call_report/',
        type: "GET",
        dataType: "html",
        data: "report_type="+report_type,
        async: false,
        cache: false,
        timeout: 30000,
        success: function(data) {
            //alert(data);
            $('#call_report').html(data);
        },
        error: function() {
            alert("Request failed");
        }
    });
}
function call_me(call_type)
{
    if (document.getElementById('id_report_today').checked)
    {
        report_type = 'today';
    }
    if (document.getElementById('id_report_seven').checked)
    {
        report_type = 'last_seven_days';
    }

    if(call_type == 'today' || call_type == 'seven_days')
    {
        var call_type_value = document.getElementById('id_call_type_select').value;

    }
    else{
        var call_type_value = call_type.options[call_type.selectedIndex].value;
    }
    //alert(call_type_value);
    //alert(report_type);

    // Update report & graph
    call_report(report_type);
    call_report_graph(call_type_value, report_type);
    return true;
}

function call_report_graph(call_type, report_type)
{
    // Call report via graph
    $.ajax({
        url: '/admin_call_report_graph/',
        type: "GET",
        dataType: "json",
        data: "call_type="+call_type+"&report_type="+report_type ,
        async: false,
        cache: false,
        timeout: 30000,
        success: function(data) {
            temp_json = data;
            // placeholder1 so div_id = 1
            plot_graph(temp_json, '1');
        },
        error: function() {
            alert("No Data found !!");
        }
    });
}

/*Campaign script*/
function campaign_report(report_type)
{
    // Campaign_report report without graph
    $.ajax({
        url: '/admin_campaign_report/',
        type: "GET",
        dataType: "html",
        data: "report_type="+report_type,
        async: false,
        cache: false,
        timeout: 30000,
        success: function(data) {
            //alert(data);
            $('#campaign_report').html(data);
        },
        error: function() {
            alert("Request failed");
        }
    });
}

function campaign_report_graph(report_type)
{
    // Campaign report via graph
    $.ajax({
        url: '/admin_campaign_report_graph/',
        type: "GET",
        dataType: "json",
        data: "report_type="+report_type ,
        async: false,
        cache: false,
        timeout: 30000,
        success: function(data) {
           // alert(data);
            temp_json = data;
            // placeholder2 so div_id = 1
            plot_graph(temp_json, '2');
        },
        error: function() {
            alert("Request failed");
        }
    });
}

function camp_click_me(report_type)
{
    campaign_report(report_type);
    campaign_report_graph(report_type);
    return true;
}

/*User infor script*/
function user_report(report_type)
{
    // User_report report without graph
    $.ajax({
        url: '/admin_user_report/',
        type: "GET",
        dataType: "html",
        data: "report_type="+report_type,
        async: false,
        cache: false,
        timeout: 30000,
        success: function(data) {
            //alert(data);
            $('#user_report').html(data);
        },
        error: function() {
            alert("Request failed");
        }
    });
}

function user_click_me(report_type)
{
    user_report(report_type);
    user_report_graph(report_type);
    return true;
}

function user_report_graph(report_type)
{
    // User report via graph
    $.ajax({
        url: '/admin_user_report_graph/',
        type: "GET",
        dataType: "json",
        data: "report_type="+report_type ,
        async: false,
        cache: false,
        timeout: 30000,
        success: function(data) {
            //alert(data);
            temp_json = data;
            // placeholder2 so div_id = 3
            plot_graph(temp_json, '3');
        },
        error: function() {
            alert("Request failed");
        }
    });
}


/*Plot graph common function*/
// Function for tooltip
function showTooltip(x, y, contents) {
    $('<div id="tooltip">' + contents + '</div>').css( {
        position: 'absolute',
        display: 'none',
        top: y + 5,
        left: x + 5,
        border: '1px solid #fdd',
        padding: '2px',
        'background-color': '#fee',
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

function plot_graph(temp_json, div_id)
{
    //alert(JSON.stringify(temp_json.user));
    var graph_start_date = JSON.stringify(temp_json.graph_start_date).replace(/['"]/g,'');
    var graph_end_date = JSON.stringify(temp_json.graph_end_date).replace(/['"]/g,'');
    var graph_type = JSON.stringify(temp_json.graph_type).replace(/['"]/g,'');
    //alert(graph_start_date);
    //alert(graph_end_date);

    if (graph_type == '')
    {
        graph_type = 'day';
    }
    //alert(graph_type);

    /* Plot graph -- LAST 7 Days */
    if (graph_type == 'day')
    {
        var d1 = [];
        $.each(temp_json.common, function(i,common_data){
            //(new Date(campaign.date)).getTime()
            d1.push([(new Date(common_data.date).getTime()), common_data.count]); //.getTime()
        });
        //alert(d1);

        $(function () {
            var stack = 0, bars = true, lines = false, steps = false;

            function plotWithOptions() {
                $.plot($("#placeholder"+div_id), [ d1 ], {
                    series: {
                        bars: { show: bars, barWidth: 60*60*1000*24 }
                        //bars: { show: bars, barWidth: 0.6 }
                    },
                    xaxis: {
                        mode: "time",
                        minTickSize: [1, String(graph_type)],
                        min: (new Date(graph_start_date)).getTime(),
                        max: (new Date(graph_end_date)).getTime()
                    },

                    grid: {
                        hoverable: true,
                        clickable: true,
                        backgroundColor: { colors: ["#fff", "#eee"] }
                    },
                    tooltip: true,
                });
            }
            plotWithOptions();
        });
    }

    /* Plot graph -- Today */
    if (graph_type == 'hour')
    {
        var d1 = [];
        $.each(temp_json.common, function(i,common_data){
            //(new Date(campaign.date)).getTime()
            d1.push([(new Date(common_data.date * 1000)), common_data.count]); //.getTime()
        });
        //alert(d1);

        $(function () {
            var stack = 0, bars = true, lines = false, steps = false;

            function plotWithOptions() {
                $.plot($("#placeholder"+div_id), [ d1 ], {
                    series: {
                        //bars: { show: bars, barWidth: 60*60*1000*24 }
                        bars: { show: bars, barWidth: 60*60*1000 }
                    },
                    xaxis: {
                        mode: "time",
                        minTickSize: [1, String(graph_type)],
                        min: (new Date(graph_start_date * 1000)), //Converting date from Python to Javascript
                        max: (new Date(graph_end_date * 1000)) // Converting date from Python to Javascript (You have to multiply by 1,000.)
                    },
                    grid: {
                        hoverable: true,
                        clickable: true,
                        backgroundColor: { colors: ["#fff", "#eee"] }
                    },
                    tooltip: true,
                });
            }
            plotWithOptions();
        });
    }

    // Bind tooltip with placeholder div
    var previousPoint = null;
    $("#placeholder"+div_id).bind("plothover", function (event, pos, item) {
        $("#x").text(pos.x.toFixed(2));
        $("#y").text(pos.y.toFixed(2));
        if (item) {

            if (previousPoint != item.dataIndex) {
                previousPoint = item.dataIndex;

                $("#tooltip").remove();
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);
                //alert(item);
                showTooltip(item.pageX, item.pageY,
                            Number(y));
            }
        }
        else {
                $("#tooltip").remove();
                previousPoint = null;
        }
    });
}
