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
var FullMax_exports = {};
__export(FullMax_exports, {
  FullMaxConfig: () => FullMaxConfig,
  default: () => FullMax_default
});
module.exports = __toCommonJS(FullMax_exports);
var import_react = __toESM(require("react"));
var FullMaxConfig = {
  name: "Full Max",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 312,
  height: 275,
  viewBox: "0 0 312 275"
};
var FullMax = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M232.994 131.311C223.681 123.014 213.242 106.334 199.863 119.532C196.554 123.261 195.214 131.621 190.154 133.261C183.434 135.441 176.774 128.331 174.484 122.871C165.114 92.5337 203.848 84.2127 225.914 89.1137C236.694 93.5407 244.634 111.361 245.114 120.661C245.424 126.911 240.134 136.101 232.994 131.311ZM303.254 84.5507C303.163 84.1477 303.036 83.7837 302.883 83.4527C298.764 81.8957 295.505 83.4837 293.491 86.4497C293.557 87.1867 293.777 87.9337 293.916 88.6647C292.362 91.9387 290.96 95.9897 288.854 98.8187C288.438 98.8507 288.007 98.8067 287.593 98.6867C252.68 102.333 269.725 65.8037 234.314 56.7307C206.941 52.2147 157.467 57.3877 144.554 85.8787C134.37 131.387 82.5873 99.6767 65.5853 76.0097C47.4443 54.4707 35.7143 28.1507 24.4043 2.61074C22.0143 -2.79426 14.5553 1.07074 15.3663 6.25674C4.91229 27.2277 5.26029 52.4177 2.67129 75.3917C-1.73271 121.227 -6.02371 185.505 36.5633 213.492C92.0503 276.209 230.608 298.341 294.606 240.715C316.76 193.085 314.029 134.978 303.254 84.5507Z", fill: outlineColor })
  );
};
FullMax.config = FullMaxConfig;
var FullMax_default = FullMax;
