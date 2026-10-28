#!/usr/bin/env node
// Serve a film for interactive preview in a normal browser:  node bin/preview.mjs <project> [--port 5178]
// Open the printed URL: play/pause (space), scrubber, arrow keys step one frame, audio plays in sync.
import { serve, parseArgs, resolveProject } from "./lib.mjs";

const args = parseArgs(process.argv.slice(2));
const { dir, entry } = resolveProject(args._[0]);
const { port } = await serve(dir, parseInt(args.port || "5178", 10));
console.log(`Preview: http://127.0.0.1:${port}/${entry}?preview   (Ctrl+C to stop)`);
