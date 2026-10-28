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
var MustacheThin_exports = {};
__export(MustacheThin_exports, {
  MustacheThinConfig: () => MustacheThinConfig,
  default: () => MustacheThin_default
});
module.exports = __toCommonJS(MustacheThin_exports);
var import_react = __toESM(require("react"));
var MustacheThinConfig = {
  name: "Mustache Thin",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 286,
  height: 230,
  viewBox: "0 0 286 230"
};
var MustacheThin = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M229.945 33.9998C241.659 34.8308 252.739 42.0988 262.816 47.7168C272.514 53.5108 279.692 62.0952 285.426 71.6662L285.798 72.2918C286.134 72.7905 285.534 73.3515 285.042 73.1612L284.965 73.1248C275.448 68.3498 265.406 64.4798 256.062 59.2708C246.938 53.6298 235.734 51.7018 226.541 46.5708C221.287 42.6758 222.864 34.3008 229.945 33.9998ZM199.476 39.6831C199.903 42.3551 198.824 46.5961 195.316 47.8351C189.153 50.0091 183.54 51.1812 177.35 52.8774L169.325 55.1249C153.91 59.4668 138.264 64.128 124.617 70.9681L124.189 70.7801C114.276 64.5781 169.04 38.7041 187.949 34.5821C191.423 33.8241 198.831 35.6511 199.476 39.6831Z", fill: outlineColor })
  );
};
MustacheThin.config = MustacheThinConfig;
var MustacheThin_default = MustacheThin;
