/**
 * Created by claytongraham on 7/16/14.
 * the c3 charts does not have jquery metaphore so I am making a widget
 *
 */
(function ( $ ) {

    $.fn.gpchart = function() {

        var chart_id = "#"+this[0].id;

        var chart = c3.generate({
            bindto: chart_id,
            data: {
              columns: [
                ['data1', 30, 200, 100, 400, 150, 250],
                ['data2', 50, 20, 10, 40, 15, 25]
              ]
            }
        });

        return chart;
    };

}( jQuery ));

