files=(
  'devices'
  'analysis'
  )

folders=(
  'sql'
)

for folder in "${folders[@]}"; do
  echo "Folder: $folder"

  for filename in "${files[@]}"; do
    echo "Running script: $filename"

    if psql -U postgres -f "/docker-entrypoint-initdb.d/${folder}/${filename}.sql"; then
      echo "Successfully executed $filename"
    else
      echo "Error executing $filename:" 1>&2
    fi

    echo "--------------------"
  done
done