# Hard-Surface Non-Destructive Modeling Blueprint

**Category:** `topology` / `modifiers`  
**Purpose:** Create clean, production-ready curved, beveled, and mechanical geometry in Blender without shading artifacts or messy vertices.

---

## 1. Core Golden Rules
1. **Never use raw Box Primitives without Bevel or Subdivision**:
   - Real objects in the physical world have no infinite sharp edges. An edge without a highlight breaks photorealism.
2. **The 3-Modifier Stack Standard**:
   - `Bevel` (Weight or Angle mode) -> `Weighted Normal` (Keep Sharp=True) -> `Subdivision Surface` (Render: 2, Viewport: 1).
3. **Keep Quads Around Cylinders**:
   - When joining cylinders or tubes to flat planes, inset (`I`) the face first to create a supporting buffer loop before extruding (`E`).

---

## 2. Python (`bpy`) Automation Templates

### A. Rounded Beveled Cube with Clean Highlights
```python
import bpy

# Create base cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
obj = bpy.context.active_object
obj.name = "HardSurface_Base"

# Smooth Shading
bpy.ops.object.shade_smooth()
obj.data.use_auto_smooth = True

# Add Bevel Modifier
bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.05
bevel.segments = 4
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 0.523599  # 30 degrees

# Add Weighted Normal (Prevents shading distortion across flat surfaces)
wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
wn.keep_sharp = True
```

### B. Curved Tubing / Piping (Bezier Curve to Bevel)
```python
import bpy

# Curve-based wires or pipes are 100x cleaner than manual cylinder extrusion
curve_data = bpy.data.curves.new(name="PipeCurve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.bevel_depth = 0.08  # Pipe radius
curve_data.bevel_resolution = 4

polyline = curve_data.splines.new('BEZIER')
polyline.bezier_points.add(2)

# Point 0
polyline.bezier_points[0].co = (0, 0, 0)
polyline.bezier_points[0].handle_left = (-0.5, 0, 0)
polyline.bezier_points[0].handle_right = (0.5, 0, 0)

# Point 1
polyline.bezier_points[1].co = (1, 1, 1)
polyline.bezier_points[1].handle_left = (0.5, 1, 1)
polyline.bezier_points[1].handle_right = (1.5, 1, 1)

# Point 2
polyline.bezier_points[2].co = (2, 0, 1.5)

pipe_obj = bpy.data.objects.new("Cable_Mesh", curve_data)
bpy.context.collection.objects.link(pipe_obj)
```
