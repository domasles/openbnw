from ursina import *


class FirstPersonController(Entity):
    def __init__(self, height=2, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        self.speed = 5
        self.height = height
        self.camera_pivot = Entity(parent=self, y=self.height)

        camera.parent = self.camera_pivot
        camera.position = Vec3(0, 0, -0.2)  # Offset backward to stay inside collision sphere
        camera.rotation = Vec3.zero
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        self.gravity = 1
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35
        self.jumping = False
        self.air_time = 0

        self.traverse_target = scene
        self.ignore_list = [self, ]
        self.on_destroy = self.on_disable

        for key, value in kwargs.items():
            setattr(self, key ,value)

        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)
            if ray.hit:
                self.y = ray.world_point.y


    def on_window_ready(self):
        camera.rotation = Vec3.zero


    def update(self):
        # Rotate entire player entity with mouse horizontal movement
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        # Camera pivot handles vertical look (pitch)
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x= clamp(self.camera_pivot.rotation_x, -90, 90)

        # Calculate movement direction (now in player's local space)
        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()

        # Calculate desired movement
        move_amount = self.direction * time.dt * self.speed
        
        # Cast rays in player's facing directions (accounts for rotation)
        # Camera is offset backward, so collision sphere protects it
        check_distance = 1.0  # Must be > camera offset (0.2) + collision radius
        safe_distance = 0.7
        
        # Check in actual movement direction and perpendiculars
        if move_amount.length() > 0:
            # Forward ray in movement direction
            forward_ray = raycast(
                self.position + Vec3(0, 1, 0),
                move_amount.normalized(),
                distance=check_distance,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list
            )
            
            if forward_ray.hit and forward_ray.distance < safe_distance:
                # Deflect velocity along wall
                dot_product = move_amount.x * forward_ray.normal.x + move_amount.z * forward_ray.normal.z
                if dot_product < 0:
                    move_amount.x -= forward_ray.normal.x * dot_product
                    move_amount.z -= forward_ray.normal.z * dot_product
        
        # Additional safety checks in cardinal directions relative to player
        for direction in [self.forward, self.back, self.right, self.left]:
            ray = raycast(
                self.position + Vec3(0, 1, 0),
                direction,
                distance=check_distance,
                traverse_target=self.traverse_target,
                ignore=self.ignore_list
            )
            
            if ray.hit and ray.distance < safe_distance:
                dot_product = move_amount.x * ray.normal.x + move_amount.z * ray.normal.z
                if dot_product < 0:
                    move_amount.x -= ray.normal.x * dot_product
                    move_amount.z -= ray.normal.z * dot_product
        
        # Apply movement
        self.position += move_amount

        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)

            if ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True

                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity


    def input(self, key):
        if key == 'space':
            self.jump()

    def jump(self):
        if not self.grounded:
            return

        self.grounded = False
        self.animate_y(self.y+self.jump_height, self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fall_after)


    def start_fall(self):
        self.y_animator.pause()
        self.jumping = False

    def land(self):
        self.air_time = 0
        self.grounded = True


    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True

        if hasattr(self, 'camera_pivot') and hasattr(self, '_original_camera_transform'):
            camera.parent = self.camera_pivot
            camera.transform = self._original_camera_transform


    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False
        self._original_camera_transform = camera.transform
        camera.world_parent = scene
