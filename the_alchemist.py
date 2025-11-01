import json, os
from datetime import datetime

REPORTS_DIR = os.path.join(os.getcwd(), 'data', 'reports')

class TheAlchemist:
    """Central manager renamed to The Alchemist."""
    def __init__(self, reports_dir=None):
        self.reports_dir = reports_dir or REPORTS_DIR

    def load_reports(self):
        reports = {}
        for fname in sorted(os.listdir(self.reports_dir)):
            if not fname.endswith('.json'):
                continue
            path = os.path.join(self.reports_dir, fname)
            try:
                with open(path, 'r') as f:
                    reports[fname.replace('.json','')] = json.load(f)
            except Exception as e:
                print('Failed to load', path, e)
        return reports

    def score_report(self, report):
        # Heuristic scoring: prefer higher 'confidence' and positive 'signal'
        score = 0.0
        score += report.get('confidence', 0) * 0.6
        score += (1 if report.get('signal','neutral')=='buy' else 0) * 0.4
        score += 0.01 * (10 - report.get('time_horizon_days', 7))
        return round(score, 3)

    def summarize_and_rank(self):
        reports = self.load_reports()
        scored = []
        for name, r in reports.items():
            s = self.score_report(r)
            scored.append({'name': name, 'score': s, 'summary': r.get('summary','')})
        scored.sort(key=lambda x: x['score'], reverse=True)
        result = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'ranking': [s['name'] for s in scored],
            'details': scored
        }
        out_path = os.path.join(os.getcwd(), 'data', 'alchemist_summary.json')
        try:
            with open(out_path, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass
        return result
