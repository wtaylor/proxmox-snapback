#!/usr/bin/env python

import typing
import urllib.parse
import cli_exec
import argparse


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


def get_all_snapback_configs():
    all_ct_ids = cli_exec.get_all_pct_ids()
    all_ct_configs = [(ct_id, cli_exec.get_pct_config(ct_id)) for ct_id in all_ct_ids]
    return [get_pct_snapback_config(ct_config[0], ct_config[1]) for ct_config in all_ct_configs if is_ct_snapback_enabled(ct_config[1])]


def snapback_create(args):
    snapback_configs = get_all_snapback_configs()
    if args.verbose:
        print("Detected snapback configurations:")
        print(snapback_configs)

    for snapback_config in snapback_configs:
        print(f"Snapshotting CT: {snapback_config['id']} - {snapback_config['hostname']}...")
        cli_exec.snapshot_ct(snapback_config['id'], args.id)
        print(f"All CTs snapped successfully.")


def snapback_destroy(args):
    snapback_configs = get_all_snapback_configs()
    if args.verbose:
        print("Detected snapback configurations:")
        print(snapback_configs)

    for snapback_config in snapback_configs:
        print(f"Deleting snapshot \"{args.id}\" on CT: {snapback_config['id']} - {snapback_config['hostname']}...")
        cli_exec.delete_snapshot(snapback_config['id'], args.id)
        print(f"All CTs snapped successfully.")

def snapback_mount(args):
    snapback_configs = get_all_snapback_configs()
    if args.verbose:
        print("Detected snapback configurations:")
        print(snapback_configs)


if __name__ == "__main__":
    root_parser = argparse.ArgumentParser("snapback")
    sub_parsers = root_parser.add_subparsers(help="command help", required=True)
    root_parser.add_argument("--id", help="Unique id to identify the snapshot", required=True)
    root_parser.add_argument("--verbose", "-v", help="Verbose output", action="store_true")

    create_parser = sub_parsers.add_parser("create", help="Snapshot all Proxmox CTs with a valid snapback config")
    create_parser.set_defaults(func=snapback_create)

    mount_parser = sub_parsers.add_parser("mount", help="Mount all snapshots in a common root directory")
    mount_parser.add_argument("--mount_root", help="Parent directory to mount the snapshots in", required=True)

    destroy_parser = sub_parsers.add_parser("destroy", help="Destroy snapshots with the specified id for all CTs with a valid snapback config")

    args = root_parser.parse_args()
    args.func(args)
