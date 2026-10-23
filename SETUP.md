# AUREVIA: set up your owner dashboard (about 30 minutes, no coding)

You need two free accounts: Supabase (database, file storage, login) and Netlify (hosting).
Free plans have limits that can change. Check their pricing pages before relying on them.

## 1. Create the database
1. Sign up at supabase.com and create a new project. Save the database password.
2. Open `schema.sql` in a text editor. On the LAST line, replace `change-me@example.com` with YOUR email (small letters).
3. In Supabase open SQL Editor > New query, paste the whole file, press Run. It should say "Success".

## 2. Connect the website
1. In Supabase go to Project Settings > API. Copy the Project URL and the "anon public" key.
2. Open `config.js`, paste them between the quotes, save.

## 3. Put the site online
1. Go to app.netlify.com/drop and drag in this whole folder (index.html, admin.html, config.js, defaults.js).
2. Netlify gives you a web address. That is your website. Your dashboard is that address + `/admin.html`.
3. In Supabase: Authentication > URL Configuration. Set "Site URL" to your Netlify address and add `your-address/admin.html` under Redirect URLs. Save.

## 4. Sign in and fill in your content
Open `/admin.html`, type your email, tap the link Supabase emails you. Use the same email on any phone, tablet or laptop.
Then, in this order: Delivery (add your areas and fees), Policies (write your real policies), Products, Brochure, Blog.
Turn on "Alerts" in the dashboard on each device you want browser notifications on.

## Add your supervisor
Dashboard > Staff > their email > Supervisor > Add. They sign in with their own email.
Supervisors can view and update requests and orders and edit content. Only you can delete things or manage staff.

## Good to know
- No online payment. Orders are requests. You mark "payment received" yourself after checking your bank or payment account.
- Alerts only work while the dashboard is open in a browser. There are no email or SMS alerts.
- Supabase's built-in sign-in email has a low sending limit. If a supervisor can't get their link, set up a custom email sender in Supabase (Authentication > Emails).
- Anyone can use the forms, so you may get spam. Delete it (owner only). Deleting a request does not delete uploaded files.
- Health information and applicant documents are stored in your Supabase project and only signed-in staff can read them. Nigerian data protection duties (privacy policy, retention, consent records) are still yours. Have a professional review.
- If the database is down or not set up, the forms fall back to opening WhatsApp.
