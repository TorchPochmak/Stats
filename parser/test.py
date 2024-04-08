from datetime import datetime, timedelta

def split_date_interval(start_date_str, end_date_str):
    date_format = "%d.%m.%Y"
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = datetime.strptime(end_date_str, date_format)
    
    result = []
    while start_date < end_date:
        next_date = start_date + timedelta(days=120)  # 4 месяца это приблизительно 120 дней
        if next_date > end_date:  # Если следующая дата выходит за пределы интервала, приводим её к конечной дате
            next_date = end_date
        result.append((start_date.strftime(date_format), next_date.strftime(date_format)))
        start_date = next_date  # Переходим к следующему периоду
    return result

# Пример использования
start_date_str = "18.02.2003"
end_date_str = "18.01.2005"
intervals = split_date_interval(start_date_str, end_date_str)
print(intervals)

