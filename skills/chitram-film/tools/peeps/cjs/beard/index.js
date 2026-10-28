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
var beard_exports = {};
__export(beard_exports, {
  Beards: () => Beards
});
module.exports = __toCommonJS(beard_exports);
var import_Chin = require("./Chin");
var import_Full = require("./Full");
var import_FullColor = require("./FullColor");
var import_FullMax = require("./FullMax");
var import_FullMedium = require("./FullMedium");
var import_Goatee = require("./Goatee");
var import_GoateeFull = require("./GoateeFull");
var import_MustacheBull = require("./MustacheBull");
var import_MustacheEight = require("./MustacheEight");
var import_MustacheFive = require("./MustacheFive");
var import_MustacheNine = require("./MustacheNine");
var import_MustacheSeven = require("./MustacheSeven");
var import_MustacheSix = require("./MustacheSix");
var import_MustacheThin = require("./MustacheThin");
var import_MustacheThinBull = require("./MustacheThinBull");
var import_MustacheYosemite = require("./MustacheYosemite");
var Beards = {
  Chin: import_Chin.ChinConfig,
  Full: import_Full.FullConfig,
  FullColor: import_FullColor.FullColorConfig,
  FullMax: import_FullMax.FullMaxConfig,
  FullMedium: import_FullMedium.FullMediumConfig,
  Goatee: import_Goatee.GoateeConfig,
  GoateeFull: import_GoateeFull.GoateeFullConfig,
  MustacheBull: import_MustacheBull.MustacheBullConfig,
  MustacheEight: import_MustacheEight.MustacheEightConfig,
  MustacheFive: import_MustacheFive.MustacheFiveConfig,
  MustacheNine: import_MustacheNine.MustacheNineConfig,
  MustacheSeven: import_MustacheSeven.MustacheSevenConfig,
  MustacheSix: import_MustacheSix.MustacheSixConfig,
  MustacheThin: import_MustacheThin.MustacheThinConfig,
  MustacheThinBull: import_MustacheThinBull.MustacheThinBullConfig,
  MustacheYosemite: import_MustacheYosemite.MustacheYosemiteConfig
};
