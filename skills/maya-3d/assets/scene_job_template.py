"""Minimal Maya job interface. Replace the sample object with the requested design."""

from pathlib import Path


def build(project_dir: Path) -> Path:
    import maya.cmds as cmds

    root = cmds.group(empty=True, name="GEO")
    object_transform = cmds.polyCube(name="sample_object", width=2, height=2, depth=2)[0]
    cmds.parent(object_transform, root)

    scene = project_dir / "scenes" / "sample_scene.ma"
    scene.parent.mkdir(parents=True, exist_ok=True)
    cmds.file(rename=str(scene))
    cmds.file(save=True, type="mayaAscii")
    return scene
