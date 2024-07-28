import snapback

valid_pct_list_output = """VMID       Status     Lock         Name
101        stopped                 failsafe-vpn
200        running                 seaweed-server
201        running                 nas-rp-server
203        running                 vault-server""".strip()

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


def test_get_all_pct_ids_returns_list_of_pct_ids():
    pct_ids = snapback.get_all_pct_ids(valid_pct_list_output)
    assert pct_ids == [101, 200, 201, 203]


def test_valid_pct_config_gets_converted_to_dict():
    config = snapback.parse_pct_config(valid_execute_pct_config_output)
    required_config = {
        'mp0': 'local-zfs:subvol-200-disk-0,mp=/mnt/index,backup=1,size=32G',
        'hostname': 'seaweed-server',
        'description': 'lxc-zfs-snapback%3A mp0%0A',
    }

    assert required_config.items() <= config.items()


def test_is_ct_snapback_enabled_returns_true_when_snapback_is_enabled():
    config = snapback.parse_pct_config(valid_execute_pct_config_output)
    assert snapback.is_ct_snapback_enabled(config)


def test_is_ct_snapback_enabled_returns_false_when_snapback_config_not_found():
    config = snapback.parse_pct_config(valid_execute_pct_config_output)
    config.pop('description')
    assert not snapback.is_ct_snapback_enabled(config)


def test_get_pct_snapback_config_parses_correctly():
    ct_id = 200
    config = snapback.parse_pct_config(valid_execute_pct_config_output)
    snapback_config = snapback.get_pct_snapback_config(ct_id, config)
    assert snapback_config == {
        'hostname': config['hostname'],
        'id': ct_id,
        'target_volumes': ['local-zfs:subvol-200-disk-0']
    }
