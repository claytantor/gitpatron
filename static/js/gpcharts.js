/**
 * Created by claytongraham on 7/16/14.
 * the c3 charts does not have jquery metaphore so I am making a widget
 *
 */
(function ( $ ) {

    $.fn.gpchart_basic = function(chart_data) {

        if(this.length>0){
            var chart_id = "#"+this[0].id;

            var chart = c3.generate({
                bindto: chart_id,
                data: chart_data
            });

            return chart;
        }
    };


    $.fn.gpchart_timeseries = function(chart_data) {

        if(chart_data.is_paid){
            $(this).addClass('gitpatron-chart-paid');
        } else {
            $(this).addClass('gitpatron-chart-open');
        }


        if(this.length>0){
            var chart_id = "#"+this[0].id;

            var chart = c3.generate({
                bindto: chart_id,
                data: chart_data,
                axis: {
                    x: {
                        type: 'timeseries',
                        tick: {
                            format: '%Y-%m-%d'
                        }
                    }
                }
            });

            return chart;
        }
    };

}( jQuery ));

