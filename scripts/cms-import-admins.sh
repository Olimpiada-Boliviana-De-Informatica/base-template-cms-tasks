#!/bin/bash

CSV_FILE="../users/admins.csv"

while IFS=',' read -r username password
do
    /opt/.venv/bin/cmsAddAdmin "$username" --password "$password"
done < "$CSV_FILE"
