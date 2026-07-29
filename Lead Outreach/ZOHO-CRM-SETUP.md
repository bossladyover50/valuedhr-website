# Zoho CRM API setup

1. Open `https://api-console.zoho.com/` and sign in with the Zoho CRM administrator.
2. Choose **Self Client**, then **Create**.
3. Under **Client Secret**, copy the Client ID and Client Secret into a local `.env` file made from `.env.example`.
4. Under **Generate Code**, use these comma-separated scopes:

   `ZohoCRM.modules.leads.CREATE,ZohoCRM.modules.leads.READ,ZohoCRM.settings.fields.READ,ZohoCRM.org.READ`

5. Select the Production CRM organization and generate the longest available grant duration.
6. Immediately exchange the short-lived grant code:

   `python3 tools/zoho_crm.py exchange-code 'PASTE_GRANT_CODE_HERE'`

7. Put the returned refresh token in `.env` as `ZOHO_REFRESH_TOKEN`.
8. Test without displaying credentials:

   `python3 tools/zoho_crm.py test`

9. Preview an import (no CRM writes):

   `python3 tools/zoho_crm.py import 'Lead Outreach/valuedhr_daily_verified_trade_leads_YYYY-MM-DD.csv'`

10. Import only after review:

   `python3 tools/zoho_crm.py import 'Lead Outreach/valuedhr_daily_verified_trade_leads_YYYY-MM-DD.csv' --commit`

The importer checks for an existing lead with the same last name and company and skips matches.
