#!/usr/bin/env python

import typing
import urllib.parse
import cli_exec


def get_all_pct_ids(pct_list_output):
    lines = pct_list_output.split('\n')
    pct_ids = []
    for line in lines[1:]:
        pct_ids.append(int(line[0:3]))
    return pct_ids


def parse_pct_config(pct_config_string):
    return dict((a.strip(), b.strip())
                for a, b in (line.split(':', 1)
                             for line in pct_config_string.split('\n')))


def is_ct_snapback_enabled(ct_config: typing.Dict[str, str]):
    return 'description' in ct_config and "lxc-zfs-snapback" in ct_config['description']


def get_pct_snapback_config(ct_id, ct_config: typing.Dict[str, str]):
    pct_description = urllib.parse.unquote(ct_config['description'])
    snapback_config_line = [line for line in pct_description.split('\n') if line.startswith("lxc-zfs-snapback:")][0].split('lxc-zfs-snapback:')[1]
    snapback_included_mountpoints = snapback_config_line.strip().replace(" ", "").split(',')

    return {
        'hostname': ct_config['hostname'],
        'id': ct_id,
        'target_volumes':  [ct_config[mp_def].split(',')[0].strip() for mp_def in snapback_included_mountpoints]
    }


if __name__ == "__main__":
    all_ct_ids = get_all_pct_ids(cli_exec.execute_pct_list())
    all_ct_configs = [(ct_id, parse_pct_config(cli_exec.execute_get_pct_config(ct_id))) for ct_id in all_ct_ids]
    ct_targets = [get_pct_snapback_config(ct_config[0], ct_config[1]) for ct_config in all_ct_configs if is_ct_snapback_enabled(ct_config[1])]
