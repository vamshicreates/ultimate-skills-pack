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
var MustacheFive_exports = {};
__export(MustacheFive_exports, {
  MustacheFiveConfig: () => MustacheFiveConfig,
  default: () => MustacheFive_default
});
module.exports = __toCommonJS(MustacheFive_exports);
var import_react = __toESM(require("react"));
var MustacheFiveConfig = {
  name: "Mustache Five",
  props: [
    {
      name: "outlineColor"
    }
  ],
  width: 297,
  height: 230,
  viewBox: "0 0 297 230"
};
var MustacheFive = function(_a) {
  var _b = _a.outlineColor, outlineColor = _b === void 0 ? "#000" : _b;
  return import_react.default.createElement(
    import_react.default.Fragment,
    null,
    import_react.default.createElement("path", { d: "M294.392 32.7225C293.059 28.7405 286.2 29.0875 286.622 33.7745C287.105 39.1295 285.272 45.1015 280.142 47.7015C274.77 50.4235 268.726 47.9765 265.449 43.3065C262.6 39.2475 260.635 34.8325 257.05 31.2925C253.717 28.0005 249.663 25.4615 245.228 23.9545C241.774 22.7815 238.191 22.4695 234.716 22.8545C226.056 20.8975 216.022 25.3485 210.625 32.1005C210.277 32.5355 209.954 32.9825 209.642 33.4335C209.107 32.7055 208.547 31.9845 207.954 31.2735C206.425 29.4415 204.527 29.0485 202.813 29.5475C193.052 22.2885 179.373 21.3265 168.287 27.8775C159.405 33.1265 152.058 40.8625 141.136 41.4645C132.485 41.9415 123.062 37.0055 122.452 27.4985C122.132 22.5345 115.368 18.3965 111.573 22.9925C103.595 32.6565 101.999 45.4935 106.413 57.1785C111.071 69.5075 120.561 78.1925 132.577 83.3015C145.553 88.8185 160.759 90.7345 174.796 90.2975C188.79 89.8615 201.514 84.4805 209.949 73.0335C210.956 71.6675 211.841 70.2795 212.617 68.8755C220.807 79.3035 233.645 83.6865 246.721 84.0015C260.401 84.3295 276.573 81.9285 286.245 71.3045C295.566 61.0645 298.783 45.8365 294.392 32.7225Z", fill: outlineColor })
  );
};
MustacheFive.config = MustacheFiveConfig;
var MustacheFive_default = MustacheFive;
