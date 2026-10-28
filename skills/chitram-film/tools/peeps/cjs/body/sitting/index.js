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
var sitting_exports = {};
__export(sitting_exports, {
  SittingBodies: () => SittingBodies
});
module.exports = __toCommonJS(sitting_exports);
var import_Bike = require("./Bike");
var import_ClosedLegsColorPants = require("./ClosedLegsColorPants");
var import_ClosedLegsColorTee = require("./ClosedLegsColorTee");
var import_CrossedLegs = require("./CrossedLegs");
var import_HandsBackColorPants = require("./HandsBackColorPants");
var import_HandsBackColorTee = require("./HandsBackColorTee");
var import_MidColorPants = require("./MidColorPants");
var import_MidColorTee = require("./MidColorTee");
var import_OneLegColorPants = require("./OneLegColorPants");
var import_OneLegColorTee = require("./OneLegColorTee");
var import_Wheelchair = require("./Wheelchair");
var SittingBodies = {
  Bike: import_Bike.BikeConfig,
  ClosedLegsColorPants: import_ClosedLegsColorPants.ClosedLegsColorPantsConfig,
  ClosedLegsColorTee: import_ClosedLegsColorTee.ClosedLegsColorTeeConfig,
  CrossedLegs: import_CrossedLegs.CrossedLegsConfig,
  HandsBackColorPants: import_HandsBackColorPants.HandsBackColorPantsConfig,
  HandsBackColorTee: import_HandsBackColorTee.HandsBackColorTeeConfig,
  MidColorPants: import_MidColorPants.MidColorPantsConfig,
  MidColorTee: import_MidColorTee.MidColorTeeConfig,
  OneLegColorPants: import_OneLegColorPants.OneLegColorPantsConfig,
  OneLegColorTee: import_OneLegColorTee.OneLegColorTeeConfig,
  Wheelchair: import_Wheelchair.WheelchairConfig
};
