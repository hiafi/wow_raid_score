import unittest
from WoWRaidScore.wcl_utils.wclogs_requests import WCLRequests


class TestWCLUtils(unittest.TestCase):

    def setUp(self):
        self.raid_id = "testraid"
        self.wcl_client = WCLRequests(self.raid_id)

    def test_single_params(self):
        self.assertEqual(self.wcl_client.build_single_filter_param("TestParam", "TestValue"), "TestParam=\"TestValue\"")
        self.assertEqual(self.wcl_client.build_single_filter_param("TestParam", ("<", "TestValue")), "TestParam<\"TestValue\"")

    def test_build_params(self):
        r = self.wcl_client._build_filters({"TestParam": "TestValue"})
        self.assertEqual(r, "&filter="+self.wcl_client._to_url("TestParam=\"TestValue\""))
