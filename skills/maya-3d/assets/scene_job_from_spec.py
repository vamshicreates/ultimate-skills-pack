"""Build a Maya blockout from the shared scene_spec.json.

Copy this file into the deliverable project and customize it when the production
asset needs geometry beyond the shared primitive vocabulary.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


TO_CENTIMETERS = {"mm": 0.1, "cm": 1.0, "m": 100.0, "in": 2.54, "ft": 30.48}


def _scaled(values: list[float], factor: float) -> list[float]:
    return [value * factor for value in values]


def _normalized(vector: list[float]) -> list[float]:
    length = math.sqrt(sum(value * value for value in vector))
    if length == 0:
        return [0.0, 1.0, 0.0]
    return [value / length for value in vector]


def _hex_color(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    if len(value) != 6:
        return 0.65, 0.69, 0.74
    return tuple(int(value[index : index + 2], 16) / 255.0 for index in (0, 2, 4))


def _material(cmds: Any, name: str, definition: dict[str, Any]) -> str:
    shader = cmds.shadingNode("standardSurface", asShader=True, name=f"{name}_MAT")
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{name}_SG")
    cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader", force=True)
    cmds.setAttr(f"{shader}.baseColor", *_hex_color(definition.get("color", "#a8b1bc")), type="double3")
    cmds.setAttr(f"{shader}.metalness", float(definition.get("metalness", 0.05)))
    cmds.setAttr(f"{shader}.specularRoughness", float(definition.get("roughness", 0.7)))
    return shading_group


def _tube(cmds: Any, part: dict[str, Any], factor: float) -> str:
    points = [_scaled(point, factor) for point in part["path"]]
    degree = min(3, len(points) - 1)
    path = cmds.curve(degree=degree, point=points, name=f"{part['name']}_PATH")
    tangent = _normalized([points[1][axis] - points[0][axis] for axis in range(3)])
    profile = cmds.circle(
        center=points[0],
        normal=tangent,
        radius=part["radius"] * factor,
        sections=int(part.get("radialSegments", 8)),
        constructionHistory=False,
        name=f"{part['name']}_PROFILE",
    )[0]
    result = cmds.extrude(
        profile,
        path,
        constructionHistory=False,
        range=False,
        polygon=1,
        extrudeType=2,
        useComponentPivot=True,
        fixedPath=True,
        useProfileNormal=True,
        reverseSurfaceIfPathReversed=True,
        name=part["name"],
    )[0]
    cmds.delete(profile, path)
    return result


def _extrude(cmds: Any, part: dict[str, Any], factor: float) -> str:
    profile_points = [[x * factor, y * factor, 0.0] for x, y in part["profile"]]
    profile_points.append(profile_points[0])
    profile = cmds.curve(degree=1, point=profile_points, name=f"{part['name']}_PROFILE")
    half_depth = part["depth"] * factor / 2.0
    path = cmds.curve(degree=1, point=[[0, 0, -half_depth], [0, 0, half_depth]], name=f"{part['name']}_PATH")
    result = cmds.extrude(
        profile,
        path,
        constructionHistory=False,
        range=False,
        polygon=1,
        extrudeType=2,
        useComponentPivot=True,
        fixedPath=True,
        useProfileNormal=True,
        reverseSurfaceIfPathReversed=True,
        name=part["name"],
    )[0]
    cmds.delete(profile, path)
    return result


def _part(cmds: Any, part: dict[str, Any], factor: float) -> str:
    part_type = part["type"]
    if part_type == "box":
        width, height, depth = _scaled(part["size"], factor)
        transform = cmds.polyCube(name=part["name"], width=width, height=height, depth=depth)[0]
    elif part_type == "cylinder":
        transform = cmds.polyCylinder(
            name=part["name"],
            radius=part["radius"] * factor,
            height=part["height"] * factor,
            subdivisionsX=int(part.get("radialSegments", 24)),
        )[0]
    elif part_type == "sphere":
        transform = cmds.polySphere(
            name=part["name"],
            radius=part["radius"] * factor,
            subdivisionsX=int(part.get("widthSegments", 24)),
            subdivisionsY=int(part.get("heightSegments", 16)),
        )[0]
    elif part_type == "tube":
        transform = _tube(cmds, part, factor)
    elif part_type == "extrude":
        transform = _extrude(cmds, part, factor)
    else:
        raise ValueError(f"Unsupported part type: {part_type}")

    cmds.xform(transform, translation=_scaled(part.get("position", [0, 0, 0]), factor), worldSpace=False)
    cmds.xform(transform, rotation=part.get("rotation", [0, 0, 0]), worldSpace=False)
    cmds.xform(transform, scale=part.get("scale", [1, 1, 1]), worldSpace=False)
    return transform


def build(project_dir: Path) -> Path:
    import maya.cmds as cmds

    scene_spec_path = project_dir / "scene_spec.json"
    spec = json.loads(scene_spec_path.read_text(encoding="utf-8"))
    factor = TO_CENTIMETERS[spec["units"]]

    cmds.file(new=True, force=True)
    cmds.currentUnit(linear="cm")
    root = cmds.group(empty=True, name="BLOCKOUT_GEO")
    shading_groups = {
        name: _material(cmds, name, definition)
        for name, definition in spec.get("materials", {}).items()
    }
    for part in spec["parts"]:
        transform = _part(cmds, part, factor)
        cmds.parent(transform, root)
        if part.get("material") in shading_groups:
            cmds.sets(transform, edit=True, forceElement=shading_groups[part["material"]])
        cmds.addAttr(transform, longName="sceneSpecType", dataType="string")
        cmds.setAttr(f"{transform}.sceneSpecType", part["type"], type="string")

    scene = project_dir / "scenes" / "blockout_scene.ma"
    scene.parent.mkdir(parents=True, exist_ok=True)
    cmds.file(rename=str(scene))
    cmds.file(save=True, type="mayaAscii")
    return scene
