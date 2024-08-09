import cli_exec
import subprocess
import re

valid_pct_list_output = """VMID       Status     Lock         Name
101        stopped                 failsafe-vpn
200        running                 seaweed-server
201        running                 nas-rp-server
203        running                 vault-server"""


def sample_pct_list_output():
    return subprocess.CompletedProcess(stdout=valid_pct_list_output, args=[], returncode=0)


valid_execute_pct_config_output = """
arch: amd64
cores: 2
description: lxc-zfs-snapback%3A mp0%0A
features: nesting=1
hostname: seaweed-server
memory: 4096
mp0: local-zfs:subvol-200-disk-0,mp=/mnt/index,backup=1,size=32G
net0: name=eth0,bridge=vmbr0,hwaddr=56:F7:FF:4C:E3:15,ip=dhcp,type=veth
onboot: 1
ostype: ubuntu
parent: backup-2024-07-16
rootfs: local-zfs:subvol-200-disk-4,size=32G
startup: order=1
swap: 512
unprivileged: 1
""".strip()


def sample_pct_config_output(pct_id):
    return subprocess.CompletedProcess(stdout=valid_execute_pct_config_output, args=[], returncode=0)


def sample_pvesm_path_output(volume_uid):
    volume_name = re.split(r':|,', volume_uid)[1]
    stdout = f"""
/rpool/data/{volume_name}
"""
    return subprocess.CompletedProcess(stdout=stdout, args=[], returncode=0)


def test_sample_pvesm_path_output_returns_expected_output():
    assert sample_pvesm_path_output('local-zfs:subvol-101-disk-0').stdout.strip() == '/rpool/data/subvol-101-disk-0'


def test_get_all_pct_ids_returns_list_of_pct_ids(monkeypatch):
    monkeypatch.setattr(cli_exec, '_raw_execute_pct_list', sample_pct_list_output)
    pct_ids = cli_exec.get_all_pct_ids()
    assert pct_ids == [101, 200, 201, 203]


def test_valid_pct_config_gets_converted_to_dict(monkeypatch):
    monkeypatch.setattr(cli_exec, '_raw_execute_get_pct_config', sample_pct_config_output)
    config = cli_exec.get_pct_config(200)
    required_config = {
        'mp0': 'local-zfs:subvol-200-disk-0,mp=/mnt/index,backup=1,size=32G',
        'hostname': 'seaweed-server',
        'description': 'lxc-zfs-snapback%3A mp0%0A',
    }

    assert required_config.items() <= config.items()
