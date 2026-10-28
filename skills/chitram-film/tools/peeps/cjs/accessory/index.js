var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
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
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);
var accessory_exports = {};
__export(accessory_exports, {
  Accessories: () => Accessories
});
module.exports = __toCommonJS(accessory_exports);
var import_Eyepatch = require("./Eyepatch");
var import_Glasses = require("./Glasses");
var import_GlassesFive = require("./GlassesFive");
var import_GlassesFour = require("./GlassesFour");
var import_GlassesSix = require("./GlassesSix");
var import_GlassesThree = require("./GlassesThree");
var import_GlassesTwo = require("./GlassesTwo");
var import_Sunglasses = require("./Sunglasses");
var import_SunglassesTwo = require("./SunglassesTwo");
var Accessories = {
  Eyepatch: import_Eyepatch.EyepatchConfig,
  Glasses: import_Glasses.GlassesConfig,
  GlassesSix: import_GlassesSix.GlassesSixConfig,
  GlassesFive: import_GlassesFive.GlassesFiveConfig,
  GlassesFour: import_GlassesFour.GlassesFourConfig,
  GlassesThree: import_GlassesThree.GlassesThreeConfig,
  GlassesTwo: import_GlassesTwo.GlassesTwoConfig,
  Sunglasses: import_Sunglasses.SunglassesConfig,
  SunglassesTwo: import_SunglassesTwo.SunglassesTwoConfig
};
