#!/bin/bash
rm -rf out
sed -i.bak 's/output: "standalone",/output: "export",/g' next.config.mjs
pnpm build
mv -f next.config.mjs.bak next.config.mjs
mv out/_next out/assets && find out -type f \( -name '*.html' -o -name '*.js' \) -exec sed -i.bak 's/\/_next/\/assets/g' {} +
find out -name "*.bak" -type f -delete
mkdir -p dist
zip -r dist/$(date -u +"%Y-%m-%dT%H:%M:%SZ").zip out