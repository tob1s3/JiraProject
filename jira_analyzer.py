import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

JIRA_URL = "https://issues.apache.org/jira"
PROJECT = "KAFKA"

def get_jira_issues():
    """Получение задач из JIRA"""
    url = f"{JIRA_URL}/rest/api/2/search"
    params = {
        "jql": f"project={PROJECT} AND status in (Closed, Resolved)",
        "maxResults": 300,
        "fields": "key,created,resolutiondate,status,reporter,assignee,priority,timespent,worklog,updated"
    }
    
    try:
        print("Получаем данные из JIRA...")
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        issues = data["issues"]
        print(f"Получено {len(issues)} задач")
        return issues
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return []

def process_issues(issues):
    """Обработка данных задач"""
    data = []
    
    for issue in issues:
        try:
            fields = issue['fields']
            
            if not fields.get('created') or not fields.get('resolutiondate'):
                continue
                
            created = datetime.strptime(fields['created'][:19], "%Y-%m-%dT%H:%M:%S")
            resolved = datetime.strptime(fields['resolutiondate'][:19], "%Y-%m-%dT%H:%M:%S")
            open_days = (resolved - created).days
            
            # Время выполнения (залогированное время)
            timespent = fields.get('timespent') or 0
            worklog_hours = timespent / 3600 if timespent else 0
            
            reporter = fields.get('reporter', {}).get('displayName', 'Неизвестно')
            assignee = fields.get('assignee', {}).get('displayName', 'Не назначен')
            priority = fields.get('priority', {}).get('name', 'Не указан')
            status = fields.get('status', {}).get('name', 'Неизвестен')
            
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
            continue
    
    print(f"Обработано {len(data)} задач")
    return pd.DataFrame(data)

