#!/bin/bash
sed -i.bak 's/output: "standalone",/output: "export",/g' next.config.mjs
pnpm build
mv -f next.config.mjs.bak next.config.mjs
mkdir -p dist
zip -r dist/$(date -u +"%Y-%m-%dT%H:%M:%SZ").zip out