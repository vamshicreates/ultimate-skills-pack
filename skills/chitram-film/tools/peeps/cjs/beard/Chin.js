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
var Chin_exports = {};
__export(Chin_exports, {
  ChinConfig: () => ChinConfig,
  default: () => Chin_default
});
module.exports = __toCommonJS(Chin_exports);
var import_react = __toESM(require("react"));
var ChinConfig = {
  name: "Chin",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 283,
  height: 245,
  viewBox: "0 0 283 245"
};
var Chin = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M212.56 153.064C212.56 153.064 168.17 159.587 148.3 150.368C128.49 141.178 109.22 132.286 91.2503 120.114C72.8403 107.642 57.2203 92.8328 46.0703 73.8757C35.7003 56.237 27.0803 37.5205 18.4003 18.9484C17.8931 17.8631 12.9103 7.0738 11.1503 3.45561C8.44034 -2.15452 0.52034 -0.393546 0.52034 8.31515C0.52034 17.0238 0.13034 82.9754 15.3503 108.919C29.0803 132.35 52.3503 148.722 75.4703 163.012C101.05 178.813 135.03 195.894 165.55 200.407C193.17 204.487 224.69 193.026 244.69 174.136C265.6 154.381 271.52 127.542 282.31 101.839C284.72 96.0941 276.177 92.6294 273.67 98.2793C268.951 108.919 212.56 153.064 212.56 153.064Z", fill: outlineColor })
  );
};
Chin.config = ChinConfig;
var Chin_default = Chin;
