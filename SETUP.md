# AUREVIA existing website — order-system update

These are updates to the existing HTML/CSS/JavaScript website, not a replacement website. Keep your current live deployment running while testing these files.

## Included
- `index.html`: multi-product cart, quantity edits/removal, customer checkout, and an order reference after successful save.
- `admin.html`: order list, delivery fee entry and final total calculation, WhatsApp/email order-total drafts, owner-only bank-details screen, a separate WhatsApp payment-request draft (available only after status is changed to `awaiting payment`), and verified-payment record form.
- `config.js` and `defaults.js`: existing site configuration/default content.
- `order-system-upgrade.sql`: reference migration for databases that have not already received the changes. Do not run it blindly; some order columns and the `private_settings` table were added manually in the existing project during this setup.
- `schema.sql`: original schema reference only. Do not run it against the existing project.

## Important: current Supabase project
The owner has already run an `ALTER TABLE public.orders ... ADD COLUMN IF NOT EXISTS ...` query and created `public.private_settings` with RLS plus two policies. Do not rerun the original schema. Do not drop tables or rows.

## Before deploying
1. Keep the current live site as-is.
2. Make a backup/export of the current Supabase tables.
3. Test these files in a separate preview or staging deployment using the existing `config.js` values.
4. Test product listing, multi-item cart, checkout, order reference, admin login, delivery-fee calculation, WhatsApp and email draft creation, owner-only bank settings, and payment recording.
5. Confirm the `private_settings` policies use the project's existing `public.is_staff()` and `public.is_owner()` functions and verify an ordinary visitor cannot read the table.
6. Only deploy after all tests pass. These files have not been deployed and have not been end-to-end tested against the live Supabase project.

## Important limitations
- WhatsApp and email confirmations open a draft for a staff member to review and send; they are not sent automatically.
- Bank details are included only in the separate WhatsApp payment-request draft when saved in the owner-only settings screen. The email draft asks the customer to confirm the total; it does not include bank details automatically.
- Payment recording requires amount to equal the order total and captures date/time, method, reference, and the signed-in staff email. A person must verify the credit in the actual bank account first.
- A full end-to-end browser test and security review are still required before production deployment.
