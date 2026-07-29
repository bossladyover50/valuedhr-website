#!/usr/bin/env python3
"""Minimal, dependency-free Zoho CRM OAuth and lead importer.

Secrets are read from .env or the process environment and are never printed.
The importer is a dry run unless --commit is explicitly supplied.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing {name} in .env")
    return value


def request_json(url: str, *, method: str = "GET", headers=None, data=None):
    body = None if data is None else urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode()
            return json.loads(content) if content.strip() else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise SystemExit(f"Zoho request failed ({exc.code}): {detail}") from exc


def exchange_code(code: str) -> None:
    result = request_json(
        required("ZOHO_ACCOUNTS_URL").rstrip("/") + "/oauth/v2/token",
        method="POST",
        data={
            "grant_type": "authorization_code",
            "client_id": required("ZOHO_CLIENT_ID"),
            "client_secret": required("ZOHO_CLIENT_SECRET"),
            "code": code,
            **({"redirect_uri": os.environ["ZOHO_REDIRECT_URI"]} if os.environ.get("ZOHO_REDIRECT_URI") else {}),
        },
    )
    refresh = result.get("refresh_token")
    if not refresh:
        raise SystemExit("Zoho did not return a refresh token. Generate a new self-client grant code.")
    print("Authorization succeeded. Add ZOHO_REFRESH_TOKEN to .env using the returned value below:")
    print(refresh)


def save_refresh_token(token: str) -> None:
    path = ROOT / ".env"
    lines = path.read_text(encoding="utf-8").splitlines()
    updated = []
    found = False
    for line in lines:
        if line.startswith("ZOHO_REFRESH_TOKEN="):
            updated.append("ZOHO_REFRESH_TOKEN=" + token)
            found = True
        else:
            updated.append(line)
    if not found:
        updated.append("ZOHO_REFRESH_TOKEN=" + token)
    path.write_text("\n".join(updated) + "\n", encoding="utf-8")


def authorize() -> None:
    redirect_uri = "http://127.0.0.1:8765/callback"
    os.environ["ZOHO_REDIRECT_URI"] = redirect_uri
    params = urllib.parse.urlencode({
        "scope": "ZohoCRM.modules.leads.CREATE,ZohoCRM.modules.leads.READ,ZohoCRM.settings.fields.READ,ZohoCRM.org.READ",
        "client_id": required("ZOHO_CLIENT_ID"),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "redirect_uri": redirect_uri,
    })
    auth_url = required("ZOHO_ACCOUNTS_URL").rstrip("/") + "/oauth/v2/auth?" + params

    class Callback(BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code = query.get("code", [""])[0]
            if not code:
                self.send_response(400); self.end_headers(); self.wfile.write(b"Zoho authorization failed.")
                return
            result = request_json(
                required("ZOHO_ACCOUNTS_URL").rstrip("/") + "/oauth/v2/token",
                method="POST",
                data={"grant_type": "authorization_code", "client_id": required("ZOHO_CLIENT_ID"),
                      "client_secret": required("ZOHO_CLIENT_SECRET"), "code": code,
                      "redirect_uri": redirect_uri},
            )
            refresh = result.get("refresh_token")
            if not refresh:
                self.send_response(500); self.end_headers(); self.wfile.write(b"No refresh token returned.")
                return
            save_refresh_token(refresh)
            self.send_response(200); self.send_header("Content-Type", "text/plain"); self.end_headers()
            self.wfile.write(b"Zoho CRM authorization succeeded. You may close this tab.")
            self.server.authorized = True

        def log_message(self, *_):
            return

    server = HTTPServer(("127.0.0.1", 8765), Callback)
    server.authorized = False
    print("Open this authorization URL:", auth_url, flush=True)
    while not server.authorized:
        server.handle_request()
    print("Authorization succeeded; refresh token saved securely in .env.")


def access_token() -> str:
    result = request_json(
        required("ZOHO_ACCOUNTS_URL").rstrip("/") + "/oauth/v2/token",
        method="POST",
        data={
            "grant_type": "refresh_token",
            "client_id": required("ZOHO_CLIENT_ID"),
            "client_secret": required("ZOHO_CLIENT_SECRET"),
            "refresh_token": required("ZOHO_REFRESH_TOKEN"),
        },
    )
    if "access_token" not in result:
        raise SystemExit("Could not obtain a Zoho access token.")
    return result["access_token"]


def zoho_get(path: str, token: str):
    return request_json(
        required("ZOHO_API_DOMAIN").rstrip("/") + path,
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
    )


def existing_lead(token: str, first: str, last: str, company: str) -> bool:
    criteria = f"((Last_Name:equals:{last})and(Company:equals:{company}))"
    query = urllib.parse.urlencode({"criteria": criteria})
    try:
        result = zoho_get(f"/crm/v8/Leads/search?{query}", token)
        return bool(result.get("data"))
    except SystemExit as exc:
        if "204" in str(exc):
            return False
        raise


def row_to_lead(row: dict[str, str]) -> dict[str, str]:
    lead = {
        "First_Name": row.get("First Name", "").strip(),
        "Last_Name": row.get("Last Name", "").strip(),
        "Company": row.get("Company", "").strip(),
        "Designation": row.get("Title", "").strip(),
        "Website": row.get("Website", "").strip(),
        "Email": row.get("Public Business Email", "").strip(),
        "Phone": row.get("Public Business Phone", "").strip(),
        "Lead_Source": "Daily Verified Trade Leads",
        "Description": row.get("Enrichment Notes", row.get("Fit Note", "")).strip(),
    }
    return {key: value for key, value in lead.items() if value}


def import_csv(path: Path, commit: bool) -> None:
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
    valid = []
    for row in rows:
        status = row.get("Enrichment Status", "").strip()
        confidence = row.get("Confidence", "").strip()
        if status and status not in {"Ready for review", "Corrected"}:
            print(f"SKIP verification status {status}: {row.get('Company', '(unknown)')}")
            continue
        if confidence == "Low":
            print(f"SKIP low confidence: {row.get('Company', '(unknown)')}")
            continue
        lead = row_to_lead(row)
        if not lead.get("Last_Name") or not lead.get("Company"):
            print(f"SKIP missing required name/company: {row.get('Company', '(unknown)')}")
            continue
        valid.append(lead)
    print(f"Validated {len(valid)} lead(s); commit={commit}.")
    if not commit:
        print("Dry run only. Re-run with --commit to write to Zoho CRM.")
        return
    token = access_token()
    created = duplicates = 0
    for lead in valid:
        if existing_lead(token, lead.get("First_Name", ""), lead["Last_Name"], lead["Company"]):
            duplicates += 1
            print(f"DUPLICATE: {lead['Last_Name']} — {lead['Company']}")
            continue
        payload = json.dumps({"data": [lead], "trigger": []}).encode()
        url = required("ZOHO_API_DOMAIN").rstrip("/") + "/crm/v8/Leads"
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={"Authorization": f"Zoho-oauthtoken {token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            raise SystemExit(f"Lead insert failed ({exc.code}): {exc.read().decode(errors='replace')}") from exc
        if result.get("data", [{}])[0].get("status") == "success":
            created += 1
            print(f"CREATED: {lead['Last_Name']} — {lead['Company']}")
        else:
            print(f"FAILED: {lead['Last_Name']} — {result}")
    print(f"Finished: {created} created, {duplicates} duplicate(s) skipped.")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    auth = sub.add_parser("exchange-code")
    auth.add_argument("code", help="Short-lived self-client grant code")
    test = sub.add_parser("test")
    sub.add_parser("authorize")
    imp = sub.add_parser("import")
    imp.add_argument("csv_file", type=Path)
    imp.add_argument("--commit", action="store_true")
    args = parser.parse_args()
    if args.command == "exchange-code":
        exchange_code(args.code)
    elif args.command == "authorize":
        authorize()
    elif args.command == "test":
        token = access_token()
        data = zoho_get("/crm/v8/org", token)
        print("Zoho CRM connection successful:", data.get("org", [{}])[0].get("company_name", "organization found"))
    else:
        import_csv(args.csv_file, args.commit)


if __name__ == "__main__":
    main()
