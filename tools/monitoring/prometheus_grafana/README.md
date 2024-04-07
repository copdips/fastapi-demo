# Prometheus and Grafana

## Prometheus Installation

```bash
cd ~/src
prometheus_version=2.51.1
wget https://github.com/prometheus/prometheus/releases/download/v${prometheus_version}/prometheus-${prometheus_version}.linux-amd64.tar.gz
tar xvfz prometheus-${prometheus_version}.linux-amd64.tar.gz
sudo cp prometheus-${prometheus_version}.linux-amd64/prometheus /usr/local/bin/
sudo cp prometheus-${prometheus_version}.linux-amd64/promtool /usr/local/bin/
```

## Prometheus configuration

```bash
sudo mkdir /etc/prometheus
sudo vim /etc/prometheus/prometheus.yml
```

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']
```

## Running Prometheus

```bash
prometheus --config.file=/etc/prometheus/prometheus.yml
http://localhost:9090
```

## Grafana Installation

From source:

```bash
cd ~/src
grafana_version=7.5.5
wget https://dl.grafana.com/oss/release/grafana-${grafana_version}.linux-amd64.tar.gz
tar xvfz grafana-${grafana_version}.linux-amd64.tar.gz
sudo cp -r grafana-${grafana_version} /usr/local/bin/grafana
```

From repository:

```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana
```

## Running Grafana

```bash
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

http://localhost:3000
#  default login: admin:admin
```

## Uninstalling Grafana

```bash
sudo systemctl stop grafana-server
sudo systemctl disable grafana-server
sudo apt-get remove grafana
```
