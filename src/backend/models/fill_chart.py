import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict 

def generate_time_grid(start_time, end_time, interval_minutes=5):
    if not isinstance(interval_minutes, int):
        print(f"ERROR: interval_minutes is not an integer: {interval_minutes}")
        return []

    times = []
    current_time = start_time
    while current_time <= end_time:
        times.append(current_time.strftime("%H:%M"))
        current_time += timedelta(minutes=interval_minutes)
    return times

#Config chart to fix any LLM chart code
def generate_chart_config(chart_config, grouped_data, all_timestamps, interval_minutes):
    min_time = min(dt.time() for dt in all_timestamps)  
    max_time = max(dt.time() for dt in all_timestamps)  

    reference_date = datetime(2000, 1, 1)  
    start_time = datetime.combine(reference_date, min_time)
    end_time = datetime.combine(reference_date, max_time)

    shared_time_labels = generate_time_grid(start_time, end_time, interval_minutes)

    print(f"DEBUG: Using shared time range from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}")

    chart_config["data"]["datasets"] = []

    colors = [
        "rgb(0, 243, 255)", "rgb(255, 99, 132)", "rgb(255, 206, 86)", "rgb(153, 102, 255)","rgb(255, 159, 64)", "rgb(54, 162, 235)", "rgb(201, 203, 207)"  
    ]

    color_index = 0  

    for sensor_name, date_data in grouped_data.items():
        for date in sorted(date_data.keys()):
            data = date_data[date]
            dataset_values = [
                {"x": time, "y": data.get(time, None)}
                for time in shared_time_labels
            ]

            color = colors[color_index % len(colors)]
            color_index += 1

            dataset = {
                "label": f"{sensor_name} - {date}",
                "data": dataset_values,
                "borderColor": color,
                "backgroundColor": color,
                "borderWidth": 2,
                "fill": False,
                "pointRadius": 3,
                "tension": 0,
                "spanGaps": True,
            }
            chart_config["data"]["datasets"].append(dataset)

    chart_config["data"]["labels"] = shared_time_labels

    chart_config["options"] = {
        "scales": {
            "x": {
                "type": "category",
                "labels": shared_time_labels,
                "ticks": {
                    "autoSkip": True,
                    "maxTicksLimit": 10,
                    "minRotation": 45
                }
            },
            "y": {
                "grid": {"color": "rgba(255, 255, 255, 0.2)"}
            }
        }
    }

    return json.dumps(chart_config)



def fill_llm_chart_data(chart_config, sensor_data, sensor_label=None, interval_minutes=5):
    if not isinstance(interval_minutes, int):
        interval_minutes = 5

    if not chart_config or not isinstance(chart_config, dict):
        return None

    try:
        grouped_data = defaultdict(lambda: defaultdict(dict))  
        all_timestamps = []

        print(f"DEBUG: Incoming Sensor Data Length: {len(sensor_data)}")

        for entry in sensor_data:
            timestamp = entry.get("timestamp")
            value = entry.get("value")

            if isinstance(sensor_label, list):
                sensor_name = entry["metadata"]["name"] if "metadata" in entry and "name" in entry["metadata"] else "Unknown Sensor"
            else:
                sensor_name = sensor_label  

            if timestamp is None or value is None:
                continue  

            dt = timestamp if isinstance(timestamp, datetime) else datetime.fromisoformat(str(timestamp))
            all_timestamps.append(dt)

            time_str = dt.strftime("%H:%M")  
            date_str = dt.date().isoformat()  

            if date_str not in grouped_data[sensor_name]:
                grouped_data[sensor_name][date_str] = {}

            grouped_data[sensor_name][date_str][time_str] = value  

        if not all_timestamps:
            print("ERROR: No valid timestamps found.")
            return None

        return generate_chart_config(chart_config, grouped_data, all_timestamps, interval_minutes)

    except Exception as e:
        print("ERROR while filling chart data:", str(e))
        return None



def fill_pie_chart_data(sensor_data):
    if not sensor_data or not isinstance(sensor_data, list):
        print("ERROR: Invalid sensor data for pie chart.")
        return None

    print("INFO: Processing pie chart data.")

    labels = [str(entry.get("_id", "Unknown")) for entry in sensor_data]  
    data_values = [entry.get("count", 0) for entry in sensor_data]  

    colors = [
        "rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 206, 86)",
        "rgb(75, 192, 192)", "rgb(153, 102, 255)", "rgb(255, 159, 64)",
        "rgb(0, 243, 255)", "rgb(128, 128, 128)"
    ]

    background_colors = [colors[i % len(colors)] for i in range(len(labels))]

    chart_config = {
        "type": "pie",
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": "Sensor Value Distribution",
                    "data": data_values,
                    "backgroundColor": background_colors,
                    "borderColor": background_colors,
                    "borderWidth": 1
                }
            ]
        },
        "options": {
            "plugins": {
                "title": {
                    "display": True,
                    "text": "pH Value Distribution"
                }
            }
        }
    }

    return json.dumps(chart_config, indent=2)
