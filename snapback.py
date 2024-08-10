#!/usr/bin/env python

import typing
import urllib.parse
import cli_exec
import argparse
from pathlib import Path
from os import listdir
import logging


def is_ct_snapback_enabled(ct_config: typing.Dict[str, str]) -> bool:
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


def snapback_create(args, logger: logging.Logger) -> int:
    snapback_configs = get_all_snapback_configs()
    logger.debug("Detected snapback configurations:")
    logger.debug(snapback_configs)

    for snapback_config in snapback_configs:
        logger.info(f"Snapshotting CT: {snapback_config['id']} - {snapback_config['hostname']}...")
        cli_exec.snapshot_ct(snapback_config['id'], args.id)

    logger.info(f"All CTs snapped successfully.")
    return 0


def snapback_destroy(args, logger: logging.Logger) -> int:
    snapback_configs = get_all_snapback_configs()
    logger.debug("Detected snapback configurations:")
    logger.debug(snapback_configs)

    for snapback_config in snapback_configs:
        logger.info(f"Deleting snapshot \"{args.id}\" on CT: {snapback_config['id']} - {snapback_config['hostname']}...")
        cli_exec.delete_snapshot(snapback_config['id'], args.id)

    logger.info(f"Snapshot {args.id} deleted from all CTs successfully.")
    return 0


def snapback_mount(args, logger: logging.Logger) -> int:
    snapback_configs = get_all_snapback_configs()
    logger.debug("Detected snapback configurations:")
    logger.debug(snapback_configs)

    Path(args.mountpoint).mkdir(parents=True, exist_ok=True)
    if len(listdir(args.mountpoint)) > 0:
        logger.error(f"Root mount point: {args.mountpoint} is not empty, aborting.")
        return 1

    for snapback_config in snapback_configs:
        for volume in snapback_config['target_volumes']:
            zfs_snapshot_uid = f"{cli_exec.get_zfs_dataset_uid_of_ct_volume(volume)}@{args.id}"
            logger.debug(f"CT Volume: {volume} translated to ZFS Dataset Snapshot: {zfs_snapshot_uid}@{args.id}")

            volume_mount_point = f"{args.mountpoint}/{volume.replace(':', '--')}"
            logger.info(f"Mounting {volume} to {volume_mount_point}...")
            Path(volume_mount_point).mkdir(parents=False, exist_ok=False)
            mount_result = cli_exec.mount_zfs_dataset_snapshot(zfs_snapshot_uid, volume_mount_point)
            if mount_result.returncode != 0:
                logger.error(f"Failed to mount {volume}")
                logger.error(mount_result.stderr)
                return 1

    return 0


if __name__ == "__main__":
    root_parser = argparse.ArgumentParser("snapback")
    sub_parsers = root_parser.add_subparsers(help="command help", required=True)
    root_parser.add_argument("--id", help="Unique id to identify the snapshot", required=True)
    root_parser.add_argument("--verbose", "-v", help="Verbose output", action="store_true")

    create_parser = sub_parsers.add_parser("create", help="Snapshot all Proxmox CTs with a valid snapback config")
    create_parser.set_defaults(func=snapback_create)

    mount_parser = sub_parsers.add_parser("mount", help="Mount all snapshots in a common root directory")
    mount_parser.add_argument("--mountpoint", help="Parent directory to mount the snapshots in", required=True)
    mount_parser.set_defaults(func=snapback_mount)

    destroy_parser = sub_parsers.add_parser("destroy", help="Destroy snapshots with the specified id for all CTs with a valid snapback config")
    destroy_parser.set_defaults(func=snapback_destroy)

    args = root_parser.parse_args()
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logLevel)
    logger = logging.getLogger()

    exit(args.func(args, logger))
