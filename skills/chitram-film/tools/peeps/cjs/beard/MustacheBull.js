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
var MustacheBull_exports = {};
__export(MustacheBull_exports, {
  MustacheBullConfig: () => MustacheBullConfig,
  default: () => MustacheBull_default
});
module.exports = __toCommonJS(MustacheBull_exports);
var import_react = __toESM(require("react"));
var MustacheBullConfig = {
  name: "Mustache Bull",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 372,
  height: 249,
  viewBox: "0 0 372 249"
};
var MustacheBull = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M350.983 2.00062C348.863 -1.18938 342.853 0.750617 344.403 4.77062C361.226 42.9426 353.443 72.6326 306.162 67.4396C277.658 65.5886 249.976 40.3836 221.349 52.9256C213.968 58.8546 209.109 59.5896 201.31 53.1736C170.364 39.6326 135.324 63.7706 104.233 67.0306C55.5884 71.8136 29.1314 55.5396 53.7044 5.64062C55.2434 2.25062 50.7734 -2.21938 48.0334 1.26062C14.1024 40.7436 12.3984 93.7566 67.0154 114.211C107.1 127.559 183.759 138.604 211.273 98.3606C228.835 127.421 266.37 129.16 296.544 123.96C369.4 117.235 391.724 60.6266 350.983 2.00062Z", fill: outlineColor })
  );
};
MustacheBull.config = MustacheBullConfig;
var MustacheBull_default = MustacheBull;
