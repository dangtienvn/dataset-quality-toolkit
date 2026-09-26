from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from jinja2 import Template

from ingestion.base import StandardDataset
from validation.base import ValidationResult, ValidationIssue
from metrics.class_distribution import ClassDistributionReport
from metrics.annotation_stats import AnnotationStatsReport


HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dataset Quality Audit - {{ dataset_name }}</title>
    <!-- Chart.js CDN with fallback script -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --bg-body: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --bg-input: #0f172a;
            --border-color: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --success: #10b981;
            --success-bg: rgba(16, 185, 129, 0.15);
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.15);
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.15);
            --info: #06b6d4;
            --info-bg: rgba(6, 182, 212, 0.15);
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.25);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.3);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.4);
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
        }

        [data-theme="light"] {
            --bg-body: #f1f5f9;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --bg-input: #f8fafc;
            --border-color: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #475569;
            --text-dim: #94a3b8;
            
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.5;
            padding: 24px;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        .dashboard-container {
            max-width: 1320px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }

        /* Top Bar & Header */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 24px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
        }

        .brand-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-logo {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--primary), #8b5cf6);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 18px;
        }

        .brand-title {
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .brand-subtitle {
            font-size: 12px;
            color: var(--text-muted);
        }

        .top-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            border-radius: var(--radius-sm);
            cursor: pointer;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-main);
            transition: all 0.2s ease;
        }

        .btn:hover {
            background: var(--bg-card-hover);
            border-color: var(--text-dim);
        }

        .btn-primary {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        .btn-primary:hover {
            background: var(--primary-hover);
        }

        /* Hero Executive Summary */
        .hero-card {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 32px;
            box-shadow: var(--shadow-lg);
            color: white;
            position: relative;
            overflow: hidden;
        }

        [data-theme="light"] .hero-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 32px;
            align-items: center;
        }

        .hero-info h1 {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin-bottom: 8px;
        }

        .hero-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 16px;
            font-size: 13px;
            color: #94a3b8;
        }

        .hero-meta-item {
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.06);
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .hero-meta-item strong {
            color: #f8fafc;
        }

        /* Quality Score Meter */
        .score-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(8px);
            padding: 20px 32px;
            border-radius: var(--radius-md);
            min-width: 200px;
            text-align: center;
        }

        .score-val {
            font-size: 42px;
            font-weight: 900;
            line-height: 1;
            margin: 4px 0;
        }

        .score-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #94a3b8;
        }

        .status-pill {
            display: inline-block;
            margin-top: 8px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: 700;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .status-healthy { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
        .status-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
        .status-critical { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }

        /* KPI Cards Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
        }

        .kpi-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 20px;
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: var(--text-muted);
            font-size: 13px;
            font-weight: 600;
        }

        .kpi-value {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.1;
        }

        .kpi-subtext {
            font-size: 12px;
            color: var(--text-dim);
        }

        /* Validator Breakdown Cards */
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .validator-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
        }

        .val-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-shadow: var(--shadow-sm);
        }

        .val-card-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .val-name {
            font-size: 14px;
            font-weight: 700;
            color: var(--text-main);
        }

        .val-metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 12px;
            color: var(--text-muted);
            background: var(--bg-body);
            padding: 10px;
            border-radius: var(--radius-sm);
        }

        .val-metric-num {
            font-weight: 700;
            color: var(--text-main);
        }

        /* Charts Layout */
        .charts-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        @media (max-width: 1024px) {
            .charts-grid { grid-template-columns: 1fr; }
            .hero-grid { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 24px;
            box-shadow: var(--shadow-sm);
        }

        .chart-wrapper {
            position: relative;
            height: 280px;
            width: 100%;
            margin-top: 16px;
        }

        /* Custom Table */
        .table-responsive {
            width: 100%;
            overflow-x: auto;
            margin-top: 16px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }

        th {
            background: var(--bg-body);
            color: var(--text-muted);
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.05em;
        }

        td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
        }

        tr:last-child td { border-bottom: none; }
        tr:hover td { background: var(--bg-card-hover); }

        /* Severity Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .badge-error { background: var(--danger-bg); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.3); }
        .badge-warning { background: var(--warning-bg); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-info { background: var(--info-bg); color: var(--info); border: 1px solid rgba(6, 182, 212, 0.3); }
        .badge-success { background: var(--success-bg); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.3); }

        /* Issues Controls */
        .table-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .search-box {
            position: relative;
            flex: 1;
            min-width: 240px;
        }

        .search-input {
            width: 100%;
            padding: 10px 14px 10px 36px;
            background: var(--bg-body);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            color: var(--text-main);
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s ease;
        }

        .search-input:focus {
            border-color: var(--primary);
        }

        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-dim);
            pointer-events: none;
        }

        .filter-group {
            display: flex;
            gap: 8px;
            align-items: center;
        }

        .filter-btn {
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 600;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-body);
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .filter-btn.active {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
        }

        select.filter-select {
            padding: 6px 12px;
            font-size: 12px;
            background: var(--bg-body);
            color: var(--text-main);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            outline: none;
            cursor: pointer;
        }

        .code-tag {
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            background: var(--bg-body);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            color: var(--primary);
            border: 1px solid var(--border-color);
        }

        .empty-state {
            padding: 48px 24px;
            text-align: center;
            color: var(--text-muted);
        }

        .empty-state-icon {
            font-size: 36px;
            margin-bottom: 8px;
            color: var(--success);
        }

        footer {
            text-align: center;
            padding: 24px;
            color: var(--text-dim);
            font-size: 12px;
            border-top: 1px solid var(--border-color);
            margin-top: 24px;
        }

        @media print {
            body { background: white; color: black; padding: 0; }
            .top-bar, .top-actions, .table-controls { display: none !important; }
            .hero-card { background: #1e293b !important; color: white !important; -webkit-print-color-adjust: exact; }
            .card, .kpi-card, .val-card { border: 1px solid #ccc !important; box-shadow: none !important; }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Top Bar -->
        <div class="top-bar">
            <div class="brand-section">
                <div class="brand-logo">DQ</div>
                <div>
                    <div class="brand-title">Dataset Quality Audit Report</div>
                    <div class="brand-subtitle">Enterprise Data Governance & Quality Engine</div>
                </div>
            </div>
            <div class="top-actions">
                <button class="btn" id="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                    <span id="theme-icon">🌙</span> <span id="theme-text">Dark Mode</span>
                </button>
                <button class="btn" onclick="window.print()" title="Print or Save to PDF">
                    🖨️ Print Report
                </button>
            </div>
        </div>

        <!-- Hero Executive Summary -->
        <div class="hero-card">
            <div class="hero-grid">
                <div class="hero-info">
                    <h1>{{ dataset_name }}</h1>
                    <p style="color: #cbd5e1; font-size: 14px;">Automated Comprehensive Quality Audit Results</p>
                    
                    <div class="hero-meta">
                        <div class="hero-meta-item">
                            <span>Format:</span>
                            <strong>{{ dataset_format | upper }}</strong>
                        </div>
                        <div class="hero-meta-item">
                            <span>Audit Date:</span>
                            <strong>{{ timestamp }}</strong>
                        </div>
                        <div class="hero-meta-item">
                            <span>Total Checks:</span>
                            <strong>{{ total_checked_items }}</strong>
                        </div>
                    </div>
                </div>

                <div class="score-box">
                    <div class="score-label">Quality Index</div>
                    <div class="score-val" style="color: {{ score_color }};">{{ quality_score }}%</div>
                    <div class="status-pill {{ status_class }}">{{ status_text }}</div>
                </div>
            </div>
        </div>

        <!-- KPI Metrics Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span>TOTAL IMAGES</span>
                    <span>🖼️</span>
                </div>
                <div class="kpi-value" style="color: var(--primary);">{{ total_images }}</div>
                <div class="kpi-subtext">Ingested image files</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <span>TOTAL ANNOTATIONS</span>
                    <span>🏷️</span>
                </div>
                <div class="kpi-value" style="color: var(--primary);">{{ total_annotations }}</div>
                <div class="kpi-subtext">Parsed object instances</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <span>CRITICAL ERRORS</span>
                    <span>🛑</span>
                </div>
                <div class="kpi-value" style="color: var(--danger);">{{ total_errors }}</div>
                <div class="kpi-subtext">Requires immediate fix</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-header">
                    <span>WARNINGS</span>
                    <span>⚠️</span>
                </div>
                <div class="kpi-value" style="color: var(--warning);">{{ total_warnings }}</div>
                <div class="kpi-subtext">Potential dataset flaws</div>
            </div>
        </div>

        <!-- Validator Suite Summary -->
        <div>
            <div class="section-header">
                <div class="section-title">🛡️ Validation Suite Breakdown</div>
            </div>
            <div class="validator-grid">
                {% for vr in validation_results %}
                <div class="val-card">
                    <div class="val-card-top">
                        <span class="val-name">{{ vr.validator_name }}</span>
                        {% if vr.failed_count > 0 %}
                            <span class="badge badge-error">FAIL</span>
                        {% elif vr.warning_count > 0 %}
                            <span class="badge badge-warning">WARN</span>
                        {% else %}
                            <span class="badge badge-success">PASS</span>
                        {% endif %}
                    </div>
                    <div class="val-metrics">
                        <div>Checked: <span class="val-metric-num">{{ vr.total_checked }}</span></div>
                        <div>Passed: <span class="val-metric-num" style="color: var(--success);">{{ vr.passed_count }}</span></div>
                        <div>Failed: <span class="val-metric-num" style="color: var(--danger);">{{ vr.failed_count }}</span></div>
                        <div>Warnings: <span class="val-metric-num" style="color: var(--warning);">{{ vr.warning_count }}</span></div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Charts Section -->
        <div class="charts-grid">
            <!-- Class Distribution Card -->
            <div class="card">
                <div class="section-header">
                    <div class="section-title">📊 Class Distribution & Imbalance</div>
                    <span class="badge {% if class_report.imbalance_ratio > 5 %}badge-error{% elif class_report.imbalance_ratio > 2 %}badge-warning{% else %}badge-success{% endif %}">
                        Ratio: {{ "%.2f"|format(class_report.imbalance_ratio) }}
                    </span>
                </div>

                <div class="chart-wrapper">
                    <canvas id="classChart"></canvas>
                </div>

                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Class Name</th>
                                <th>Count</th>
                                <th>Percentage</th>
                                <th>Distribution</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cname, cnt in class_report.class_counts.items() %}
                            <tr>
                                <td><strong>{{ cname }}</strong></td>
                                <td>{{ cnt }}</td>
                                <td>{{ "%.2f"|format(class_report.class_percentages[cname]) }}%</td>
                                <td style="width: 40%;">
                                    <div style="background: var(--bg-body); border-radius: 4px; height: 8px; overflow: hidden; width: 100%;">
                                        <div style="background: var(--primary); height: 100%; width: {{ class_report.class_percentages[cname] }}%;"></div>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Annotation Statistics Card -->
            <div class="card" style="display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div class="section-header">
                        <div class="section-title">📐 BBox Size Distribution</div>
                    </div>

                    <div class="chart-wrapper" style="height: 220px;">
                        <canvas id="sizeChart"></canvas>
                    </div>

                    <div style="margin-top: 24px; display: flex; flex-direction: column; gap: 12px;">
                        <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: var(--bg-body); border-radius: var(--radius-sm); font-size: 13px;">
                            <span style="color: var(--text-muted);">Avg per Image</span>
                            <strong>{{ ann_report.avg_annotations_per_image }}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: var(--bg-body); border-radius: var(--radius-sm); font-size: 13px;">
                            <span style="color: var(--text-muted);">Max per Image</span>
                            <strong>{{ ann_report.max_annotations_per_image }}</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: var(--bg-body); border-radius: var(--radius-sm); font-size: 13px;">
                            <span style="color: var(--text-muted);">Min per Image</span>
                            <strong>{{ ann_report.min_annotations_per_image }}</strong>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Audit Findings & Issues Table -->
        <div class="card">
            <div class="section-header">
                <div class="section-title">🔍 Audit Findings & Issues (<span id="visible-issue-count">{{ issues|length }}</span> / {{ issues|length }})</div>
            </div>

            <div class="table-controls">
                <div class="search-box">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="issue-search" class="search-input" placeholder="Search by message, validator, type, image ID..." oninput="filterIssues()">
                </div>
                
                <div class="filter-group">
                    <button class="filter-btn active" data-filter="ALL" onclick="setSeverityFilter('ALL', this)">All</button>
                    <button class="filter-btn" data-filter="ERROR" onclick="setSeverityFilter('ERROR', this)">Errors ({{ total_errors }})</button>
                    <button class="filter-btn" data-filter="WARNING" onclick="setSeverityFilter('WARNING', this)">Warnings ({{ total_warnings }})</button>
                    <button class="filter-btn" data-filter="INFO" onclick="setSeverityFilter('INFO', this)">Info</button>

                    <select id="validator-filter" class="filter-select" onchange="filterIssues()">
                        <option value="ALL">All Validators</option>
                        {% for vr in validation_results %}
                        <option value="{{ vr.validator_name }}">{{ vr.validator_name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>

            <div class="table-responsive">
                <table id="issues-table">
                    <thead>
                        <tr>
                            <th>Severity</th>
                            <th>Validator</th>
                            <th>Issue Type</th>
                            <th>Target Image / Ann</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody id="issues-tbody">
                        {% for issue in issues %}
                        <tr class="issue-row" data-severity="{{ issue.severity }}" data-validator="{{ issue.validator }}">
                            <td>
                                {% if issue.severity == "ERROR" %}
                                    <span class="badge badge-error">ERROR</span>
                                {% elif issue.severity == "WARNING" %}
                                    <span class="badge badge-warning">WARN</span>
                                {% else %}
                                    <span class="badge badge-info">INFO</span>
                                {% endif %}
                            </td>
                            <td><strong>{{ issue.validator }}</strong></td>
                            <td><span class="code-tag">{{ issue.issue_type }}</span></td>
                            <td>
                                {% if issue.image_id or issue.annotation_id %}
                                    <code>img:{{ issue.image_id or "-" }} / ann:{{ issue.annotation_id or "-" }}</code>
                                {% else %}
                                    <span style="color: var(--text-dim);">-</span>
                                {% endif %}
                            </td>
                            <td>{{ issue.message }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>

                {% if issues|length == 0 %}
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <div style="font-weight: 700; font-size: 16px; color: var(--text-main);">No Quality Issues Detected</div>
                    <div>Your dataset passed all automated validation criteria with flying colors!</div>
                </div>
                {% endif %}
            </div>
        </div>

        <footer>
            Dataset Quality Toolkit &bull; Executive Quality Audit Report &bull; Generated on {{ timestamp }}
        </footer>
    </div>

    <script>
        // Theme Toggle Functionality
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            
            document.getElementById('theme-icon').textContent = newTheme === 'dark' ? '🌙' : '☀️';
            document.getElementById('theme-text').textContent = newTheme === 'dark' ? 'Dark Mode' : 'Light Mode';
            localStorage.setItem('dq_theme', newTheme);
        }

        // Load saved theme
        (function() {
            const savedTheme = localStorage.getItem('dq_theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            document.getElementById('theme-icon').textContent = savedTheme === 'dark' ? '🌙' : '☀️';
            document.getElementById('theme-text').textContent = savedTheme === 'dark' ? 'Dark Mode' : 'Light Mode';
        })();

        // Filtering Logic
        let activeSeverity = 'ALL';

        function setSeverityFilter(severity, btn) {
            activeSeverity = severity;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterIssues();
        }

        function filterIssues() {
            const searchVal = document.getElementById('issue-search').value.toLowerCase();
            const valFilter = document.getElementById('validator-filter').value;
            const rows = document.querySelectorAll('.issue-row');
            let visibleCount = 0;

            rows.forEach(row => {
                const severity = row.getAttribute('data-severity');
                const validator = row.getAttribute('data-validator');
                const text = row.textContent.toLowerCase();

                const matchesSeverity = (activeSeverity === 'ALL' || severity === activeSeverity);
                const matchesValidator = (valFilter === 'ALL' || validator === valFilter);
                const matchesSearch = text.includes(searchVal);

                if (matchesSeverity && matchesValidator && matchesSearch) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            const countEl = document.getElementById('visible-issue-count');
            if (countEl) countEl.textContent = visibleCount;
        }

        // Render Charts with Chart.js
        window.addEventListener('DOMContentLoaded', () => {
            if (typeof Chart === 'undefined') return;

            // Class Distribution Chart
            const classLabels = {{ class_chart_labels | tojson }};
            const classData = {{ class_chart_data | tojson }};
            
            const ctxClass = document.getElementById('classChart');
            if (ctxClass && classLabels.length > 0) {
                new Chart(ctxClass, {
                    type: 'bar',
                    data: {
                        labels: classLabels,
                        datasets: [{
                            label: 'Instances',
                            data: classData,
                            backgroundColor: '#3b82f6',
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { display: false }, ticks: { color: '#94a3b8' } },
                            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                        }
                    }
                });
            }

            // Size Distribution Chart
            const sizeLabels = {{ size_chart_labels | tojson }};
            const sizeData = {{ size_chart_data | tojson }};

            const ctxSize = document.getElementById('sizeChart');
            if (ctxSize && sizeLabels.length > 0) {
                new Chart(ctxSize, {
                    type: 'doughnut',
                    data: {
                        labels: sizeLabels,
                        datasets: [{
                            data: sizeData,
                            backgroundColor: ['#06b6d4', '#3b82f6', '#8b5cf6'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { color: '#94a3b8', font: { size: 11 } }
                            }
                        },
                        cutout: '70%'
                    }
                });
            }
        });
    </script>
</body>
</html>
"""


class ReportGenerator:
    """Quality Report Generator producing HTML, JSON, and CLI summaries."""

    def __init__(self, output_dir: Union[str, Path] = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json(
        self,
        dataset: StandardDataset,
        validation_results: List[ValidationResult],
        class_report: ClassDistributionReport,
        ann_report: AnnotationStatsReport,
        filename: str = "audit_report.json",
    ) -> Path:
        all_issues = []
        for vr in validation_results:
            for issue in vr.issues:
                all_issues.append(issue.model_dump())

        report_data = {
            "dataset_name": dataset.name,
            "dataset_format": dataset.format,
            "total_images": dataset.total_images,
            "total_annotations": dataset.total_annotations,
            "class_distribution": class_report.model_dump(),
            "annotation_statistics": ann_report.model_dump(),
            "validation_summary": {
                vr.validator_name: {
                    "total_checked": vr.total_checked,
                    "passed": vr.passed_count,
                    "failed": vr.failed_count,
                    "warnings": vr.warning_count,
                }
                for vr in validation_results
            },
            "issues": all_issues,
        }

        json_path = self.output_dir / filename
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        return json_path

    def _calculate_quality_score(
        self, total_checked: int, errors: int, warnings: int
    ) -> tuple[float, str, str, str]:
        """Calculates 0-100% Quality Score and returns (score, status_text, status_class, color)."""
        if total_checked == 0:
            return 100.0, "EXCELLENT", "status-healthy", "#10b981"

        # Deduct weight: Error = 10 points per 100 checked, Warning = 2 points per 100 checked
        deduction = ((errors * 10.0) + (warnings * 2.0)) / max(total_checked, 1) * 100.0
        score = max(0.0, min(100.0, round(100.0 - deduction, 1)))

        if score >= 90.0:
            return score, "EXCELLENT", "status-healthy", "#10b981"
        elif score >= 70.0:
            return score, "NEEDS ATTENTION", "status-warning", "#f59e0b"
        else:
            return score, "CRITICAL ISSUES", "status-critical", "#ef4444"

    def generate_html(
        self,
        dataset: StandardDataset,
        validation_results: List[ValidationResult],
        class_report: ClassDistributionReport,
        ann_report: AnnotationStatsReport,
        filename: str = "audit_report.html",
        timestamp: Optional[str] = None,
    ) -> Path:
        all_issues: List[ValidationIssue] = []
        total_errors = 0
        total_warnings = 0
        total_checked_items = 0

        for vr in validation_results:
            total_checked_items += vr.total_checked
            for issue in vr.issues:
                all_issues.append(issue)
                if issue.severity == "ERROR":
                    total_errors += 1
                elif issue.severity == "WARNING":
                    total_warnings += 1

        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        score, status_text, status_class, score_color = self._calculate_quality_score(
            total_checked_items, total_errors, total_warnings
        )

        class_chart_labels = list(class_report.class_counts.keys())
        class_chart_data = list(class_report.class_counts.values())

        size_chart_labels = list(ann_report.size_distribution.keys())
        size_chart_data = list(ann_report.size_distribution.values())

        template = Template(HTML_REPORT_TEMPLATE)
        html_content = template.render(
            dataset_name=dataset.name,
            dataset_format=dataset.format,
            timestamp=timestamp,
            total_images=dataset.total_images,
            total_annotations=dataset.total_annotations,
            total_checked_items=total_checked_items,
            total_errors=total_errors,
            total_warnings=total_warnings,
            quality_score=score,
            status_text=status_text,
            status_class=status_class,
            score_color=score_color,
            validation_results=[
                {
                    "validator_name": vr.validator_name,
                    "total_checked": vr.total_checked,
                    "passed_count": vr.passed_count,
                    "failed_count": vr.failed_count,
                    "warning_count": vr.warning_count,
                }
                for vr in validation_results
            ],
            class_report=class_report,
            ann_report=ann_report,
            class_chart_labels=class_chart_labels,
            class_chart_data=class_chart_data,
            size_chart_labels=size_chart_labels,
            size_chart_data=size_chart_data,
            issues=[i.model_dump() for i in all_issues],
        )

        html_path = self.output_dir / filename
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return html_path

    def generate_cli_summary(
        self,
        dataset: StandardDataset,
        validation_results: List[ValidationResult],
        class_report: ClassDistributionReport,
        ann_report: AnnotationStatsReport,
    ) -> str:
        lines = [
            "=" * 60,
            f"   DATASET QUALITY AUDIT DASHBOARD: {dataset.name.upper()}",
            "=" * 60,
            f"Format: {dataset.format} | Total Images: {dataset.total_images} | Total Annotations: {dataset.total_annotations}",
            "-" * 60,
            "VALIDATION SUMMARY:",
        ]

        total_errs = 0
        total_warns = 0
        for vr in validation_results:
            lines.append(
                f"  - {vr.validator_name:<20}: Checked={vr.total_checked} | Failed={vr.failed_count} | Warnings={vr.warning_count}"
            )
            total_errs += vr.failed_count
            total_warns += vr.warning_count

        lines.extend([
            "-" * 60,
            f"CLASSES ({len(class_report.class_counts)} found, Imbalance Ratio: {class_report.imbalance_ratio}):",
        ])
        for cname, cnt in list(class_report.class_counts.items())[:5]:
            lines.append(f"  - {cname:<20}: {cnt} ({class_report.class_percentages[cname]:.1f}%)")
        if len(class_report.class_counts) > 5:
            lines.append(f"  ... and {len(class_report.class_counts) - 5} more classes.")

        lines.extend([
            "-" * 60,
            f"TOTAL ISSUES AUDITED: Errors={total_errs}, Warnings={total_warns}",
            "=" * 60,
        ])
        return "\n".join(lines)