def plot_graph_1(df):
    """Гистограмма потраченного времени на решение задачи"""
    plt.figure(figsize=(12, 6))
    plt.hist(df['open_days'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    plt.xlabel('Дни в открытом состоянии')
    plt.ylabel('Количество задач')
    plt.title('Гистограмма потраченного времени на решение задачи')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_graph_2(df):
    """Гистограмма распределения времени в состоянии Open"""
    plt.figure(figsize=(10, 6))
    plt.hist(df['open_days'], bins=20, color='lightcoral', edgecolor='black', alpha=0.7)
    plt.xlabel('Дни в состоянии Open')
    plt.ylabel('Количество задач')
    plt.title('Гистограмма распределения времени в состоянии Open')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_graph_3(df):
    """Гистограмма распределения времени в состоянии Resolved"""
    resolved_tasks = df[df['status'] == 'Resolved']
    if len(resolved_tasks) > 0:
        plt.figure(figsize=(10, 6))
        plt.hist(resolved_tasks['open_days'], bins=20, color='lightgreen', edgecolor='black', alpha=0.7)
        plt.xlabel('Дни в состоянии Resolved')
        plt.ylabel('Количество задач')
        plt.title('Гистограмма распределения времени в состоянии Resolved')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

def plot_graph_4(df):
    """Гистограмма распределения времени в состоянии In Progress"""
    in_progress_tasks = df[df['status'].str.contains('Progress', na=False)]
    if len(in_progress_tasks) > 0:
        plt.figure(figsize=(10, 6))
        plt.hist(in_progress_tasks['open_days'], bins=15, color='orange', edgecolor='black', alpha=0.7)
        plt.xlabel('Дни в состоянии In Progress')
        plt.ylabel('Количество задач')
        plt.title('Гистограмма распределения времени в состоянии In Progress')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

def plot_graph_5(df):
    """Гистограмма распределения времени в состоянии Patch Available"""
    patch_tasks = df[df['status'].str.contains('Patch', na=False)]
    if len(patch_tasks) > 0:
        plt.figure(figsize=(10, 6))
        plt.hist(patch_tasks['open_days'], bins=10, color='purple', edgecolor='black', alpha=0.7)
        plt.xlabel('Дни в состоянии Patch Available')
        plt.ylabel('Количество задач')
        plt.title('Гистограмма распределения времени в состоянии Patch Available')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

def plot_graph_6(df):
    """Гистограмма распределения времени в состоянии Reopened"""
    reopened_tasks = df[df['status'].str.contains('Reopen', na=False)]
    if len(reopened_tasks) > 0:
        plt.figure(figsize=(10, 6))
        plt.hist(reopened_tasks['open_days'], bins=10, color='brown', edgecolor='black', alpha=0.7)
        plt.xlabel('Дни в состоянии Reopened')
        plt.ylabel('Количество задач')
        plt.title('Гистограмма распределения времени в состоянии Reopened')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

def plot_graph_7(df):
    """График заведенных и закрытых задач с накопительным итогом"""
    # Фильтруем последние 90 дней
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    df_recent = df[df['created'] >= start_date]
    
    daily_created = df_recent.groupby(df_recent['created'].dt.date).size()
    daily_resolved = df_recent.groupby(df_recent['resolved'].dt.date).size()
    
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
    plt.title('График заведенных и закрытых задач с накопительным итогом')
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

def plot_graph_8(df):
    """Гистограмма топ-30 пользователей по количеству задач"""
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
    plt.title('Гистограмма топ-30 пользователей по количеству задач\n(исполнитель или репортер)')
    plt.gca().invert_yaxis()
    
    for i, count in enumerate(top_users.values):
        plt.text(count + 0.5, i, str(int(count)), va='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()

def plot_graph_9(df):
    """Гистограмма времени выполнения задач"""
    plt.figure(figsize=(12, 6))
    
    # Используем open_days как время выполнения
    plt.hist(df['open_days'], bins=25, color='orange', edgecolor='black', alpha=0.7)
    plt.xlabel('Время выполнения (дни)')
    plt.ylabel('Количество задач')
    plt.title('Гистограмма времени выполнения задач')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_graph_10(df):
    """График распределения задач по степени серьезности"""
    priority_counts = df['priority'].value_counts()
    
    plt.figure(figsize=(10, 6))
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink']
    bars = plt.bar(priority_counts.index, priority_counts.values, 
                   color=colors[:len(priority_counts)], alpha=0.7, edgecolor='black')
    
    plt.xlabel('Приоритет (степень серьезности)')
    plt.ylabel('Количество задач')
    plt.title('График распределения задач по степени серьезности')
    plt.xticks(rotation=45)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def plot_graph_11(df):
    """Дополнительный анализ - статистика по времени"""
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
    plt.title('Анализ времени выполнения задач')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def main():
    print("Запуск анализатора задач JIRA...")
    print(f"Проект: {PROJECT}")
    print("=" * 50)
    
    issues = get_jira_issues()
    if not issues:
        print("Не удалось получить данные")
        return
    
    df = process_issues(issues)
    if df.empty:
        print("Нет данных для анализа")
        return
    
    print(f"Доступно для анализа: {len(df)} задач")
    print("Строим 11 графиков...")
    print("=" * 50)
    
    # Построение всех 11 графиков
    plot_graph_1(df)   # Гистограмма потраченного времени
    plot_graph_2(df)   # Время в состоянии Open
    plot_graph_3(df)   # Время в состоянии Resolved
    plot_graph_4(df)   # Время в состоянии In Progress
    plot_graph_5(df)   # Время в состоянии Patch Available
    plot_graph_6(df)   # Время в состоянии Reopened
    plot_graph_7(df)   # График заведенных и закрытых задач
    plot_graph_8(df)   # Топ-30 пользователей
    plot_graph_9(df)   # Время выполнения задач
    plot_graph_10(df)  # Распределение по серьезности
    plot_graph_11(df)  # Детальный анализ
    
    # Статистика
    print(f"\nСтатистика времени выполнения:")
    print(f"Всего задач: {len(df)}")
    print(f"Минимальное время: {df['open_days'].min()} дней")
    print(f"Максимальное время: {df['open_days'].max()} дней")
    print(f"Среднее время: {df['open_days'].mean():.1f} дней")
    print(f"Медианное время: {df['open_days'].median():.1f} дней")
    
    print("\n" + "=" * 50)
    print("Все 11 графиков построены!")

if __name__ == "__main__":
    main()