# Leonardo Graphs Specification

Here is the list of configuration directives you can add in any .graph YAML files

Each .graph file represent a Graph that will be displayed on a dashboard.

Each directive represents an URL Parameter or a Function, as described in Graphite's Documentation:


## Parameters
See the [Graphite Documentation](http://graphite.readthedocs.org/en/1.0/url-api.html) for details on URL API Parameters

### *title*
This sets the main title at the top of the produced graph

    title: "A sample graph"

### *vtitle*
The vertical title that is shown along the left y axis of your graph

    vtitle: "bytes/sec"

### *width*
The physical width of the graph in pixels

    width: 800

### *height*
The physical height of the graph in pixels

    height: 600

### *from* and *until*
The timespan to graph for, this is specific in RRDTool [AT-Style](http://oss.oetiker.ch/rrdtool/doc/rrdfetch.en.html) time format

    from: "-2days"
    until: "-1days"

### *area*
This controls the area mode of the graph.  Graphite supports 3 modes at present:

    area: all

 * all - all graph fields are filled
 * first - the first field is stacked while the rest are lines
 * stacked - all graph fields are filled and stacked ontop of each other
 * none - everything are lines (default)

### *description*
This is just some text associated with the graph, it is not shown on any graph but dashboards and the like can access this in the ruby code

    description: "A graph of CPU usage"

### *hide_legend*
The main legend can be force disabled or enabled.  By default it will automatically be disabled if graphite thinks its too big but when set to _true_ it will always show and never when set to _false_
You can also set it to an integer : it will hide the legend only if the graph's height is under this value.

    hide_legend: true
    hide_legend: 400

### *ymin* and *ymax*
These are the minimum and maximum values of the graph, only points between these will be shown.

    ymin: 100
    ymax: 200

### *yunit_system*

The unit system for thousands, millions, etc. Graphite supports 3 systems at present:

    yunit_system: binary

 * si - powers of 1000 - K, M, G, T, P
 * binary - powers of 1024 - Ki, Mi, Gi, Ti, Pi
 * none - no interpretation (raw numbers)

### *draw_null_as_zero*
Draw missing data from graphite as 0

    draw_null_as_zero: true

### *linewidth*
Sets the global line width

    linewidth: 2

### *fontsize*
Sets the global font size

    fontsize: 15

### *fontbold*
Set all fonts to bold

    fontbold: true

### *fontname*
Set the name of the global font

    fontname: "mono"

### *timezone*
The timezone to convert all data into

    timezone: Europe\London

### *linemode*
Influence how all lines are drawn

    linemode: slope

or

    linemode: staircase

### *hide_grid*
Disables the grid on the graph

     hide_grid: false

### *major_grid_line_color* and *minor_grid_line_color*
Adjusts the colors for the grid lines

    minor_grid_line_color: "green"
    minor_grid_line_color: "#000"

### *theme*

Used to specify a template from _graphTemplates.conf_ to use for default
colors and graph styles.

    theme: name_of_theme

### *margin*

Used to specify a margin between the graph and image borders

    margin: 30

### *color_list*

Use one color of the list for each target.

    color_list:
     - FEA400
     - #00FF22
     - FFFF00
     - blue

### *unique_legend*

Display only unique legend items, removing any duplicates.

### *min_x_step*

Sets the minimum pixel-step to use between datapoints drawn.

### *area_alpha*

Takes a floating point number between 0.0 and 1.0 Sets the alpha (transparency) value of filled areas when using an areaMode

### *logbase*

If set, draws the graph with a logarithmic scale of the specified base (e.g. 10 for common logarithm)

### *vtitle_right*

In dual Y-axis mode, sets the title of the right Y-Axis (See: vtitle)



## Functions
See the [Graphite Documentation](http://graphite.readthedocs.org/en/1.0/functions.html) for details on Functions

The following properties can be applied to any single field and applies to that field only.  Fields appear in the graph in the order they are in the file.

The first argument - _iowait_ above - is the field name and should be unique for this graph.

### *data*
The main data for the field, this can be anything graphite will accept as a target.  There are a number of properties that you can apply to this data so you can generally keep this pretty simple even for derived data etc.

    fields:
          foo:
               data: fqdn.load.load
          load:
               data: sumSeries(*.load.load)


### *derivative*
The data is of an ever increasing type, you can derive the rate of change using this property.

     fields:
          foo:
               data: fqdn.cpu.iowait
               derivative: true

Corresponds to the graphite function *derivative()*

### *scale*
Some data are in milliseconds and you might want it in seconds, this let you scale the data by some fraction.

     fields:
          foo:
               data: fqdn.cpu.iowait
               scale: 0.001

Corresponds to the graphite function *scale()*

### *scale_to_seconds*
With derivative data, scale the data automatically to the desired rate in seconds. For example, put 60 to display the rate per minute.

     fields:
          foo:
               data: fqdn.disk.reads
               derivative: true
               scale_to_seconds: 1

Corresponds to the graphite function *scaleToSeconds()*

### *line*
Sometimes you have infrequent data like git commits.  This allow you to draw any non zero value as a vertical line.

     fields:
          foo:
               data: site.deploy
               line: true

Corresponds to the graphite function *drawAsInfinite()*

### *color*
Sets the line color either to one of graphites well known types or a hex value

     fields:
          foo:
               data: site.deploy
               line: true
               color: red

Corresponds to the graphite function *color()*

### *dashed*
Causes a line to be drawn as a dashed line rather than solid

     fields:
          foo:
               data: site.deploy
               line: true
               dashed: true

Corresponds to the graphite function *dashed()*

### *second_y_axis*
Since graphite 0.9.9 you can draw data using both y axis, this allows you to set a specific field on the 2nd y axis

     fields:
          foo:
               data: fqdn.cpu.iowait
               scale: 0.001
               second_y_axis: true

Corresponds to the graphite function *secondYAxis()*

### *alias*
You can set a custom legend caption for this field.  By default this will be the graph name capitalized but you can adjust that easily.

     fields:
          io_wait:
               data: fqdn.cpu.iowait
               scale: 0.001
               alias: "IO Wait"

Without the alias property the graph caption would have been *Io_wait*.

Corresponds to the graphite function *alias()*

### *no_alias*
Disables automatic aliasing of targets

### *cacti_style*
Renders a data item in the same style as Cacti using current, min and max legends.

     fields:
          io_wait:
               data: fqdn.cpu.iowait
               scale: 0.001
               alias: "IO Wait"
               cacti_style: true

### *highest_average*
Draws the top n servers with the highest average value.

     fields:
          io_wait:
               data: *.cpu.iowait
               scale: 0.001
               alias: IO Wait
               highest_average: 5

### *alias_by_node*
Alias values based on a sub part of the data item names. For a negative index value, the number of the sub parts is added to the index.

     fields:
          io_wait:
               data: *.cpu.iowait
               scale: 0.001
               alias_by_node: 0

This will create graphs with items aliased by the first part of each data item

### *alias_sub*
Run series names through a regex search/replace.

     fields:
          io_wait:
               data: *.disk.*.reads
               alias_sub_search: '.*(\w+)\.reads'
               alias_sub_replace: 'disk \1'

Corresponds to the graphite function *aliasSub()*

### *legend_value*
Appends a value to the metric, one of last, avg, total, min or max.  Mutually exclusive to the above *cacti_style* option

     fields:
          io_wait:
               data: *.cpu.iowait
               scale: 0.001
               legend_value: avg

### *field_linewidth*
The linewidth for this one specific field

     fields:
          io_wait:
               data: *.cpu.iowait
               field_linewidth: 2
               legend_value: avg
