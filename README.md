# Leonardo

A Graphite Dashboard, massively inspired by the excellent [GDash](https://github.com/ripienaar/gdash) made by [ripienaar](https://github.com/ripienaar)

It was rewritten in Python.

Differences with Gdash :
- Configuration is in full YAML instead of a DSL.
- Ability to display multiple dashboards on a single page for comparison
- Zoom in/out

![Sample dashboard](https://github.com/prfalken/leonardo/raw/master/sample/dashboard.jpg)

Configuration
-------------

This dashboard is a Flask application. Have a look at [this documentation](http://flask.pocoo.org/docs/deploying/) if you want to deploy it in a production environment.

If you just want to play with it, simply install dependencies and launch the run script:

    # pip install pyyaml
    # pip install flask
    # ./run.py

Main configuration example is included in config/leonardo.yaml.example, you should rename it to
leonardo.yaml and adjust the main options here.

Two config options are mandatory in leonardo.yaml:
    
    * graphite: put your Graphite server url there
    * templatedir: directory where your dashboards are.

and additional options:

    * The title to show at the top of your Dashboard
    * How many columns of graphs to create, 3 by default.
    * How often dashboard page is refreshed, 30 sec by default.
    * The width of the graphs, 450 by default
    * The height of the graphs, 220 by default
    * Optional interval quick filters

Creating Dashboards
--------------------

You can have multiple top level categories of dashboard.  Just create directories
in the _templatedir_ for each top level category.

In each top level category create a sub directory with a short name for each new dashboard.

You need a file called _dash.yaml_ for each dashboard, here is a sample:

    name: Server-1
    description: Main System Metrics for server-1

Then create descriptions in files like _cpu.graph_ in the same directory, in pure YAML.
here is a sample:

    title: Combined CPU Usage
    vtitle: percent
    area: stacked
    description: The combined CPU usage
   
    fields:
        iowait: 
            color: red
            alias: IO Wait
            data: sumSeries(collectd.server-1.cpu.*.cpu.wait.value)
            cacti_style: si
   
        system:
            color: orange
            alias: System
            data: sumSeries(collectd.server-1.cpu.*.cpu.system.value)
            cacti_style: si
   
        user:
            color: 4169E1
            alias: User
            data: sumSeries(collectd.server.cpu.*.cpu.user.value)
            cacti_style: si

Template Directory Layout
--------------------------

The directory layout is such that you can have many groupins of dashboards each with
many dashboards underneath it, an example layout of your templates dir would be:

        graph_templates
        `-- virtualization
            |-- dom0
            |   |-- dash.yaml
            |   |-- iowait.graph
            |   |-- load.graph
            |   |-- system.graph
            |   |-- threads.graph
            |   `-- user.graph
            `-- kvm1
                |-- dash.yaml
                |-- disk_read.graph
                |-- disk_write.graph
                |-- ssd_read.graph
                `-- ssd_write.graph

Here we have a group of dashboards called 'virtualization' with 2 dashboards inside it
each with numerous graphs.

You can create as many groups as you want each with many dashboards inside.

Custom Time Intervals
--------------------

You can reuse your dashboards and adjust the time interval by using the following url
structure:

    http://gdash.example.com/System/Server-1/?from=-8d&until=-7d

This will display the _email_ dashboard with a time interval same day last week.

Quick interval filters shown in interface are configurable in _leonardo.yaml_ options sections. Eg:

    options:
      interval_filters:
        - label: 30 minutes
          from: -30min
          to: now
        - label: 24 hours
          from: -1day
        - label: 1 week
          from: -7day
        - label: 1 month
          from: -30day
        - label: 1 year
          from: -1year


Time Intervals Display
-----------------------

If you configure time intervals in the config file you can click on any graph in
the main dashboard view and get a view with different time intervals of the same
graph

    options:
        intervals:
            - [ "-1hour", "1 hour" ]
            - [ "-2hour", "2 hour" ]
            - [ "-1day", "1 day" ]
            - [ "-1month", "1 month" ]
            - [ "-1year", "1 year" ]

With this in place in the _leonardo.yaml_ clicking on a graph will show the 5 intervals
defined above of that graph

Full Screen Displays
---------------------

You can reuse your dashboards for big displays against a wall in your NOC or office
by using the following url structure:

    http://gdash.example.com/System/Server-1/?full=yes

This is how it looks :

![fullscreen dashboard](https://github.com/prfalken/leonardo/raw/master/sample/dashboard-full.png)



Include graphs from other dashboard
------------------------------------

This option from Gdash is not yet implemented in Leonardo.

Load dashboard properties from a external YAML file 
----------------------------------------------------

If you got a set of common properties that you want to reuse in the 
dashboard, you can load a external yaml file from in dash.yaml. 
The path is relative to the _templatedir_ and it does not support 
recursive includes.

Examples are a list of server colors, timezones, etc. In _dash.yaml_:

    include_properties: 
     - common.yml
     - black-theme.yml

Example _common.yml_:

    graph_properties: 
        timezone:         Europe/London
        hide_legend:      false

Example _black-theme.yml_:

    graph_properties: 
        background_color: white
        foreground_color: black
        vertical_mark_color: "#330000"


Additional Features on Leonardo
--------------------------------

I wrote Leonardo to be able to add features that I find useful in a production environment :

Multiple Dashboards
-------------------

You can use regexps in the search box to display multiple Dashboards at the same time.
That way you can compare dashboards with each other, which is very useful for instance when comparing several server metrics :

![Multiple Dashboards](https://github.com/prfalken/leonardo/raw/master/sample/multiple.png)


Zoom in/out
-----------

Using the + / -  buttons on a dashboard, you can zoom in or out. The number of columns will adapt automatically :

![Zoomed in](https://github.com/prfalken/leonardo/raw/master/sample/zoomed-in.png)

![Zoomed out](https://github.com/prfalken/leonardo/raw/master/sample/zoomed-out.png)

