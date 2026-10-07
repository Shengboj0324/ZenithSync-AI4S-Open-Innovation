import hashlib

import pytest

from zenithsync.farin import load_farin, REQUIRED


def fixture_file(tmp_path, rows):
    path = tmp_path/'example.txt'
    payload = ('\t'.join(REQUIRED)+'\n'+'\n'.join('\t'.join(row) for row in rows)+'\n').encode()
    path.write_bytes(payload)
    return path, hashlib.sha256(payload).hexdigest()


def row(number='1', dose='DMSO', replicate='1', used='100'):
    return [number, 'O01', 'Monoculture', '', 'Gef', dose, replicate, '100', used]


def test_preserves_author_exclusion_and_source_identity(tmp_path):
    path, digest = fixture_file(tmp_path, [row(), row('2', '.1', used='cells lost')])
    data = load_farin(path, expected_sha256=digest)
    assert data.eligible.tolist() == [True, False]
    assert data.source_row.tolist() == [1, 2]
    assert data.author_exclusion.tolist() == ['', 'cells lost']
    assert data.raw_luminescence.tolist() == [100, 100]
    with pytest.raises(ValueError, match='hash'):
        load_farin(path)


@pytest.mark.parametrize('rows', [[row(), row('2', '0.0')], [row(), row('2')]])
def test_ambiguous_dose_or_replicate_quarantines_entire_curve(tmp_path, rows):
    path, digest = fixture_file(tmp_path, rows)
    data = load_farin(path, expected_sha256=digest)
    assert data.ambiguous_curve.all()
    assert not data.eligible.any()


def test_unknown_exclusion_is_not_silently_missing(tmp_path):
    path, digest = fixture_file(tmp_path, [row(used='unrecognized')])
    with pytest.raises(ValueError, match='annotation'):
        load_farin(path, expected_sha256=digest)
