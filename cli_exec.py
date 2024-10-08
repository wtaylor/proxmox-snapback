import subprocess
import json

def _raw_execute_pct_list():
    return subprocess.run(['pct', 'list'], text=True, capture_output=True)


def get_all_pct_ids():
    raw_pct_list_exec = _raw_execute_pct_list().stdout
    lines = raw_pct_list_exec.strip().split('\n')
    pct_ids = []
    for line in lines[1:]:
        pct_ids.append(int(line[0:3]))
    return pct_ids


def _raw_execute_get_pct_config(pct_id):
    return subprocess.run(['pct', 'config', f'{pct_id}'], text=True, capture_output=True)


def get_pct_config(pct_id):
    raw_cli_exec = _raw_execute_get_pct_config(pct_id).stdout
    return dict((a.strip(), b.strip())
                for a, b in (line.split(':', 1)
                             for line in raw_cli_exec.strip().split('\n')))


def _raw_execute_pct_snapshot_create(pct_id, snap_name):
    return subprocess.run(['pct', 'snapshot', f'{pct_id}', f'{snap_name}'], text=True, capture_output=True)


def snapshot_ct(pct_id, snap_name):
    return _raw_execute_pct_snapshot_create(pct_id, snap_name)


def _raw_execute_pct_snapshot_destroy(pct_id, snap_name):
    return subprocess.run(['pct', 'delsnapshot', f'{pct_id}', f'{snap_name}', '--force'], text=True, capture_output=True)


def delete_snapshot(pct_id, snap_name):
    return _raw_execute_pct_snapshot_destroy(pct_id, snap_name)


def _raw_execute_snapshot_mount(zfs_dataset_snapshot_uid, mountpoint):
    return subprocess.run(['mount', '-t', 'zfs', f'{zfs_dataset_snapshot_uid}', f'{mountpoint}'], text=True, capture_output=True)


def _raw_execute_pvesm_path(volume_name):
    return subprocess.run(['pvesm', 'path', f'{volume_name}'], text=True, capture_output=True)


def _raw_execute_pvesh_get_json(resource: str):
    return subprocess.run(['pvesh', 'get', resource, '--output-format', 'json'], text=True, capture_output=True)


def pvesh_get_json(resource: str):
    return json.loads(_raw_execute_pvesh_get_json(resource).stdout)


def mount_zfs_dataset_snapshot(zfs_dataset_snapshot_uid, mountpoint):
    return _raw_execute_snapshot_mount(zfs_dataset_snapshot_uid, mountpoint)


def get_zfs_dataset_uid_of_ct_volume(volume_name):
    volume_components = volume_name.split(':')
    storage_pool_info = pvesh_get_json(f"/storage/{volume_components[0]}")
    return f"{storage_pool_info['pool']}/{volume_components[1]}"


def _raw_execute_umount(path):
    return subprocess.run(['umount', path], text=True, capture_output=True)


def umount(path):
    return _raw_execute_umount(path)
