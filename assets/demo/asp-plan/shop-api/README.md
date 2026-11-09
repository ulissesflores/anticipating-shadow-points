# shop-api
Flask + SQLAlchemy API. PostgreSQL 15 primary with one streaming read replica used by the nightly
reporting job. Deploys run `deploy.sh` from CI on every merge to main; there is no maintenance window
on weekdays.
