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
var index_exports = {};
__export(index_exports, {
  Accessories: () => import_accessory.Accessories,
  Beards: () => import_beard.Beards,
  Effigy: () => import_Effigy.Effigy,
  EffigyBodies: () => import_effigy.EffigyBodies,
  Faces: () => import_face.Faces,
  Heads: () => import_head.Heads,
  SittingBodies: () => import_sitting.SittingBodies,
  StandingBodies: () => import_standing.StandingBodies
});
module.exports = __toCommonJS(index_exports);
var import_accessory = require("./accessory");
var import_beard = require("./beard");
var import_effigy = require("./body/effigy");
var import_sitting = require("./body/sitting");
var import_standing = require("./body/standing");
var import_face = require("./face");
var import_head = require("./head");
var import_Effigy = require("./Effigy");
