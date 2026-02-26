#!/bin/bash

# Build script for Vercel deployment

echo "Installing dependencies..."
npm install

echo "Building the Next.js application..."
npm run build

echo "Build completed successfully!"