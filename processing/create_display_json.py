import argparse
import json
import os
import logging

import shipping
import country
import geo
import trade

def find_closest_port(shipping_nodes, country):
    return shipping.get_nearest_port(shipping_nodes, country.lat, country.lon)

def get_all_paths(shipping_nodes, countries, trade_data, subject):
    paths = []
    ports = []
    from_node = find_closest_port(shipping_nodes, subject)
    from_node['name'] = subject.name

    ports.append(from_node)

    node_lookup = {}
    for node in shipping_nodes:
        node_id = node['node']
        node_lookup[node_id] = node

    for c in countries:
        if c.name == subject.name:
            continue

        print c.name

        to_node = find_closest_port(shipping_nodes, c)
        to_node['name'] = c.name
        ports.append(to_node)

        try:
            short_path = shipping.get_short_path(shipping_nodes, from_node['node'], to_node['node'])
        except:
            logging.warning('could not determine path for %s' % c.name)
            continue

        if c.name in trade_data:
            # Add in values to the path
            for node in short_path:
                if 'value' not in node:
                    node['value'] = 0
                node['value'] += trade_data[c.name]['2014']

        paths.append(short_path)

    return paths, ports

def normalise_weights(nodes, trade_data):
    total_value = float(trade_data['(Total)']['2014'])

    for node in nodes:
        node['weight'] = node['value'] / total_value

def combine_nodes_directed(all_paths):
    result = []
    nodes = {}

    for path in all_paths:
        path_count = len(path)

        for i in range(path_count):
            node_from = path[i]
            node_to = None

            if i + 2 <= path_count:
                node_to = path[i + 1]

            node_from_id = node_from['node']

            if node_from_id not in nodes:
                node = {
                    'node': node_from_id,
                    'lat': node_from['lat'],
                    'lon': node_from['lon'],
                    'edges': [],
                    'value': node_from['value']
                }

                result.append(node)
                nodes[node_from_id] = node
            else:
                node = nodes[node_from_id]

            if node_to and node_to['node'] not in node['edges']:
                node['edges'].append(node_to['node'])

    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--shipping')
    parser.add_argument('-c', '--countries')
    parser.add_argument('-d', '--tradedata')
    parser.add_argument('-o','--output', default='outputs')

    args = parser.parse_args()

    shipping_path = args.shipping
    countries_path = args.countries
    data_path = args.tradedata
    output_path = args.output

    if not os.path.exists(shipping_path):
        parser.error('Shipping path does not exist')
    if not os.path.exists(countries_path):
        parser.error('Countries path does not exist')
    if not os.path.exists(data_path):
        parser.error('Data path does not exist')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    shipping_data = shipping.read_path_json(shipping_path)
    nodes = shipping_data['nodes']

    trade_data = trade.read_csv(data_path)

    countries = country.read_json(countries_path)
    subject = None

    for c in countries:
        if c.name == 'New Zealand':
            subject = c
            break

    paths, ports = get_all_paths(nodes, countries, trade_data, subject)

    nodes = combine_nodes_directed(paths)
    normalise_weights(nodes, trade_data)

    shipping.write_path_json(os.path.join(output_path, 'paths.json'), nodes)
    shipping.write_port_json(os.path.join(output_path, 'ports.json'), ports)

if __name__ == "__main__":
    main()