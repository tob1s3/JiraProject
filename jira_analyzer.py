import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# Настройка единого стиля
plt.style.use('default')
PRIMARY_COLOR = '#2E86AB'  # Единый основной цвет
SECONDARY_COLOR = '#A23B72'  # Второстепенный цвет для контраста
GRID_COLOR = '#F0F0F0'
TEXT_COLOR = '#333333'

# Применение глобальных настроек
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['grid.color'] = GRID_COLOR
plt.rcParams['text.color'] = TEXT_COLOR
plt.rcParams['axes.labelcolor'] = TEXT_COLOR
plt.rcParams['xtick.color'] = TEXT_COLOR
plt.rcParams['ytick.color'] = TEXT_COLOR

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

def create_figure(title, xlabel, ylabel, figsize=(12, 6)):
    """Создание фигуры с единым стилем"""
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor('white')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20, color=TEXT_COLOR)
    ax.set_xlabel(xlabel, fontsize=12, color=TEXT_COLOR)
    ax.set_ylabel(ylabel, fontsize=12, color=TEXT_COLOR)
    ax.grid(True, alpha=0.3, color=GRID_COLOR)
    return fig, ax

def plot_гистограмма_потраченного_времени_на_решение_задачи(df):
    """Гистограмма потраченного времени на решение задачи"""
    fig, ax = create_figure(
        'Гистограмма потраченного времени на решение задачи',
        'Дни в открытом состоянии', 
        'Количество задач'
    )
    ax.hist(df['open_days'], bins=30, color=PRIMARY_COLOR, edgecolor='white', alpha=0.8)
    plt.tight_layout()
    plt.show()

def plot_гистограмма_распределения_времени_в_состоянии_Open(df):
    """Гистограмма распределения времени в состоянии Open"""
    fig, ax = create_figure(
        'Гистограмма распределения времени в состоянии Open',
        'Дни в состоянии Open', 
        'Количество задач'
    )
    ax.hist(df['open_days'], bins=20, color=PRIMARY_COLOR, edgecolor='white', alpha=0.8)
    plt.tight_layout()
    plt.show()

def plot_гистограмма_распределения_времени_в_состоянии_Resolved(df):
    """Гистограмма распределения времени в состоянии Resolved"""
    resolved_tasks = df[df['status'] == 'Resolved']
    if len(resolved_tasks) > 0:
        fig, ax = create_figure(
            'Гистограмма распределения времени в состоянии Resolved',
            'Дни в состоянии Resolved', 
            'Количество задач'
        )
        ax.hist(resolved_tasks['open_days'], bins=20, color=PRIMARY_COLOR, edgecolor='white', alpha=0.8)
        plt.tight_layout()
        plt.show()

def plot_гистограмма_распределения_времени_в_состоянии_In_Progress(df):
    """Гистограмма распределения времени в состоянии In Progress"""
    in_progress_tasks = df[df['status'].str.contains('Progress', na=False)]
    if len(in_progress_tasks) > 0:
        fig, ax = create_figure(
            'Гистограмма распределения времени в состоянии In Progress',
            'Дни в состоянии In Progress', 
            'Количество задач'
        )
        ax.hist(in_progress_tasks['open_days'], bins=15, color=PRIMARY_COLOR, edgecolor='white', alpha=0.8)
        plt.tight_layout()
        plt.show()

def plot_гистограмма_распределения_времени_в_состоянии_Patch_Available(df):
    """Гистограмма распределения времени в состоянии Patch Available"""
    patch_tasks = df[df['status'].str.contains('Patch', na=False)]
    if len(patch_tasks) > 0:
        fig, ax = create_figure(
            'Гистограмма распределения времени в состоянии Patch Available',
            'Дни в состоянии Patch Available', 
            'Количество задач'
        )
        ax.hist(patch_tasks['open_days'], bins=10, color=PRIMARY_COLOR, edgecolor='white', alpha=0.8)
        plt.tight_layout()
        plt.show()

def plot_гистограмма_распределения_времени_в_состоянии_Reopened(df):
    """Гистограмма распределения времени в состоянии Reopened"""
    reopened_tasks = df[df['status'].str.contains('Reopen', na=False)]
    if len(reopened_tasks) > 0:
        fig, ax = create_figure(
            'Гистограмма распределения времени в состоянии Reopened',
            'Дни в состоянии Reopened', 
            'Количество задач'
        )
        ax.hist(reopened_tasks['open_days'], bins=10, color=PRIMARY_COLOR, edgecolor='white', alpha=0.8)
        plt.tight_layout()
        plt.show()

