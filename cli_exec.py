import subprocess


def execute_pct_list():
    return subprocess.run(['pct', 'list'])


def execute_get_pct_config(pct_id):
    return subprocess.run(['pct', 'config', f'{pct_id}'])
