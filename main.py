import yaml
import argparse
import src.service.configuration.configuration_parser as config_parser

parser = argparse.ArgumentParser(description="ExpenseFetcher")
parser.add_argument(
    "--config-file", dest="config_file", help="expense fetcher config file path"
)

args = parser.parse_args()

print(args.config_file)

config = yaml.load(open(args.config_file), Loader=yaml.FullLoader)


def build_sync_flows(config):
    assert "calendars" in config and "sync" in config
    calendars_by_name = config_parser.parse_calendars(config["calendars"])
    sync_flows_by_name = config_parser.parse_sync_flows(config["sync"], calendars_by_name)
    return sync_flows_by_name


flows_by_name = build_sync_flows(config)
for flow_name in flows_by_name.keys():
    print(f"Synchronizing {flow_name}")
    flows_by_name[flow_name].sync()

