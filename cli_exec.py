import subprocess


def execute_pct_list():
    return subprocess.run(['pct', 'list'], text=True, capture_output=True)


def execute_get_pct_config(pct_id):
    return subprocess.run(['pct', 'config', f'{pct_id}'], text=True, capture_output=True)


def execute_pct_snapshot_create(pct_id, run_id):
    return subprocess.run(['pct', 'snapshot', f'{pct_id}'], text=True, capture_output=True)


def execute_pct_snapshot_destroy(pct_id, run_id):
    print("TODO")


def execute_snapshot_mount(pct_id, run_id, mount_root):
    print("TODO")

