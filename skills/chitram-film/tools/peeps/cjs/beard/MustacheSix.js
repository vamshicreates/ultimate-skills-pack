var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var MustacheSix_exports = {};
__export(MustacheSix_exports, {
  MustacheSixConfig: () => MustacheSixConfig,
  default: () => MustacheSix_default
});
module.exports = __toCommonJS(MustacheSix_exports);
var import_react = __toESM(require("react"));
var MustacheSixConfig = {
  name: "Mustache Six",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 286,
  height: 230,
  viewBox: "0 0 286 230"
};
var MustacheSix = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M258.53 37.2405C249.479 33.0085 239.751 30.4895 229.757 29.5965C225.435 29.2095 216.945 27.9885 212.348 30.8075C210.198 32.1275 208.381 33.9715 206.94 36.2235C206.378 35.4465 205.638 34.7845 205.17 33.9445C202.653 29.4225 187.205 29.3285 182.541 29.7125C171.481 30.6225 160.716 33.2195 150.578 37.5855C132.377 45.4255 117.087 61.7145 121.895 82.3945C122.575 85.3235 125.856 86.4625 128.559 85.9565C146.778 82.5415 164.997 79.1255 183.217 75.7105C187.446 74.9185 191.676 74.1255 195.905 73.3325C199.73 72.6155 204.418 72.3885 208.048 70.7385C209.508 71.3625 211.134 71.7585 212.87 72.1025C234.791 76.4565 256.74 80.6805 278.675 84.9695C281.305 85.4845 284.755 84.1505 285.227 81.2365C288.375 61.7925 275.992 45.4045 258.53 37.2405Z", fill: outlineColor })
  );
};
MustacheSix.config = MustacheSixConfig;
var MustacheSix_default = MustacheSix;
