from manim import *
import numpy as np

# Código de Manim


class ThomsonScattering2D(Scene):
    def construct(self):
        scale_factor = 1e6
        visual_speed = 2.0

        light_speed = 2.99e8
        c = light_speed
        electron_charge = 1
        electron_mass = 1

        # wavelength = 500e-9  # m
        # field_strength = 1e6 # V/m

        wavelength_fact = 1.0
        field_strength_fact = 1.5
        wavelength = wavelength_fact * 1.5  # m
        field_strength = field_strength_fact * 0.5  # V/m

        wave_number = 2 * PI / wavelength
        # omega = visual_speed * wave_number
        omega = wave_number

        # ángulo de scattering del fotón (no importa para Thomson)
        theta = 60 * DEGREES

        # amplitud de oscilación del electrón
        # oscillation = (electron_charge * field_strength) / (electron_mass * omega**2)
        oscillation = field_strength * 1

        t = ValueTracker(0)
        wave_meet = 7.0 / visual_speed

        def mk_wave():
            time = t.get_value()
            x_start = -7.0
            x_end = 0.0
            x_front = x_start + visual_speed * time

            draw_end = min(x_front, x_end)

            if draw_end < x_start + 0.1:
                return VMobject()

            xs = np.linspace(x_start, draw_end, 150)

            phase = wave_number * (xs - visual_speed * time)
            ys = field_strength * np.sin(phase)

            points = [np.array([x, y, 0]) for x, y in zip(xs, ys)]
            wave = VMobject(color=BLUE)
            wave.set_points_smoothly(points)
            return wave

        meeting = 7.0 / visual_speed

        def mk_wave_out():
            time = t.get_value()
            if time < meeting:
                return VMobject()

            x_start = 0.0
            x_end = 7.0
            timep = time - meeting
            x_front = x_start + visual_speed * timep

            draw_end = min(x_front, x_end)

            if draw_end < x_start + 0.1:
                return VMobject()

            xs = np.linspace(x_start, draw_end, 150)

            phase = wave_number * (xs - visual_speed * timep)
            ys = field_strength * np.sin(phase)

            points = [np.array([x, y, 0]) for x, y in zip(xs, ys)]
            wave = VMobject(color=BLUE)
            wave.set_points_smoothly(points)
            wave.rotate(45 * DEGREES, about_point=ORIGIN)
            return wave

        def mk_electron():
            time = t.get_value()
            if time < meeting:
                return Dot(ORIGIN, color=YELLOW, radius=0.12)
            else:
                y = oscillation * np.sin(omega * (time - wave_meet))
                return Dot(np.array([0, y, 0]), color=YELLOW, radius=0.12)

        incoming_photon = always_redraw(mk_wave)
        outgoing_photon = always_redraw(mk_wave_out)
        electron = always_redraw(mk_electron)

        head = Text("[ Oscilación exagerada ]", color=WHITE, font_size=24)
        head.to_corner(UL)
        self.play(FadeIn(head))

        self.play(FadeIn(electron))
        self.play(Create(incoming_photon), run_time=1.5)
        self.play(Create(outgoing_photon), run_time=1.5)
        runtime = 2 * meeting
        self.play(
            t.animate.increment_value(runtime), run_time=runtime, rate_func=linear
        )
        self.wait()


class ThomsonScattering3D(ThreeDScene):
    def construct(self):
        visual_speed = 2.0

        wavelength_fact = 1.0
        field_strength_fact = 2.5

        wavelength = wavelength_fact * 1.5
        field_strength = field_strength_fact * 0.5

        wave_number = 2 * PI / wavelength
        omega = wave_number
        oscillation = field_strength * 1

        theta = 60 * DEGREES  # ángulo polar desde +x (dispersión)
        phi = 50 * DEGREES  # ángulo azimutal angle in the y-z plane

        t = ValueTracker(0)
        meeting = 7.0 / visual_speed

        def mk_electron():
            time = t.get_value()
            if time < meeting:
                pos = ORIGIN
            else:
                pos = np.array([0, oscillation * np.sin(omega * (time - meeting)), 0])
            sphere = Sphere(radius=0.15, color=YELLOW, resolution=(18, 18))
            sphere.move_to(pos)
            sphere.set_shade_in_3d(True)
            return sphere

        def mk_wave_in():
            time = t.get_value()
            x_start, x_end = -7.0, 0.0
            x_front = x_start + visual_speed * time
            draw_end = min(x_front, x_end)
            if draw_end < x_start + 0.1:
                return VMobject()

            xs = np.linspace(x_start, draw_end, 150)
            phase = wave_number * (xs - visual_speed * time)
            ys = field_strength * np.sin(phase)
            points = [np.array([x, y, 0]) for x, y in zip(xs, ys)]
            wave = VMobject(color=BLUE)
            wave.set_points_smoothly(points)
            wave.set_shade_in_3d(True)
            return wave

        def mk_wave_out():
            time = t.get_value()
            if time < meeting:
                return VMobject()
            tau = time - meeting

            n = np.array(
                [
                    np.cos(theta),
                    np.sin(theta) * np.cos(phi),
                    np.sin(theta) * np.sin(phi),
                ]
            )
            eps = np.array([0, 1, 0]) - np.dot([0, 1, 0], n) * n
            eps = eps / np.linalg.norm(eps)

            front = min(visual_speed * tau, 7.0)
            if front < 0.1:
                return VMobject()
            ss = np.linspace(0, front, 150)
            phase = wave_number * (ss - visual_speed * tau)
            wiggle = field_strength * np.sin(phase) * np.cos(theta)

            electron_y = oscillation * np.sin(omega * (time - meeting))
            # source = np.array([0, electron_y, 0]) # para que el fotón dispersado salga del electrón
            source = ORIGIN

            points = [source + n * s + eps * w for s, w in zip(ss, wiggle)]
            wave = VMobject(color=TEAL)
            wave.set_points_smoothly(points)
            wave.set_shade_in_3d(True)
            return wave

        incoming = always_redraw(mk_wave_in)
        outgoing = always_redraw(mk_wave_out)
        electron = always_redraw(mk_electron)

        head = Text("[ Oscilación exagerada ]", color=WHITE, font_size=24)
        self.add_fixed_orientation_mobjects(head)
        # head.move_to([-5,3,0])
        head.to_corner(UL)
        self.play(FadeIn(head))

        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=0.9)

        axes = ThreeDAxes(x_range=[-7, 7, 1], y_range=[-3, 3, 1], z_range=[-3, 3, 1])

        self.add(axes, electron, incoming, outgoing)

        runtime = 2 * meeting
        self.play(
            t.animate.increment_value(runtime), run_time=runtime, rate_func=linear
        )

        self.begin_ambient_camera_rotation(rate=0.15)
        self.play(t.animate.increment_value(4), run_time=4, rate_func=linear)
        self.stop_ambient_camera_rotation()
        self.wait()
