# Business Funnel

> How the business turns attention into revenue. Read by the daily brief.
> Copy this to the root of your project (or `context/`) and fill it in.
> Each metric line points at a table and column in your SQLite database.
> The table needs a `date` column (YYYY-MM-DD) for the 7-day averages.

## Currency
EUR

## Stages

### 1. Awareness
How people find you.
- YouTube views -> youtube_daily.total_views
- Website sessions -> web_daily.sessions

### 2. Conversion
Prospects becoming customers.
- Demo bookings -> bookings_daily.count

### 3. Revenue
Money in the bank.
- Revenue -> stripe_daily.revenue
- Active subscriptions -> stripe_daily.active_subs

## Monthly Targets
- Revenue: 50,000
- New customers: 10
