import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import json
from collections import defaultdict

JIRA_URL = "https://issues.apache.org/jira"
PROJECT = "KAFKA"

def get_jira_issues():
    """Получение задач из JIRA"""
    url = f"{JIRA_URL}/rest/api/2/search"
    params = {
        "jql": f"project={PROJECT} AND status in (Closed, Resolved)",
        "maxResults": 500,
        "fields": "key,created,resolutiondate,status,reporter,assignee,priority,updated,worklog,timespent,aggregatetimespent"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        issues = data["issues"]
        print(f"Получено {len(issues)} задач")
        return issues
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return []

def get_issue_changelog(issue_key):
    """Получить историю изменений статусов задачи"""
    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/changelog"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None

def calculate_time_in_statuses(issue_key, created_date):
    """Рассчитать время в каждом статусе"""
    changelog = get_issue_changelog(issue_key)
    if not changelog or 'values' not in changelog:
        return {}
    
    status_times = defaultdict(timedelta)
    current_status = "Open"
    last_change = created_date
    
    for history in changelog['values']:
        for item in history['items']:
            if item['field'] == 'status':
                change_time = datetime.strptime(history['created'][:19], "%Y-%m-%dT%H:%M:%S")
                time_in_status = change_time - last_change
                status_times[current_status] += time_in_status
                current_status = item['toString']
                last_change = change_time
    
    # Добавляем время в текущем статусе до текущего момента
    final_time = datetime.now() - last_change
    status_times[current_status] += final_time
    
    # Конвертируем в дни
    status_days = {status: time.total_seconds() / (24 * 3600) for status, time in status_times.items()}
    return status_days

def process_issues(issues):
    """Обработка данных задач"""
    data = []
    status_data = []
    
    for issue in issues:
        try:
            fields = issue['fields']
            
            created = datetime.strptime(fields['created'][:19], "%Y-%m-%dT%H:%M:%S")
            resolved = datetime.strptime(fields['resolutiondate'][:19], "%Y-%m-%dT%H:%M:%S") if fields.get('resolutiondate') else None
            
            open_days = (resolved - created).days if resolved else (datetime.now() - created).days
            
            # Время выполнения (залогированное время)
            timespent = fields.get('timespent') or fields.get('aggregatetimespent') or 0
            worklog_hours = timespent / 3600 if timespent else 0
            
            reporter = fields.get('reporter', {}).get('displayName', 'Неизвестно')
            assignee = fields.get('assignee', {}).get('displayName', 'Не назначен')
            priority = fields.get('priority', {}).get('name', 'Не указан')
            status = fields.get('status', {}).get('name', 'Неизвестен')
            
            # Анализ времени по статусам
            status_times = calculate_time_in_statuses(issue['key'], created)
            for status_name, days_in_status in status_times.items():
                status_data.append({
                    'issue_key': issue['key'],
                    'status': status_name,
                    'days': days_in_status
                })
            
            data.append({
                'key': issue['key'],
                'created': created,
                'resolved': resolved,
                'open_days': open_days,
                'worklog_hours': worklog_hours,
                'reporter': reporter,
                'assignee': assignee,
                'priority': priority,
                'status': status,
                'timespent': timespent
            })
            
        except Exception as e:
            print(f"Ошибка обработки задачи {issue.get('key', 'unknown')}: {e}")
            continue
    
    print(f"Обработано {len(data)} задач")
    print(f"Собрано {len(status_data)} записей о времени в статусах")
    return pd.DataFrame(data), pd.DataFrame(status_data)

def plot_graph_1(df):
    """Гистограмма потраченного времени на решение задачи"""
    plt.figure(figsize=(12, 6))
    plt.hist(df['open_days'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    plt.xlabel('Дни в открытом состоянии')
    plt.ylabel('Количество задач')
    plt.title('1. Гистограмма потраченного времени на решение задачи')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_status_time_histograms(status_df):
    """Гистограммы распределения времени по состояниям"""
    statuses_to_plot = ['Open', 'Resolved', 'In Progress', 'Patch Available', 'Reopened']
    
    for status_name in statuses_to_plot:
        status_data = status_df[status_df['status'] == status_name]
        if len(status_data) > 0:
            plt.figure(figsize=(10, 6))
            plt.hist(status_data['days'], bins=20, color='lightcoral', edgecolor='black', alpha=0.7)
            plt.xlabel(f'Дни в состоянии {status_name}')
            plt.ylabel('Количество задач')
            plt.title(f'2.{statuses_to_plot.index(status_name)+1}. Распределение времени в состоянии {status_name}')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

def plot_graph_3(df):
    """График заведенных и закрытых задач с накопительным итогом"""
    # Фильтруем последние 90 дней
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    df_recent = df[df['created'] >= start_date]
    
    daily_created = df_recent.groupby(df_recent['created'].dt.date).size()
    daily_resolved = df_recent[df_recent['resolved'].notna()].groupby(
        df_recent[df_recent['resolved'].notna()]['resolved'].dt.date
    ).size()
    
    # Заполняем пропущенные даты
    all_dates = pd.date_range(start=start_date.date(), end=end_date.date())
    daily_created = daily_created.reindex(all_dates, fill_value=0)
    daily_resolved = daily_resolved.reindex(all_dates, fill_value=0)
    
    cumulative_created = daily_created.cumsum()
    cumulative_resolved = daily_resolved.cumsum()
    
    plt.figure(figsize=(14, 10))
    
    plt.subplot(2, 1, 1)
    plt.plot(daily_created.index, daily_created.values, label='Создано задач', marker='o', markersize=3, linewidth=2)
    plt.plot(daily_resolved.index, daily_resolved.values, label='Закрыто задач', marker='s', markersize=3, linewidth=2)
    plt.title('3. Ежедневное количество задач (последние 90 дней)')
    plt.ylabel('Количество задач')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.subplot(2, 1, 2)
    plt.plot(cumulative_created.index, cumulative_created.values, label='Всего создано', linewidth=3)
    plt.plot(cumulative_resolved.index, cumulative_resolved.values, label='Всего закрыто', linewidth=3)
    plt.title('Накопительный итог')
    plt.xlabel('Дата')
    plt.ylabel('Количество задач')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()

def plot_graph_4(df):
    """Топ-30 пользователей по количеству задач"""
    reporter_counts = df['reporter'].value_counts()
    assignee_counts = df['assignee'].value_counts()
    user_counts = reporter_counts.add(assignee_counts, fill_value=0)
    
    top_users = user_counts.nlargest(30)
    
    plt.figure(figsize=(12, 10))
    y_pos = np.arange(len(top_users))
    
    plt.barh(y_pos, top_users.values, color='lightgreen', alpha=0.7, edgecolor='grey')
    plt.yticks(y_pos, [name[:25] + '...' if len(name) > 25 else name for name in top_users.index])
    plt.xlabel('Количество задач')
    plt.ylabel('Пользователь')
    plt.title('4. Топ-30 пользователей по количеству задач\n(исполнитель или репортер)')
    plt.gca().invert_yaxis()
    
    for i, count in enumerate(top_users.values):
        plt.text(count + 0.5, i, str(int(count)), va='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()

def plot_graph_5(df):
    """Гистограмма времени выполнения задач (по залогированному времени)"""
    plt.figure(figsize=(12, 6))
    
    # Фильтруем задачи с ненулевым залогированным временем
    worklog_data = df[df['worklog_hours'] > 0]['worklog_hours']
    
    if len(worklog_data) > 0:
        plt.hist(worklog_data, bins=20, color='orange', edgecolor='black', alpha=0.7)
        plt.xlabel('Залогированное время (часы)')
        plt.ylabel('Количество задач')
        plt.title('5. Гистограмма времени выполнения задач\n(на основе залогированного времени)')
        plt.grid(True, alpha=0.3)
    else:
        plt.text(0.5, 0.5, 'Нет данных о залогированном времени', 
                ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
    
    plt.tight_layout()
    plt.show()

def plot_graph_6(df):
    """Распределение задач по степени серьезности (приоритету)"""
    priority_counts = df['priority'].value_counts()
    
    plt.figure(figsize=(10, 6))
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink']
    bars = plt.bar(priority_counts.index, priority_counts.values, 
                   color=colors[:len(priority_counts)], alpha=0.7, edgecolor='black')
    
    plt.xlabel('Приоритет')
    plt.ylabel('Количество задач')
    plt.title('6. Распределение задач по степени серьезности')
    plt.xticks(rotation=45)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def plot_graph_7(df):
    """Детальный анализ времени выполнения"""
    plt.figure(figsize=(12, 6))
    
    plt.hist(df['open_days'], bins=30, color='purple', alpha=0.7, edgecolor='black')
    
    mean_days = df['open_days'].mean()
    median_days = df['open_days'].median()
    
    plt.axvline(mean_days, color='red', linestyle='--', linewidth=2, 
                label=f'Среднее: {mean_days:.1f} дней')
    plt.axvline(median_days, color='blue', linestyle='--', linewidth=2,
                label=f'Медиана: {median_days:.1f} дней')
    
    plt.xlabel('Время выполнения (дни)')
    plt.ylabel('Количество задач')
    plt.title('7. Детальный анализ времени выполнения задач')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    print(f"Статистика времени выполнения:")
    print(f"Всего задач: {len(df)}")
    print(f"Минимальное время: {df['open_days'].min()} дней")
    print(f"Максимальное время: {df['open_days'].max()} дней")
    print(f"Среднее время: {mean_days:.1f} дней")
    print(f"Медианное время: {median_days:.1f} дней")

def main():
    print("Запуск анализатора задач JIRA...")
    print(f"Проект: {PROJECT}")
    print("=" * 50)
    
    issues = get_jira_issues()
    if not issues:
        print("Не удалось получить данные")
        return
    
    df, status_df = process_issues(issues)
    if df.empty:
        print("Нет данных для анализа")
        return
    
    print("\nСтроим графики...")
    print("=" * 50)
    
    # Построение всех графиков
    plot_graph_1(df)  # Время решения задач
    plot_status_time_histograms(status_df)  # Время по статусам (5 графиков)
    plot_graph_3(df)  # Ежедневная статистика
    plot_graph_4(df)  # Топ пользователей
    plot_graph_5(df)  # Залогированное время
    plot_graph_6(df)  # Распределение по приоритетам
    plot_graph_7(df)  # Детальный анализ
    
    print("\n" + "=" * 50)
    print("Все графики построены!")
    print(f"Итого построено: 11 графиков аналитики")

if __name__ == "__main__":
    main()