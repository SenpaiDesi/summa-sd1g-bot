from datetime import datetime

current_date = datetime.utcnow()
new_time = current_date.strftime('%Y-%m-%d')
print(new_time)