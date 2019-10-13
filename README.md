# fronius-to-influx
Collect Fronius inverter data and save in Influxdb for Grafana. This tool collects the most basic Fronius inverter data for a most basic fotovoltaic setup. If your installation is more sophisticated, then probably some extra work will be reqired. 

# install reqirements
To install requirements:

    pip install -r requirements.txt

# run "production" environment
To run this tool with real inverter data, first copy the `src/dev.py` file to `src/prod.py` and adjust configuration (IP addresses, port numbers, user names and passwords):

    vim src/prod.py 

Then run:

    python src/prod.py

# install dev environment
To install dev environment:

    pip install -r requirements/dev.txt

# mock fronius server
To run mock fronius server:

    export FLASK_APP=json_server
    flask run

# run "development" environment
For development, I used this Grafana + Influx Docker image: https://hub.docker.com/r/philhawthorne/docker-influxdb-grafana/

Edit the `dev.py` file and adjust accordingly. Then run:

    python src/dev.py

# grafana dashboards
I put my dashboards in `grafana_dashboards` directory. Feel free to use them.

![Screenshot](img/screenshot.png?raw=true "Screenshot")
![Screenshot2](img/screenshot2.png?raw=true "Screenshot2")
![Screenshot3](img/screenshot3.png?raw=true "Screenshot3")
