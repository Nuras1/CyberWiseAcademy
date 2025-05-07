import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from elasticsearch import Elasticsearch

df = pd.read_csv('logs.csv')

print("=== First few rows ===")
print(df.head())

print("\n=== Dataset Info ===")
print(df.info())

# Step 3: Analyze Security Logs
df['timestamp'] = pd.to_datetime(df['timestamp'])

plt.figure(figsize=(10, 6))
sns.histplot(df['timestamp'], bins=30, kde=False)
plt.title('Log Frequency Over Time')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

top_ips = df['source_ip'].value_counts().head(10)
print("\n=== Top 10 Source IPs ===")
print(top_ips)

# Step 4: Automate Threat Intelligence Lookup
API_KEY = 'your_api_key_here'
url = 'https://www.virustotal.com/api/v3/ip_addresses/'

def check_ip(ip):
    headers = {'x-apikey': API_KEY}
    response = requests.get(url + ip, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
    else:
        return None

if not top_ips.empty:
    sample_ip = top_ips.index[0]
    ip_reputation = check_ip(sample_ip)
    print(f"\nReputation for {sample_ip}: {ip_reputation}")
else:
    print("\nNo IP addresses found to check reputation.")

# Step 5: Automate Incident Response Workflow
threshold = 5

suspicious_logins = df[df['event_type'] == 'login_failure'].groupby('user')['user'].count()
suspicious_logins = suspicious_logins[suspicious_logins > threshold]

for user in suspicious_logins.index:
    print(f"Alert: {user} exceeded login failure threshold with {suspicious_logins[user]} attempts.")

top_events = df['event_type'].value_counts()

plt.figure(figsize=(8, 6))
sns.barplot(x=top_events.index, y=top_events.values)
plt.title('Top Event Types')
plt.xlabel('Event Type')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Step 7: Integrate with ElasticSearch (Fixed Connection)
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

doc = {
    'timestamp': datetime.now(),
    'event_type': 'test_event',
    'source_ip': '192.168.1.1',
    'description': 'This is a test log'
}

res = es.index(index="security-logs", document=doc)
print(f"\nDocument indexed: {res['result']}")

res = es.search(index="security-logs", query={"match_all": {}})
print("\n=== ElasticSearch Query Results ===")
for hit in res['hits']['hits']:
    print(hit['_source'])
