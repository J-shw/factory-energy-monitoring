files=(
  'devices'
  'analysis'
  'communication'
  )

for filename in "${files[@]}"; do
  echo "Running script: $filename"

  if psql -U postgres -f "/docker-entrypoint-initdb.d/sql/${filename}.sql"; then
    echo "Successfully executed $filename"
  else
    echo "Error executing $filename:" 1>&2
  fi

  echo "--------------------"
done

