/* One-time: install Open Peeps (CC0) + react + esbuild here and convert the ESM build to CommonJS
   (its files use `require` inside ESM, so they can't be imported directly).  node setup.cjs */
const { execSync } = require("child_process"), fs = require("fs"), path = require("path");
process.chdir(__dirname);
if (!fs.existsSync("package.json")) fs.writeFileSync("package.json", '{"name":"peeps-tool","private":true}');
execSync("npm install @opeepsfun/open-peeps react@18 react-dom@18 esbuild --no-audit --no-fund", { stdio: "inherit" });
const esbuild = require(path.join(__dirname, "node_modules", "esbuild"));
const root = "node_modules/@opeepsfun/open-peeps/build", files = [];
(function walk(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f); fs.statSync(p).isDirectory() ? walk(p) : p.endsWith(".js") && files.push(p); } })(root);
// esbuild API, not the CLI: 180+ paths overflow the Windows command line
esbuild.buildSync({ entryPoints: files, format: "cjs", outdir: "cjs", outbase: root, logLevel: "warning" });
console.log("open-peeps ready:", files.length, "modules → tools/peeps/cjs");
