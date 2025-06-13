#!/bin/bash

CSV_FILE="../users/users.csv"

while IFS=',' read -r username password
do
    /opt/.venv/bin/cmsAddUser "" "" $username -p "$password"
    /opt/.venv/bin/cmsAddParticipation "$username" -c 1
done < "$CSV_FILE"
