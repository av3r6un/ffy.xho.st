import unittest

from src.services.proxy import _parse_segment_ranges


def mp4_box(box_type: bytes, payload: bytes) -> bytes:
  return (len(payload) + 8).to_bytes(4, 'big') + box_type + payload


class ParseSegmentRangesTests(unittest.TestCase):
  def test_finds_sidx_after_large_moov_box(self):
    ftyp = mp4_box(b'ftyp', b'isom')
    moov = mp4_box(b'moov', b'\0' * (1024 * 1024))
    sidx = mp4_box(b'sidx', b'\0' * 32)

    initialization, index = _parse_segment_ranges(ftyp + moov + sidx)

    self.assertEqual(initialization, (0, len(ftyp) + len(moov) - 1))
    self.assertEqual(
      index,
      (len(ftyp) + len(moov), len(ftyp) + len(moov) + len(sidx) - 1),
    )

  def test_rejects_data_without_sidx(self):
    data = mp4_box(b'ftyp', b'isom') + mp4_box(b'moov', b'\0' * 32)

    with self.assertRaisesRegex(ValueError, 'Unable to locate MP4 sidx box'):
      _parse_segment_ranges(data)


if __name__ == '__main__':
  unittest.main()
