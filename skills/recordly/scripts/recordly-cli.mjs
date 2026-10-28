#!/usr/bin/env node
/**
 * Recordly CLI Helper for Antigravity Skill (.agents/skills/recordly)
 *
 * Commands:
 *   node scripts/recordly-cli.mjs create-project --video <abs_path> --output <project.recordly> [options]
 *   node scripts/recordly-cli.mjs export --input <video_or_project> --output <output.mp4> [options]
 *   node scripts/recordly-cli.mjs install-mac
 *   node scripts/recordly-cli.mjs open <video_or_project>
 */

import { execFile, spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");

function parseArgs(argv) {
	const args = { _: [] };
	for (let i = 0; i < argv.length; i++) {
		const token = argv[i];
		if (token.startsWith("--")) {
			const key = token.slice(2);
			const next = argv[i + 1];
			if (!next || next.startsWith("--")) {
				args[key] = true;
			} else {
				if (args[key] !== undefined) {
					args[key] = Array.isArray(args[key]) ? [...args[key], next] : [args[key], next];
				} else {
					args[key] = next;
				}
				i++;
			}
		} else {
			args._.push(token);
		}
	}
	return args;
}

function parseZoomSpecs(rawSpecs) {
	if (!rawSpecs) return [];
	const specs = Array.isArray(rawSpecs) ? rawSpecs : [rawSpecs];
	return specs.map((spec, index) => {
		// Format: startMs:endMs[:depth[:cx[:cy]]]
		const parts = String(spec).split(":");
		const startMs = Number(parts[0] ?? 0);
		const endMs = Number(parts[1] ?? startMs + 2000);
		const depth = Math.min(6, Math.max(1, Number(parts[2] ?? 3)));
		const cx = Math.min(1, Math.max(0, Number(parts[3] ?? 0.5)));
		const cy = Math.min(1, Math.max(0, Number(parts[4] ?? 0.5)));
		return {
			id: `zoom-${index + 1}`,
			startMs,
			endMs,
			depth,
			focus: { cx, cy },
			mode: "manual",
		};
	});
}

function parseSpeedSpecs(rawSpecs) {
	if (!rawSpecs) return [];
	const specs = Array.isArray(rawSpecs) ? rawSpecs : [rawSpecs];
	return specs.map((spec, index) => {
		// Format: startMs:endMs:speed
		const parts = String(spec).split(":");
		return {
			id: `speed-${index + 1}`,
			startMs: Number(parts[0] ?? 0),
			endMs: Number(parts[1] ?? 2000),
			speed: Number(parts[2] ?? 1.5),
		};
	});
}

function parseTrimSpecs(rawSpecs) {
	if (!rawSpecs) return [];
	const specs = Array.isArray(rawSpecs) ? rawSpecs : [rawSpecs];
	return specs.map((spec, index) => {
		// Format: startMs:endMs
		const parts = String(spec).split(":");
		return {
			id: `trim-${index + 1}`,
			startMs: Number(parts[0] ?? 0),
			endMs: Number(parts[1] ?? 1000),
		};
	});
}

async function cmdCreateProject(args) {
	const videoPath = args.video ? path.resolve(String(args.video)) : null;
	if (!videoPath) {
		throw new Error("Missing required --video <path>");
	}
	const outputPath = args.output
		? path.resolve(String(args.output))
		: `${videoPath.replace(/\.[^.]+$/, "")}.recordly`;

	const paddingVal = args.padding !== undefined ? Number(args.padding) : 20;
	const projectData = {
		version: 2,
		videoPath,
		editor: {
			wallpaper: String(args.wallpaper ?? "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)"),
			shadowIntensity: args.shadow !== undefined ? Number(args.shadow) : 0.6,
			backgroundBlur: args.blur !== undefined ? Number(args.blur) : 0,
			zoomMotionBlur: args["zoom-motion-blur"] !== undefined ? Number(args["zoom-motion-blur"]) : 0.35,
			connectZooms: args["connect-zooms"] !== "false",
			showCursor: args["show-cursor"] !== "false",
			loopCursor: Boolean(args["loop-cursor"]),
			cursorStyle: String(args["cursor-style"] ?? "tahoe"),
			cursorClickEffect: String(args["click-effect"] ?? "ripple"),
			cursorClickEffectColor: String(args["click-color"] ?? "#2563EB"),
			cursorSize: args["cursor-size"] !== undefined ? Number(args["cursor-size"]) : 3.0,
			cursorSmoothing: args["cursor-smoothing"] !== undefined ? Number(args["cursor-smoothing"]) : 0.67,
			cursorMotionBlur: args["cursor-motion-blur"] !== undefined ? Number(args["cursor-motion-blur"]) : 0.6,
			cursorClickBounce: args["cursor-bounce"] !== undefined ? Number(args["cursor-bounce"]) : 2,
			cursorSway: args["cursor-sway"] !== undefined ? Number(args["cursor-sway"]) : 0.4,
			borderRadius: args["border-radius"] !== undefined ? Number(args["border-radius"]) : 8,
			padding: {
				top: paddingVal,
				bottom: paddingVal,
				left: paddingVal,
				right: paddingVal,
				linked: true,
			},
			cropRegion: { x: 0, y: 0, width: 1, height: 1 },
			zoomRegions: parseZoomSpecs(args.zoom),
			trimRegions: parseTrimSpecs(args.trim),
			speedRegions: parseSpeedSpecs(args.speed),
			annotationRegions: [],
			audioRegions: [],
			autoCaptions: [],
			aspectRatio: String(args["aspect-ratio"] ?? "16:9"),
			exportEncodingMode: String(args["encoding-mode"] ?? "balanced"),
			exportQuality: String(args.quality ?? "high"),
			mp4FrameRate: args.fps !== undefined ? Number(args.fps) : 60,
			exportFormat: String(args.format ?? "mp4"),
		},
	};

	if (args.webcam) {
		projectData.editor.webcam = {
			enabled: true,
			sourcePath: path.resolve(String(args.webcam)),
			timeOffsetMs: 0,
			mirror: true,
			cropRegion: { x: 0, y: 0, width: 1, height: 1 },
			corner: "bottom-right",
			positionPreset: String(args["webcam-position"] ?? "bottom-right"),
			positionX: 1,
			positionY: 1,
			size: args["webcam-size"] !== undefined ? Number(args["webcam-size"]) : 40,
			width: 40,
			height: 40,
			reactToZoom: true,
			roundness: args["webcam-roundness"] !== undefined ? Number(args["webcam-roundness"]) : 100,
			shadow: 0.3,
			margin: 24,
		};
	}

	await fs.mkdir(path.dirname(outputPath), { recursive: true });
	await fs.writeFile(outputPath, JSON.stringify(projectData, null, 2), "utf8");
	console.log(JSON.stringify({ ok: true, projectPath: outputPath, videoPath }));
}

async function cmdExport(args) {
	const inputRaw = args.input ?? args.project ?? args.video;
	if (!inputRaw) {
		throw new Error("Missing --input <video_or_project.recordly>");
	}
	const inputPath = path.resolve(String(inputRaw));
	const isProject = inputPath.endsWith(".recordly");
	const outputPath = args.output
		? path.resolve(String(args.output))
		: `${inputPath.replace(/\.[^.]+$/, "")}-polished.mp4`;

	const env = {
		...process.env,
		RECORDLY_SMOKE_EXPORT: "1",
		RECORDLY_SMOKE_EXPORT_OUTPUT: outputPath,
		...(isProject
			? { RECORDLY_SMOKE_EXPORT_PROJECT: inputPath }
			: { RECORDLY_SMOKE_EXPORT_INPUT: inputPath }),
		...(args.quality ? { RECORDLY_SMOKE_EXPORT_QUALITY: String(args.quality) } : {}),
		...(args.fps ? { RECORDLY_SMOKE_EXPORT_FPS: String(args.fps) } : {}),
		...(args["encoding-mode"]
			? { RECORDLY_SMOKE_EXPORT_ENCODING_MODE: String(args["encoding-mode"]) }
			: {}),
		...(args.shadow !== undefined
			? { RECORDLY_SMOKE_EXPORT_SHADOW_INTENSITY: String(args.shadow) }
			: {}),
		...(args.webcam
			? { RECORDLY_SMOKE_EXPORT_WEBCAM_INPUT: path.resolve(String(args.webcam)) }
			: {}),
	};

	const appBinary = "/Applications/Recordly.app/Contents/MacOS/Recordly";
	let cmd = appBinary;
	let cmdArgs = [];
	try {
		await fs.access(appBinary);
	} catch {
		const localElectron = path.join(repoRoot, "node_modules", ".bin", "electron");
		cmd = localElectron;
		cmdArgs = [repoRoot];
	}

	await new Promise((resolve, reject) => {
		const child = spawn(cmd, cmdArgs, { cwd: repoRoot, env, stdio: "inherit" });
		child.on("error", reject);
		child.on("close", (code) => {
			if (code === 0) resolve();
			else reject(new Error(`Recordly export exited with code ${code}`));
		});
	});

	console.log(JSON.stringify({ ok: true, outputPath }));
}

async function cmdInstallMac() {
	const arch = process.arch === "arm64" ? "arm64" : "x64";
	console.log(`Checking latest Recordly macOS (${arch}) release...`);
	const { stdout } = await execFileAsync("curl", [
		"-sL",
		"https://api.github.com/repos/webadderallorg/Recordly/releases/latest",
	]);
	const release = JSON.parse(stdout);
	const asset = (release.assets ?? []).find(
		(a) => a.name.endsWith(".dmg") && a.name.toLowerCase().includes(arch),
	) ?? (release.assets ?? []).find((a) => a.name.endsWith(".dmg"));

	if (!asset) {
		throw new Error("Could not find a macOS .dmg asset in the latest GitHub release.");
	}

	const dmgPath = path.join("/tmp", asset.name);
	console.log(`Downloading ${asset.browser_download_url} -> ${dmgPath}...`);
	await execFileAsync("curl", ["-L", "-o", dmgPath, asset.browser_download_url]);
	console.log(`Downloaded ${dmgPath}. Mounting and installing to /Applications/Recordly.app...`);
	const { stdout: attachOut } = await execFileAsync("hdiutil", ["attach", dmgPath, "-nobrowse"]);
	const mountLine = attachOut
		.split("\n")
		.find((line) => line.includes("/Volumes/"));
	const mountPoint = mountLine ? mountLine.slice(mountLine.indexOf("/Volumes/")).trim() : "/Volumes/Recordly";
	try {
		await execFileAsync("cp", ["-R", `${mountPoint}/Recordly.app`, "/Applications/"]);
		await execFileAsync("xattr", ["-rd", "com.apple.quarantine", "/Applications/Recordly.app"]).catch(() => {});
	} finally {
		await execFileAsync("hdiutil", ["detach", mountPoint, "-quiet"]).catch(() => {});
	}
	console.log(JSON.stringify({ ok: true, installed: "/Applications/Recordly.app", version: release.tag_name }));
}

async function cmdOpen(args) {
	const target = args._[1] ? path.resolve(String(args._[1])) : null;
	if (target) {
		await execFileAsync("open", ["-a", "/Applications/Recordly.app", target]);
	} else {
		await execFileAsync("open", ["-a", "/Applications/Recordly.app"]);
	}
}

async function main() {
	const args = parseArgs(process.argv.slice(2));
	const subcmd = args._[0];
	if (subcmd === "create-project") {
		await cmdCreateProject(args);
	} else if (subcmd === "export") {
		await cmdExport(args);
	} else if (subcmd === "install-mac") {
		await cmdInstallMac();
	} else if (subcmd === "open") {
		await cmdOpen(args);
	} else {
		console.log(`Usage:
  node scripts/recordly-cli.mjs create-project --video <path> [--output <path.recordly>] [--zoom "startMs:endMs:depth:cx:cy"] [--speed "startMs:endMs:speed"] [--trim "startMs:endMs"] [--wallpaper "<css-or-path>"] [--cursor-style tahoe] [--click-effect ripple]
  node scripts/recordly-cli.mjs export --input <video_or_project.recordly> --output <output.mp4> [--quality high|source] [--fps 60]
  node scripts/recordly-cli.mjs install-mac
  node scripts/recordly-cli.mjs open [file.recordly|video.mp4]`);
	}
}

main().catch((err) => {
	console.error(err.message || err);
	process.exit(1);
});
