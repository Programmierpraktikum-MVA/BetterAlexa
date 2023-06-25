#!/bin/bash
rm -rf out
sed -i.bak 's/output: "standalone",/output: "export",/g' next.config.mjs
NEXT_PUBLIC_IS_EXTENSION=true next build
mv -f next.config.mjs.bak next.config.mjs
sed -i.bak "s#{{CRX_GOOGLE_CLIENT_ID}}#"$CRX_GOOGLE_CLIENT_ID"#g" out/manifest.json
sed -i.bak "s#{{CRX_PUBLIC_KEY}}#"$CRX_PUBLIC_KEY"#g" out/manifest.json
mv out/_next out/assets && find out -type f \( -name '*.html' -o -name '*.js' \) -exec sed -i.bak 's/\/_next/\/assets/g' {} +
find out -name "*.bak" -type f -delete
mkdir -p dist
zip -r dist/$(date -u +"%Y-%m-%dT%H:%M:%SZ").zip out