Plan: cron at 08:00 daily running ~/ulisses-kb/sync/update.sh.

1. Edit crontab: `crontab -e` and add
   `0 8 * * * ~/ulisses-kb/sync/update.sh`.
2. Ensure update.sh is executable: `chmod +x update.sh`.
3. Log output to ~/ulisses-kb/sync/cron.log via shell redirection.
4. Verify after one day that the log shows successful runs.

For more robust behavior we can wrap the script in `flock` to avoid
overlapping runs, and rotate the log periodically.
