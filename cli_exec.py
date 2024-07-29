import subprocess


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


def _raw_execute_pct_snapshot_create(pct_id, run_id):
    return subprocess.run(['pct', 'snapshot', f'{pct_id}'], text=True, capture_output=True)


def _raw_execute_pct_snapshot_destroy(pct_id, run_id):
    print("TODO")


def _raw_execute_snapshot_mount(pct_id, run_id, mount_root):
    print("TODO")

