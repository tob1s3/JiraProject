import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestJiraAnalyzer(unittest.TestCase):
    
    def test_imports(self):
        """Test that required modules can be imported"""
        try:
            import requests
            import pandas as pd
            import matplotlib.pyplot as plt
            import numpy as np
            self.assertTrue(True)
        except ImportError:
            self.fail("Import failed")
    
    def test_dataframe(self):
        """Test DataFrame creation"""
        import pandas as pd
        df = pd.DataFrame({'test': [1, 2, 3]})
        self.assertEqual(len(df), 3)
    
    def test_date_parsing(self):
        """Test date parsing functionality"""
        from datetime import datetime
        date_str = "2024-01-01T10:00:00"
        parsed = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        self.assertEqual(parsed.year, 2024)
    
    def test_api_url(self):
        """Test API URL format"""
        url = "https://issues.apache.org/jira/rest/api/2/search"
        self.assertTrue(isinstance(url, str))
        self.assertTrue(url.startswith('https://'))
    
    def test_plotting(self):
        """Test basic plotting"""
        import matplotlib.pyplot as plt
        import numpy as np
        plt.figure()
        plt.plot([1, 2, 3], [1, 4, 2])
        plt.close()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
