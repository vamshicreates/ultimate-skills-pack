# Platform, execution, and rendering reference

This reference was checked against Autodesk documentation in October 2026. Verify the installed product's own help for version-dependent flags and plug-ins.

## Windows and macOS

Maya 2026 supports Windows 10/11 and macOS 13–15, including Apple silicon and Intel Macs. Check the system requirements of the installed version rather than applying those ranges to every release. `mayapy` is normally under `C:\Program Files\Autodesk\Maya<version>\bin\mayapy.exe` on Windows or `/Applications/Autodesk/maya<version>/Maya.app/Contents/bin/mayapy` on macOS. Autodesk also documents running scripts from Maya's Python Script Editor.

Use `pathlib.Path`, subprocess argument lists, and `sys.executable` or the discovered `mayapy` path. Do not hard-code `/`, drive letters, shell quoting, or a particular Python minor version. Maya's own Python environment and license must be available. External `mayapy` programs initialize and uninitialize `maya.standalone`; scripts run inside Maya do not.

## Projects and formats

The Maya project is rooted at `workspace.mel`; `scenes`, `sourceimages`, and rendered image folders are resolved through workspace rules. Native `.ma` and `.mb` preserve the full Maya scene. FBX, USD, OBJ, and Alembic are interchange formats with differing support for materials, animation, cameras, or scene nodes; choose according to the receiving app and test round trips when compatibility matters. Do not assume a newer native scene opens in an older Maya release.

## Rendering

Prefer a simple preview using the available renderer and licensed features. Arnold rendering inside Maya's UI can be watermark-free under a Maya license; Arnold command-line or batch rendering requires a separate Arnold license for watermark-free output. If that license is unavailable, use Maya's interactive Render Sequence for Arnold or another installed renderer; do not promise an automated Arnold batch render. Arnold GPU support and device availability are system specific, so CPU is the conservative choice unless verified. Record renderer, resolution, and whether the image was actually rendered.

## Autodesk sources

- [Maya 2026 system requirements](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/System-Requirements-for-Autodesk-Maya-2026.html)
- [The `mayapy` interpreter and platform paths](https://help.autodesk.com/cloudhelp/2025/ENU/Maya-Scripting/files/GUID-D64ACA64-2566-42B3-BE0F-BCE843A1702F.htm)
- [Initialize Maya Python externally](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-Scripting/files/GUID-D457D6A0-1E7F-4ED2-B0B4-8B57153B563B.htm)
- [Maya project/workspace command](https://help.autodesk.com/cloudhelp/2022/ENU/Maya-Tech-Docs/CommandsPython/workspace.html)
- [Maya project folders and relative paths](https://help.autodesk.com/cloudhelp/2022/ENU/Maya-ManagingScenes/files/GUID-D5CA162A-0956-49C6-9FAC-2F73DCF03409.htm)
- [Supported export formats](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-ManagingScenes/files/GUID-864BD203-C437-4481-8BFC-3A6C1D2C824C.htm)
- [Maya USD import/export](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-USD/files/USD-for-Maya/GUID-2755A1ED-4857-4111-8571-5D658EE90FA0.html)
- [Image plane command](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-Tech-Docs/Commands/imagePlane.html)
- [Arnold licensing](https://help.autodesk.com/cloudhelp/ENU/AR-Core/files/arnold-setup/arnold_user_guide_arnold_setup_ac_licensing_home_html.html)
- [Maya Script Editor](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-Scripting/files/GUID-B66020CC-1BBE-4EA1-B1DE-A288B044DD80.htm)
