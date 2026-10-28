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
var Effigy_exports = {};
__export(Effigy_exports, {
  Effigy: () => Effigy
});
module.exports = __toCommonJS(Effigy_exports);
var import_react = __toESM(require("react"));
var Effigy = function(_a) {
  var style = _a.style, body = _a.body, head = _a.head, face = _a.face, beard = _a.beard, mask = _a.mask, accessory = _a.accessory;
  return import_react.default.createElement(
    "svg",
    { style, xmlns: "http://www.w3.org/2000/svg", viewBox: "184.21621621621625 210.7874999999999 940.2702702702704 1130.5875", overflow: "visible", width: "940.2702702702704px", height: "1130.5875px" },
    import_react.default.createElement(
      "g",
      { id: "Bust" },
      import_react.default.createElement("g", { id: "Body", transform: "translate(147, 639) scale(1 1)" }, createBody(body)),
      createHead(body, import_react.default.createElement(
        import_react.default.Fragment,
        null,
        import_react.default.createElement("g", { id: "Hair", transform: "translate(342, 190) scale(1 1)" }, createHair(head)),
        import_react.default.createElement("g", { id: "Face", transform: "translate(531, 366) scale(1 1)" }, createFace(face)),
        import_react.default.createElement("g", { id: "Beard", transform: "translate(495, 518) scale(1 1)" }, createBeard(beard)),
        import_react.default.createElement("g", { id: "Mask", transform: "translate(400, 480) scale(1 1)" }),
        import_react.default.createElement("g", { id: "Accessories", transform: "translate(419, 421) scale(1 1)" }, createAccessory(accessory))
      ))
    )
  );
};
var createHair = function(head) {
  var _a;
  if (!head) {
    return null;
  }
  var element = (_a = require("./head/".concat(head.type))) === null || _a === void 0 ? void 0 : _a.default;
  var reactElement = import_react.default.createElement(element, head.options);
  if (head.type === "Bald") {
    return import_react.default.createElement("g", { transform: "translate(50 20)" }, reactElement);
  }
  if (head.type === "BangsTwo") {
    return import_react.default.createElement("g", { transform: "translate(20 0)" }, reactElement);
  }
  if (head.type === "BantuKnots") {
    return import_react.default.createElement("g", { transform: "translate(30 0)" }, reactElement);
  }
  if (head.type === "Bear") {
    return import_react.default.createElement("g", { transform: "translate(20 0)" }, reactElement);
  }
  if (head.type === "Bun") {
    return import_react.default.createElement("g", { transform: "translate(-20 -30)" }, reactElement);
  }
  if (head.type === "Beanie") {
    return import_react.default.createElement("g", { transform: "translate(20 0)" }, reactElement);
  }
  if (head.type === "BunClip") {
    return import_react.default.createElement("g", { transform: "translate(20 -70)" }, reactElement);
  }
  if (head.type === "BunKnots") {
    return import_react.default.createElement("g", { transform: "translate(10 -30)" }, reactElement);
  }
  if (head.type === "BunTwo") {
    return import_react.default.createElement("g", { transform: "translate(-50 -90)" }, reactElement);
  }
  if (head.type === "ColorMedium") {
    return import_react.default.createElement("g", { transform: "translate(30 0)" }, reactElement);
  }
  if (head.type === "CornrowsLight") {
    return import_react.default.createElement("g", { transform: "translate(-15 0)" }, reactElement);
  }
  if (head.type === "DreadsTwo") {
    return import_react.default.createElement("g", { transform: "translate(0 -15)" }, reactElement);
  }
  if (head.type === "FlatTop") {
    return import_react.default.createElement("g", { transform: "translate(50 0)" }, reactElement);
  }
  if (head.type === "FlatTopLong") {
    return import_react.default.createElement("g", { transform: "translate(50 0)" }, reactElement);
  }
  if (head.type === "GrayShort") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "HatHip") {
    return import_react.default.createElement("g", { transform: "translate(-30 0)" }, reactElement);
  }
  if (head.type === "Hijab") {
    return import_react.default.createElement("g", { transform: "translate(50 20)" }, reactElement);
  }
  if (head.type === "LongAfro") {
    return import_react.default.createElement("g", { transform: "translate(-100 -130)" }, reactElement);
  }
  if (head.type === "LongBangs") {
    return import_react.default.createElement("g", { transform: "translate(-25 0)" }, reactElement);
  }
  if (head.type === "LongCurly") {
    return import_react.default.createElement("g", { transform: "translate(-50 -40)" }, reactElement);
  }
  if (head.type === "LongHair") {
    return import_react.default.createElement("g", { transform: "translate(-50 0)" }, reactElement);
  }
  if (head.type === "MediumBangs") {
    return import_react.default.createElement("g", { transform: "translate(-50 0)" }, reactElement);
  }
  if (head.type === "MediumBangsColor") {
    return import_react.default.createElement("g", { transform: "translate(-20 0)" }, reactElement);
  }
  if (head.type === "MediumBangsOne") {
    return import_react.default.createElement("g", { transform: "translate(40 10)" }, reactElement);
  }
  if (head.type === "MediumOne") {
    return import_react.default.createElement("g", { transform: "translate(40 10)" }, reactElement);
  }
  if (head.type === "MediumStraight") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "MediumTwo") {
    return import_react.default.createElement("g", { transform: "translate(-20 0)" }, reactElement);
  }
  if (head.type === "Mohawk") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "MohawkKnots") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "NoHairThree") {
    return import_react.default.createElement("g", { transform: "translate(30 0)" }, reactElement);
  }
  if (head.type === "NoHairTwo") {
    return import_react.default.createElement("g", { transform: "translate(30 0)" }, reactElement);
  }
  if (head.type === "Pomp") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "Shaved") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "ShavedOne") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "ShavedThree") {
    return import_react.default.createElement("g", { transform: "translate(10 -20)" }, reactElement);
  }
  if (head.type === "ShortFive") {
    return import_react.default.createElement("g", { transform: "translate(40 -10)" }, reactElement);
  }
  if (head.type === "ShortFour") {
    return import_react.default.createElement("g", { transform: "translate(40 -10)" }, reactElement);
  }
  if (head.type === "ShortOne") {
    return import_react.default.createElement("g", { transform: "translate(40 -10)" }, reactElement);
  }
  if (head.type === "ShortThree") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "ShortTwo") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "Turban") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "Twists") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "TwistsTwo") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  if (head.type === "Wavy") {
    return import_react.default.createElement("g", { transform: "translate(40 0)" }, reactElement);
  }
  return reactElement;
};
var createFace = function(face) {
  var _a;
  var element = (_a = require("./face/".concat(face.type))) === null || _a === void 0 ? void 0 : _a.default;
  var reactElement = import_react.default.createElement(element, face.options);
  return reactElement;
};
var createBody = function(body) {
  var _a;
  var element = (_a = require("./body/effigy/".concat(body.type))) === null || _a === void 0 ? void 0 : _a.default;
  var reactElement = import_react.default.createElement(element, body.options);
  return reactElement;
};
var createBeard = function(beard) {
  var _a;
  if (!beard) {
    return null;
  }
  var element = (_a = require("./beard/".concat(beard.type))) === null || _a === void 0 ? void 0 : _a.default;
  var reactElement = import_react.default.createElement(element, beard.options);
  if (beard.type === "FullColor") {
    return import_react.default.createElement("g", { transform: "translate(0 -20) scale(0.94 0.97)" }, reactElement);
  }
  if (beard.type === "FullMax") {
    return import_react.default.createElement("g", { transform: "translate(0 -20) scale(0.98 1)" }, reactElement);
  }
  if (beard.type === "FullMedium") {
    return import_react.default.createElement("g", { transform: "translate(0 -10) scale(0.98 1)" }, reactElement);
  }
  if (beard.type === "MustacheBull") {
    return import_react.default.createElement("g", { transform: "translate(0 -20)" }, reactElement);
  }
  if (beard.type === "MustacheEight") {
    return import_react.default.createElement("g", { transform: "translate(-240 -75)" }, reactElement);
  }
  return reactElement;
};
var createAccessory = function(accessory) {
  var _a;
  if (!accessory) {
    return null;
  }
  var element = (_a = require("./accessory/".concat(accessory.type))) === null || _a === void 0 ? void 0 : _a.default;
  var reactElement = import_react.default.createElement(element, accessory.options);
  if (accessory.type === "Eyepatch") {
    return import_react.default.createElement("g", { transform: "translate(0 -60)" }, reactElement);
  }
  if (accessory.type === "SunglassesTwo") {
    return import_react.default.createElement("g", { transform: "translate(-10 0)" }, reactElement);
  }
  return reactElement;
};
var createHead = function(body, children) {
  var group = import_react.default.createElement("g", { id: "Head", transform: "translate(0 0)" }, children);
  if (body.type === "Explaining") {
    return import_react.default.createElement("g", { transform: "translate(0 30)" }, group);
  }
  if (body.type === "PointingUp") {
    return import_react.default.createElement("g", { transform: "translate(0 30)" }, group);
  }
  if (body.type === "PolkadotJacket") {
    return import_react.default.createElement("g", { transform: "translate(0 20)" }, group);
  }
  if (body.type === "Killer") {
    return import_react.default.createElement("g", { transform: "translate(0 10)" }, group);
  }
  if (body.type === "StrippedPocketTee") {
    return import_react.default.createElement("g", { transform: "translate(250 0)" }, group);
  }
  if (body.type === "Whatever") {
    return import_react.default.createElement("g", { transform: "translate(90 0)" }, group);
  }
  return group;
};
