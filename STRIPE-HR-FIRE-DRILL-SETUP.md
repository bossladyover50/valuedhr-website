# Stripe post-payment setup — HR Fire Drill

In the Stripe Payment Link for **HR Fire Drill — $495**, set the after-payment behavior to redirect customers to this exact URL:

**https://valuedhr.com/hr-fire-drill-intake.html**

Stripe path: **Payment Links → HR Fire Drill → Edit → After payment → Redirect customers to your website**.

The intake page sends the paid buyer's high-level brief into the existing Zoho CRM web-to-lead pipeline with the lead source `Website – HR Fire Drill (Paid)`. Its confirmation state then links the buyer to the current ValuedHR scheduling page.

Before changing the Stripe redirect, confirm that `https://valuedhr.com/hr-fire-drill-intake.html` is live. Test the complete flow with a Stripe test-mode Payment Link (or a temporary low-value test product), then verify:

1. Stripe redirects to the intake page after payment.
2. The intake creates a Zoho lead with the expected paid lead source and description.
3. The on-page confirmation appears and the scheduling link opens.

Do not add payment details, employee names, medical information, identity numbers, confidential documents, or other sensitive data to the intake URL or form.
