#!/bin/bash

# Start the Docker Compose
echo "Starting Docker Compose..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Failed to start Docker Compose."
    exit 1
fi

# Wait for the database to initialize
echo "Waiting for the database to initialize..."
sleep 10  # Adjust the sleep time if necessary

# Run the food_gene.py script
echo "Running food_gene.py..."
python food_gene.py
if [ $? -ne 0 ]; then
    echo "Failed to run food_gene.py."
    exit 1
fi

# Run the transports_gene.py script
echo "Running transports_gene.py..."
python transports_gene.py
if [ $? -ne 0 ]; then
    echo "Failed to run transports_gene.py."
    exit 1
fi

# Run the chauffage_gene.py script
echo "Running chauffage_gene.py..."
python chauffage_gene.py
if [ $? -ne 0 ]; then
    echo "Failed to run chauffage_gene.py."
    exit 1
fi

# Run the end_gene.py script
echo "Running end_gene.py..."
python end_gene.py
if [ $? -ne 0 ]; then
    echo "Failed to run end_gene.py."
    exit 1
fi

# Run the defi_gene.py script
echo "Running defi_gene.py..."
python defi_gene.py
if [ $? -ne 0 ]; then
    echo "Failed to run defi_gene.py."
    exit 1
fi

# Confirmation message
echo "All scripts executed successfully!"
