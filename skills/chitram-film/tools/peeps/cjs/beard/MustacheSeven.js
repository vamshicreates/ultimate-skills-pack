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
var MustacheSeven_exports = {};
__export(MustacheSeven_exports, {
  MustacheSevenConfig: () => MustacheSevenConfig,
  default: () => MustacheSeven_default
});
module.exports = __toCommonJS(MustacheSeven_exports);
var import_react = __toESM(require("react"));
var MustacheSevenConfig = {
  name: "Mustache Seven",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 285,
  height: 230,
  viewBox: "0 0 285 230"
};
var MustacheSeven = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M258.635 38.6644C252.041 37.4254 245.224 37.7734 238.674 36.3314C232.284 34.9234 227.209 30.7364 221.035 28.7874C215.602 27.0714 209.234 28.2334 205.003 31.5594C201.072 29.7424 196.605 29.3494 192.133 29.9494C185.351 30.8594 179.023 33.7294 172.982 36.8334C172.282 37.1934 171.581 37.5364 170.881 37.8834C159.719 37.6044 148.276 37.6264 137.323 40.0184C127.624 42.1374 118.455 47.0694 112.671 55.3074C106.198 64.5284 105.029 76.2704 104.031 87.1664C103.396 94.0824 113.002 95.4854 116.257 90.4774C119.632 85.2854 123.145 80.0814 127.642 75.7794C132.75 70.8924 138.963 68.9684 145.926 68.5224C161.294 67.5384 176.764 68.3634 192.147 67.6824C201.064 67.2874 210.992 63.8584 214.586 56.1064C218.422 62.1174 227.114 65.6914 234.263 66.2334C241.818 66.8074 249.489 65.4344 256.969 67.0084C264.115 68.5124 272.609 73.8344 271.02 82.3464C270.086 87.3464 276.407 90.2944 279.316 85.8444C291.195 67.6614 279.49 42.5854 258.635 38.6644Z", fill: outlineColor })
  );
};
MustacheSeven.config = MustacheSevenConfig;
var MustacheSeven_default = MustacheSeven;
