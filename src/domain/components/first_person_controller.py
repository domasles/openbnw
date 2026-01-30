from ursina import *


class FirstPersonController(Entity):
    def __init__(self, height=2, **kwargs):
        self.cursor = Entity(parent=camera.ui, model="quad", color=color.pink, scale=0.008, rotation_z=45)
        super().__init__()
        self.speed = 5
        self.height = height
        self.camera_pivot = Entity(parent=self, y=self.height)

        camera.parent = self.camera_pivot
        camera.position = Vec3(0, 0, -0.2)
        camera.rotation = Vec3.zero
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 1
        self.grounded = False
        self.jump_impulse = 8.0
        self.gravity_strength = 20.0
        self.y_velocity = 0

        self.traverse_target = scene
        self.ignore_list = [self]
        self.on_destroy = self.on_disable

        for key, value in kwargs.items():
            setattr(self, key, value)

        if self.gravity:
            ray = raycast(
                self.world_position + (0, self.height, 0),
                self.down,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list,
            )
            if ray.hit:
                self.y = ray.world_point.y

    def on_window_ready(self):
        camera.rotation = Vec3.zero

    def _deflect_along_wall(self, move_amount, wall_normal):
        """Deflect movement vector along wall to enable wall sliding."""
        dot_product = move_amount.x * wall_normal.x + move_amount.z * wall_normal.z
        if dot_product < 0:
            move_amount.x -= wall_normal.x * dot_product
            move_amount.z -= wall_normal.z * dot_product

    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        if self.gravity:
            # Ground detection raycast
            ray = raycast(
                self.world_position + (0, self.height, 0),
                self.down,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list,
            )

            if ray.hit and ray.distance <= self.height + 0.05:  # Small tolerance for ground contact
                # On ground - process landing
                if self.y_velocity <= 0:  # Only snap if falling, not jumping up
                    if not self.grounded:
                        self.land()
                    self.grounded = True

                    # Snap to exact ground height to prevent clipping
                    self.y = ray.world_point[1]
                    self.y_velocity = 0
            else:
                # In air
                self.grounded = False

                # Apply gravity acceleration
                self.y_velocity -= self.gravity_strength * time.dt * self.gravity

            # Apply vertical velocity (happens whether grounded or not for upward jumps)
            if self.y_velocity != 0:
                self.y += self.y_velocity * time.dt
            
            # Check for ceiling collision when jumping upward
            if self.y_velocity > 0:
                ceiling_ray = raycast(
                    self.world_position,
                    Vec3(0, 1, 0),
                    distance=self.height + 0.1,
                    traverse_target=self.traverse_target,
                    ignore=self.ignore_list
                )
                if ceiling_ray.hit and ceiling_ray.distance < self.height:
                    self.y_velocity = 0
                    self.y = ceiling_ray.world_point[1] - self.height

        if held_keys["space"] and self.grounded:
            self.jump()

        self.direction = Vec3(self.forward * (held_keys["w"] - held_keys["s"]) + self.right * (held_keys["d"] - held_keys["a"])).normalized()

        # Calculate desired movement
        move_amount = self.direction * time.dt * self.speed

        # 8-direction collision detection for comprehensive wall coverage
        check_distance = 1.0  # Lookahead distance
        safe_distance = 0.7  # Collision threshold
        
        # Define 8 directions: 4 cardinal + 4 diagonal for complete coverage
        check_directions = [
            self.forward, self.back, self.left, self.right,           # Cardinal
            self.forward + self.left, self.forward + self.right,      # Forward diagonals
            self.back + self.left, self.back + self.right             # Back diagonals
        ]
        
        # Check all directions and deflect movement along walls
        for direction in check_directions:
            ray = raycast(
                self.position + Vec3(0, 1, 0),
                direction.normalized(),
                distance=check_distance,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list,
            )

            if ray.hit and ray.distance < safe_distance:
                self._deflect_along_wall(move_amount, ray.normal)

        # Apply movement
        self.position += move_amount

    def _deflect_along_wall(self, move_amount, wall_normal):
        """Deflect movement vector along wall to enable wall sliding."""
        dot_product = move_amount.x * wall_normal.x + move_amount.z * wall_normal.z
        if dot_product < 0:
            move_amount.x -= wall_normal.x * dot_product
            move_amount.z -= wall_normal.z * dot_product

    def jump(self):
        """Apply upward velocity for physics-based jump."""
        if not self.grounded:
            return

        # Apply instant upward velocity
        self.y_velocity = self.jump_impulse
        self.grounded = False

    def land(self):
        """Called when player lands on ground."""
        self.y_velocity = 0
        self.grounded = True

    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True

        if hasattr(self, "camera_pivot") and hasattr(self, "_original_camera_transform"):
            camera.parent = self.camera_pivot
            camera.transform = self._original_camera_transform

    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False
        self._original_camera_transform = camera.transform
        camera.world_parent = scene
