import datetime
import gzip
import os
import smtplib
import time
import urllib
from email.mime.text import MIMEText
from collections import Counter
from StringIO import StringIO

import requests


def send_weekly_summary():
    if not os.environ.get('EVERY_DAY') and datetime.datetime.today().weekday() != 5:
        # Heroku's free scheduler doesn't let you set weekly tasks. So we make
        # our daily task a weekly one with 3 extra lines of code.
        print("Skipping because today isn't Saturday. Set environment variable "
              'EVERY_DAY to something non-empty to force a run.')
        return

    papertrail_token = os.environ['PAPERTRAIL_API_TOKEN']
    summary_recipient_emails = os.environ['SUMMARY_RECIPIENT_EMAILS'].split(',')
    gmail_id = os.environ['SENDER_GMAIL_ID']
    gmail_password = os.environ['SENDER_GMAIL_PASSWORD']

    log_lines = get_log_lines(papertrail_token)
    summary = summarize_logs(log_lines)
    send_email(summary, summary_recipient_emails, gmail_id, gmail_password)


def get_log_lines(papertrail_token):
    headers = {'X-Papertrail-Token': papertrail_token}

    response = requests.get('https://papertrailapp.com/api/v1/archives.json', headers=headers)
    response.raise_for_status()
    archive_index = response.json()

    now_minus_7d = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    archive_index = [
        block for block in archive_index if date_from_str(block['end']) >= now_minus_7d
    ]
    archive_index.sort(key=lambda b: b['end'])

    for block in archive_index:
        url = block['_links']['download']['href']
        response = requests.get(url, headers=headers)
        try:
            response.raise_for_status()
        except Exception as e:
            yield 'error_downloading_logs {}'.format(e)
            continue

        gzip_data = StringIO(response.content)
        log_text = gzip.GzipFile(fileobj=gzip_data, mode='r').read()
        for line in log_text.splitlines():
            yield line


def date_from_str(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')


def summarize_logs(log_lines):
    summary = {
        'searches': Counter(),
        'words': Counter(),
        'other_2xx': Counter(),
        'paths_4xx': Counter(),
        'paths_5xx': Counter(),
        'ips': Counter(),
        'total_requests': 0,
    }

    for line in log_lines:
        cols = line.split('\t')
        if cols[8] != 'heroku/router':
            continue

        info = {
            k: v
            for pair in cols[9].split()
            for k, v in (pair.split('=', 1),)
        }
        path = info['path'][1:-1]

        if info['status'].startswith('4'):
            summary['paths_4xx'][path] += 1
        elif info['status'].startswith('5'):
            summary['paths_5xx'][path] += 1
        elif path.startswith('/ems/search/?q='):
            query = urllib.unquote_plus(path[len('/ems/search/?q='):])
            summary['searches'][query] += 1
        elif path.startswith('/ems/w/'):
            word = urllib.unquote(path[len('/ems/w/'):])
            if word.endswith('/'):
                word = word[:-1]
            summary['words'][word] += 1
        elif info['status'].startswith('2') and not path.startswith('/static/'):
            summary['other_2xx'][path] += 1

        summary['ips'][info['fwd'][1:-1]] += 1
        summary['total_requests'] += 1

    return summary


def send_email(summary, summary_recipient_emails, sender_id, sender_password):
    lines = []

    total_page_views = sum(sum(summary[key].values()) for key in ('searches', 'words', 'other_2xx'))
    unique_page_views = sum(len(summary[key]) for key in ('searches', 'words', 'other_2xx'))
    location_map = get_location_map(list(summary['ips']))

    lines.append('Total requests: {}'.format(summary['total_requests']))
    lines.append('Total pages viewed: {}'.format(total_page_views))
    lines.append('Unique pages viewed: {}'.format(unique_page_views))
    lines.append('Unique IP visitors: {}'.format(len(summary['ips'])))

    if summary['searches']:
        lines.append('')
        lines.append('Searches:')
        for query, count in summary['searches'].most_common():
            lines.append('  ({}) {}'.format(count, query))

    if summary['words']:
        lines.append('')
        lines.append('Words viewed:')
        for query, count in summary['words'].most_common():
            lines.append('  ({}) {}'.format(count, query))

    if summary['other_2xx']:
        lines.append('')
        lines.append('Other pages viewed:')
        for query, count in summary['other_2xx'].most_common():
            lines.append('  ({}) {}'.format(count, query))

    if summary['paths_4xx']:
        lines.append('')
        lines.append('4xx responses (not found and other client errors):')
        for query, count in summary['paths_4xx'].most_common():
            lines.append('  ({}) {}'.format(count, query))

    if summary['paths_5xx']:
        lines.append('')
        lines.append('5xx responses (server errors):')
        for query, count in summary['paths_5xx'].most_common():
            lines.append('  ({}) {}'.format(count, query))

    if location_map:
        lines.append('')
        lines.append('Request geolocations:')
        for loc, ips in location_map.items():
            total_requests = sum(summary['ips'][ip] for ip in ips)
            lines.append('  ({} IPs, {} requests) {}'.format(len(ips), total_requests, loc))

    body = '\n'.join(lines)
    print(body)

    msg = MIMEText(body)
    sender_email = '{}@gmail.com'.format(sender_id)
    msg['Subject'] = 'Weekly Wiinaq summary'
    msg['From'] = 'Wiinaq <{}>'.format(sender_email)
    msg['To'] = ', '.join(summary_recipient_emails)

    s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    try:
        s.login(sender_id, sender_password)
        s.sendmail(sender_email, summary_recipient_emails, msg.as_string())
    finally:
        s.quit()


def get_location_map(ips):
    location_map = {}

    for ip in ips:
        try:
            response = requests.get(
                'http://ip-api.com/json/{}'
                '?fields=status,message,country,regionName,city,district,proxy'.format(ip)
            )
            data = response.json()
            if data.get('message'):
                raise RuntimeError(data['message'])
            response.raise_for_status()
        except Exception as e:
            print(e)
            location = 'unknown'
        else:
            parts = [
                part
                for key in ('district', 'city', 'regionName', 'country')
                for part in (data[key],)
                if part
            ]
            location = ', '.join(parts)
            if data['proxy']:
                location += ' [proxy]'

        location_map.setdefault(location, []).append(ip)

        if int(response.headers.get('x-rl') or '0') <= 0:
            secs_to_wait = float(response.headers.get('x-ttl') or '1.5')
            time.sleep(secs_to_wait + 0.1)

    return location_map


if __name__ == '__main__':
    send_weekly_summary()
