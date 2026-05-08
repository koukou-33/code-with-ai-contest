import unittest

import pandas as pd

from app import filter_signal_data, normalize_column_height, signal_color


class SignalDashboardTest(unittest.TestCase):
    def test_signal_color_thresholds(self):
        self.assertEqual(signal_color(-89.9), [43, 180, 92, 190])
        self.assertEqual(signal_color(-100), [244, 171, 54, 190])
        self.assertEqual(signal_color(-110.1), [221, 64, 64, 190])

    def test_filter_signal_data_combines_all_sidebar_filters(self):
        df = pd.DataFrame(
            {
                "Band": ["n78", "n41", "n78"],
                "TerminalType": ["CPE", "IoT", "Smartphone"],
                "RSRP_dBm": [-88, -111, -95],
                "SINR_dB": [20, 5, -2],
            }
        )

        filtered = filter_signal_data(
            df,
            bands=["n78"],
            terminals=["CPE", "Smartphone"],
            rsrp_range=(-100, -80),
            sinr_range=(0, 30),
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]["TerminalType"], "CPE")

    def test_normalize_column_height_handles_flat_series(self):
        heights = normalize_column_height(pd.Series([10, 10, 10]))
        self.assertEqual(heights.tolist(), [120, 120, 120])


if __name__ == "__main__":
    unittest.main()
