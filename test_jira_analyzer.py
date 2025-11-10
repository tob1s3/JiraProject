import unittest
from unittest.mock import patch, Mock
import sys
import os

# Добавляем путь к вашему коду
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Импортируем ВАШИ функции
from jira_analytics import calculate_time, get_jira_issues

class TestJiraAnalytics(unittest.TestCase):

    def test_calculate_time_correct(self):
        """Тест правильного расчета времени между датами"""
        created = "2023-01-01T10:00:00.000+0000"
        resolved = "2023-01-05T10:00:00.000+0000"
        result = calculate_time(created, resolved)
        self.assertEqual(result, 4)  # 4 дня разницы

    def test_calculate_time_same_day(self):
        """Тест расчета времени в тот же день"""
        created = "2023-01-01T10:00:00.000+0000"
        resolved = "2023-01-01T20:00:00.000+0000"
        result = calculate_time(created, resolved)
        self.assertEqual(result, 0)  # 0 дней разницы

    @patch('jira_analytics.requests.get')
    def test_get_jira_issues_success(self, mock_get):
        """Тест успешного получения задач из JIRA"""
        # Мокаем ответ от JIRA
        mock_response = Mock()
        mock_response.json.return_value = {
            'issues': [
                {
                    'key': 'KAFKA-1',
                    'fields': {
                        'created': '2023-01-01T10:00:00.000+0000',
                        'resolutiondate': '2023-01-05T10:00:00.000+0000',
                        'status': {'name': 'Closed'},
                        'summary': 'Test issue'
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        issues = get_jira_issues()
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['key'], 'KAFKA-1')

    @patch('jira_analytics.requests.get')
    def test_get_jira_issues_empty(self, mock_get):
        """Тест получения пустого списка задач"""
        mock_response = Mock()
        mock_response.json.return_value = {'issues': []}
        mock_get.return_value = mock_response

        issues = get_jira_issues()
        self.assertEqual(len(issues), 0)

    @patch('jira_analytics.requests.get')
    def test_get_jira_issues_network_error(self, mock_get):
        """Тест обработки ошибки сети"""
        mock_get.side_effect = Exception("Connection error")
        
        issues = get_jira_issues()
        self.assertEqual(issues, [])  # Должен вернуть пустой список при ошибке

if __name__ == '__main__':
    unittest.main()