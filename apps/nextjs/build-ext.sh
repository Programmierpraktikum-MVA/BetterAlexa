#!/bin/bash
sed -i.bak 's/output: "standalone",/output: "export",/g' next.config.mjs
pnpm build
mv -f next.config.mjs.bak next.config.mjs
mkdir -p dist
mv out/_next out/assets && find out -name '*.html' -exec sed -i.bak 's/\/_next/\/assets/g' {} +
rm out/*.bak
zip -r dist/$(date -u +"%Y-%m-%dT%H:%M:%SZ").zip out