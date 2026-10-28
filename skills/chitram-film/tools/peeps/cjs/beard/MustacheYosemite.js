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
var MustacheYosemite_exports = {};
__export(MustacheYosemite_exports, {
  MustacheYosemiteConfig: () => MustacheYosemiteConfig,
  default: () => MustacheYosemite_default
});
module.exports = __toCommonJS(MustacheYosemite_exports);
var import_react = __toESM(require("react"));
var MustacheYosemiteConfig = {
  name: "Mustache Yosemite",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 299,
  height: 230,
  viewBox: "0 0 299 230"
};
var MustacheYosemite = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M279.528 190.863C281.547 192.778 285.93 196.993 290.129 198.846H294.056C294.899 198.688 295.727 198.447 296.549 198.175C297.618 195.552 297.824 192.496 297.299 189.418C294.331 172.372 291.68 155.111 293.093 137.762C294.424 121.405 299.132 105.128 297.861 88.6151C296.088 49.6481 258.461 22.6651 225.52 30.5541C221.267 30.9311 217.108 32.1281 213.404 34.2561C162.018 12.7001 98.5068 49.1221 110.469 108.704C112.762 124.814 116.46 140.093 115.324 156.512C114.78 164.37 113.529 172.142 112.061 179.874C110.959 185.676 108.042 192.83 110.722 198.557C121.488 205.356 132.712 191.226 139.903 179.099C143.667 168.907 146.794 158.472 150.32 148.201C156.682 129.74 158.156 119.544 179.151 114.51C188.219 111.417 196.313 106.857 203.254 100.845C208.589 98.2901 211.63 93.1721 213.448 87.9971C214.354 90.5451 213.101 93.6381 212.874 96.2831C228.101 116.465 246.944 112.644 253.723 126.678C258.91 139.889 261.825 153.973 265.794 167.643C266.337 169.514 276.384 187.881 279.528 190.863Z", fill: outlineColor })
  );
};
MustacheYosemite.config = MustacheYosemiteConfig;
var MustacheYosemite_default = MustacheYosemite;