def plot_график_заведенных_и_закрытых_задач_с_накопительным_итогом(df):
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
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Первый график - ежедневные значения
    ax1.set_facecolor('white')
    ax1.plot(daily_created.index, daily_created.values, label='Создано задач', 
             marker='o', markersize=3, linewidth=2, color=PRIMARY_COLOR)
    ax1.plot(daily_resolved.index, daily_resolved.values, label='Закрыто задач', 
             marker='s', markersize=3, linewidth=2, color=SECONDARY_COLOR)
    ax1.set_title('График заведенных и закрытых задач с накопительным итогом', 
                  fontsize=14, fontweight='bold', pad=20, color=TEXT_COLOR)
    ax1.set_ylabel('Количество задач', color=TEXT_COLOR)
    ax1.legend()
    ax1.grid(True, alpha=0.3, color=GRID_COLOR)
    ax1.tick_params(axis='x', rotation=45, colors=TEXT_COLOR)
    ax1.tick_params(axis='y', colors=TEXT_COLOR)
    
    # Второй график - накопительный итог
    ax2.set_facecolor('white')
    ax2.plot(cumulative_created.index, cumulative_created.values, label='Всего создано', 
             linewidth=3, color=PRIMARY_COLOR)
    ax2.plot(cumulative_resolved.index, cumulative_resolved.values, label='Всего закрыто', 
             linewidth=3, color=SECONDARY_COLOR)
    ax2.set_title('Накопительный итог', fontsize=14, fontweight='bold', pad=20, color=TEXT_COLOR)
    ax2.set_xlabel('Дата', color=TEXT_COLOR)
    ax2.set_ylabel('Количество задач', color=TEXT_COLOR)
    ax2.legend()
    ax2.grid(True, alpha=0.3, color=GRID_COLOR)
    ax2.tick_params(axis='x', rotation=45, colors=TEXT_COLOR)
    ax2.tick_params(axis='y', colors=TEXT_COLOR)
    
    plt.tight_layout()
    plt.show()

def plot_гистограмма_топ_30_пользователей_по_количеству_задач(df):
    """Гистограмма топ-30 пользователей по количеству задач (исполнитель или репортер)"""
    reporter_counts = df['reporter'].value_counts()
    assignee_counts = df['assignee'].value_counts()
    user_counts = reporter_counts.add(assignee_counts, fill_value=0)
    
    top_users = user_counts.nlargest(30)
    
    fig, ax = create_figure(
        'Гистограмма топ-30 пользователей по количеству задач\n(исполнитель или репортер)',
        'Количество задач', 
        'Пользователь',
        figsize=(12, 10)
    )
    
    y_pos = np.arange(len(top_users))
    bars = ax.barh(y_pos, top_users.values, color=PRIMARY_COLOR, alpha=0.8, edgecolor='white')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([name[:25] + '...' if len(name) > 25 else name for name in top_users.index])
    ax.invert_yaxis()
    
    # Добавляем подписи значений
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                str(int(width)), ha='left', va='center', fontsize=9, color=TEXT_COLOR)
    
    plt.tight_layout()
    plt.show()

def plot_гистограмма_времени_выполнения_задач(df):
    """Гистограмма времени выполнения задач"""
    fig, ax = create_figure(
        'Гистограмма времени выполнения задач',
        'Время выполнения (дни)', 
        'Количество задач'
    )
    ax.hist(df['open_days'], bins=25, color=PRIMARY_COLOR, edgecolor='white', alpha=0.8)
    plt.tight_layout()
    plt.show()

def plot_график_распределения_задач_по_степени_серьезности(df):
    """График распределения задач по степени серьезности"""
    priority_counts = df['priority'].value_counts()
    
    fig, ax = create_figure(
        'График распределения задач по степени серьезности',
        'Приоритет (степень серьезности)', 
        'Количество задач'
    )
    
    # Используем основной цвет с разной прозрачностью
    colors = [PRIMARY_COLOR] * len(priority_counts)
    alphas = np.linspace(0.6, 1.0, len(priority_counts))
    
    bars = ax.bar(priority_counts.index, priority_counts.values, 
                  color=colors, alpha=alphas, edgecolor='white')
    
    ax.tick_params(axis='x', rotation=45, colors=TEXT_COLOR)
    
    # Добавляем подписи значений
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', 
                fontweight='bold', color=TEXT_COLOR, fontsize=10)
    
    plt.tight_layout()
    plt.show()

def plot_пример_выбора_задачи(df):
    """Пример выбора задачи (дополнительный анализ)"""
    fig, ax = create_figure(
        'Статистика времени выполнения задач',
        'Время выполнения (дни)', 
        'Количество задач'
    )
    
    ax.hist(df['open_days'], bins=30, color=PRIMARY_COLOR, alpha=0.7, edgecolor='white')
    
    mean_days = df['open_days'].mean()
    median_days = df['open_days'].median()
    
    ax.axvline(mean_days, color=SECONDARY_COLOR, linestyle='--', linewidth=2, 
                label=f'Среднее: {mean_days:.1f} дней')
    ax.axvline(median_days, color=TEXT_COLOR, linestyle='--', linewidth=2,
                label=f'Медиана: {median_days:.1f} дней')
    
    ax.legend()
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
    
    # Построение всех графиков в соответствии с названиями в отчете
    plot_пример_выбора_задачи(df)
    plot_гистограмма_потраченного_времени_на_решение_задачи(df)
    plot_гистограмма_распределения_времени_в_состоянии_Open(df)
    plot_гистограмма_распределения_времени_в_состоянии_Resolved(df)
    plot_гистограмма_распределения_времени_в_состоянии_In_Progress(df)
    plot_гистограмма_распределения_времени_в_состоянии_Patch_Available(df)
    plot_гистограмма_распределения_времени_в_состоянии_Reopened(df)
    plot_график_заведенных_и_закрытых_задач_с_накопительным_итогом(df)
    plot_гистограмма_топ_30_пользователей_по_количеству_задач(df)
    plot_гистограмма_времени_выполнения_задач(df)
    plot_график_распределения_задач_по_степени_серьезности(df)
    
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