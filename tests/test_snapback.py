import snapback
import cli_exec


def test_is_ct_snapback_enabled_returns_true_when_snapback_is_enabled():
    config = {
        'description': 'lxc-zfs-snapback%3A mp0%0A'
    }
    assert snapback.is_ct_snapback_enabled(config)


def test_is_ct_snapback_enabled_returns_false_when_ct_description_field_not_found():
    config = {}
    assert not snapback.is_ct_snapback_enabled(config)


def test_is_ct_snapback_enabled_returns_false_when_snapback_config_not_found():
    config = {
        'description': 'my lxc'
    }
    assert not snapback.is_ct_snapback_enabled(config)


def test_get_pct_snapback_config_parses_correctly():
    ct_id = 200
    config = {
        'hostname': 'my-host',
        'description': 'lxc-zfs-snapback%3A mp0%0A',
        'mp0': 'local-zfs:subvol-200-disk-0,mp=/mnt/index,backup=1,size=32G'
    }
    snapback_config = snapback.get_pct_snapback_config(ct_id, config)
    assert snapback_config == {
        'hostname': config['hostname'],
        'id': ct_id,
        'target_volumes': ['local-zfs:subvol-200-disk-0']
    }