from manim import *
import numpy as np

# Código de Manim


class ComptonScattering3D(ThreeDScene):
    def construct(self):
        visual_speed = 2.0

        wavelength_fact = 1.0
        field_strength_fact = 1.0

        wavelength = wavelength_fact * 1.5
        field_strength = field_strength_fact * 0.5
        wave_number = 2 * PI / wavelength
        omega = wave_number
        oscillation = field_strength * 1

        theta_raw = 25
        theta = theta_raw * DEGREES  # ángulo polar desde +x (dispersión)
        phi = 50 * DEGREES  # ángulo azimutal angle in the y-z plane

        compton_const = 1  # hc/m, debería ser 0.00243 nm
        delta_wavelength = compton_const * (1 - np.cos(theta))
        wavelength_f = wavelength + delta_wavelength
        wave_number_f = 2 * PI / wavelength_f

        photon_to_rest_electron_energy_ratio = 0.8
        energy_ratio = 1 / (
            1 + photon_to_rest_electron_energy_ratio * (1 - np.cos(theta))
        )
        field_strength_f = field_strength * energy_ratio

        t = ValueTracker(0)
        meeting = 7.0 / visual_speed

        #----- Para acertar la dirección del electrón
        k_in = np.array([1, 0, 0])
        n_out = np.array([
            np.cos(theta),
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
        ])

        p_in = 1.0
        p_out = energy_ratio

        recoil_vec = p_in * k_in - p_out * n_out
        recoil_dir = recoil_vec / np.linalg.norm(recoil_vec)
        recoil_speed = 1.0
        #-----

        def mk_electron():
            time = t.get_value()
            if time < meeting:
                pos = ORIGIN
            else:
                tau = time - meeting
                pos = recoil_dir * (recoil_speed * tau)
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
            phase = wave_number_f * (ss - visual_speed * tau)
            wiggle = field_strength_f * np.sin(phase) * np.cos(theta)

            electron_y = oscillation * np.sin(omega * (time - meeting))
            # source = np.array([0, electron_y, 0])
            source = ORIGIN

            points = [source + n * s + eps * w for s, w in zip(ss, wiggle)]
            wave = VMobject(color=ORANGE)
            wave.set_points_smoothly(points)
            wave.set_shade_in_3d(True)
            return wave

        incoming = always_redraw(mk_wave_in)
        outgoing = always_redraw(mk_wave_out)
        electron = always_redraw(mk_electron)

        head = Text("- Compton (relativista) -", color=WHITE, font_size=24)
        self.add_fixed_orientation_mobjects(head)
        head.to_corner(UL)

        angle = Tex(f"$\\theta = {theta_raw}^\\circ$")
        self.add_fixed_orientation_mobjects(angle)
        angle.to_corner(UR)

        self.play(FadeIn(head))
        self.play(FadeIn(angle))

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
