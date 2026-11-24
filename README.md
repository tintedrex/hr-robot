# hr-robot

Humanoid Robot (HR) software workspace — ROS 2 **Humble**, Jetson / real-time MCU / drives control stack.

Software requirements: [`docs/HR-SRS-SW-v0.1.md`](docs/HR-SRS-SW-v0.1.md) (ISO/IEC/IEEE 29148).

## What you get

| Piece | Purpose |
| --- | --- |
| `src/` | ROS 2 Humble colcon workspace |
| `docker/` | Dev container image (Humble + build tools) |
| `docs/` | SRS and branch rules |
| `.github/` | PR template + CI build workflow |

## Quick start (Docker — recommended on Windows)

Prerequisites: [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 backend.

```bash
# From repo root
docker compose build
docker compose run --rm hr-dev
```

Inside the container:

```bash
cd /ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch hr_bringup bringup.launch.py
```

## Native build (Linux / WSL2 with ROS 2 Humble)

```bash
source /opt/ros/humble/setup.bash
cd /path/to/hr-robot
rosdep update
rosdep install --from-paths src -y --ignore-src
colcon build --symlink-install
source install/setup.bash
```

## Workspace layout

```text
hr-robot/
  src/
    hr_msgs/          # shared messages / interfaces
    hr_bringup/       # launch + config entrypoint
    hr_balance_jetson/# Jetson-side balance outer loop (stub)
  docker/
    Dockerfile
    docker-compose.yml
  docs/
    HR-SRS-SW-v0.1.md
    BRANCH_RULES.md
```

## Branch rules (summary)

- Default branch: `main` (protected).
- Work on `feature/*` or `fix/*`; open a PR into `main`.
- Require CI (`colcon build`) to pass before merge.
- Full policy: [`docs/BRANCH_RULES.md`](docs/BRANCH_RULES.md).

## Packages (v0.1 stubs)

| Package | Control level | Notes |
| --- | --- | --- |
| `hr_msgs` | System | Messages for mode, faults, balance refs |
| `hr_bringup` | System | Launch file wiring stubs together |
| `hr_balance_jetson` | Jetson | Outer balance node stub (SW-BAL-002) |

MCU and drive firmware live outside this ROS workspace; they talk to Jetson over the ICD defined in the SRS.

## Create / connect GitHub remote

If this folder is not yet on GitHub:

```bash
# Install GitHub CLI, then:
gh auth login
gh repo create hr-robot --private --source=. --remote=origin --push
```

Then apply branch protection (see `docs/BRANCH_RULES.md`).

## License

Internal engineering — all rights reserved until otherwise stated.
